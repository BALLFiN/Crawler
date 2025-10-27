import json
import pymongo
import re
from pymongo import MongoClient
from datetime import datetime
import _config as cfg

# --- industry_classification.py에서 분류 데이터 가져오기 ---
from industry_whitelist import corp_to_category

# --- 설정 부분 ---
MONGO_URI = cfg.MONGO_URI
MONGO_DB_NAME = cfg.MONGO_DB_NAME
MONGO_COLLECTION_NAME = cfg.MONGO_COLLECTION_NAME
KEY_WORD_FILE_PATH = 'company_whitelist.json'  # "미국", "코스피"가 여기에 포함되어야 함
OUTPUT_FILE_PATH = 'classified_articles_all.json'

# [변경] 1. MongoDB의 날짜 필드 이름
MONGO_DATE_FIELD = 'published_date'
# [변경] 2. MongoDB와 JSON에서 사용되는 날짜 '문자열' 형식
DATE_STRING_FORMAT = '%Y-%m-%d %H:%M:%S'


# ---------------------


def load_keywords(file_path):
    """지정된 경로에서 JSON 파일을 읽어 키워드 데이터를 반환합니다."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            print(f"'{file_path}' 파일에서 키워드를 불러옵니다.")
            return json.load(f)
    except FileNotFoundError:
        print(f"에러: '{file_path}' 파일을 찾을 수 없습니다.")
        return None
    except json.JSONDecodeError:
        print(f"에러: '{file_path}' 파일의 형식이 올바르지 않습니다.")
        return None


def preprocess_text(text):
    """뉴스 본문에서 불필요한 공통 패턴들을 제거합니다."""
    patterns_to_remove = [
        # 1. '카카오톡'/'카톡' 문자열 자체를 다른 모든 패턴보다 먼저 제거
        r'(카카오톡|카톡)',

        r'[\w\.-]+@[\w\.-]+', r'\w+\s*(기자|특파원|앵커|인턴기자)', r'\[.*?\]|\(.*?\)',
        r'무단 ?전재[ -]?재배포 금지', r'재판매 ?및 ?DB ?금지', r'저작권자ⓒ',

        # 2. '카카오톡'이 이미 지워졌으므로, ID/제보 관련 패턴에서는 제외
        r'(?:텔레그램|페이스북)\s*ID\s*:?\s*[\w\.]+',
        r'제보\s*([=:]|는)?\s*\S+',
        r'https?:\/\/\S+',
    ]
    cleaned_text = text
    for pattern in patterns_to_remove:
        cleaned_text = re.sub(pattern, ' ', cleaned_text)

    cleaned_text = re.sub(r'\s+', ' ', cleaned_text).strip()
    return cleaned_text


def find_mentioned_corps(text_to_search, keywords_data):
    """주어진 텍스트에서 언급된 모든 기업의 이름을 set으로 반환합니다."""
    found_corps = set()
    for corp_name, data in keywords_data.items():
        for keyword in data['keywords']:
            if re.search(r'\b' + re.escape(keyword.lower()) + r'\b', text_to_search):
                found_corps.add(corp_name)
                break
    return found_corps


def load_existing_data_and_get_latest_date(file_path, date_field_name):
    """
    JSON 파일을 읽어 데이터 리스트와 가장 최신 날짜 '문자열'을 반환합니다.
    """
    existing_data = []
    latest_date_string = None

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            existing_data = json.load(f)
            if not isinstance(existing_data, list):
                print(f"경고: '{file_path}' 파일의 형식이 리스트가 아닙니다. 새롭게 시작합니다.")
                existing_data = []

            print(f"'{file_path}' 파일에서 {len(existing_data)}개의 기존 데이터를 불러왔습니다.")

        if existing_data:
            all_date_strings = []
            for article in existing_data:
                if isinstance(article, dict):
                    date_str = article.get(date_field_name)
                    if date_str and isinstance(date_str, str):
                        try:
                            datetime.strptime(date_str, DATE_STRING_FORMAT)  # 형식 검증
                            all_date_strings.append(date_str)
                        except (ValueError, TypeError):
                            print(f"경고: 기존 파일에서 잘못된 날짜 형식({date_str})을 건너뜁니다.")
                            pass

            if all_date_strings:
                latest_date_string = max(all_date_strings)
                print(f"파일에서 확인된 가장 최신 기사 날짜(string): {latest_date_string}")

    except FileNotFoundError:
        print(f"'{file_path}' 파일이 없습니다. DB에서 모든 데이터를 새로 가져옵니다.")
    except json.JSONDecodeError:
        print(f"에러: '{file_path}' 파일 형식이 잘못되었습니다. 데이터를 새로 가져옵니다.")
        existing_data = []
    except Exception as e:
        print(f"기존 파일 로드 중 예외 발생: {e}. 데이터를 새로 가져옵니다.")
        existing_data = []

    return existing_data, latest_date_string


# --- [신규] 리팩토링된 헬퍼 함수 ---
def get_classification(matches_set, category_map):
    """
    탐지된 기업명(set)을 기반으로 기업명과 산업군을 분류하여 반환합니다.
    '미국', '코스피'는 산업군을 '분류 없음'으로 처리합니다.
    """
    identified_corp = "미분류"
    industry_category = "분류 없음"

    match_count = len(matches_set)

    if match_count == 1:
        # 1. 한 개 기업만 매칭된 경우
        identified_corp = list(matches_set)[0]
        if identified_corp == "미국" or identified_corp == "코스피":
            industry_category = "분류 없음"
        else:
            industry_category = category_map.get(identified_corp, "분류 없음")

    elif match_count > 1:
        # 2. 여러 기업이 매칭된 경우
        identified_corp = sorted(list(matches_set))
        industry_list = []
        for c in identified_corp:
            if c == "미국" or c == "코스피":
                industry_list.append("분류 없음")
            else:
                industry_list.append(category_map.get(c, "분류 없음"))
        industry_category = industry_list

    # 3. 매칭된 기업이 없는 경우 (match_count == 0)
    #    -> 기본값 ("미분류", "분류 없음")이 반환됨

    return identified_corp, industry_category


# -----------------------------------


def classify_news_and_add_industry():
    """
    MongoDB에서 '가장 최신 날짜 문자열' 이후의 새 뉴스만 가져와 분류하고
    기존 JSON 파일 데이터에 '추가'하여 저장합니다.
    """
    company_keywords = load_keywords(KEY_WORD_FILE_PATH)
    if not company_keywords:
        return

    if not MONGO_DATE_FIELD:
        print(f"에러: 'MONGO_DATE_FIELD' 상수가 설정되지 않았습니다.")
        return

    existing_articles, latest_processed_date_string = load_existing_data_and_get_latest_date(
        OUTPUT_FILE_PATH, MONGO_DATE_FIELD
    )

    classified_results = []
    try:
        client = MongoClient(MONGO_URI)
        db = client[MONGO_DB_NAME]
        collection = db[MONGO_COLLECTION_NAME]
        print("MongoDB에 성공적으로 연결되었습니다.")

        query = {}
        if latest_processed_date_string:
            query[MONGO_DATE_FIELD] = {'$gt': latest_processed_date_string}
            print(f"MongoDB에서 '{latest_processed_date_string}' 이후(string 비교)의 새 뉴스만 쿼리합니다.")
        else:
            print("MongoDB에서 모든 뉴스를 쿼리합니다 (첫 실행 또는 기존 데이터 없음).")

        articles_to_classify = list(collection.find(query))
        total_articles = len(articles_to_classify)

        if total_articles == 0:
            print("분석할 새 뉴스가 없습니다.")
            client.close()
            return

        print(f"총 {total_articles}개의 신규 뉴스를 분석하고 분류합니다...")

        for i, article in enumerate(articles_to_classify, 1):

            date_str = article.get(MONGO_DATE_FIELD)
            if not date_str or not isinstance(date_str, str):
                print(f"경고: Article {article.get('_id')}에 '{MONGO_DATE_FIELD}'(문자열) 필드가 없습니다. 건너뜁니다.")
                continue

            try:
                datetime.strptime(date_str, DATE_STRING_FORMAT)  # 날짜 형식 검증
            except ValueError:
                print(f"경고: Article {article.get('_id')}의 날짜 형식({date_str})이 잘못되었습니다. 건너뜁니다.")
                continue

            title = article.get('title', '') or ''
            content = article.get('content', '') or ''

            title_search_text = preprocess_text(title).lower()
            content_search_text = preprocess_text(content).lower()

            # --- [로직 수정] 리팩토링된 함수 사용 ---

            # 1. 제목에서 먼저 탐색
            title_matches = find_mentioned_corps(title_search_text, company_keywords)
            identified_corp, industry_category = get_classification(title_matches, corp_to_category)

            # 2. 제목에서 못 찾았으면 (미분류) 본문에서 탐색
            if identified_corp == "미분류":
                content_matches = find_mentioned_corps(content_search_text, company_keywords)
                identified_corp, industry_category = get_classification(content_matches, corp_to_category)

            # --- 분류 로직 종료 ---

            article['corp'] = identified_corp
            article['category'] = industry_category

            if '_id' in article:
                article['_id'] = str(article['_id'])

            classified_results.append(article)

            if i % 100 == 0 or i == total_articles:
                print(f" - {i}/{total_articles}개 신규 분석 완료...")

        print("\n--- 신규 뉴스 분류 및 산업군 추가 완료 ---")

        final_output_data = existing_articles + classified_results

        try:
            final_output_data.sort(key=lambda x: x.get(MONGO_DATE_FIELD, '1970-01-01 00:00:00'))
            print("최종 데이터를 날짜순(string 기준)으로 정렬했습니다.")
        except Exception as e:
            print(f"데이터 정렬 중 오류 발생 (무시하고 진행): {e}")

        with open(OUTPUT_FILE_PATH, 'w', encoding='utf-8') as f:
            json.dump(final_output_data, f, ensure_ascii=False, indent=4)

        print(
            f"✅ 총 {len(final_output_data)}개의 결과가 '{OUTPUT_FILE_PATH}' 파일로 성공적으로 저장되었습니다. (신규 {len(classified_results)}개 추가)")

    except pymongo.errors.ConnectionFailure as e:
        print(f"MongoDB 연결에 실패했습니다: {e}")
    except Exception as e:
        print(f"오류가 발생했습니다: {e}")
    finally:
        if 'client' in locals() and client:
            client.close()
            print("MongoDB 연결이 종료되었습니다.")


if __name__ == '__main__':
    classify_news_and_add_industry()