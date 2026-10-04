# -*- coding: utf-8 -*-
"""
서브컬처 이벤트 허브 - 통합 크롤링 파이프라인

수집(Crawl) → 정제(Parse) → 좌표변환(Geocode) → DB 저장 전체 흐름을 담당합니다.

실행: python crawler.py
"""

import os
import sys
import time
import re
import requests
import feedparser
import urllib.parse
from datetime import datetime
from bs4 import BeautifulSoup

# Windows 콘솔 인코딩 문제 방지
sys.stdout.reconfigure(encoding='utf-8')

# ------------------------------------------------------------------
# .env 파일 로드 (API 키를 환경변수로 주입)
# ------------------------------------------------------------------
def _load_env():
    env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, v = line.split("=", 1)
                k = k.strip()
                v = v.strip().strip('"').strip("'")
                if k not in os.environ:
                    os.environ[k] = v

_load_env()


# ==============================================================================
# 1. 네이버 API 수집기 (NaverBot)
# ==============================================================================
NAVER_SEARCH_QUERIES = [
    "팝업스토어 서울",
    "콜라보카페 서브컬처",
    "게임 팝업 행사",
    "애니메이션 팝업스토어",
    "버튜버 팬미팅 오프라인",
    "동인행사 코믹월드",
]

def crawl_naver_api() -> list:
    """
    네이버 클라우드 검색 API로 서브컬처 행사 관련 블로그 글을 수집합니다.
    """
    client_id = os.environ.get("NAVER_CLIENT_ID", "")
    client_secret = os.environ.get("NAVER_CLIENT_SECRET", "")

    if not client_id or not client_secret:
        print("[NaverBot] 네이버 API 키가 없습니다. .env 파일을 확인해 주세요.")
        return []

    print(f"[NaverBot] 네이버 클라우드 검색 시작 ({len(NAVER_SEARCH_QUERIES)}개 키워드)...")
    raw_items = []

    for query in NAVER_SEARCH_QUERIES:
        encoded = urllib.parse.quote(query)
        url = f"https://naverapihub.apigw.ntruss.com/search/v1/blog?query={encoded}&display=10&sort=date"
        headers = {
            "X-NCP-APIGW-API-KEY-ID": client_id,
            "X-NCP-APIGW-API-KEY": client_secret,
        }

        try:
            res = requests.get(url, headers=headers, timeout=8)
            if res.status_code == 200:
                data = res.json()
                items = data.get("items", [])
                for item in items:
                    # HTML 태그 제거
                    title = re.sub(r'<[^>]+>', '', item.get("title", "")).strip()
                    description = re.sub(r'<[^>]+>', '', item.get("description", "")).strip()
                    raw_items.append({
                        "source": "naver_blog",
                        "title": title,
                        "description": description,
                        "link": item.get("link", ""),
                        "pubDate": item.get("postdate", ""),
                    })
                print(f"  [{query}] {len(items)}건 수집")
            else:
                print(f"  [{query}] API 오류: HTTP {res.status_code}")
        except Exception as e:
            print(f"  [{query}] 수집 실패: {e}")

        time.sleep(0.3)  # API 속도 제한 방지

    print(f"[NaverBot] 총 {len(raw_items)}건 원시 데이터 수집 완료")
    return raw_items


# ==============================================================================
# 2. RSS 기반 공식 사이트 수집기 (RssBot)
# ==============================================================================
RSS_FEEDS = [
    # 향후 확인된 RSS URL을 여기에 추가
    # 예: ("https://event.nexon.com/feed/news.rss", "nexon"),
]

def crawl_official_rss() -> list:
    """RSS 피드에서 공식 공지를 수집합니다."""
    if not RSS_FEEDS:
        print("[RssBot] 등록된 RSS 피드가 없습니다. 건너뜁니다.")
        return []

    raw_items = []
    for feed_url, source_name in RSS_FEEDS:
        try:
            feed = feedparser.parse(feed_url)
            for entry in feed.entries:
                title = entry.get("title", "")
                if any(kw in title for kw in ["팝업", "콜라보", "행사", "이벤트", "오프라인"]):
                    raw_items.append({
                        "source": source_name,
                        "title": title,
                        "description": entry.get("summary", ""),
                        "link": entry.get("link", ""),
                    })
        except Exception as e:
            print(f"  [{source_name}] RSS 수집 실패: {e}")

    print(f"[RssBot] 총 {len(raw_items)}건 수집 완료")
    return raw_items


# ==============================================================================
# 3. 넥슨 이벤트 페이지 전용 크롤러 (NexonBot)
# ==============================================================================
def crawl_nexon_events() -> list:
    """
    넥슨 공식 이벤트 페이지(event.nexon.com)에서 진행 중인 이벤트를 수집합니다.
    HTML 구조가 잘 정리되어 있어 제목/날짜/게임명을 정확히 추출할 수 있습니다.
    """
    print("[NexonBot] 넥슨 공식 이벤트 수집 시작...")
    raw_items = []
    url = "https://event.nexon.com/event/ongoinglist.aspx"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

    try:
        res = requests.get(url, headers=headers, timeout=10)
        if res.status_code != 200:
            print(f"  HTTP {res.status_code} 오류")
            return []

        soup = BeautifulSoup(res.text, "html.parser")
        items = soup.find_all("li", class_="eventItem")

        for item in items:
            # 제목
            tit_el = item.find("span", class_="eventTit")
            title = tit_el.get_text(strip=True) if tit_el else ""

            # 설명
            cnts_el = item.find("span", class_="eventCnts")
            description = cnts_el.get_text(strip=True) if cnts_el else ""

            # 날짜 (YYYY-MM-DD ~ YYYY-MM-DD)
            period_el = item.find("span", class_="eventPeriod")
            period_text = period_el.get_text(strip=True) if period_el else ""

            # 게임명
            game_el = item.find("span", class_="eventGameName")
            game_name = game_el.get_text(strip=True) if game_el else ""

            # 링크
            a_tag = item.find("a", href=True)
            link = a_tag.get("href", "") if a_tag else ""

            # 종료일이 9999인 항목은 상시 이벤트이므로 제외
            if "9999" in period_text:
                continue

            if title:
                raw_items.append({
                    "source": "nexon",
                    "title": f"[{game_name}] {title}" if game_name else title,
                    "description": f"{description} {period_text}",
                    "link": link,
                })

        print(f"  => {len(raw_items)}건 수집 완료 (상시 이벤트 제외)")
    except Exception as e:
        print(f"  [NexonBot] 수집 실패: {e}")

    return raw_items


# ==============================================================================
# 4. 범용 웹 크롤러 (WebBot) - 향후 사이트 추가용
# ==============================================================================
WEB_TARGETS = [
    # 향후 파서 개발 완료된 사이트를 여기에 추가
    # 형식: (URL, 소스명)
]

def crawl_web() -> list:
    """공식 홈페이지에서 HTML을 직접 파싱하여 공지를 수집합니다."""
    if not WEB_TARGETS:
        print("[WebBot] 등록된 수집 대상이 없습니다. 건너뜁니다.")
        return []

    raw_items = []
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    for url, source_name in WEB_TARGETS:
        try:
            res = requests.get(url, headers=headers, timeout=10)
            if res.status_code == 200:
                soup = BeautifulSoup(res.text, "html.parser")
                for article in soup.find_all(["article", "li", "div"], limit=30):
                    title_tag = article.find(["h2", "h3", "a"])
                    if title_tag:
                        title = title_tag.get_text().strip()
                        if any(kw in title for kw in ["팝업", "콜라보", "행사", "오프라인"]):
                            raw_items.append({
                                "source": source_name,
                                "title": title,
                                "description": "",
                                "link": url,
                            })
        except Exception as e:
            print(f"  [{source_name}] 수집 실패: {e}")

    print(f"[WebBot] 총 {len(raw_items)}건 수집 완료")
    return raw_items


# ==============================================================================
# 메인 파이프라인: 수집 → 정제 → 좌표변환 → DB 저장
# ==============================================================================
def run_pipeline(dry_run: bool = False) -> dict:
    """
    전체 크롤링 파이프라인을 실행합니다.

    Args:
        dry_run: True면 DB에 저장하지 않고 결과만 출력합니다.

    Returns:
        {"collected": int, "parsed": int, "saved": int} 결과 요약
    """
    print("=" * 60)
    print("  서브컬처 이벤트 허브 - 크롤링 파이프라인 가동")
    print(f"  실행 시각: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    if dry_run:
        print("  [DRY RUN 모드] DB에 저장하지 않고 결과만 출력합니다.")
    print("=" * 60)

    # 1단계: 수집 (Crawl)
    print("\n[1단계] 데이터 수집 중...")
    all_raw = []
    all_raw.extend(crawl_naver_api())
    all_raw.extend(crawl_nexon_events())
    all_raw.extend(crawl_official_rss())
    all_raw.extend(crawl_web())
    print(f"\n  => 총 {len(all_raw)}건 원시 데이터 수집 완료")

    if not all_raw:
        print("\n수집된 데이터가 없습니다. 파이프라인 종료.")
        return {"collected": 0, "parsed": 0, "saved": 0}

    # 2단계: 정제 (Parse)
    print("\n[2단계] 데이터 정제 중 (날짜/장소/카테고리 추출)...")
    from parser import parse_raw_items
    parsed_events = parse_raw_items(all_raw)
    print(f"  => {len(all_raw)}건 중 날짜 추출 성공: {len(parsed_events)}건")

    if not parsed_events:
        print("\n정제된 이벤트가 없습니다. (날짜 정보를 포함한 글이 없음)")
        print("수집된 원시 데이터 샘플:")
        for item in all_raw[:3]:
            print(f"  - {item['title'][:60]}")
        return {"collected": len(all_raw), "parsed": 0, "saved": 0}

    # 3단계: 좌표 변환 (Geocode)
    print("\n[3단계] 주소 → 좌표 변환 중...")
    from geocoder import geocode_event
    geocoded_count = 0
    for ev in parsed_events:
        before_lat = ev.get("lat")
        ev = geocode_event(ev)
        if ev.get("lat") and not before_lat:
            geocoded_count += 1
    print(f"  => {geocoded_count}건 좌표 변환 완료")

    # 결과 미리보기 출력
    print("\n[정제 결과 미리보기]")
    print("-" * 60)
    for ev in parsed_events[:5]:
        print(f"  제목: {ev['title'][:40]}")
        print(f"  날짜: {ev['startDate']} ~ {ev['endDate']}")
        print(f"  장소: {ev['venueName']}")
        print(f"  카테고리: {ev['category']}")
        print(f"  좌표: ({ev.get('lat')}, {ev.get('lng')})")
        print()

    saved_count = 0
    if not dry_run:
        # 4단계: DB 저장
        print("[4단계] DB 저장 중...")
        from database import init_db, insert_events_bulk
        init_db()
        saved_count = insert_events_bulk(parsed_events)
        print(f"  => {saved_count}건 신규 저장 완료 (중복 제외)")

    print("=" * 60)
    print(f"  파이프라인 완료!")
    print(f"  수집: {len(all_raw)}건 / 정제: {len(parsed_events)}건 / 저장: {saved_count}건")
    print("=" * 60)

    return {
        "collected": len(all_raw),
        "parsed": len(parsed_events),
        "saved": saved_count,
    }


if __name__ == "__main__":
    # dry_run=True: DB 저장 없이 결과만 확인
    # dry_run=False: 실제 DB에 저장
    run_pipeline(dry_run=False)
