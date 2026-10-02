# 🎮 서브컬처 이벤트 허브 (Subculture Events Hub)

> 게임, 애니메이션, 버튜버, 웹툰 등 서브컬처 오프라인 행사·팝업스토어·콜라보카페 정보를 한곳에 모아서 캘린더·지도·리스트로 보여주는 웹 서비스

---

## 📋 목차

- [프로젝트 개요](#프로젝트-개요)
- [현재 완성된 기능](#현재-완성된-기능)
- [프로젝트 구조](#프로젝트-구조)
- [환경 설정 및 실행 방법](#환경-설정-및-실행-방법)
- [API 명세](#api-명세)
- [데이터 스키마](#데이터-스키마)
- [크롤링 파이프라인](#크롤링-파이프라인)
- [앞으로 구현할 기능 (로드맵)](#앞으로-구현할-기능-로드맵)
- [기술 스택](#기술-스택)
- [알려진 이슈 및 주의사항](#알려진-이슈-및-주의사항)

---

## 프로젝트 개요

### 목적
한국 내 서브컬처(게임, 애니메이션, 버튜버, 웹툰, 동인행사, 피규어/굿즈) 관련 오프라인 행사 정보가 트위터, 인스타그램, 각 회사 공식 사이트 등에 분산되어 있어 놓치기 쉬운 문제를 해결한다. 여러 소스에서 정보를 자동 수집하여 하나의 웹 서비스에서 캘린더, 지도, 리스트 형태로 한눈에 확인할 수 있게 한다.

### 대상 행사 유형
| 카테고리 | 예시 |
|---------|------|
| 게임 | 블루아카이브 팝업, 원신 콜라보카페, FGO 전시 |
| 애니메이션 | 귀멸의 칼날 전시회, 스파이패밀리 팝업 |
| 버튜버 | 홀로라이브 팬미팅, 니지산지 오프라인 이벤트 |
| 웹툰 | 나혼렙 팝업, 전지적독자시점 전시 |
| 동인행사 | 코믹월드, 서코 |
| 피규어/굿즈 | 피규어 전시, 원더페스티벌 |

---

## 현재 완성된 기능

### ✅ 완료 (작동 확인됨)

| # | 기능 | 파일 | 상태 |
|---|------|------|------|
| 1 | Flask 웹 서버 | `app.py` | ✅ 작동 확인 |
| 2 | SPA 프론트엔드 (캘린더/지도/리스트 3개 뷰) | `templates/index.html` | ✅ 작동 확인 |
| 3 | REST API (이벤트 CRUD, 카테고리 조회, 상태 필터) | `app.py` | ✅ 테스트 30개 통과 |
| 4 | 동적 상태 계산 (진행중/예정/종료/예약중) | `app.py` | ✅ 작동 확인 |
| 5 | 지도 뷰 (Leaflet + OpenStreetMap) | `templates/index.html` | ✅ 작동 확인 |
| 6 | 이벤트 상세 모달 (미니맵 포함) | `templates/index.html` | ✅ 작동 확인 |
| 7 | 6개 카테고리 × 4개 상태 필터 | `templates/index.html` | ✅ 작동 확인 |
| 8 | 네이버 클라우드(NCP) 검색 API 연동 | `test_naver_api.py` | ✅ 165만건 검색 성공 |
| 9 | 통합 크롤러 뼈대 (NaverBot/RssBot/WebBot) | `crawler.py` | ✅ NaverBot 30건 수집 성공 |

### ⚠️ 부분 완료

| # | 기능 | 상태 | 설명 |
|---|------|------|------|
| 10 | RssBot (RSS 피드 수집) | 🟡 뼈대만 완성 | RSS URL 목록 미입력, 실제 수집 0건 |
| 11 | WebBot (공식 사이트 HTML 파싱) | 🟡 뼈대만 완성 | 대상 사이트별 DOM 구조 분석 미완료 |

### ❌ 미구현

| # | 기능 | 우선순위 | 설명 |
|---|------|---------|------|
| 12 | 데이터 정제 (Raw → 구조화) | 🔴 최우선 | 수집된 블로그 텍스트에서 날짜/장소/IP명 추출 |
| 13 | 카카오 Geocoding API 연동 | 🔴 높음 | 주소 텍스트 → 위경도 좌표 변환 |
| 14 | SQLite DB 저장 | 🔴 높음 | 현재 Mock 데이터(가짜)를 실제 DB로 교체 |
| 15 | 이벤트 제보 폼 (사용자 입력) | 🟠 중간 | X/인스타 전용 행사를 수동으로 등록 |
| 16 | 관리자 페이지 | 🟠 중간 | 수집된 데이터 검토/승인/수정 |
| 17 | 자동 스케줄러 | 🟡 낮음 | 크롤러 주기적 자동 실행 (예: 매일 09:00) |
| 18 | 중복 제거 로직 | 🟡 낮음 | 같은 행사가 여러 소스에서 수집될 때 병합 |
| 19 | 검색 기능 | 🟡 낮음 | 프론트엔드에서 행사명/장소 텍스트 검색 |

---

## 프로젝트 구조

```
subculture-events/
├── app.py                  # Flask 메인 서버 (383줄)
│                           #   - SPA HTML 서빙
│                           #   - REST API 엔드포인트
│                           #   - 날짜 파싱 및 동적 상태 계산
│
├── crawler.py              # 통합 크롤링 파이프라인 (126줄)
│                           #   - crawl_naver_api(): 네이버 클라우드 검색 API
│                           #   - crawl_official_rss(): RSS 피드 수집
│                           #   - crawl_aniplus(): HTML 직접 파싱
│                           #   - run_pipeline(): 전체 파이프라인 실행
│
├── data/
│   ├── __init__.py         # 패키지 초기화
│   └── events.py           # 이벤트 데이터 (현재: Mock 18건, 향후: DB로 교체)
│                           #   - EVENTS: List[Dict] 형태의 이벤트 목록
│                           #   - CATEGORIES: 6개 카테고리 정의
│                           #   - RESERVATION_TYPES: 5개 예약 유형 정의
│
├── templates/
│   └── index.html          # SPA 프론트엔드 (841줄)
│                           #   - 캘린더 뷰 (월간)
│                           #   - 지도 뷰 (Leaflet + OpenStreetMap)
│                           #   - 리스트 뷰 (카드형)
│                           #   - 이벤트 상세 모달
│                           #   - 카테고리/상태 필터
│
├── test_naver_api.py       # 네이버 API 인증 테스트 스크립트
├── test_api.py             # 기본 API 테스트
├── test_final.py           # 통합 테스트 (30개 항목)
├── requirements.txt        # Python 의존성 목록
└── .gitignore              # Git 추적 제외 파일 목록
```

---

## 환경 설정 및 실행 방법

### 사전 요구사항
- Python 3.10 이상
- pip (Python 패키지 관리자)
- Git

### 1. 저장소 클론
```bash
git clone https://github.com/Gajaml/subculture-events-hub.git
cd subculture-events-hub
```

### 2. 의존성 설치
```bash
pip install -r requirements.txt
```

### 3. 웹 서버 실행
```bash
python app.py
```
브라우저에서 `http://localhost:5000` 접속

### 4. 크롤러 실행 (네이버 API 키 필요)

> ⚠️ **보안 주의**: API 키는 절대 코드에 직접 입력하지 않습니다. 환경변수로만 전달합니다.

**Windows PowerShell:**
```powershell
$env:NAVER_CLIENT_ID="발급받은_Client_ID"
$env:NAVER_CLIENT_SECRET="발급받은_Client_Secret"
python crawler.py
```

**Linux / macOS:**
```bash
export NAVER_CLIENT_ID="발급받은_Client_ID"
export NAVER_CLIENT_SECRET="발급받은_Client_Secret"
python crawler.py
```

### 5. 네이버 API 키 발급 방법

네이버 검색 API는 2026년 7월 말에 기존 개발자센터에서 **네이버 클라우드 플랫폼(NCP)**으로 이관되었습니다.

1. [네이버 클라우드 플랫폼](https://www.ncloud.com/) 회원가입 및 로그인
2. 콘솔 → Services → **NAVER API HUB** 이동
3. Application 등록 → API 선택에서 **블로그, 뉴스, 카페** (NAVER 검색) 선택
4. Application 정보 입력 후 등록 완료
5. 발급된 **API Key ID**와 **API Secret Key**를 환경변수로 사용

### 6. 테스트 실행
```bash
python -m pytest test_final.py -v
```

---

## API 명세

### 기본 정보
- Base URL: `http://localhost:5000`
- 응답 형식: JSON (UTF-8)

### 엔드포인트 목록

| Method | Path | 설명 |
|--------|------|------|
| GET | `/` | SPA 메인 페이지 (HTML) |
| GET | `/api/events` | 이벤트 목록 조회 (필터 지원) |
| GET | `/api/events/<id>` | 이벤트 상세 조회 |
| GET | `/api/categories` | 카테고리 목록 조회 |
| GET | `/api/health` | 서버 상태 확인 |

### 필터 파라미터 (`/api/events`)

| 파라미터 | 타입 | 설명 | 예시 |
|---------|------|------|------|
| `category` | string | 카테고리 필터 | `?category=게임` |
| `status` | string | 상태 필터 | `?status=ongoing` |

### 상태(status) 값

| 값 | 한국어 | 조건 |
|----|--------|------|
| `ongoing` | 진행 중 | startDate ≤ 오늘 ≤ endDate |
| `upcoming` | 예정 | 오늘 < startDate |
| `ended` | 종료 | 오늘 > endDate |
| `reservation_open` | 예약 중 | reservationStartDate ≤ 오늘 ≤ reservationEndDate |

---

## 데이터 스키마

### 이벤트 객체 (Event)

`data/events.py`의 `EVENTS` 리스트에 저장되는 각 이벤트의 필드 정의:

```python
{
    "id": 1,                              # int: 고유 식별자
    "title": "블루아카이브 팝업스토어",       # str: 행사 제목
    "category": "게임",                     # str: 카테고리 (6종)
    "subCategory": "블루아카이브",           # str: 세부 IP/작품명
    "startDate": "2026-09-25",             # str: 시작일 (YYYY-MM-DD)
    "endDate": "2026-10-08",               # str: 종료일 (YYYY-MM-DD)
    "location": "성수동 XYZ갤러리",          # str: 장소명
    "address": "서울특별시 성동구 ...",       # str: 상세 주소
    "lat": 37.5445,                        # float: 위도
    "lng": 127.0567,                       # float: 경도
    "description": "행사 설명 텍스트",       # str: 행사 상세 설명
    "thumbnailUrl": "https://...",          # str: 썸네일 이미지 URL
    "officialUrl": "https://...",           # str: 공식 사이트 URL
    "reservationType": "네이버예약",         # str: 예약 방식 (5종)
    "reservationStartDate": "2026-09-20",  # str|null: 예약 시작일
    "reservationEndDate": "2026-10-07",    # str|null: 예약 종료일
    "source": "naver"                      # str: 데이터 출처 (naver/rss/web/manual)
}
```

### 카테고리 목록
```python
["게임", "애니메이션", "버튜버", "웹툰", "동인행사", "피규어/굿즈"]
```

### 예약 유형
```python
["자유입장", "네이버예약", "캐치테이블", "사전예약", "현장대기"]
```

---

## 크롤링 파이프라인

### 아키텍처 개요

```
┌─────────────────────────────────────────────────────┐
│                  crawler.py                         │
│                                                     │
│  ┌─────────────┐  ┌──────────┐  ┌───────────────┐  │
│  │  NaverBot   │  │  RssBot  │  │    WebBot     │  │
│  │ (NCP API)   │  │ (RSS/XML)│  │ (HTML 파싱)   │  │
│  │ ✅ 작동중    │  │ 🟡 뼈대  │  │ 🟡 뼈대      │  │
│  └──────┬──────┘  └────┬─────┘  └──────┬────────┘  │
│         │              │               │            │
│         └──────────────┼───────────────┘            │
│                        ▼                            │
│              Raw Data (원시 데이터)                   │
│              ❌ 미구현: 정제 파서                     │
│                        ▼                            │
│              ❌ 미구현: 카카오 Geocoding              │
│                        ▼                            │
│              ❌ 미구현: SQLite DB 저장               │
│                        ▼                            │
│              app.py (Flask 서버)                     │
│              ✅ 작동중                               │
└─────────────────────────────────────────────────────┘
```

### 수집 대상 소스 (실증 테스트 완료)

이전 세션에서 총 17개 소스를 대상으로 3라운드에 걸쳐 실제 접속 테스트를 수행했습니다.

#### 작동 확인된 소스

| 소스 | 방식 | 상태 | 비고 |
|------|------|------|------|
| 네이버 클라우드 블로그 검색 | API | ✅ 작동 | 165만건 검색 가능 확인 |
| 네이버 클라우드 뉴스 검색 | API | ✅ 작동 | 키 발급 완료 |
| 네이버 클라우드 카페 검색 | API | ✅ 작동 | 키 발급 완료 |
| 넥슨 이벤트 (event.nexon.com) | RSS/HTML | 🟡 접속 확인 | RSS 피드 존재, 파서 미작성 |
| 홀로라이브 (hololivepro.com/news) | HTML | 🟡 접속 확인 | 76KB, 날짜 패턴 4개 발견 |
| 니지산지 KR (nijisanji.jp/news) | HTML | 🟡 접속 확인 | 347KB, 파서 미작성 |
| 애니플러스 뉴스 | HTML | 🟡 접속 확인 | 373KB, 파서 미작성 |
| 컴투스 (com2us.com/news) | HTML | 🟡 접속 확인 | '팝업' 키워드 3건 발견 |

#### 접속 불가 확인된 소스 (사용 불가)

| 소스 | 사유 |
|------|------|
| Nitter (Twitter/X 대안) | 4개 인스턴스 모두 폐쇄됨 |
| 팝업레이더, 어라운드팝업, 이벤터스 | DNS 실패 (도메인 폐쇄) |
| DC인사이드 팝업스토어 갤러리 | 관리자 요청으로 폐쇄 |
| 팝업.kr | HTTP 406 (봇 차단) |
| Instagram | 무료 API 없음, 스크래핑 차단 |

---

## 앞으로 구현할 기능 (로드맵)

### Phase 1: 데이터 파이프라인 완성 (최우선)

> 목표: 크롤러가 수집한 원시(Raw) 데이터를 실제 서비스에서 사용 가능한 구조화된 데이터로 변환

#### 1-1. 데이터 정제 파서 (`parser.py` 신규 생성)
- [ ] 블로그 제목/본문에서 **행사 제목** 추출 (IP명 + 행사 유형)
- [ ] **날짜** 추출: 정규식으로 `YYYY.MM.DD`, `MM월 DD일`, `~`, `부터`, `까지` 등 패턴 인식
- [ ] **장소** 추출: `서울`, `성수`, `더현대`, `홍대` 등 장소 키워드 매칭
- [ ] **카테고리** 자동 분류: IP명 기반으로 6개 카테고리에 매핑
- [ ] 중복 제거: 같은 행사가 여러 블로그에서 언급될 때 제목 유사도로 병합

#### 1-2. 카카오 Geocoding 연동 (`geocoder.py` 신규 생성)
- [ ] 카카오 개발자 콘솔에서 REST API 키 발급
- [ ] 주소 텍스트 → 위경도(lat/lng) 좌표 변환 함수 구현
- [ ] 환경변수 `KAKAO_REST_API_KEY`로 키 관리

#### 1-3. DB 저장 (`database.py` 신규 생성)
- [ ] SQLite 데이터베이스 파일 (`events.db`) 생성
- [ ] 이벤트 테이블 스키마 정의
- [ ] `app.py`의 데이터 로드 로직을 `data/events.py` → SQLite DB로 교체
- [ ] 기존 Mock 데이터(가짜 18건) 완전 제거

### Phase 2: 크롤러 실제 소스 확장

#### 2-1. RssBot 실제 URL 추가
- [ ] 넥슨 이벤트 RSS (`event.nexon.com/feed/news.rss`) 연동
- [ ] 기타 게임사 RSS 피드 탐색 및 추가

#### 2-2. WebBot 사이트별 파서 작성
- [ ] 홀로라이브 뉴스 페이지 파서 (CSS selector 기반)
- [ ] 니지산지 KR 뉴스 페이지 파서
- [ ] 애니플러스 뉴스 파서
- [ ] 컴투스 뉴스 파서

#### 2-3. 네이버 검색 키워드 확장
- [ ] 현재 3개 키워드 → IP별 세분화 키워드 추가
  - 예: `"블루아카이브 팝업"`, `"원신 콜라보카페"`, `"홀로라이브 팬미팅"`, `"코믹월드"` 등
- [ ] 뉴스/카페 검색 엔드포인트 추가 (현재 블로그만 사용 중)

### Phase 3: 사용자 참여 기능

#### 3-1. 이벤트 제보 폼
- [ ] 프론트엔드에 "이벤트 제보하기" 버튼 및 입력 폼 추가
- [ ] POST `/api/events/submit` 엔드포인트 구현
- [ ] 제보된 데이터를 '미승인' 상태로 DB에 저장

#### 3-2. 관리자 페이지
- [ ] 관리자 로그인 (기본 비밀번호 방식)
- [ ] 미승인 이벤트 목록 조회/승인/반려/수정 기능
- [ ] 크롤링 수집 데이터 수동 검토 기능

### Phase 4: 서비스 고도화

#### 4-1. 자동 스케줄러
- [ ] APScheduler 또는 cron을 이용한 크롤러 자동 실행 (매일 09:00, 18:00)
- [ ] 수집 결과 로그 저장

#### 4-2. 프론트엔드 개선
- [ ] 텍스트 검색 기능 추가
- [ ] 즐겨찾기(북마크) 기능
- [ ] 모바일 반응형 UI 개선
- [ ] PWA (Progressive Web App) 지원

#### 4-3. 알림 기능
- [ ] 관심 카테고리/IP 새 행사 알림
- [ ] 행사 시작 D-day 알림

---

## 기술 스택

| 구분 | 기술 | 용도 |
|------|------|------|
| **백엔드** | Python + Flask | 웹 서버, REST API |
| **프론트엔드** | Vanilla HTML/CSS/JS | SPA (별도 프레임워크 없음) |
| **지도** | Leaflet + OpenStreetMap | 행사 위치 지도 표시 |
| **크롤링** | requests + BeautifulSoup4 | HTTP 요청 및 HTML 파싱 |
| **RSS** | feedparser | RSS/Atom 피드 파싱 |
| **검색 API** | 네이버 클라우드 NAVER API HUB | 블로그/뉴스/카페 검색 |
| **Geocoding** | 카카오 Local API (예정) | 주소 → 좌표 변환 |
| **DB** | SQLite (예정) | 이벤트 데이터 영구 저장 |

---

## 알려진 이슈 및 주의사항

### 🔴 현재 Mock 데이터는 가짜입니다
`data/events.py`에 들어있는 18건의 이벤트 데이터는 AI가 생성한 **허구의 데이터**입니다. 실제 존재하지 않는 행사들이므로, 공식 사이트 링크 등이 작동하지 않습니다. 크롤링 파이프라인이 완성되면 실제 데이터로 교체될 예정입니다.

### 🔴 API 키 보안
- API 키는 **절대** 코드에 하드코딩하거나 Git에 커밋하지 마세요.
- 반드시 **환경변수**를 통해 전달하세요.
- `.gitignore`에 `secrets.json`, `.env` 등이 이미 등록되어 있습니다.
- 키가 실수로 노출된 경우, 즉시 네이버 클라우드 콘솔에서 **키 재발급(Rotation)**하세요.

### 🟡 네이버 검색 API 약관 변경 (2026.09.07)
네이버가 검색 API 데이터를 AI 모델 학습/가공에 사용하는 것을 약관으로 금지했습니다. 본 프로젝트는 검색 결과를 **사용자에게 직접 보여주는 용도**(검색 결과 표시)로만 사용하며, AI 학습 데이터로 활용하지 않습니다.

### 🟡 트위터(X) / 인스타그램 데이터 수집 불가
2026년 10월 현재, X(구 트위터)와 Instagram의 데이터를 무료로 자동 수집할 수 있는 방법은 존재하지 않습니다. Nitter 등 대안 서비스도 전부 폐쇄되었습니다. 이 채널에서만 공지되는 행사는 **사용자 제보(Phase 3)**에 의존해야 합니다.

---

## Antigravity 에이전트를 위한 작업 가이드

> 이 섹션은 AI 코딩 에이전트(Antigravity 등)가 이 프로젝트를 이어받아 작업할 때 참고하는 가이드입니다.

### 작업 원칙
1. **코드 작성 후 반드시 테스트를 실행**하여 기존 기능이 깨지지 않았는지 확인할 것.
2. **작업 완료 후 반드시 `git commit` + `git push`**를 실행하여 GitHub를 최신 상태로 유지할 것.
3. API 키는 **환경변수**로만 다루고, 절대 코드나 로그에 평문으로 노출하지 말 것.
4. 사용자는 프로그래밍 비전공자이므로, 기술 결정은 에이전트가 독자적으로 판단하되, 결과물이 작동하는지 반드시 검증할 것.

### 다음으로 착수해야 할 작업 (우선순위 순)
1. `parser.py` 작성 → 수집된 Raw Data에서 날짜/장소/카테고리 추출
2. `geocoder.py` 작성 → 카카오 API로 주소→좌표 변환
3. `database.py` 작성 → SQLite DB 생성 및 `app.py` 연동
4. `crawler.py` 내 RssBot/WebBot에 실제 URL과 파서 로직 추가
5. Mock 데이터(`data/events.py`) 제거 후 DB 기반으로 전환

### 환경변수 목록

| 변수명 | 용도 | 발급처 |
|--------|------|--------|
| `NAVER_CLIENT_ID` | 네이버 검색 API Key ID | [NCP 콘솔](https://www.ncloud.com/) |
| `NAVER_CLIENT_SECRET` | 네이버 검색 API Secret | [NCP 콘솔](https://www.ncloud.com/) |
| `KAKAO_REST_API_KEY` | 카카오 Geocoding API 키 (예정) | [카카오 개발자](https://developers.kakao.com/) |
