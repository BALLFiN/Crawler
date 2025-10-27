# dify_knowledge.py
import os
import json
import time
import hashlib
from datetime import date
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

import _config
from dify_api import DifyClient
from datetime import datetime, timedelta, date
import re

# ------------------------------- 공용 유틸 -------------------------------

STATE_PATH = os.path.join(os.path.dirname(__file__), "state.json")


def load_state():
    """증분 수집을 위한 로컬 상태 로드"""
    if os.path.exists(STATE_PATH):
        with open(STATE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    # 기본 스키마
    return {
        "industry": {"last_key": None},
        "corporate": {"last_key": None},
        "macro": {"last_date": None},
        "seen": {}
    }


def save_state(state):
    with open(STATE_PATH, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)


def make_doc_key(type_tag: str, category: str, date_str: str, src_name: str = "") -> str:
    """
    업로드 항목의 유니크 키(해시) 생성.
    type|category|date|src 로 구성 → 16자리 해시
    """
    raw = f"{type_tag}|{category}|{date_str}|{src_name}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]


def tag_prefix(_type: str, **meta) -> str:
    """
    태그 프리픽스 생성
    예) tag_prefix('industry', CODE='GICS-4510', COUNTRY='KR')
       -> "[TYPE=industry][CODE=GICS-4510][COUNTRY=KR]"
    """
    tags = [f"[TYPE={_type}]"]
    for k, v in meta.items():
        if v is None or v == "":
            continue
        tags.append(f"[{k.upper()}={v}]")
    return "".join(tags)


def get_page(url: str):
    try:
        resp = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=20)
        resp.raise_for_status()
        return BeautifulSoup(resp.text, "html.parser")
    except requests.exceptions.RequestException as e:
        print(f"[오류] 페이지 로드 실패: {url} ({e})")
        return None


# --------------------------- 오래된 정보 사전 삭제 ---------------------------


# 날짜 패턴
DATE_PATTERNS = [
    re.compile(r"\[DATE=(\d{4}-\d{2}-\d{2})\]"),     # [DATE=YYYY-MM-DD]
    re.compile(r"(\d{4}[.-]\d{2}[.-]\d{2})"),        # YYYY.MM.DD or YYYY-MM-DD
]

def _extract_date_from_name(name: str):
    """문서명에서 날짜 추출 → datetime.date or None"""
    for pat in DATE_PATTERNS:
        m = pat.search(name)
        if m:
            s = m.group(1).replace(".", "-")
            try:
                return datetime.strptime(s, "%Y-%m-%d").date()
            except ValueError:
                pass
    return None


def cleanup_old_documents(dify_client, knowledge_id: str):
    """
    KB 문서 목록 중 오래된 문서 삭제:
    - [TYPE=macro] → 1일 초과 삭제
    - [TYPE=industry] / [TYPE=company] → 7일 초과 삭제
    """
    print("\n🧹 오래된 문서 정리 중...")
    try:
        docs = dify_client.list_all_documents(knowledge_id)
    except Exception as e:
        print(f"❌ 문서 목록 조회 실패: {e}")
        return

    today = date.today()
    deleted_count = 0

    for doc in docs:
        name = doc.get("name", "")
        doc_id = doc.get("id")
        d = _extract_date_from_name(name)
        if not d:
            continue  # 날짜 추출 실패 → 보존

        age = (today - d).days
        # 거시경제: 하루 초과 삭제
        if "[TYPE=macro]" in name and age >= 1:
            dify_client.delete_document(knowledge_id, doc_id)
            print(f"🗑️ [거시경제] {name} ({age}일 경과) 삭제")
            deleted_count += 1
        # 산업/기업 리포트: 7일 초과 삭제
        elif ("[TYPE=industry]" in name or "[TYPE=company]" in name or "[TYPE=corporate]" in name) and age > 7:
            dify_client.delete_document(knowledge_id, doc_id)
            print(f"🗑️ [리포트] {name} ({age}일 경과) 삭제")
            deleted_count += 1

    print(f"✅ 정리 완료: {deleted_count}개 문서 삭제\n")
# --------------------------- 리포트(산업/기업) 수집 ---------------------------

def scrape_and_upload_reports(
    dify_client: DifyClient,
    knowledge_id: str,
    base_url: str,
    max_pages: int,
    job_name: str,
    type_tag: str,
    state: dict
):
    """
    네이버금융 리포트 리스트 증분 수집 후 integration_KB에 업로드.
    - 최신 페이지부터 순회
    - state['<type>'].last_key 에 도달하면 중단
    - state['seen'][doc_key] 존재 시 스킵
    - 파일 업로드 + 검색 힌트 텍스트 업로드(짧은 TAGS 문서)
    """
    print(f"\n{'='*60}\n💼 {job_name} 증분 수집 시작... (KB: {knowledge_id})\n{'='*60}")

    last_anchor = state.get(type_tag, {}).get("last_key")
    first_new_key = None
    hit_old_anchor = False
    uploaded = 0

    for page in range(1, max_pages + 1):
        if hit_old_anchor:
            break

        url = f"{base_url}?&page={page}"
        print(f" - 목록 페이지: {url}")
        soup = get_page(url)
        if not soup:
            continue

        rows = soup.select("table.type_1 tr")
        if not rows or len(rows) <= 1:
            continue

        # 헤더 제거 후 본문
        for row in rows[1:]:
            cols = row.find_all("td")
            if len(cols) < 6:
                continue

            category = cols[0].get_text(strip=True)  # 업종명/종목명
            date_str = cols[4].get_text(strip=True)  # 예: 2025.01.03
            a = cols[3].find("a")
            if not a or not a.has_attr("href"):
                continue

            src_url = urljoin("https://finance.naver.com", a["href"])
            src_name = src_url.split("/")[-1].split("?")[0]

            doc_key = make_doc_key(type_tag, category, date_str, src_name)

            # 앵커(마지막 처리 지점)에 도달하면 종료
            if last_anchor and doc_key == last_anchor:
                hit_old_anchor = True
                print("   · 이전 기준점 도달 → 이번 수집 종료")
                break

            # 이미 업로드한 문서면 스킵
            if state["seen"].get(doc_key):
                continue

            # 새 문서면 첫 번째 키를 기록(이게 새로운 기준점)
            if not first_new_key:
                first_new_key = doc_key

            # 파일 다운로드
            try:
                f_resp = requests.get(src_url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=30)
                f_resp.raise_for_status()
                file_content = f_resp.content
            except requests.exceptions.RequestException as e:
                print(f"   · [다운로드 실패] {src_url} ({e})")
                continue

            # 업로드 (파일 제목에도 TYPE 태그 넣어 검색 보강)
            tagged_name = f"{tag_prefix(type_tag)} {category}-{date_str}"
            ok = dify_client.upload_file_to_dify(tagged_name, file_content, src_name, knowledge_id)
            if ok:
                uploaded += 1
                state["seen"][doc_key] = True
                print(f"   · 업로드 완료: {tagged_name}")

            # 아주 짧은 힌트 텍스트도 함께 업로드(검색 강화를 위해)
            hint_text = f"{tag_prefix(type_tag, NAME=category, DATE=date_str)}\nsource_file: {src_name}"
            dify_client.upload_text_to_dify(f"{tagged_name} [TAGS]", hint_text, knowledge_id)

            time.sleep(0.6)

    # 새 기준점 갱신
    if first_new_key:
        state.setdefault(type_tag, {})["last_key"] = first_new_key

    print(f"✅ {job_name} 완료: 업로드 {uploaded}건\n{'='*60}\n")


# --------------------------- 거시경제 생성 & 업로드 ---------------------------

def run_macro_analysis_and_upload(
    dify_client: DifyClient,
    knowledge_id: str,
    perplexity_key: str,
    state: dict
):
    """
    Perplexity로 거시경제 요약 생성 후 integration_KB에 텍스트 업로드.
    - 당일 이미 올렸다면 스킵
    - 본문 맨 앞에 [TYPE=macro][DATE=YYYY-MM-DD] 삽입
    - 프롬프트는 사용자 요청대로 '절대 변경하지 않음'
    """
    today = date.today().strftime('%Y-%m-%d')
    if state.get("macro", {}).get("last_date") == today:
        print(f"🌍 거시경제: 이미 오늘({today}) 업로드되어 스킵")
        return

    print(f"\n{'='*60}\n🌍 거시경제 분석 생성 시작...\n{'='*60}")

    # ⛔ 프롬프트는 사용자가 바꾸지 말라고 한 그대로 둠
    prompt_content = """
    너는 대한민국 최고의 경제 분석가다. 오늘의 경제 동향을 CEO 아침 보고 형식으로 요약해라.
    Part 1: 핵심 지표 대시보드(텍스트 나열)
    Part 2: Top 이슈 심층 분석(영향/산업별 명암/실행 제언)
    """

    try:
        resp = requests.post(
            'https://api.perplexity.ai/chat/completions',
            headers={'Authorization': f'Bearer {perplexity_key}', 'Content-Type': 'application/json'},
            json={
                'model': 'sonar-pro',
                'messages': [{'role': 'user', 'content': prompt_content}]
            },
            timeout=60
        )
        if resp.status_code != 200:
            print(f"❌ Perplexity API 실패: {resp.status_code} - {resp.text}")
            return

        result = resp.json()
        content = result['choices'][0]['message']['content']
        print("✅ 거시경제 분석 수신")

        header = tag_prefix('macro', DATE=today)
        tagged_text = f"{header}\n\n{content}"
        doc_name = f"{header} 데일리 거시경제 보고서 - {today}"
        dify_client.upload_text_to_dify(doc_name, tagged_text, knowledge_id)

        # 상태 갱신
        state.setdefault("macro", {})["last_date"] = today
        print(f"✅ 거시경제 업로드 완료: {doc_name}")

    except Exception as e:
        print(f"❌ 거시경제 생성/업로드 오류: {e}")

    print(f"{'='*60}\n")


# --------------------------------- 메인 ---------------------------------

def main():
    print("🚀 integration_KB 업데이트 시작")

    # ---- 설정 로드
    API_KEY = _config.DIFY_API_KEY
    HOST = _config.DIFY_HOST
    PERPLEXITY_KEY = _config.perplexity_api
    INTEGRATION_ID = _config.INTEGRETION_KNOWLEDGE_ID  # ✅ 단일 KB만 사용

    URLS = {
        "industry": _config.INDUSTRY_BASE_URL,   # 예: 'https://finance.naver.com/research/industry_list.naver'
        "corporate": _config.CORP_BASE_URL       # 예: 'https://finance.naver.com/research/company_list.naver'
    }
    MAX_PAGES = {"industry": 3, "corporate": 5}  # 필요시 조절

    client = DifyClient(api_key=API_KEY, host=HOST, knowledge_ids={"integration": INTEGRATION_ID})
    state = load_state()

    try:
        # --- 산업 리포트 (TYPE=industry) ---
        scrape_and_upload_reports(
            dify_client=client,
            knowledge_id=INTEGRATION_ID,
            base_url=URLS["industry"],
            max_pages=MAX_PAGES["industry"],
            job_name="산업 리포트",
            type_tag="industry",
            state=state
        )

        # --- 기업 리포트 (TYPE=company) ---
        scrape_and_upload_reports(
            dify_client=client,
            knowledge_id=INTEGRATION_ID,
            base_url=URLS["corporate"],
            max_pages=MAX_PAGES["corporate"],
            job_name="기업 리포트",
            type_tag="corporate",   # 내부 키는 'corporate'로, 태그는 company로 내려도 됨
            state=state
        )

        # 태그는 company로 표시되길 원하면 여기서 보정
        # (위에서 type_tag='corporate'로 돌렸으니, 검색에서 [TYPE=company]로 쓰고 싶다면 아래 라인만 바꾸면 됨)
        # → 필요 시 type_tag='company' 로 바꿔 사용하세요.

        # --- 거시경제 (TYPE=macro) ---
        run_macro_analysis_and_upload(
            dify_client=client,
            knowledge_id=INTEGRATION_ID,
            perplexity_key=PERPLEXITY_KEY,
            state=state
        )

    finally:
        save_state(state)
        print("💾 상태 저장 완료")
        print("🎉 모든 작업 종료")


if __name__ == "__main__":
    main()
