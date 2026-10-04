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
        raw: 원시 데이터 딕셔너리
    Returns:
        정제된 이벤트 딕셔너리, 또는 날짜/장소 누락 시 None
    """
    # 이미 정형화된 데이터(예: Popply 등)가 전달된 경우
    if raw.get("startDate") and raw.get("endDate") and raw.get("venueName"):
        return {
            "title": raw.get("title", "").strip(),
            "category": raw.get("category", "팝업스토어"),
            "subCategory": raw.get("subCategory", ""),
            "startDate": raw.get("startDate"),
            "endDate": raw.get("endDate"),
            "reservationType": raw.get("reservationType", "현장방문"),
            "reservationUrl": raw.get("reservationUrl", ""),
            "reservationStartDate": raw.get("reservationStartDate"),
            "reservationEndDate": raw.get("reservationEndDate"),
            "venueName": raw.get("venueName", ""),
            "address": raw.get("address", ""),
            "lat": raw.get("lat"),
            "lng": raw.get("lng"),
            "description": raw.get("description", ""),
            "thumbnailUrl": raw.get("thumbnailUrl", ""),
            "tags": raw.get("tags", []),
            "sourceUrl": raw.get("sourceUrl", raw.get("link", "")),
            "source": raw.get("source", "crawler"),
        }

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


# ==============================================================================
# 관련성 필터: 오프라인 서브컬처(애니/게임/버튜버/웹툰/캐릭터) 전용 필터
# ==============================================================================

# 비서브컬처(패션/뷰티/스포츠/일반F&B/라이프스타일/인게임업데이트) 차단 키워드
NON_SUBCULTURE_KEYWORDS = [
    # 패션/의류
    "패션", "의류", "코디", "니트", "자켓", "팬츠", "데님", "스니커즈", "모자", "가방",
    "엘무드", "비그룸", "미드나잇무브", "EQL", "무신사 스토어", "블랙업", "여성복", "남성복",
    # 뷰티/화장품
    "뷰티", "화장품", "코스메틱", "스킨케어", "쿠션", "향수", "퍼퓸", "립스틱",
    "스킨앤랩", "티르티르", "에이지투웨니스", "쿠오카", "리센느", "올리브영", "토너", "세럼",
    # 스포츠
    "야구", "축구", "LG트윈스", "FC서울", "K리그", "골프", "잠실야구장", "프로야구", "농구",
    # F&B / 일반 음식 / 주류
    "김밥", "식품", "푸드", "파삭", "김밥축제", "와인", "위스키", "소주", "맥주", "베이커리", "브런치",
    # 리빙/라이프스타일/사우나
    "사우나", "백옥사우나", "레고트", "텀블러", "식기", "가구", "침구", "글입다", "인테리어",
    # 인게임 업데이트 / 점검
    "업데이트", "서버 점검", "인게임", "버닝", "출석체크", "사전등록",
    "신규 캐릭터", "클래스 업데이트", "점검 안내", "패치노트", "신규 보스",
    "확률형", "가챠", "쿠폰", "접속", "보상", "이벤트 던전", "레이드",
    # 비서브컬처 일반
    "주식", "코스피", "나스닥", "부동산", "아파트", "분양", "다이어트", "헬스", "피부과"
]

# 서브컬처 긍정 키워드 (하나라도 매칭되면 서브컬처로 판별)
SUBCULTURE_POSITIVE_KEYWORDS = [
    # 애니메이션 / 만화
    "애니", "만화", "코믹", "애니메이션", "주술회전", "귀멸", "귀멸의 칼날", "원피스", "나루토",
    "스파이패밀리", "하이큐", "체인소맨", "최애의 아이", "프리렌", "슬램덩크", "건담",
    "타네무라 아리나", "달빛천사", "신의 괴도 잔느", "PEACH-PIT", "캐릭캐릭체인지", "로젠메이든",
    "마도카", "마기카", "지박소년 하나코", "하나코 군", "오란고교", "점프샵", "명탐정 코난", "코난",
    "아따맘마", "블루 록", "진격의 거인", "드래곤볼", "헌터X헌터",
    # 게임
    "게임", "블루아카이브", "블아", "원신", "스타레일", "붕괴", "명일방주", "젠레스", "ZZZ", "니케", "NIKKE",
    "우마무스메", "페그오", "FGO", "포켓몬", "피카츄", "닌텐도", "젤다", "메이플", "던파",
    "로스트아크", "이터널리턴", "롤", "LOL", "발로란트", "유희왕", "프로젝트 세카이", "세카이",
    "하비소울", "메카소울", "메카", "프라모델", "건프라", "쿠키런", "루나 팝업",
    # 버튜버 / 보컬로이드
    "버튜버", "VTuber", "홀로라이브", "니지산지", "스텔라이브", "이세돌", "플레이브", "보컬로이드", "하츠네 미쿠",
    # 웹툰 / 서브컬처 IP
    "웹툰", "나혼렙", "전독시", "화산귀환", "내가 키운 S급들", "내스급", "데못죽", "스누피",
    # 캐릭터 / 마스코트 / 굿즈 / 피규어
    "캐릭터", "굿즈", "피규어", "산리오", "우사하나", "쿠로미", "시나모롤", "치이카와", "먼작귀",
    "이라스토야", "무민", "지브리", "짱구", "커비", "고길동", "둘리", "굿스마일", "52TOYS", "나가노마켓",
    # 행사 / 콜라보 카페 / 페스
    "덕후", "아덕페", "코믹월드", "일러스타", "콜라보카페", "콜라보 카페", "Gratte", "그라테", "애니메이트", "팝퍼블"
]

def is_subculture_text(title: str, category_tag: str = "", text: str = "") -> bool:
    """텍스트가 서브컬처(애니/게임/버튜버/웹툰/캐릭터)에 해당하는지 판별합니다."""
    combined = f"{title} {category_tag} {text}".lower()

    # 1. 긍정 서브컬처 키워드가 있는지 확인
    has_positive = any(kw.lower() in combined for kw in SUBCULTURE_POSITIVE_KEYWORDS)
    if has_positive:
        return True

    # 2. 명확한 비서브컬처 단어가 포함되어 있다면 무조건 탈락
    for kw in NON_SUBCULTURE_KEYWORDS:
        if kw.lower() in combined:
            return False

    # 3. 카테고리 태그가 명확히 서브컬처인 경우
    if any(k in category_tag for k in ["애니", "캐릭터", "게임", "만화"]):
        return True

    return False

def is_relevant(raw: dict) -> bool:
    """오프라인 서브컬처 행사와 관련된 글인지 엄격하게 판단합니다."""
    title = raw.get("title", "")
    category = raw.get("subCategory", "") or raw.get("category", "")
    desc = raw.get("description", "")

    # 오프라인 장소(venueName 또는 address)가 전혀 없으면 탈락
    has_venue = bool(raw.get("venueName") or raw.get("address"))
    if not has_venue and not any(loc in f"{title} {desc}" for loc in ["홍대", "용산", "잠실", "성수", "더현대", "코엑스", "킨텍스"]):
        return False

    # 서브컬처 판별 통과 여부
    return is_subculture_text(title, category, desc)


def parse_raw_items(raw_items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """원시 데이터 목록을 일괄 정제합니다. 관련 없는 글과 날짜/장소 추출 실패 항목은 자동 제외됩니다."""
    # 1차 관련성 필터
    relevant = [item for item in raw_items if is_relevant(item)]
    print(f"  [필터] {len(raw_items)}건 → 오프라인 필터 통과: {len(relevant)}건")

    # 2차 정제 (날짜 및 장소 필수)
    results = []
    for item in relevant:
        parsed = parse_raw_item(item)
        if parsed and parsed.get("venueName"): # 장소가 반드시 있어야 함
            results.append(parsed)
            
    print(f"  [필터] 날짜/장소 모두 추출된 진짜 오프라인 행사: {len(results)}건")
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
