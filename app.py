# -*- coding: utf-8 -*-
"""
서브컬처 행사 일정 모아보기 (Subculture Events Aggregator)
메인 백엔드 Flask 서버

기능:
1. SPA (Single Page Application) HTML 서빙 ('templates/index.html')
2. 행사 목록 및 상세 조회 REST API 제공 (/api/events)
3. 카테고리별(game, anime, vtuber, popup, offline 등) 필터링
4. 현재 날짜 기준 동적 상태(ongoing, upcoming, ended, reservation_open) 계산 및 필터링
5. CORS 헤더 지원 및 UTF-8 인코딩 보장
"""

import os
import sys
from datetime import date, datetime
from flask import Flask, jsonify, render_template, request

# ==============================================================================
# 모듈 경로 및 환경 설정
# ==============================================================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

# Flask 애플리케이션 초기화 (템플릿 및 정적 파일 경로 지정)
app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, 'templates'),
    static_folder=os.path.join(BASE_DIR, 'static')
)

# JSON 응답 시 한글 깨짐 방지 및 UTF-8 보장 설정
app.config['JSON_AS_ASCII'] = False
if hasattr(app, 'json'):
    app.json.ensure_ascii = False


# ==============================================================================
# 이벤트 원본 데이터 임포트
# ==============================================================================
# SQLite DB를 우선 사용합니다.
try:
    from database import init_db, get_all_events as db_get_all_events, get_event_count
    # 서버 시작 시 DB 초기화
    init_db()
    _USE_DB = True
except ImportError:
    _USE_DB = False


def get_all_raw_events():
    """
    이벤트 원본 데이터를 SQLite DB에서 로드합니다.
    """
    if _USE_DB:
        try:
            db_events = db_get_all_events()
            if db_events:
                return db_events
        except Exception:
            pass

    return []


# ==============================================================================
# 유틸리티 함수: 날짜 파싱 및 동적 상태 계산
# ==============================================================================
def parse_date(date_val):
    """
    다양한 형식(str, date, datetime)의 날짜 데이터를 datetime.date 객체로 변환합니다.
    지원 형식: 'YYYY-MM-DD', 'YYYY.MM.DD', 'YYYY/MM/DD' 등
    """
    if not date_val:
        return None
    if isinstance(date_val, datetime):
        return date_val.date()
    if isinstance(date_val, date):
        return date_val
    if isinstance(date_val, str):
        cleaned = date_val.strip().replace('.', '-').replace('/', '-')
        # YYYY-MM-DD 형태 추출
        if len(cleaned) >= 10:
            try:
                return datetime.strptime(cleaned[:10], "%Y-%m-%d").date()
            except ValueError:
                pass
        for fmt in ("%Y-%m-%d", "%Y-%m-%d %H:%M:%S", "%Y%m%d"):
            try:
                return datetime.strptime(cleaned, fmt).date()
            except ValueError:
                continue
    return None


def enrich_event_status(event_dict, today=None):
    """
    이벤트 데이터에 현재 날짜 기준의 동적 상태 정보를 계산하여 추가합니다.
    
    상태 계산 규칙:
    - 'reservation_open': reservationStartDate <= today <= reservationEndDate
    - 'ongoing': startDate <= today <= endDate
    - 'upcoming': today < startDate
    - 'ended': today > endDate
    
    반환 딕셔너리에 추가되는 주요 필드:
    - status: 'reservation_open' | 'ongoing' | 'upcoming' | 'ended'
    - is_reservation_open: bool (현재 사전 예약 접수 중 여부)
    - event_status: 'ongoing' | 'upcoming' | 'ended' (행사 자체의 진행 상태)
    """
    if today is None:
        today = date.today()

    event = dict(event_dict)

    # 필드명 호환 (카멜케이스 및 스네이크케이스 모두 지원)
    start_date = parse_date(event.get('startDate') or event.get('start_date'))
    end_date = parse_date(event.get('endDate') or event.get('end_date'))
    res_start = parse_date(event.get('reservationStartDate') or event.get('reservation_start_date'))
    res_end = parse_date(event.get('reservationEndDate') or event.get('reservation_end_date'))

    # 1. 사전 예약 진행 여부
    is_reservation_open = bool(res_start and res_end and (res_start <= today <= res_end))

    # 2. 행사 본 행사 진행 상태 (ongoing, upcoming, ended)
    if start_date and end_date:
        if start_date <= today <= end_date:
            base_status = "ongoing"
        elif today < start_date:
            base_status = "upcoming"
        else:
            base_status = "ended"
    elif start_date:
        if today < start_date:
            base_status = "upcoming"
        else:
            base_status = "ongoing"
    elif end_date:
        if today <= end_date:
            base_status = "ongoing"
        else:
            base_status = "ended"
    else:
        base_status = "upcoming"

    # 3. 대표 status 결정
    # - 예약 기간 중이고 행사가 아직 시작 전이거나 예약 진행 중일 때 'reservation_open'
    # - 행사가 진행 중이면 'ongoing'
    # - 행사가 종료되었으면 'ended'
    # - 행사 시작 전이면 'upcoming'
    if is_reservation_open:
        status = "reservation_open"
    elif base_status == "ongoing":
        status = "ongoing"
    elif base_status == "ended":
        status = "ended"
    else:
        status = "upcoming"

    # 동적으로 계산된 상태 정보 주입
    event['status'] = status
    event['event_status'] = base_status
    event['is_reservation_open'] = is_reservation_open

    return event


# 카테고리 별칭 매핑 (한글/영문 검색 편의 지원)
CATEGORY_ALIASES = {
    'game': {'game', 'games', '게임'},
    'anime': {'anime', 'animation', '애니', '애니메이션'},
    'vtuber': {'vtuber', 'vtubers', '버튜버', '가상유튜버'},
    'popup': {'popup', 'pop-up', '팝업', '팝업스토어', '콜라보카페', '카페'},
    'offline': {'offline', '오프라인', '행사', '페스티벌', '전시', '콘서트'}
}


def matches_category(event_category, query_category):
    """
    이벤트의 카테고리가 사용자가 요청한 필터 조건과 일치하는지 검사합니다.
    """
    if not query_category or query_category.lower() == 'all':
        return True

    q = query_category.lower().strip()
    
    # 이벤트 카테고리 정규화
    if isinstance(event_category, list):
        event_cats = [str(c).lower().strip() for c in event_category]
    else:
        event_cats = [c.strip().lower() for c in str(event_category or '').split(',') if c.strip()]

    # 1. 단순 일치 검사
    if q in event_cats or str(event_category).lower() == q:
        return True

    # 2. 별칭 맵을 통한 검사
    for alias_key, aliases in CATEGORY_ALIASES.items():
        if q == alias_key or q in aliases:
            # query가 이 카테고리 그룹에 속하는 경우, 이벤트 카테고리 중 하나라도 이 그룹에 속하면 매칭
            if any(cat == alias_key or cat in aliases for cat in event_cats):
                return True

    return False


# ==============================================================================
# CORS 헤더 및 공통 응답 처리
# ==============================================================================
@app.after_request
def add_cors_headers(response):
    """
    외부 프론트엔드 환경이나 API 클라이언트에서의 원활한 호출을 위해
    모든 응답에 CORS 헤더를 추가하고 UTF-8 캐릭터셋을 설정합니다.
    """
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'

    if response.mimetype == 'application/json' and 'charset' not in response.headers.get('Content-Type', ''):
        response.headers['Content-Type'] = 'application/json; charset=utf-8'

    return response


# ==============================================================================
# 라우트: 웹 프론트엔드 (SPA)
# ==============================================================================
@app.route('/')
def index():
    """
    메인 싱글 페이지 애플리케이션 (SPA) 서빙
    'templates/index.html'을 렌더링합니다.
    """
    try:
        return render_template('index.html')
    except Exception:
        # templates/index.html 파일이 아직 생성되지 않은 경우 친절한 안내 메시지 표시
        return (
            "<!DOCTYPE html>"
            "<html lang='ko'>"
            "<head><meta charset='UTF-8'><title>서브컬처 행사 일정 알리미</title></head>"
            "<body style='font-family: sans-serif; padding: 40px; text-align: center;'>"
            "<h1>서브컬처 행사 일정 애그리게이터 백엔드 정상 구동 중</h1>"
            "<p>현재 <code>templates/index.html</code> 파일 준비 중입니다.</p>"
            "<p>REST API 테스트: <a href='/api/events'>/api/events</a></p>"
            "</body>"
            "</html>"
        ), 200


# ==============================================================================
# REST API 엔드포인트
# ==============================================================================
@app.route('/api/events', methods=['GET'])
def get_events():
    """
    모든 이벤트 목록을 JSON으로 반환하는 REST API
    
    Query Parameters:
      - category: 카테고리 필터링 (예: game, anime, vtuber, popup, offline)
      - status: 진행 상태 필터링 (ongoing, upcoming, reservation / reservation_open, ended)
      - q, search: 제목 및 장소 텍스트 검색 (선택 사항)
      
    Returns:
      JSON Array of Events
    """
    category_param = request.args.get('category', '').strip()
    status_param = request.args.get('status', '').strip().lower()
    search_query = (request.args.get('q') or request.args.get('search') or '').strip().lower()

    raw_events = get_all_raw_events()
    today = date.today()

    filtered_events = []

    for ev in raw_events:
        # 동적 상태 정보가 계산된 이벤트 데이터 생성
        enriched = enrich_event_status(ev, today=today)

        # 1. 카테고리 필터링
        if category_param and category_param.lower() != 'all':
            if not matches_category(enriched.get('category'), category_param):
                continue

        # 2. 상태 필터링 (ongoing, upcoming, reservation / reservation_open, ended)
        if status_param and status_param != 'all':
            current_status = enriched.get('status', '')
            base_status = enriched.get('event_status', '')
            is_res_open = enriched.get('is_reservation_open', False)

            if status_param in ('reservation', 'reservation_open', 'reservation-open'):
                if not (is_res_open or current_status == 'reservation_open'):
                    continue
            elif status_param == 'ongoing':
                if current_status != 'ongoing' and base_status != 'ongoing':
                    continue
            elif status_param == 'upcoming':
                if current_status != 'upcoming' and base_status != 'upcoming':
                    continue
            elif status_param == 'ended':
                if current_status != 'ended' and base_status != 'ended':
                    continue
            else:
                if current_status != status_param:
                    continue

        # 3. 검색어 필터링 (제목, 장소, 설명)
        if search_query:
            title = str(enriched.get('title', '')).lower()
            location = str(enriched.get('location', '')).lower()
            description = str(enriched.get('description', '')).lower()
            if search_query not in title and search_query not in location and search_query not in description:
                continue

        filtered_events.append(enriched)

    return jsonify(filtered_events)


@app.route('/api/events/<event_id>', methods=['GET'])
def get_event_by_id(event_id):
    """
    특정 이벤트 ID의 상세 정보를 반환하는 REST API
    """
    raw_events = get_all_raw_events()
    today = date.today()

    for ev in raw_events:
        if str(ev.get('id', '')) == str(event_id):
            enriched = enrich_event_status(ev, today=today)
            return jsonify(enriched)

    return jsonify({
        'error': 'NotFound',
        'message': f'ID가 "{event_id}"인 이벤트를 찾을 수 없습니다.'
    }), 404


@app.route('/api/categories', methods=['GET'])
def get_categories():
    """
    등록된 이벤트들에서 사용되는 고유 카테고리 목록을 반환합니다.
    """
    raw_events = get_all_raw_events()
    categories = set()

    for ev in raw_events:
        cat = ev.get('category')
        if not cat:
            continue
        if isinstance(cat, list):
            for c in cat:
                if c:
                    categories.add(str(c).strip())
        else:
            for c in str(cat).split(','):
                c_clean = c.strip()
                if c_clean:
                    categories.add(c_clean)

    return jsonify(sorted(list(categories)))


@app.route('/api/health', methods=['GET'])
def health_check():
    """
    서버 상태 및 현재 기준 날짜, 등록된 이벤트 수를 반환하는 헬스체크 API
    """
    events = get_all_raw_events()
    return jsonify({
        'status': 'healthy',
        'today': date.today().isoformat(),
        'total_events': len(events)
    })


# ==============================================================================
# 메인 서버 실행 엔트리포인트
# ==============================================================================
if __name__ == '__main__':
    # 요구사항: port 5000, debug=True로 실행
    print(f"[*] 서브컬처 행사 일정 서버 시작: http://localhost:5000 (디버그 모드)")
    app.run(host='0.0.0.0', port=5000, debug=True)
