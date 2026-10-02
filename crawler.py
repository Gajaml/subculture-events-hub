import os
import time
import requests
import feedparser
from bs4 import BeautifulSoup
import urllib.parse
import json
from datetime import datetime

# ==========================================
# 1. Naver API 수집기
# ==========================================
def crawl_naver_api():
    client_id = os.environ.get("NAVER_CLIENT_ID")
    client_secret = os.environ.get("NAVER_CLIENT_SECRET")
    
    if not client_id or not client_secret:
        print("⚠️ [NaverBot] 네이버 API 키가 환경변수에 없습니다. 네이버 수집을 건너뜁니다.")
        return []

    print("🤖 [NaverBot] 네이버 클라우드 검색 시작...")
    events = []
    queries = ["팝업스토어", "콜라보카페", "서브컬처 행사"]
    
    for q in queries:
        url = f"https://naverapihub.apigw.ntruss.com/search/v1/blog?query={urllib.parse.quote(q)}&display=10"
        headers = {
            "X-NCP-APIGW-API-KEY-ID": client_id,
            "X-NCP-APIGW-API-KEY": client_secret
        }
        
        try:
            res = requests.get(url, headers=headers, timeout=5)
            if res.status_code == 200:
                data = res.json()
                for item in data.get('items', []):
                    # 임시 변환 로직 (추후 정규식이나 LLM으로 날짜/장소 정밀 추출)
                    events.append({
                        "source": "naver",
                        "title": item.get('title', '').replace('<b>', '').replace('</b>', ''),
                        "link": item.get('link', ''),
                        "description": item.get('description', '')
                    })
            time.sleep(0.5) # API 속도 제한 방지
        except Exception as e:
            print(f"⚠️ [NaverBot] 수집 에러: {e}")
            
    print(f"   -> {len(events)}건의 기초 데이터 수집 완료")
    return events

# ==========================================
# 2. RSS 기반 공식 사이트 수집기 (넥슨 등)
# ==========================================
def crawl_official_rss():
    print("🤖 [RssBot] 게임사 공식 RSS 수집 시작...")
    events = []
    # 예시: 넥슨 또는 기타 서브컬처 게임 공지 RSS
    rss_urls = [
        # 실제 넥슨 RSS가 없으면 에러가 날 수 있으므로 예시 용도로 빈배열. 
        # (실제 URL 발견 시 여기에 추가)
    ]
    
    for url in rss_urls:
        feed = feedparser.parse(url)
        for entry in feed.entries:
            if '팝업' in entry.title or '콜라보' in entry.title:
                events.append({
                    "source": "rss",
                    "title": entry.title,
                    "link": entry.link,
                    "description": entry.description
                })
    
    print(f"   -> {len(events)}건 수집 완료 (RSS)")
    return events

# ==========================================
# 3. HTML 직접 파싱 수집기 (애니플러스 등)
# ==========================================
def crawl_aniplus():
    print("🤖 [WebBot] 애니플러스 공지사항 수집 시작...")
    events = []
    url = "https://www.aniplus-asia.com/ko/news" # 예시 URL
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    
    try:
        # 애니플러스의 실제 HTML 구조에 맞게 파싱 로직 세팅 필요
        res = requests.get(url, headers=headers, timeout=10)
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, 'html.parser')
            # 예시 추출 (실제 DOM 구조 분석 후 수정됨)
            articles = soup.find_all('article')
            for article in articles:
                title_tag = article.find('h2')
                if title_tag and ('콜라보' in title_tag.text or '카페' in title_tag.text):
                    events.append({
                        "source": "aniplus",
                        "title": title_tag.text.strip(),
                        "link": url
                    })
    except Exception as e:
        print(f"⚠️ [WebBot] 애니플러스 수집 에러: {e}")
        
    print(f"   -> {len(events)}건 수집 완료 (WebBot)")
    return events

# ==========================================
# 메인 파이프라인
# ==========================================
def run_pipeline():
    print("="*50)
    print("서브컬처 이벤트 허브 - 통합 크롤링 파이프라인 가동")
    print("="*50)
    
    all_raw_data = []
    
    all_raw_data.extend(crawl_naver_api())
    all_raw_data.extend(crawl_official_rss())
    all_raw_data.extend(crawl_aniplus())
    
    print(f"\n총 {len(all_raw_data)}건의 원시(Raw) 데이터 수집이 완료되었습니다.")
    print("다음 단계: 이 원시 데이터에서 '장소', '시작일', '종료일'을 정밀 추출하는 파서를 가동해야 합니다.")

if __name__ == "__main__":
    run_pipeline()
