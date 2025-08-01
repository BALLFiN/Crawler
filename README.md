# 📰 실시간 뉴스 크롤러 (Kafka & MongoDB)

다양한 경제 뉴스 사이트에서 실시간으로 기사를 수집하고, 기사 내용에 언급된 기업을 태깅하여 Kafka로 스트리밍하는 시스템입니다.

## 📌 주요 기능

- **실시간 뉴스 크롤링**: `news_list.py`에 정의된 여러 언론사의 최신 기사를 주기적으로 수집합니다.
- **기업명 자동 태깅**: `company_whitelist.py`의 키워드를 기반으로 기사에 언급된 기업을 자동으로 식별하고 태그를 부여합니다.
- **Kafka 연동**: 수집 및 태깅된 뉴스 데이터를 실시간으로 Kafka 토픽에 발행(Produce)합니다.
- **데이터 소비**: 발행된 뉴스 데이터를 구독(Consume)하여 확인할 수 있는 `consumer.py` 예제를 포함합니다.
- **확장성**: `news_list.py`와 `company_whitelist.py` 파일을 수정하여 손쉽게 크롤링 대상 사이트와 태깅할 기업을 추가/변경할 수 있습니다.

## 📂 프로젝트 구조

```
├── news_crawler.py           # 메인 크롤러 (Producer)
├── consumer.py               # Kafka 메시지 확인용 (Consumer)
├── identify_company_module.py  # 기업명 태깅 로직
├── company_whitelist.py      # 태깅할 기업 정보 및 키워드, 가중치 정의
├── news_list.py              # 크롤링 대상 사이트 목록 및 설정
├── requirements.txt          # 필요 패키지 목록
└── README.md                 # 프로젝트 설명 파일
```

## 🚀 실행 방법

**사전 준비:**

1.  **Kafka 실행**: 로컬 또는 원격 환경에 Kafka가 실행 중이어야 합니다. (기본 설정: `localhost:9092`)
2.  **필요 패키지 설치**:
    ```bash
    pip install -r requirements.txt
    ```

**실행 순서:**

1.  **Consumer 실행 (터미널 1)**:
    Kafka로 들어오는 뉴스 데이터를 실시간으로 확인하기 위해 `consumer.py`를 실행합니다.
    ```bash
    python consumer.py
    ```
    실행하면 "뉴스 수신 대기 중..." 메시지가 표시됩니다.

2.  **Crawler 실행 (터미널 2)**:
    `news_crawler.py`를 실행하여 뉴스 수집 및 발행을 시작합니다.
    ```bash
    python news_crawler.py
    ```
    크롤러가 실행되면 `news_list.py`에 설정된 사이트들을 주기적으로 확인하며 새로운 기사를 Kafka로 보냅니다.

## 📝 예상 출력

`consumer.py`를 실행한 터미널에서는 다음과 같이 `news_crawler.py`가 수집한 기사 데이터가 JSON 형식으로 출력됩니다.

```json
📥 전체 데이터 수신:
{
    "publisher": "서울경제",
    "category": "증권",
    "title": "삼성전자, AI 가속기 '마하-1' 공개…HBM 없는 혁신",
    "published_date": "2024-07-29 10:30:00",
    "content": "삼성전자가 자체 개발한 AI 가속기 '마하-1'을 공개했다. 이 칩은 고대역폭메모리(HBM) 없이도 빠른 속도를 구현하는 것이 특징이다...",
    "url": "https://www.sedaily.com/NewsView/XXXXXXXX",
    "image_url": "https://www.sedaily.com/some_image.jpg",
    "company_tag": "삼성전자",
    "company_score": 8,
    "stock_code": 5930,
    "crawled_at": "2024-07-29 10:31:15"
}
```

- **company_tag**: `identify_company_module.py`에 의해 태깅된 기업명입니다.
- **company_score**: 태깅 정확도를 나타내는 점수입니다.
- **stock_code**: `news_list.py`의 `STOCK_CODE` 딕셔너리를 참조하여 매핑된 종목 코드입니다.