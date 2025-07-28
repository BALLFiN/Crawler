
# 📰 Real-Time News Crawler with Kafka & MongoDB


> **실시간 뉴스 크롤러**로 다양한 경제 뉴스 사이트에서 기사를 수집하고, 기업명 태깅 후 **Kafka**를 통해 스트리밍하며, MongoDB에 저장할 수 있는 시스템입니다.

---

## 📌 Features
- 🌐 **다수 언론사 뉴스 크롤링** (`requests`, `BeautifulSoup`, `newspaper3k`)
- 🏷 **기업명 태깅**: 기사 제목 및 본문 기반 기업 식별 (`identify_company_module.py`)
- 🔗 **Kafka Producer**: 뉴스 데이터를 `confluent-kafka`로 실시간 발행
- 🗄 **MongoDB 저장 지원** (선택)
- 🔍 **확장성 있는 뉴스 사이트 추가** (`news_list.py` 기반 관리)

---

## 📂 Project Structure

├── news_crawler.py # 뉴스 크롤링 및 Kafka 발행 (Producer)
├── consumer.py # Kafka Consumer (뉴스 데이터 수신)
├── identify_company_module.py # 기업명 매칭 로직
├── company_whitelist.py # 기업 리스트 및 키워드/가중치 정의
├── news_list.py # 크롤링 대상 뉴스 사이트 및 MongoDB 설정
├── requirements.txt # Python 패키지 의존성
└── test.ipynb # 기능 테스트용 Jupyter Notebook
