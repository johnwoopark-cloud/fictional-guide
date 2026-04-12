import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime, timedelta, timezone

def get_ratings_by_category(query):
    url = f"https://search.daum.net/search?w=tot&q={query}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    try:
        res = requests.get(url, headers=headers, timeout=20)
        soup = BeautifulSoup(res.text, 'html.parser')
        
        rows = []
        tables = soup.find_all('table')
        for t in tables:
            if '순위' in t.text and '프로그램' in t.text:
                rows = t.find_all('tr')
                break
        
        data = []
        for row in rows:
            cols = row.find_all(['td', 'th'])
            txt = [c.get_text(strip=True) for c in cols]
            if len(txt) >= 4 and txt[0].isdigit():
                data.append({
                    'rank': txt[0],
                    'program': txt[1],
                    'channel': txt[2],
                    'rate': txt[3].replace('%', '')
                })
        return data[:20]
    except Exception as e:
        print(f"❌ {query} 수집 에러: {e}")
        return []

# 수집할 카테고리 정의
categories = {
    'terrestrial': '지상파시청률',
    'comprehensive': '종합편성시청률',
    'cable': '케이블시청률'
}

# 데이터 수집 실행
kst = timezone(timedelta(hours=9))
result = {
    'date': datetime.now(kst).strftime('%Y-%m-%d %H:%M'),
    'terrestrial': [],
    'comprehensive': [],
    'cable': []
}

for key, query in categories.items():
    print(f"--- {query} 수집 시작 ---")
    result[key] = get_ratings_by_category(query)
    print(f"✅ {key} 완료: {len(result[key])}건")

# 통합 데이터 저장
with open('data.json', 'w', encoding='utf-8') as f:
    json.dump(result, f, ensure_ascii=False, indent=4)
