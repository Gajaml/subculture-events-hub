# -*- coding: utf-8 -*-
"""
데이터 정제 파서 모듈

크롤러가 수집한 원시 텍스트(Raw Data)에서 행사 정보를 추출합니다.
- 날짜(시작일/종료일) 추출: 다양한 한국어 날짜 표현 패턴 지원
- 장소 추출: 서울/수도권 주요 행사 장소 키워드 매칭
- 카테고리 자동 분류: IP명/키워드 기반 6개 카테고리 매핑
"""

import re
from datetime import datetime, date
from typing import Any, Dict, List, Optional, Tuple


# ==============================================================================
# 날짜 추출
# ==============================================================================

# 날짜 패턴 정규식 목록
DATE_PATTERNS = [
    # 2026.10.01 ~ 2026.10.15 / 2026-10-01 ~ 2026-10-15
    r'(\d{4})[.\-/](\d{1,2})[.\-/](\d{1,2})\s*[~\-–—부터]\s*(\d{4})[.\-/](\d{1,2})[.\-/](\d{1,2})',
    # 2026.10.01 ~ 10.15 (같은 해)
    r'(\d{4})[.\-/](\d{1,2})[.\-/](\d{1,2})\s*[~\-–—]\s*(\d{1,2})[.\-/](\d{1,2})',
    # 10월 1일 ~ 10월 15일 (연도 없음, 올해로 추정)
    r'(\d{1,2})월\s*(\d{1,2})일\s*[~\-–—부터]\s*(\d{1,2})월\s*(\d{1,2})일',
    # 10월 1일 ~ 15일 (같은 월)
    r'(\d{1,2})월\s*(\d{1,2})일\s*[~\-–—]\s*(\d{1,2})일',
    # 단일 날짜: 2026년 10월 1일
    r'(\d{4})년\s*(\d{1,2})월\s*(\d{1,2})일',
    # 단일 날짜: 2026.10.01
    r'(\d{4})[.\-/](\d{1,2})[.\-/](\d{1,2})',
]


def extract_dates(text: str) -> Tuple[Optional[str], Optional[str]]:
    """
    텍스트에서 시작일과 종료일을 추출합니다.
    
    Returns:
        (start_date, end_date) 튜플. 형식: 'YYYY-MM-DD'. 추출 실패 시 None.
    """
    if not text:
        return None, None

    current_year = date.today().year

    # 패턴 1: YYYY.MM.DD ~ YYYY.MM.DD (완전한 범위)
    m = re.search(DATE_PATTERNS[0], text)
    if m:
        start = f"{m.group(1)}-{int(m.group(2)):02d}-{int(m.group(3)):02d}"
        end = f"{m.group(4)}-{int(m.group(5)):02d}-{int(m.group(6)):02d}"
        return start, end

    # 패턴 2: YYYY.MM.DD ~ MM.DD (같은 해)
    m = re.search(DATE_PATTERNS[1], text)
    if m:
        year = m.group(1)
        start = f"{year}-{int(m.group(2)):02d}-{int(m.group(3)):02d}"
        end = f"{year}-{int(m.group(4)):02d}-{int(m.group(5)):02d}"
        return start, end

    # 패턴 3: MM월 DD일 ~ MM월 DD일
    m = re.search(DATE_PATTERNS[2], text)
    if m:
        start = f"{current_year}-{int(m.group(1)):02d}-{int(m.group(2)):02d}"
        end = f"{current_year}-{int(m.group(3)):02d}-{int(m.group(4)):02d}"
        return start, end

    # 패턴 4: MM월 DD일 ~ DD일 (같은 월)
    m = re.search(DATE_PATTERNS[3], text)
    if m:
        month = int(m.group(1))
        start = f"{current_year}-{month:02d}-{int(m.group(2)):02d}"
        end = f"{current_year}-{month:02d}-{int(m.group(3)):02d}"
        return start, end

    # 패턴 5: YYYY년 MM월 DD일 (단일)
    m = re.search(DATE_PATTERNS[4], text)
    if m:
        single = f"{m.group(1)}-{int(m.group(2)):02d}-{int(m.group(3)):02d}"
        return single, single

    # 패턴 6: YYYY.MM.DD (단일)
    m = re.search(DATE_PATTERNS[5], text)
    if m:
        single = f"{m.group(1)}-{int(m.group(2)):02d}-{int(m.group(3)):02d}"
        return single, single

    return None, None


# ==============================================================================
# 장소 추출
# ==============================================================================

# 주요 서브컬처 행사 장소 키워드 → 정식 명칭 및 주소 매핑
VENUE_KEYWORDS = {
    "더현대 서울": {"venueName": "더현대 서울 (여의도)", "address": "서울특별시 영등포구 여의대로 108"},
    "더현대서울": {"venueName": "더현대 서울 (여의도)", "address": "서울특별시 영등포구 여의대로 108"},
    "코엑스": {"venueName": "코엑스 (삼성)", "address": "서울특별시 강남구 영동대로 513"},
    "COEX": {"venueName": "코엑스 (삼성)", "address": "서울특별시 강남구 영동대로 513"},
    "킨텍스": {"venueName": "킨텍스 (일산)", "address": "경기도 고양시 일산서구 킨텍스로 217-60"},
    "KINTEX": {"venueName": "킨텍스 (일산)", "address": "경기도 고양시 일산서구 킨텍스로 217-60"},
    "DDP": {"venueName": "DDP 동대문디자인플라자", "address": "서울특별시 중구 을지로 281"},
    "동대문디자인플라자": {"venueName": "DDP 동대문디자인플라자", "address": "서울특별시 중구 을지로 281"},
    "에스팩토리": {"venueName": "에스팩토리 (성수)", "address": "서울특별시 성동구 연무장15길 11"},
    "아이파크몰": {"venueName": "용산 아이파크몰", "address": "서울특별시 용산구 한강대로23길 55"},
    "용산아이파크": {"venueName": "용산 아이파크몰", "address": "서울특별시 용산구 한강대로23길 55"},
    "롯데월드몰": {"venueName": "잠실 롯데월드몰", "address": "서울특별시 송파구 올림픽로 300"},
    "AK플라자 홍대": {"venueName": "AK플라자 홍대", "address": "서울특별시 마포구 양화로 188"},
    "AK플라자홍대": {"venueName": "AK플라자 홍대", "address": "서울특별시 마포구 양화로 188"},
    "홍대": {"venueName": "홍대 (마포)", "address": "서울특별시 마포구"},
    "성수": {"venueName": "성수동", "address": "서울특별시 성동구 성수동"},
    "신촌": {"venueName": "신촌", "address": "서울특별시 서대문구 신촌"},
    "강남": {"venueName": "강남", "address": "서울특별시 강남구"},
    "건대": {"venueName": "건대입구", "address": "서울특별시 광진구"},
    "아케이드 성수": {"venueName": "아케이드 성수", "address": "서울특별시 성동구 아차산로 68"},
}


def extract_venue(text: str) -> Dict[str, str]:
    """
    텍스트에서 행사 장소를 추출합니다.
    더 구체적인 키워드부터 먼저 매칭하여 정확도를 높입니다.
    
    Returns:
        {"venueName": "...", "address": "..."} 딕셔너리.
        매칭 실패 시 빈 값.
    """
    if not text:
        return {"venueName": "", "address": ""}

    # 긴(구체적) 키워드부터 먼저 검색 (greedy matching)
    sorted_keywords = sorted(VENUE_KEYWORDS.keys(), key=len, reverse=True)

    for keyword in sorted_keywords:
        if keyword in text:
            return VENUE_KEYWORDS[keyword].copy()

    return {"venueName": "", "address": ""}


# ==============================================================================
# 카테고리 자동 분류
# ==============================================================================

# IP명/키워드 → 카테고리 매핑
CATEGORY_KEYWORDS = {
    "게임": [
        "블루아카이브", "블아", "원신", "스타레일", "붕괴", "명일방주", "아크나이츠",
        "FGO", "페그오", "페이트", "Fate", "우마무스메", "말딸", "니케", "NIKKE",
        "리그오브레전드", "롤", "LoL", "배틀그라운드", "배그", "발로란트",
        "메이플스토리", "던전앤파이터", "던파", "넥슨", "호요버스", "miHoYo",
        "카카오게임즈", "VCR", "게임",
    ],
    "애니메이션": [
        "귀멸의 칼날", "귀멸", "주술회전", "체인소맨", "체인소 맨", "하이큐",
        "나루토", "원피스", "진격의 거인", "스파이패밀리", "스파이×패밀리",
        "신카이 마코토", "너의 이름은", "초속5센티미터", "스즈메의 문단속",
        "슬램덩크", "드래곤볼", "건담", "애니메이션", "애니", "극장판",
        "MAPPA", "유포테이블", "ufotable",
    ],
    "버튜버": [
        "홀로라이브", "hololive", "니지산지", "nijisanji", "스텔라이브", "stellive",
        "이세돌", "버튜버", "VTuber", "V튜버", "가상유튜버", "팬미팅",
    ],
    "웹툰": [
        "나혼자만레벨업", "나 혼자만 레벨업", "나혼렙", "전지적독자시점", "전독시",
        "신의 탑", "갓오브하이스쿨", "카카오페이지", "네이버웹툰", "웹툰",
    ],
    "동인행사": [
        "코믹월드", "서코", "코미케", "동인", "동인지", "코스프레", "회지",
    ],
    "피규어/굿즈": [
        "피규어", "넨도로이드", "굿스마일", "스케일피규어", "프라모델",
        "반다이", "원더페스티벌", "원페스", "피규어엑스포",
    ],
}


def classify_category(text: str) -> str:
    """
    텍스트 내용을 분석하여 6개 카테고리 중 가장 적합한 것을 반환합니다.
    
    Returns:
        카테고리 문자열. 매칭 실패 시 '게임' (기본값).
    """
    if not text:
        return "게임"

    # 카테고리별 키워드 히트 수를 세어 가장 많이 매칭된 카테고리 선택
    scores = {}
    for category, keywords in CATEGORY_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw in text)
        if score > 0:
            scores[category] = score

    if scores:
        return max(scores, key=scores.get)

    return "게임"


# ==============================================================================
# 통합 파싱 함수
# ==============================================================================
def parse_raw_item(raw: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    크롤러가 수집한 원시 데이터 1건을 정제된 이벤트 데이터로 변환합니다.
    
    Args:
        raw: {"title": "...", "description": "...", "link": "...", ...} 형태의 원시 데이터

    Returns:
        정제된 이벤트 딕셔너리, 또는 날짜 추출 실패 시 None
    """
    title = raw.get("title", "")
    description = raw.get("description", "")
    link = raw.get("link", "")
    combined_text = f"{title} {description}"

    # 1. 날짜 추출
    start_date, end_date = extract_dates(combined_text)
    if not start_date:
        return None  # 날짜를 추출할 수 없으면 이벤트로 인정하지 않음

    # 2. 장소 추출
    venue_info = extract_venue(combined_text)

    # 3. 카테고리 분류
    category = classify_category(combined_text)

    # 4. 제목 정리 (HTML 태그 제거)
    clean_title = re.sub(r'<[^>]+>', '', title).strip()
    clean_desc = re.sub(r'<[^>]+>', '', description).strip()

    return {
        "title": clean_title,
        "category": category,
        "subCategory": "",
        "startDate": start_date,
        "endDate": end_date,
        "reservationType": "",
        "reservationUrl": "",
        "reservationStartDate": None,
        "reservationEndDate": None,
        "venueName": venue_info["venueName"],
        "address": venue_info["address"],
        "lat": None,
        "lng": None,
        "description": clean_desc,
        "thumbnailUrl": "",
        "tags": [],
        "sourceUrl": link,
        "source": raw.get("source", "naver"),
    }


def parse_raw_items(raw_items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """원시 데이터 목록을 일괄 정제합니다. 날짜 추출 실패 항목은 자동 제외됩니다."""
    results = []
    for item in raw_items:
        parsed = parse_raw_item(item)
        if parsed:
            results.append(parsed)
    return results


# ==============================================================================
# 테스트 (직접 실행 시)
# ==============================================================================
if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding='utf-8')

    test_cases = [
        "블루아카이브 3.5주년 팝업스토어 2026.09.25~2026.10.08 더현대 서울",
        "원신 콜라보카페 10월 1일 ~ 10월 15일 홍대",
        "코믹월드 2026년 10월 24일 킨텍스",
        "주술회전 전시회 2026-11-05 ~ 2026-11-18 코엑스",
        "날짜 없는 텍스트 입니다",
    ]

    print("=" * 60)
    print("  Parser 테스트")
    print("=" * 60)

    for text in test_cases:
        print(f"\n입력: {text}")
        dates = extract_dates(text)
        venue = extract_venue(text)
        cat = classify_category(text)
        print(f"   날짜: {dates[0]} ~ {dates[1]}")
        print(f"   장소: {venue['venueName']} ({venue['address']})")
        print(f"   카테고리: {cat}")
