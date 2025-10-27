# main.py
import json
import os
import time
from typing import Any, Dict, Iterable, List

import requests
from tqdm import tqdm

import _config

# ----------------------------
# 환경설정 (_config.py 에서 가져옴)
# ----------------------------
DIFY_HOST = _config.DIFY_HOST.rstrip("/")
DIFY_API_KEY = _config.DIFY_API_KEY
NEWS_JSON_PATH = _config.NEWS_JSON_PATH

DEFAULT_COUNTRY = getattr(_config, "DEFAULT_COUNTRY", "KR")
DEFAULT_USER_QUESTION = getattr(
    _config, "DEFAULT_USER_QUESTION",
    "이 뉴스의 의미와 투자 관점에서 핵심 포인트를 요약해줘."
)
REQUEST_TIMEOUT = getattr(_config, "WORKFLOW_TIMEOUT", 120)
USER_ID = getattr(_config, "USER_ID", "news-batch")   # Dify 쪽 user 식별자


# ----------------------------
# Dify Workflow Client
# ----------------------------
class DifyWorkflowClient:
    def __init__(self, host: str, api_key: str, timeout: int = 120):
        self.host = host
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        })

    def run_workflow(self, inputs: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        """
        공식 문서: POST {host}/v1/workflows/run
        body:
          {
            "inputs": {...},
            "response_mode": "blocking",
            "user": "unique-user-id"
          }
        """
        url = f"{self.host}/v1/workflows/run"
        payload = {
            "inputs": inputs,
            "response_mode": "blocking",
            "user": user_id,
        }
        resp = self.session.post(url, data=json.dumps(payload), timeout=self.timeout)
        # 2xx 외에는 예외로
        try:
            resp.raise_for_status()
        except requests.HTTPError as e:
            # 본문을 함께 보여줘 디버깅 쉬움
            raise RuntimeError(f"Workflow run failed ({resp.status_code}): {resp.text}") from e
        return resp.json()


# ----------------------------
# 데이터 유틸
# ----------------------------
def load_news(path: str) -> List[Dict[str, Any]]:
    """JSON 파일이 리스트 또는 {items:[...]} 형태여도 유연하게 읽기"""
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        # 흔한 래핑 키들 시도
        for k in ("items", "data", "results", "articles"):
            if k in data and isinstance(data[k], list):
                return data[k]
        # 단일 객체만 있을 수도 있음
        return [data]
    raise ValueError("지원하지 않는 JSON 구조입니다.")


def to_inputs(item: Dict[str, Any]) -> Dict[str, Any]:
    """
    JSON 필드 매핑:
      news_contents  ← item["content"] (원문 전체, 절대 자르지 않음)
      company_name   ← item["corp"]
      industry_name  ← item["category"]
      country        ← DEFAULT_COUNTRY
      user_question  ← DEFAULT_USER_QUESTION
      (메타) title, url, published_date, publisher
    """
    return {
        "news_contents": item.get("content", "") or "",
        "company_name": item.get("corp", "") or "",
        "industry_name": item.get("category", "") or "",
        "country": DEFAULT_COUNTRY,
        "user_question": DEFAULT_USER_QUESTION,
        # 메타(워크플로우에서 사용하거나 결과 저장용)
        "title": item.get("title", "") or "",
        "url": item.get("url", "") or "",
        "published_date": item.get("published_date", "") or "",
        "publisher": item.get("publisher", "") or "",
    }


# ----------------------------
# 메인
# ----------------------------
def main():
    client = DifyWorkflowClient(DIFY_HOST, DIFY_API_KEY, timeout=REQUEST_TIMEOUT)
    items = load_news(NEWS_JSON_PATH)

    os.makedirs("outputs", exist_ok=True)
    out_path = os.path.join("outputs", "news_results.jsonl")

    success = 0
    fail = 0

    with open(out_path, "w", encoding="utf-8") as fout:
        for item in tqdm(items, desc="Sending to Dify"):
            inputs = to_inputs(item)

            # 간단한 재시도(429/5xx)
            for attempt in range(3):
                try:
                    result = client.run_workflow(inputs, USER_ID)
                    # 결과를 그대로 저장 (워크플로우 출력 구조가 팀마다 달라서 일반형으로 저장)
                    record = {
                        "input_meta": {
                            "title": inputs.get("title"),
                            "url": inputs.get("url"),
                            "published_date": inputs.get("published_date"),
                            "publisher": inputs.get("publisher"),
                            "company_name": inputs.get("company_name"),
                            "industry_name": inputs.get("industry_name"),
                        },
                        "dify_result": result,
                    }
                    fout.write(json.dumps(record, ensure_ascii=False) + "\n")
                    success += 1
                    break
                except Exception as e:
                    last_err = str(e)
                    # 가벼운 백오프
                    time.sleep(1.5 * (attempt + 1))
            else:
                # 3회 실패
                record = {
                    "input_meta": {
                        "title": inputs.get("title"),
                        "url": inputs.get("url"),
                    },
                    "error": last_err,
                }
                fout.write(json.dumps(record, ensure_ascii=False) + "\n")
                fail += 1

    print(f"\nDone. success={success}, fail={fail}")
    print(f"Saved to: {out_path}")


if __name__ == "__main__":
    main()
