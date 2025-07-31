import requests
from bs4 import BeautifulSoup
import newspaper
import time
import difflib
from datetime import datetime, timezone, timedelta
from urllib.parse import urljoin, urlparse, urlunparse
from news_list import TARGET_SITES, CHECK_INTERVAL_SECONDS, MONGO_URI, MONGO_DB_NAME, MONGO_COLLECTION_NAME, STOCK_CODE
from pymongo import MongoClient
from collections import deque
from concurrent.futures import ThreadPoolExecutor, as_completed
from identify_company_module import identify_company  # 실제 모듈명에 맞게 수정
from confluent_kafka import Producer  # confluent-kafka 사용
import json
import re

maxlen = 100

# 설정
KST = timezone(timedelta(hours=9))
SCRIPT_START_TIME = datetime.utcnow().replace(tzinfo=timezone.utc).astimezone(KST)
recent_titles = deque(maxlen=maxlen)
processed_urls = deque(maxlen=maxlen)

# Kafka Producer 설정 (confluent-kafka 방식)
kafka_config = {
    'bootstrap.servers': 'localhost:9092',
    'client.id': 'news-monitor-producer',
    'compression.type': 'gzip',
    'batch.size': 16384,
    'linger.ms': 10,
}

producer = Producer(kafka_config)

def delivery_callback(err, msg):
    """Kafka 메시지 전송 결과 콜백"""
    if err is not None:
        print(f"[ERROR] Kafka 발행 실패: {err}")
    else:
        print(f"  [Kafka 발행 성공] Topic: {msg.topic()}, Partition: {msg.partition()}")

session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36',
    'Referer': 'https://dealsite.co.kr/',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'ko,en-US;q=0.9,en;q=0.8',
    'Connection': 'keep-alive'
})

last_seen_urls = {
    f"{site['name']} - {site.get('category', '')}": None for site in TARGET_SITES
}

client = MongoClient(MONGO_URI)
db = client[MONGO_DB_NAME]
articles_collection = db[MONGO_COLLECTION_NAME]

def localize_to_kst(dt):
    if dt is None:
        return None
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc).astimezone(KST)
    return dt.astimezone(KST)

def clean_url(url):
    parsed = urlparse(url)
    return urlunparse(parsed._replace(query=""))

def fetch_article_details(url, site=None):
    try:
        article = newspaper.Article(url, language='ko')
        article.download()
        article.parse()
        publish_time = localize_to_kst(article.publish_date)

        return {
            'title': article.title,
            'text': article.text,
            'publish_time': publish_time,
            'url': url
        }

    except Exception as e:
        print(f"[ERROR] 기사 처리 중 오류 (건너뜀): {url}\n  └ {e}")
        return None

def send_article_to_kafka(article_data):
    """confluent-kafka를 사용한 메시지 발행"""
    try:
        # JSON 직렬화
        message_value = json.dumps(article_data, ensure_ascii=False).encode('utf-8')
        
        # 메시지 발행 (비동기)
        producer.produce(
            topic='news',
            value=message_value,
            callback=delivery_callback
        )
        
        # 버퍼 플러시 (즉시 전송)
        producer.flush(timeout=5)
        
        print(f"  [Kafka 발행] ({article_data['publisher']}) {article_data['title'][:50]}...")
        
    except Exception as e:
        print(f"[ERROR] Kafka 발행 실패: {e}")

def get_latest_articles(site):
    try:
        if not site.get('selector'):
            print(f"[ERROR] {site['name']} - {site.get('category', '')} → selector 누락")
            return []

        res = session.get(site['url'], timeout=10)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, 'html.parser')

        if site.get("container_selector"):
            container = soup.select_one(site["container_selector"])
            if not container:
                print(f"[ERROR] {site['name']} → container_selector 영역을 찾을 수 없습니다.")
                return []
            links = container.select(site["selector"])
        else:
            links = soup.select(site["selector"])

        articles = []
        for a in links:
            href = a.get('href')
            if not href or site['pattern'] not in href:
                continue

            # 제목 추출
            # 언론사별로 제목 태그 분기 처리
            if site['name'] in ["매일경제", "헤럴드경제", "한겨레"]:
                if site['name'] == "매일경제":
                    title_tag = a.select_one("h3.news_ttl")
                elif site['name'] == "헤럴드경제":
                    title_tag = a.select_one("p.news_title")
                elif site['name'] == "한겨레":
                    title_tag = a.select_one("div.BaseArticleCard_title__TVFqt")
                if not title_tag:
                    continue
                title = title_tag.get_text(strip=True)
            else:
                title = a.get_text(strip=True)
            full_url = urljoin(site['base_url'], href)

            img_url = None

            # 매일경제 전용 처리
            if site['name'] == "매일경제":
                parent_container = a.find_parent('li', class_='news_node')
                if parent_container:
                    img_tag = parent_container.select_one('div.thumb_area > img')
                    if img_tag:
                        if img_tag.has_attr('data-src') and img_tag['data-src'].strip():
                            img_url = img_tag['data-src']
                        elif img_tag.has_attr('src') and img_tag['src'].strip():
                            img_url = img_tag['src']
                        img_url = urljoin(site['base_url'], img_url)
                # 매일경제 전용 처리 후 일반 로직은 타지 않음
            else:
                # 일반 이미지 추출 로직
                parent_container = a.find_parent(['li', 'div', 'article'])
                img_tag = None
                if parent_container:
                    img_tag = parent_container.select_one(site['image_selector'])
                if not img_tag:
                    img_tag = a.select_one('img')
                if not img_tag:
                    img_tag = soup.select_one(f"a[href='{href}'] img")
                if img_tag:
                    img_url = img_tag.get('data-src') or img_tag.get('src')
                    if img_url:
                        img_url = urljoin(site['base_url'], img_url)

            # 4️⃣ 백업: data-share-img 속성 확인
            if not img_url:
                share_div = parent_container.select_one("div[class^='share-data-']")
                if share_div and share_div.has_attr("data-share-img"):
                    img_url = share_div["data-share-img"]




            articles.append({
                'title': title,
                'url': full_url,
                'image': img_url if img_url else None  # ✅ 이미지 없으면 None
            })

        return articles
    except Exception as e:
        print(f"[ERROR] 목록 수집 실패 ({site['name']}) → {e}")
        return []


def monitor_news():
    print("\n[실시간 뉴스 모니터링 시작]")
    print(f"  기준 시간: {SCRIPT_START_TIME.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  Kafka 설정: {kafka_config['bootstrap.servers']}")
    first_run = True

    while True:
        with ThreadPoolExecutor(max_workers=8) as executor:
            futures = {executor.submit(get_latest_articles, site): site for site in TARGET_SITES if not site.get('dynamic')}

            for future in as_completed(futures):
                site = futures[future]
                try:
                    article_list = future.result()
                except Exception as e:
                    print(f"[ERROR] {site['name']} 처리 실패 → {e}")
                    continue

                site_key = f"{site['name']} - {site.get('category', '')}"
                if not article_list:
                    continue
                

                top_article = article_list[0]
                top_url = top_article['url']
                top_title = top_article['title']
                top_image = top_article['image']  # ✅ 이미지 URL 추출

                if first_run:
                    last_seen_urls[site_key] = top_url
                    print(f"  🔹 [{site_key}] 초기 기준 기사 설정: {top_title}")
                    continue

                if top_url == last_seen_urls[site_key]:
                    continue

                details = fetch_article_details(top_url, site=site)
                if not details:
                    continue

                pub_time = localize_to_kst(details['publish_time']) if details['publish_time'] else datetime.now(KST)

                if pub_time < SCRIPT_START_TIME:
                    continue

                if top_title in recent_titles or top_url in processed_urls:
                    continue

                recent_titles.append(top_title)
                processed_urls.append(top_url)

                # 기업 태깅
                company_name, max_score, _ = identify_company(details['title'], details['text'])
                company_code = None if company_name in ["미국", "코스피", "다른기업"] else STOCK_CODE.get(company_name)

                # ✅ Kafka 발행 데이터 (이미지 URL 추가)
                article_data = {
                    "publisher": site['name'],
                    "category": site.get('category', 'N/A'),
                    "title": details['title'],
                    "published_date": pub_time.strftime('%Y-%m-%d %H:%M:%S'),
                    "content": details['text'],
                    "url": top_url,
                    "image_url": top_image if top_image else None,  # ✅ 이미지 URL 추가
                    "company_tag": company_name,
                    "company_score": max_score,
                    "stock_code": company_code,
                    "crawled_at": datetime.now(KST).strftime('%Y-%m-%d %H:%M:%S')
                }

                send_article_to_kafka(article_data)
                last_seen_urls[site_key] = top_url
                print(f"  ✅ 기준 기사 업데이트: {site_key} → {top_title[:50]}... (이미지: { '있음' if top_image else '없음'})")

        first_run = False
        print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 다음 체크까지 {CHECK_INTERVAL_SECONDS}초 대기...")
        time.sleep(CHECK_INTERVAL_SECONDS)


if __name__ == "__main__":
    try:
        monitor_news()
    except KeyboardInterrupt:
        print("\n[종료] 사용자에 의해 중단됨")
    except Exception as e:
        print(f"[ERROR] 예기치 못한 오류: {e}")
    finally:
        print("\n[정리] 리소스 정리 중...")
        try:
            producer.flush(timeout=10)  # 남은 메시지 전송
            client.close()
            print("  MongoDB 연결 종료 완료")
            print("  Kafka Producer 종료 완료")
        except Exception as e:
            print(f"[ERROR] 리소스 정리 중 오류: {e}")