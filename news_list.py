MONGO_URI = 'mongodb://localhost:27017'
MONGO_DB_NAME = 'stock'
MONGO_COLLECTION_NAME = 'new_news'
# 2. 기업 이름과 코드 매핑


STOCK_CODE = {
    '삼성전자': '005930', 'SK하이닉스': '000660', 'LG에너지솔루션': '373220', '삼성바이오로직스': '207940', '현대자동차': '005380',
    '기아': '000270', '셀트리온': '068270', '한화에어로스페이스': '012450', 'KB금융': '105560', 'NAVER': '035420',
    'HD현대중공업': '329180', '신한지주': '055550', '현대모비스': '012330', '한화오션': '042660', '메리츠금융지주': '138040',
    'POSCO홀딩스': '005490', '삼성물산': '002826', '크래프톤': '259960', '카카오': '035720', 'HMM': '011200',
    '삼성화재': '000810', 'LG화학': '051910', '하나금융지주': '086790', '삼성생명': '032830', 'SK이노베이션': '096770',
    'HD한국조선해양': '009540', '한국전력': '015760', '고려아연': '010130', '두산에너빌리티': '034020', 'KT&G': '033780',
    '삼성중공업': '010140', '삼성SDI': '006400', 'KT': '030200', 'SK텔레콤': '017670', '우리금융지주': '316140',
    'SK스퀘어': '402340', '기업은행': '024110', 'HD현대일렉트릭': '267260', 'LG전자': '066570', '현대로템': '064350',
    '포스코퓨처엠': '003670', '카카오뱅크': '323410', 'LG': '003550', '하이브': '352820', '포스코인터내셔널': '047050',
    '삼성전기': '009150', 'SK': '003473', '삼성에스디에스': '018260', '유한양행': '000100', '현대글로비스': '086280',
    '대한항공': '003490', 'SK바이오팜': '326030', '한국항공우주': '047810', 'HD현대마린솔루션': '443060', '삼양식품': '003230',
    '한화시스템': '272210', '한미반도체': '042700', '아모레퍼시픽': '090430', 'DB손해보험': '005830', 'S-Oil': '010950',
    'LIG넥스원': '079550', 'HD현대': '267250', '한진칼': '180640', '미래에셋증권': '006800', '맥쿼리인프라': '088980',
    '코웨이': '021240', 'LS ELECTRIC': '010120', 'HD현대미포': '010620', 'LG생활건강': '051900', 'LG씨엔에스': '064400',
    '한국타이어앤테크놀로지': '161390', '두산': '000150', 'LG유플러스': '032640', '오리온': '271560', '삼성카드': '002978',
    '두산밥캣': '241560', '현대건설': '000720', 'NH투자증권': '005940', '효성중공업': '298040', 'LG디스플레이': '034220',
    '포스코DX': '022100', '삼성증권': '016360', '한국금융지주': '071050', '에코프로머티': '450080', '삼성E&A': '028050',
    '카카오페이': '377300', 'SKC': '011790', 'CJ제일제당': '097950', 'CJ': '001040', '한화솔루션': '009830',
    'LS': '006260', '넷마블': '251270', 'GS': '078930', '알테오젠': '196170', '에코프로비엠': '247540',
    'HLB': '028300', '에코프로': '086520', '레인보우로보틱스': '277810'
}


TARGET_SITES = [
    
    #서울경제
    {
        'name': '서울경제',
        'category': '증권',
        'url': 'https://www.sedaily.com/newsList/GA01',
        'base_url': 'https://www.sedaily.com',
        'pattern': '/NewsView/',
        'selector': 'li .article_tit a',
        'image_selector': 'li .thumb img',  # ✅ 이미지 선택자 추가
        'dynamic': False
    },
    {
        'name': '서울경제',
        'category': '경제',
        'url': 'https://www.sedaily.com/newsList/GC01',
        'base_url': 'https://www.sedaily.com',
        'pattern': '/NewsView/',
        'selector': 'li .article_tit a',
        'image_selector': 'li .thumb img',  # ✅ 이미지 선택자 추가
        'dynamic': False
    },
    {
        'name': '서울경제',
        'category': '산업',
        'url': 'https://www.sedaily.com/newsList/GD01',
        'base_url': 'https://www.sedaily.com',
        'pattern': '/NewsView/',
        'selector': 'li .article_tit a',
        'image_selector': 'li .thumb img',  # ✅ 이미지 선택자 추가
        'dynamic': False
    },
    {
        'name': '서울경제',
        'category': '국제',
        'url': 'https://www.sedaily.com/newsList/GF02',
        'base_url': 'https://www.sedaily.com',
        'pattern': '/NewsView/',
        'selector': 'li .article_tit a',
        'image_selector': 'li .thumb img',  # ✅ 이미지 선택자 추가
        'dynamic': False
    },
    
    # 매일경제
    {
        'name': '매일경제',
        'category': '경제',
        'url': 'https://www.mk.co.kr/news/economy/latest/',
        'base_url': 'https://www.mk.co.kr',
        'pattern': '/news/',
        'selector': 'li.news_node > a.news_item',
        'image_selector': 'div.thumb_area img',
        'dynamic': False
    },
    {
        'name': '매일경제',
        'category': '기업',
        'url': 'https://www.mk.co.kr/news/business/latest/',
        'base_url': 'https://www.mk.co.kr',
        'pattern': '/news/',
        'selector': 'li.news_node > a.news_item',
        'image_selector': 'div.thumb_area img',
        'dynamic': False
    },
    {
        'name': '매일경제',
        'category': '국제',
        'url': 'https://www.mk.co.kr/news/world/latest/',
        'base_url': 'https://www.mk.co.kr',
        'pattern': '/news/',
        'selector': 'li.news_node > a.news_item',
        'image_selector': 'div.thumb_area img',
        'dynamic': False
    },
    {
        'name': '매일경제',
        'category': '금융',
        'url': 'https://www.mk.co.kr/news/stock/latest/',
        'base_url': 'https://www.mk.co.kr',
        'pattern': '/news/',
        'selector': 'li.news_node > a.news_item',
        'image_selector': 'div.thumb_area img',
        'dynamic': False
    },
    
    #연합뉴스
    {
        'name': '연합뉴스',
        'category': '금융',
        'url': 'https://www.yna.co.kr/economy/finance',  # 또는 적절한 카테고리 URL
        'base_url': 'https://www.yna.co.kr',
        'pattern': '/view/AKR',
        'selector': 'a.tit-news',
        'image_selector': 'figure.img-con01 img',
        'dynamic': False
    },
    {
        'name': '연합뉴스',
        'category': '경제',
        'url': 'https://www.yna.co.kr/economy/economic-policy',
        'base_url': 'https://www.yna.co.kr',
        'pattern': '/view/AKR',
        'selector': 'a.tit-news',
        'image_selector': 'figure.img-con01 img',
        'dynamic': False
    },
    {
        'name': '연합뉴스',
        'category': '국제',
        'url': 'https://www.yna.co.kr/international/all',
        'base_url': 'https://www.yna.co.kr',
        'pattern': '/view/AKR',
        'selector': 'a.tit-news',
        'image_selector': 'figure.img-con01 img',
        'dynamic': False
    },
    {
        'name': '연합뉴스',
        'category': '산업',
        'url': 'https://www.yna.co.kr/industry/all',
        'base_url': 'https://www.yna.co.kr',
        'pattern': '/view/AKR',
        'selector': 'a.tit-news',
        'image_selector': 'figure.img-con01 img',
        'dynamic': False
    },
    
    #인포스탁 데일리
    {
        'name': '인포스탁데일리',
        'category': '통합',
        'url': 'https://www.infostockdaily.co.kr/news/articleList.html?sc_section_code=S1N17&view_type=sm',
        'base_url': 'https://www.infostockdaily.co.kr',
        'pattern': '/news/articleView.html?idxno=',
        'selector': 'div.list-titles > a',
        'image_selector': '.list-image',
        'dynamic': False
    },
    
    #한겨례
    {
        'name': '한겨레',
        'category': '경제',
        'url': 'https://www.hani.co.kr/arti/economy/economy_general/',
        'base_url': 'https://www.hani.co.kr',
        'pattern': '/arti/economy/economy_general/',
        'selector': 'a.BaseArticleCard_link__Q3YFK',
        'image_selector': 'div.BaseThumbnail_wrap__pkRwr img', # ✅ 이미지 선택자
        'dynamic': False
    },
    {
        'name': '한겨레',
        'category': '증권',
        'url': 'https://www.hani.co.kr/arti/economy/finance/',
        'base_url': 'https://www.hani.co.kr',
        'pattern': '/arti/economy/finance/',
        'selector': 'a.BaseArticleCard_link__Q3YFK',
        'image_selector': 'div.BaseThumbnail_wrap__pkRwr img', # ✅ 이미지 선택자
        'dynamic': False
    },
    {
        'name': '한겨레',
        'category': '국제',
        'url': 'https://www.hani.co.kr/arti/international/international_general/',
        'base_url': 'https://www.hani.co.kr',
        'pattern': '/arti/international/international_general/',
        'selector': 'a.BaseArticleCard_link__Q3YFK',
        'image_selector': 'div.BaseThumbnail_wrap__pkRwr img', # ✅ 이미지 선택자
        'dynamic': False
    },
    
    #이투데이
    {
        'name': '이투데이',
        'category': '증권',
        'url': 'https://www.etoday.co.kr/news/section/subsection?MID=1206',
        'base_url': 'https://www.etoday.co.kr',
        'pattern': '/news/view/',
        'selector': 'li.sp_newslist .cluster_text_headline21 a',
        'image_selector': 'div.cluster_thumb_link21 img',           # ✅ 이미지 선택자 추가
        'dynamic': False
    },
    {
        'name': '이투데이',
        'category': '산업',
        'url': 'https://www.etoday.co.kr/news/section/subsection?MID=1391',
        'base_url': 'https://www.etoday.co.kr',
        'pattern': '/news/view/',
        'selector': 'li.sp_newslist .cluster_text_headline21 a',
        'image_selector': 'div.cluster_thumb_link21 img',           # ✅ 이미지 선택자 추가
        'dynamic': False
    },
    {
        'name': '이투데이',
        'category': '국제',
        'url': 'https://www.etoday.co.kr/news/section/subsection?MID=1601',
        'base_url': 'https://www.etoday.co.kr',
        'pattern': '/news/view/',
        'selector': 'li.sp_newslist .cluster_text_headline21 a',
        'image_selector': 'div.cluster_thumb_link21 img',           # ✅ 이미지 선택자 추가
        'dynamic': False
    },
    {
        'name': '이투데이',
        'category': '경제',
        'url': 'https://www.etoday.co.kr/news/section/subsection?MID=1701',
        'base_url': 'https://www.etoday.co.kr',
        'pattern': '/news/view/',
        'selector': 'li.sp_newslist .cluster_text_headline21 a',
        'image_selector': 'div.cluster_thumb_link21 img',           # ✅ 이미지 선택자 추가
        'dynamic': False
    },
    
    #헤럴드경제
    {
        "name": "헤럴드경제",
        "category": "경제",
        "url": "https://biz.heraldcorp.com/economy",
        "base_url": "https://biz.heraldcorp.com",
        "container_selector": "article.recent_news",   # ✅ 이 영역 내부에서만
        "selector": "ul.news_list li a",               # ✅ 기사 링크들만 추출
        "pattern": "/article/",
        "image_selector": "div.news_img img",          # ✅ 이미지 선택자 추가
        "dynamic": False
    },
    {
        "name": "헤럴드경제",
        "category": "산업",
        "url": "https://biz.heraldcorp.com/industry",
        "base_url": "https://biz.heraldcorp.com",
        "container_selector": "article.recent_news",   # ✅ 이 영역 내부에서만
        "selector": "ul.news_list li a",               # ✅ 기사 링크들만 추출
        "pattern": "/article/",
        "image_selector": "div.news_img img",          # ✅ 이미지 선택자 추가
        "dynamic": False
    },
    {
        "name": "헤럴드경제",
        "category": "국제",
        "url": "https://biz.heraldcorp.com/world",
        "base_url": "https://biz.heraldcorp.com",
        "container_selector": "article.recent_news",   # ✅ 이 영역 내부에서만
        "selector": "ul.news_list li a",               # ✅ 기사 링크들만 추출
        "pattern": "/article/",
        "image_selector": "div.news_img img",          # ✅ 이미지 선택자 추가
        "dynamic": False
    },
    
    #딜사이트
    {
        "name": "딜사이트",
        "category": "금융",
        "url": "https://dealsite.co.kr/categories/083000",
        "base_url": "https://dealsite.co.kr",
        "container_selector": "div.mnm-news-list",
        "selector": ".mnm-news-title-wrap a",
        "pattern": "/articles/",
        "image_selector": "img.thumb-img",  # ✅ style 속성에서 background url 추출
        "dynamic": False
    },
    {
        "name": "딜사이트",
        "category": "산업",
        "url": "https://dealsite.co.kr/categories/068000",
        "base_url": "https://dealsite.co.kr",
        "container_selector": "div.mnm-news-list",
        "selector": ".mnm-news-title-wrap a",
        "pattern": "/articles/",
        "image_selector": "img.thumb-img",  # ✅ style 속성에서 background url 추출
        "dynamic": False
    },
    {
        "name": "딜사이트",
        "category": "기업",
        "url": "https://dealsite.co.kr/categories/080057",
        "base_url": "https://dealsite.co.kr",
        "container_selector": "div.mnm-news-list",
        "selector": ".mnm-news-title-wrap a",
        "pattern": "/articles/",
        "image_selector": "img.thumb-img",  # ✅ style 속성에서 background url 추출
        "dynamic": False
    },
    
    #아주경제
    {
        "name": "아주경제",
        "category": "경제",
        "url": "https://www.ajunews.com/economy/policy",
        "base_url": "https://www.ajunews.com",
        "container_selector": "ul.sc_news_lst",
        "selector": "a.tit",
        "pattern": "/view/",
        "image_selector": "a.thumb img",         # ✅ 이미지 선택자 추가
        "dynamic":False
    },
    {
        "name": "아주경제",
        "category": "산업",
        "url": "https://www.ajunews.com/industry",
        "base_url": "https://www.ajunews.com",
        "container_selector": "ul.sc_news_lst",
        "selector": "a.tit",
        "pattern": "/view/",
        "image_selector": "a.thumb img",         # ✅ 이미지 선택자 추가
        "dynamic": False
    },
    {
        "name": "아주경제",
        "category": "금융",
        "url": "https://www.ajunews.com/global/economarket",
        "base_url": "https://www.ajunews.com",
        "container_selector": "ul.sc_news_lst",
        "selector": "a.tit",
        "pattern": "/view/",
        "image_selector": "a.thumb img",         # ✅ 이미지 선택자 추가
        "dynamic": False
    },
    
    #한국경제
    {
        "name": "한국경제",
        "category": "경제",
        "url": "https://www.hankyung.com/all-news-economy",  
        "base_url": "https://www.hankyung.com",
        "container_selector": "ul.allnews-list",
        "selector": "h2.news-tit a",
        "pattern": "/article/",
        "image_selector": "figure.thumb img",    # ✅ 이미지 선택자 추가
        "dynamic": False
    },
    {
        "name": "한국경제",
        "category": "금융",
        "url": "https://www.hankyung.com/all-news-finance",  
        "base_url": "https://www.hankyung.com",
        "container_selector": "ul.allnews-list",
        "selector": "h2.news-tit a",
        "pattern": "/article/",
        "image_selector": "figure.thumb img",    # ✅ 이미지 선택자 추가
        "dynamic": False
    },
    {
        "name": "한국경제",
        "category": "국제",
        "url": "https://www.hankyung.com/all-news-international",  
        "base_url": "https://www.hankyung.com",
        "container_selector": "ul.allnews-list",
        "selector": "h2.news-tit a",
        "pattern": "/article/",
        "image_selector": "figure.thumb img",    # ✅ 이미지 선택자 추가
        "dynamic": False
    },
    
    #중앙일보
    {
    "name": "중앙일보",
    "category": "경제",
    "url": "https://www.joongang.co.kr/money/general",
    "base_url": "https://www.joongang.co.kr",
    "selector": "h2.headline a",  # ✅ 수정된 selector
    "pattern": "/article/",
    "image_selector": "figure.card_image img", # ✅ 이미지 선택자 추가
    "dynamic": False
    },
    {
    "name": "중앙일보",
    "category": "산업",
    "url": "https://www.joongang.co.kr/money/industry",
    "base_url": "https://www.joongang.co.kr",
    "selector": "h2.headline a",  # ✅ 수정된 selector
    "pattern": "/article/",
    "image_selector": "figure.card_image img", # ✅ 이미지 선택자 추가
    "dynamic": False
    },
    {
    "name": "중앙일보",
    "category": "금융",
    "url": "https://www.joongang.co.kr/money/finance",
    "base_url": "https://www.joongang.co.kr",
    "selector": "h2.headline a",  # ✅ 수정된 selector
    "pattern": "/article/",
    "image_selector": "figure.card_image img", # ✅ 이미지 선택자 추가
    "dynamic": False
    },
    {
    "name": "중앙일보",
    "category": "국제",
    "url": "https://www.joongang.co.kr/money/globaleconomy",
    "base_url": "https://www.joongang.co.kr",
    "selector": "h2.headline a",  # ✅ 수정된 selector
    "pattern": "/article/",
    "image_selector": "figure.card_image img", # ✅ 이미지 선택자 추가
    "dynamic": False
    },

    #연합인포맥스
    {
    "name": "연합인포맥스 ",
    "category": "통합",
    "url": "https://news.einfomax.co.kr/news/articleList.html?view_type=sm",
    "base_url": "https://news.einfomax.co.kr",
    "selector": "h4.titles a",  # ✅ 핵심 선택자
    "pattern": "/news/articleView.html",  # ✅ 기사 링크 판별
    "image_selector": "a.thumb img",            # ✅ 이미지 선택자 추가
    "dynamic": False
    },
    
    #머니투데이
    {
    "name": "머니투데이",
    "category": "경제",
    "url": "https://news.mt.co.kr/newsList.html?type=1&comd=&pDepth=news&pDepth1=politics&pDepth2=Ptotal",
    "base_url": "https://news.mt.co.kr",
    "selector": "ul.conlist_p1 li.bundle strong.subject a", 
    "pattern": "/mtview.php",
    "image_selector": "a.thum img",                          # ✅ 이미지 선택자
    "dynamic": False
    }, 
    {
    "name": "머니투데이",
    "category": "국제",
    "url": "https://news.mt.co.kr/newsList.html?pDepth1=world&pDepth2=Wtotal",
    "base_url": "https://news.mt.co.kr",
    "selector": "ul.conlist_p1 li.bundle strong.subject a", 
    "pattern": "/mtview.php",
    "image_selector": "a.thum img",                          # ✅ 이미지 선택자
    "dynamic": False
    }, 
    {
    "name": "머니투데이",
    "category": "산업",
    "url": "https://news.mt.co.kr/newsList.html?pDepth1=industry&pDepth2=Itotal",
    "base_url": "https://news.mt.co.kr",
    "selector": "ul.conlist_p1 li.bundle strong.subject a", 
    "pattern": "/mtview.php",
    "image_selector": "a.thum img",                          # ✅ 이미지 선택자
    "dynamic": False
    }, 
    {
    "name": "머니투데이",
    "category": "증권",
    "url": "https://news.mt.co.kr/newsList.html?pDepth1=finance&pDepth2=Ftotal",
    "base_url": "https://news.mt.co.kr",
    "selector": "ul.conlist_p1 li.bundle strong.subject a", 
    "pattern": "/mtview.php",
    "image_selector": "a.thum img",                          # ✅ 이미지 선택자
    "dynamic": False
    }, 
    
    #이코노미스트
    {
        "name": "이코노미스트",
        "category": "통합",
        "url": "https://www.economist.co.kr/article/list/ecn_SC011000000",
        "base_url": "https://www.economist.co.kr",
        "selector": "div.analysis_wrap dt.analysis_ttl a",  # 기사 제목과 링크가 포함된 태그
        "pattern": "/article/view/",
        "image_selector": "div.img_mark_reporter figure img", # ✅ 이미지 선택자 추가
        "dynamic": False
    },
    
    #뉴시스
    {
        "name": "뉴시스",
        "category": "경제",
        "url": "https://www.newsis.com/economy/list/?cid=10400&scid=10401",  # 실제 사용하는 페이지 URL로 수정 가능
        "base_url": "https://www.newsis.com",
        "selector": "ul.articleList2 li p.tit a",  # 제목과 링크가 있는 <a> 태그
        "pattern": "/view/NISX",                   # 기사 본문 URL 패턴
        "image_selector": "div.thumCont img",              # ✅ 이미지 선택자 추가
        "dynamic": False
    },
    {
        "name": "뉴시스",
        "category": "국제",
        "url": "https://www.newsis.com/economy/list/?cid=10400&scid=10410",  # 실제 사용하는 페이지 URL로 수정 가능
        "base_url": "https://www.newsis.com",
        "selector": "ul.articleList2 li p.tit a",  # 제목과 링크가 있는 <a> 태그
        "pattern": "/view/NISX",                   # 기사 본문 URL 패턴
        "image_selector": "div.thumCont img",              # ✅ 이미지 선택자 추가
        "dynamic": False
    },
    {
        "name": "뉴시스",
        "category": "금융",
        "url": "https://www.newsis.com/money/list/?cid=15000&scid=15001",  # 실제 사용하는 페이지 URL로 수정 가능
        "base_url": "https://www.newsis.com",
        "selector": "ul.articleList2 li p.tit a",  # 제목과 링크가 있는 <a> 태그
        "pattern": "/view/NISX",                   # 기사 본문 URL 패턴
        "image_selector": "div.thumCont img",              # ✅ 이미지 선택자 추가
        "dynamic": False
    }, 
    {
        "name": "뉴시스",
        "category": "산업",
        "url": "https://www.newsis.com/business/list/?cid=13000&scid=13001",  # 실제 사용하는 페이지 URL로 수정 가능
        "base_url": "https://www.newsis.com",
        "selector": "ul.articleList2 li p.tit a",  # 제목과 링크가 있는 <a> 태그
        "pattern": "/view/NISX",                   # 기사 본문 URL 패턴
        "image_selector": "div.thumCont img",              # ✅ 이미지 선택자 추가
        "dynamic": False
    },
    
    

    
]

# 새 기사 확인 주기 (초 단위)
CHECK_INTERVAL_SECONDS = 10