# producer.py (전체 코드)

import requests
from bs4 import BeautifulSoup
import newspaper
import time
from datetime import datetime, timezone, timedelta
from urllib.parse import urljoin
from kafka import KafkaProducer
import json
import re
from collections import deque
from concurrent.futures import ThreadPoolExecutor, as_completed

# ----------------- 설정 파일 import -----------------
# 아래 파일들이 .py와 같은 폴더에 있어야 합니다.
from news_list import TARGET_SITES, CHECK_INTERVAL_SECONDS, STOCK_CODE 
from identify_company_module import identify_company 

# ----------------- 전역 변수 및 설정 -----------------
KST = timezone(timedelta(hours=9))
SCRIPT_START_TIME = datetime.utcnow().replace(tzinfo=timezone.utc).astimezone(KST)
recent_titles = deque(maxlen=100)
processed_urls = deque(maxlen=100)
last_seen_urls = {f"{site['name']} - {site.get('category', '')}": None for site in TARGET_SITES}

# ----------------- Kafka Producer 설정 -----------------
# ⚠️ 중요: Kafka 서버가 실행 중인 PC의 IP 주소로 변경해야 합니다.
# 만약 맥에서 Kafka 서버를 실행 중이라면, 'localhost' 대신 맥의 내부 IP 주소를 입력하세요.
# 예: bootstrap_servers=['192.168.1.10:9092']
try:
    producer = KafkaProducer(
        bootstrap_servers=['localhost:9092'],
        value_serializer=lambda v: json.dumps(v, ensure_ascii=False).encode('utf-8')
    )
    print("✅ Kafka Producer에 성공적으로 연결되었습니다.")
except Exception as e:
    print(f"❌ Kafka Producer 연결에 실패했습니다. bootstrap_servers 주소를 확인하세요.")
    print(f"오류: {e}")
    exit()

# ----------------- 세션 및 헬퍼 함수 -----------------
session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36',
})

def localize_to_kst(dt):
    if dt is None: return None
    if dt.tzinfo is None: return dt.replace(tzinfo=timezone.utc).astimezone(KST)
    return dt.astimezone(KST)

def fetch_article_details(url):
    try:
        article = newspaper.Article(url, language='ko')
        article.download()
        article.parse()
        return {
            'title': article.title,
            'text': article.text,
            'publish_time': localize_to_kst(article.publish_date),
        }
    except Exception as e:
        print(f"[ERROR] 기사 상세 내용 처리 중 오류 (건너뜀): {url}\n  └ {e}")
        return None

# ----------------- 뉴스 수집 및 처리 함수 -----------------
def get_latest_articles(site):
    try:
        res = session.get(site['url'], timeout=10)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, 'html.parser')

        container = soup.select_one(site.get("container_selector", "body"))
        if not container:
            # print(f"[INFO] {site['name']} → container_selector 영역을 찾을 수 없음. body 전체에서 탐색합니다.")
            container = soup
        
        links = container.select(site["selector"])
        articles = []
        for a in links:
            href = a.get('href')
            if not href or site.get('pattern', '') not in href:
                continue

            # 제목 추출 로직 (언론사별 대응)
            title = a.get_text(strip=True)
            if site['name'] == "매일경제":
                title_tag = a.select_one("h3.news_ttl")
                if title_tag: title = title_tag.get_text(strip=True)
            elif site['name'] == "헤럴드경제":
                title_tag = a.select_one("p.news_title")
                if title_tag: title = title_tag.get_text(strip=True)
            elif site['name'] == "한겨레":
                title_tag = a.select_one("div.BaseArticleCard_title__TVFqt")
                if title_tag: title = title_tag.get_text(strip=True)
                
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


            articles.append({'title': title, 'url': full_url, 'image': img_url})
        return articles
    except Exception as e:
        print(f"[ERROR] 목록 수집 실패 ({site['name']}) → {e}")
        return []

def send_article_to_kafka(article_data):
    """kafka-python을 사용하여 컨슈머가 원하는 형식으로 메시지 발행"""
    try:
        producer.send("news", value=article_data)
        print(f"🚀 메시지 발행: [{article_data['company']}] {article_data['title'][:40]}...")
    except Exception as e:
        print(f"[ERROR] Kafka 메시지 발행 실패: {e}")

# ----------------- 메인 모니터링 로직 -----------------
def monitor_news():
    print("\n[실시간 뉴스 모니터링 시작]")
    print(f"  - Kafka Server: {producer.config['bootstrap_servers']}")
    first_run = True

    while True:
        with ThreadPoolExecutor(max_workers=8) as executor:
            future_to_site = {executor.submit(get_latest_articles, site): site for site in TARGET_SITES}
            for future in as_completed(future_to_site):
                site = future_to_site[future]
                site_key = f"{site['name']} - {site.get('category', '')}"
                
                try:
                    article_list = future.result()
                    if not article_list: continue

                    top_article = article_list[0]
                    top_url = top_article['url']
                    
                    if first_run:
                        last_seen_urls[site_key] = top_url
                        # print(f"  🔹 [{site_key}] 초기 기준 기사 설정 완료.")
                        continue

                    if top_url == last_seen_urls[site_key]: continue
                    
                    # 새 기사 발견 시 로직
                    last_seen_urls[site_key] = top_url
                    if top_article['title'] in recent_titles or top_url in processed_urls: continue
                    
                    print(f"\n✨ 새 기사 발견: [{site['name']}] {top_article['title']}")
                    recent_titles.append(top_article['title'])
                    processed_urls.append(top_url)
                    
                    details = fetch_article_details(top_url)
                    if not details: continue
                    
                    # 기업명 태깅
                    company_name, _, _ = identify_company(details['title'], details['text'])
                    company_code = STOCK_CODE.get(company_name)
                    
                    # 유효한 회사 코드가 식별된 경우에만 카프카로 전송
                    if not company_code:
                        print(f"  ⚠️ 기사 건너뜀 (관련 기업 코드 없음)")
                        continue
                    
                    pub_time = details.get('publish_time') or datetime.now(KST)

                    # 컨슈머가 기대하는 최종 데이터 형식으로 조립
                    article_data = {
                        "company": company_name,
                        "code": company_code,
                        "link": top_url,
                        "press": site['name'],
                        "published_at": pub_time.strftime('%Y-%m-%d %H:%M:%S'),
                        "title": details['title'],
                        "image_url": top_article.get('image'),
                        "content": details['text']
                    }
                    
                    send_article_to_kafka(article_data)

                except Exception as e:
                    print(f"[ERROR] {site['name']} 처리 중 오류 발생: {e}")
        
        if first_run:
            print("\n초기 기준 설정이 모두 완료되었습니다. 지금부터 새로운 뉴스를 감시합니다.")
            first_run = False
            
        print(f"\n[{datetime.now(KST).strftime('%H:%M:%S')}] 다음 체크까지 {CHECK_INTERVAL_SECONDS}초 대기...")
        time.sleep(CHECK_INTERVAL_SECONDS)

# ----------------- 프로그램 시작 -----------------
if __name__ == "__main__":
    try:
        monitor_news()
    except KeyboardInterrupt:
        print("\n\n[프로그램 종료] 사용자에 의해 중단됨.")
    except Exception as e:
        print(f"\n[치명적 오류] 예기치 못한 오류로 프로그램을 종료합니다: {e}")
    finally:
        print("\n[정리] 리소스 정리 중...")
        if 'producer' in locals() and producer:
            producer.flush(timeout=10)
            producer.close()
            print("  - Kafka Producer 연결 종료 완료")
        print("프로그램을 완전히 종료합니다.")