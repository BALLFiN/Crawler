import requests
from bs4 import BeautifulSoup
import json
from industry_whitelist import STOCK_CODE, WICS_to_category


all_stock_data = []

def url_parser(code):
    url = f"https://finance.daum.net/api/quotes/A{code}?summary=false&changeStatistics=true"
    headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
            'Referer': 'https://finance.daum.net'
        }
    resp = requests.get(url, headers=headers)
    data = resp.json()  # requests가 바로 JSON 디코딩 지원
    wics = data.get("wicsSectorName", "")
    return wics


for corp, code in STOCK_CODE.items():
    wics = url_parser(code)
    print(wics)
    category = WICS_to_category.get(wics, "분류 없음")
    # 각 종목의 데이터를 딕셔너리 형태로 만듦
    stock_info = {
        corp : category
    }
    # 만들어진 딕셔너리를 리스트에 추가
    all_stock_data.append(stock_info)
print(all_stock_data)


