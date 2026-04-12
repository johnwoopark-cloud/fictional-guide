import requests
from bs4 import BeautifulSoup
import json
import os
from datetime import datetime, timedelta, timezone

def get_daum_ratings(query):
    url = f"https://search.daum.net/search?w=tot&q={query}"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
    try:
        res = requests.get(url, headers=headers, timeout=20)
        soup = BeautifulSoup(res.text, 'html.parser')
        rows = []
        for t in soup.find_all('table'):
            if '순위' in t.text and '프로그램' in t.text:
                rows = t.find_all('tr')
                break
        data = []
        for row in rows:
            cols = row.find_all(['td', 'th'])
            txt = [c.get_text(strip=True) for c in cols]
            if len(txt) >= 4 and txt[0].isdigit():
                data.append({'rank': txt[0], 'program': txt[1], 'channel': txt[2], 'rate': txt[3].replace('%', '')})
        return data[:20]
    except Exception as e:
        print(f"❌ {query} 에러: {e}")
        return []

# 1. 기본 설정 및 시간 계산
kst = timezone(timedelta(hours=9))
now = datetime.now(kst)
today_str = now.strftime('%Y-%m-%d')
today_time = now.strftime('%Y-%m-%d %H:%M')

# 2. 데이터 수집
categories = {'terrestrial': '지상파시청률', 'comprehensive': '종합편성시청률', 'cable': '케이블시청률'}
daily_data = {'date': today_time, 'terrestrial': [], 'comprehensive': [], 'cable': []}

for key, query in categories.items():
    daily_data[key] = get_daum_ratings(query)

# 3. 파일 저장 경로 설정 (history 폴더 없으면 생성)
os.makedirs('history', exist_ok=True)

# A. 오늘자 개별 기록 저장 (history/2026-04-12.json)
history_path = f'history/{today_str}.json'
with open(history_path, 'w', encoding='utf-8') as f:
    json.dump(daily_data, f, ensure_ascii=False, indent=4)

# B. 최신 데이터 업데이트 (data.json - 기존 index.html용)
with open('data.json', 'w', encoding='utf-8') as f:
    json.dump(daily_data, f, ensure_ascii=False, indent=4)

# C. [핵심] 누적 데이터 업데이트 (all_ratings.json - 그래프용)
all_ratings_path = 'all_ratings.json'
if os.path.exists(all_ratings_path):
    with open(all_ratings_path, 'r', encoding='utf-8') as f:
        try:
            all_history = json.load(f)
        except:
            all_history = {}
else:
    all_history = {}

# 오늘 날짜 키로 데이터 누적 (중복 방지)
all_history[today_str] = daily_data

with open(all_ratings_path, 'w', encoding='utf-8') as f:
    json.dump(all_history, f, ensure_ascii=False, indent=4)

print(f"✅ {today_str} 아카이빙 완료 (history 파일 및 통합 로그 갱신)")
