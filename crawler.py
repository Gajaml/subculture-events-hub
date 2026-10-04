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
    '"콜라보 카페" 기간 위치',
    '"팝업스토어" 기간 더현대',
    '"팝업스토어" 기간 성수',
    '"팝업스토어" 기간 홍대',
    '애니메이트 팝업 기간',
    '서브컬처 오프라인 행사 기간',
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

# ==============================================================================
# 5. Playwright 기반 오프라인 팝업스토어 수집기 (PopplyBot & PopgaBot)
# ==============================================================================

def _parse_event_dates(date_str: str):
    """'26.10.01 - 26.10.07' 또는 '09. 23 - 12. 01' 등의 날짜 문자열을 (YYYY-MM-DD, YYYY-MM-DD)로 변환"""
    parts = re.split(r'[-~]', date_str)
    if len(parts) == 2:
        def fmt(s):
            m = re.findall(r'\d+', s)
            if len(m) == 3:
                y, mo, d = m
                if len(y) == 2:
                    y = '20' + y
                return f"{y}-{int(mo):02d}-{int(d):02d}"
            elif len(m) == 2:
                # 연도가 없는 경우 현재 연도(2026) 부여
                mo, d = m
                return f"2026-{int(mo):02d}-{int(d):02d}"
            return ""
        s_date, e_date = fmt(parts[0]), fmt(parts[1])
        if s_date and e_date:
            return s_date, e_date
    return "", ""

def _extract_venue_from_address(address_text: str, default_region: str = "") -> str:
    venues = ["아이파크몰", "더현대 서울", "더현대", "EQL", "코엑스", "킨텍스", "AK플라자", "롯데백화점", "신세계백화점", "현대백화점", "애니메이트", "홍대", "잠실"]
    for v in venues:
        if v in address_text:
            return v
    parts = address_text.split()
    if len(parts) >= 4:
        return " ".join(parts[3:])
    return default_region


def crawl_popga(max_items: int = 10) -> list:
    """
    Playwright를 사용해 팝가(Popga)에서 실제 서브컬처(애니/게임/캐릭터) 팝업스토어를 수집합니다.
    """
    print(f"[PopgaBot] 팝가(Popga) 서브컬처 팝업스토어 수집 시작 (최대 {max_items}건)...")
    try:
        from playwright.sync_api import sync_playwright
        from parser import is_subculture_text
    except ImportError:
        return []

    events = []
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
            )
            page = context.new_page()
            page.goto("https://popga.co.kr", timeout=30000, wait_until="networkidle")
            page.wait_for_timeout(2000)

            cards = page.query_selector_all("a[href*='/popup/']")
            seen_links = set()
            candidates = []

            for card in cards:
                href = card.get_attribute("href")
                if not href or href in seen_links:
                    continue
                seen_links.add(href)
                raw_text = card.inner_text().strip().replace("\n", " ")

                # 서브컬처 판별
                if is_subculture_text(raw_text, "애니/캐릭터", raw_text):
                    candidates.append((href, raw_text))

            print(f"  => 팝가 서브컬처 후보 {len(candidates)}건 발견, 상세 주소 수집...")

            for href, raw_text in candidates[:max_items]:
                detail_url = f"https://popga.co.kr{href}" if href.startswith("/") else href
                detail_page = context.new_page()
                try:
                    detail_page.goto(detail_url, timeout=15000)
                    detail_page.wait_for_timeout(1000)
                    body_text = detail_page.inner_text("body")

                    # 주소 추출
                    full_address = ""
                    for line in body_text.split("\n"):
                        line = line.strip()
                        if any(c in line for c in ["서울", "경기", "인천", "부산", "대구"]) and \
                           any(c in line for c in ["길", "로", "대로", "구", "동"]):
                            if len(line) > 8 and "쿠팡" not in line and "지도" not in line and "영업" not in line:
                                full_address = line
                                break

                    # 대표 이미지 추출
                    img_url = ""
                    img_elem = detail_page.query_selector("img[src*='cdn.popga.co.kr/spot'], img[src*='thumbnail']")
                    if img_elem:
                        img_url = img_elem.get_attribute("src") or ""

                    # 제목 추출 (H1 또는 페이지 타이틀)
                    title = ""
                    h1 = detail_page.query_selector("h1")
                    if h1:
                        title = h1.inner_text().strip()
                    if not title:
                        title = raw_text.split("·")[-1].strip() if "·" in raw_text else raw_text[:30]

                    # 날짜 추출
                    dates = re.findall(r'(\d{2}\.\s*\d{2})\s*[-~]\s*(\d{2}\.\s*\d{2})', raw_text)
                    start_date, end_date = "", ""
                    if dates:
                        s_raw, e_raw = dates[0]
                        start_date, end_date = _parse_event_dates(f"{s_raw} - {e_raw}")

                    if not start_date or not full_address:
                        continue

                    venue_name = _extract_venue_from_address(full_address, "서울")
                    cat = "콜라보카페" if "카페" in title else ("전시회" if "전시" in title else "팝업스토어")

                    events.append({
                        "title": title,
                        "category": cat,
                        "subCategory": "애니/캐릭터",
                        "startDate": start_date,
                        "endDate": end_date,
                        "reservationType": "현장방문",
                        "reservationUrl": detail_url,
                        "reservationStartDate": None,
                        "reservationEndDate": None,
                        "venueName": venue_name,
                        "address": full_address,
                        "lat": None,
                        "lng": None,
                        "description": f"[서브컬처] {title} - 위치: {full_address}",
                        "thumbnailUrl": img_url,
                        "tags": ["서브컬처", "애니/캐릭터", cat],
                        "sourceUrl": detail_url,
                        "source": "popga",
                    })
                    print(f"    [Popga] {title} ({start_date}~{end_date}) -> {full_address}")
                except Exception as e:
                    print(f"    - {href} 수집 오류: {e}")
                finally:
                    detail_page.close()

            browser.close()
        print(f"[PopgaBot] 총 {len(events)}건 서브컬처 팝업 수집 완료")
    except Exception as e:
        print(f"[PopgaBot] 수집 실패: {e}")

    return events


def crawl_popply(max_items: int = 25) -> list:
    """
    Playwright를 사용해 팝플리(Popply)에서 실제 서브컬처(애니/게임/캐릭터/콜라보) 팝업스토어를 수집합니다.
    """
    print(f"[PopplyBot] 팝플리(Popply) 서브컬처 팝업스토어 수집 시작 (최대 {max_items}건)...")
    try:
        from playwright.sync_api import sync_playwright
        from parser import is_subculture_text
    except ImportError:
        return []

    events = []
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
            )
            page = context.new_page()
            page.goto("https://popply.co.kr/popup", timeout=30000, wait_until="networkidle")
            page.wait_for_timeout(2000)

            cards = page.query_selector_all("a[href*='/popup/']")
            seen_links = set()
            candidates = []

            for card in cards:
                href = card.get_attribute("href")
                if not href or href in seen_links:
                    continue
                text = card.inner_text().strip()
                lines = [l.strip() for l in text.split("\n") if l.strip()]
                if len(lines) >= 4:
                    seen_links.add(href)
                    cat_tag = lines[0]
                    title = lines[1]
                    date_str = lines[2]
                    region = lines[3]

                    # 엄격한 서브컬처 판별: 패션/뷰티/스포츠/푸드 등 완전 배제
                    if is_subculture_text(title, cat_tag, f"{title} {region}"):
                        candidates.append({
                            "href": href,
                            "category_tag": cat_tag,
                            "title": title,
                            "date_str": date_str,
                            "region": region,
                        })

            print(f"  => 팝플리 서브컬처 후보 {len(candidates)}건 발견, 상세 주소 추출 시작...")

            for item in candidates[:max_items]:
                detail_url = f"https://popply.co.kr{item['href']}"
                detail_page = context.new_page()
                try:
                    detail_page.goto(detail_url, timeout=15000)
                    detail_page.wait_for_timeout(1000)
                    body_text = detail_page.inner_text("body")

                    full_address = item["region"]
                    for line in body_text.split("\n"):
                        line = line.strip()
                        if any(c in line for c in ["서울", "경기", "인천", "부산", "대구"]) and \
                           any(c in line for c in ["길", "로", "대로", "구", "동", "층"]):
                            if len(line) > 10 and not line.startswith("📅") and "지도" not in line and "영업" not in line:
                                full_address = line
                                break

                    img_url = ""
                    img_elem = detail_page.query_selector("img[src*='cloudfront.net/store'], img[alt*='썸네일']")
                    if img_elem:
                        raw_src = img_elem.get_attribute("src") or ""
                        if "url=" in raw_src:
                            match = re.search(r'url=([^&]+)', raw_src)
                            if match:
                                img_url = urllib.parse.unquote(match.group(1))
                        else:
                            img_url = raw_src

                    start_date, end_date = _parse_event_dates(item["date_str"])
                    venue_name = _extract_venue_from_address(full_address, item["region"])

                    cat = "팝업스토어"
                    if "카페" in item["title"]:
                        cat = "콜라보카페"
                    elif "전시" in item["title"] or "특별전" in item["title"]:
                        cat = "전시회"
                    elif "게임" in item["title"] or "IP" in item["category_tag"]:
                        cat = "게임"

                    events.append({
                        "title": item["title"],
                        "category": cat,
                        "subCategory": item["category_tag"],
                        "startDate": start_date,
                        "endDate": end_date,
                        "reservationType": "현장방문",
                        "reservationUrl": detail_url,
                        "reservationStartDate": None,
                        "reservationEndDate": None,
                        "venueName": venue_name,
                        "address": full_address,
                        "lat": None,
                        "lng": None,
                        "description": f"[{item['category_tag']}] {item['title']} - 위치: {full_address}",
                        "thumbnailUrl": img_url,
                        "tags": ["서브컬처", item["category_tag"], cat],
                        "sourceUrl": detail_url,
                        "source": "popply",
                    })
                    print(f"    [Popply] {item['title']} ({start_date}~{end_date}) -> {full_address}")
                except Exception as e:
                    print(f"    - {item['title']} 상세 수집 에러: {e}")
                finally:
                    detail_page.close()

            browser.close()

        print(f"[PopplyBot] 총 {len(events)}건 서브컬처 팝업 수집 완료")
    except Exception as e:
        print(f"[PopplyBot] 크롤링 실패: {e}")

    return events


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
    print("  서브컬처 이벤트 허브 - 오프라인 서브컬처 크롤링 파이프라인 가동")
    print(f"  실행 시각: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    if dry_run:
        print("  [DRY RUN 모드] DB에 저장하지 않고 결과만 출력합니다.")
    print("=" * 60)

    # 1단계: 수집 (Crawl)
    print("\n[1단계] 데이터 수집 중...")
    all_raw = []
    all_raw.extend(crawl_popga(max_items=10))
    all_raw.extend(crawl_popply(max_items=25))
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
