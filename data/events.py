# -*- coding: utf-8 -*-
"""Mock events dataset for Korean subculture events application.

Current reference date: 2026-10-01
Categories: '게임', '애니메이션', '버튜버', '웹툰', '동인행사', '피규어/굿즈'
Reservation Types: '자유입장', '네이버예약', '캐치테이블', '사전예약', '현장대기'
"""

from typing import Any, Dict, List, Optional

CURRENT_DATE = "2026-10-01"

CATEGORIES: List[str] = [
    "게임",
    "애니메이션",
    "버튜버",
    "웹툰",
    "동인행사",
    "피규어/굿즈",
]

RESERVATION_TYPES: List[str] = [
    "자유입장",
    "네이버예약",
    "캐치테이블",
    "사전예약",
    "현장대기",
]

EVENTS: List[Dict[str, Any]] = [
    # =========================================================================
    # 1. 현재 진행 중인 행사 (Ongoing Events - as of 2026-10-01)
    # =========================================================================
    {
        "id": 1,
        "title": "블루아카이브 3.5주년 기념 팝업스토어",
        "category": "게임",
        "subCategory": "블루아카이브",
        "startDate": "2026-09-25",
        "endDate": "2026-10-08",
        "reservationType": "네이버예약",
        "reservationUrl": "https://booking.naver.com/booking/12/bizes/bluearchive-3rd5",
        "reservationStartDate": "2026-09-15",
        "reservationEndDate": "2026-09-22",
        "venueName": "더현대 서울 (여의도)",
        "address": "서울특별시 영등포구 여의대로 108 더현대 서울 B2F 아이코닉존",
        "lat": 37.5256,
        "lng": 126.9289,
        "description": "블루아카이브 3.5주년을 기념하여 밀레니엄 사이언스 스쿨 콘셉트로 꾸며진 대형 팝업스토어입니다. 아리스, 유우카, 노아의 신규 일러스트 한정 굿즈 및 대형 포토존, 스탬프 랠리 이벤트가 진행됩니다.",
        "thumbnailUrl": "https://placehold.co/400x300/2563eb/white?text=Blue+Archive+3.5th",
        "tags": ["블루아카이브", "넥슨", "팝업스토어", "더현대", "밀레니엄", "키보토스"],
        "sourceUrl": "https://bluearchive.nexon.com/news/event/view/35th-popup",
    },
    {
        "id": 2,
        "title": "원신 × 카페 드 파리 콜라보레이션 카페",
        "category": "게임",
        "subCategory": "원신",
        "startDate": "2026-09-18",
        "endDate": "2026-10-15",
        "reservationType": "캐치테이블",
        "reservationUrl": "https://app.catchtable.co.kr/ct/shop/genshin_cafe",
        "reservationStartDate": "2026-09-05",
        "reservationEndDate": "2026-10-14",
        "venueName": "홍대 (마포)",
        "address": "서울특별시 마포구 와우산로21길 19 카페 드 파리 홍대점",
        "lat": 37.5563,
        "lng": 126.9237,
        "description": "원신 나타(Natlan) 테마의 특별 한정 디저트와 음료를 만나볼 수 있는 콜라보 카페입니다. 테마 음료 주문 시 캐릭터 코스터 및 포토카드가 증정되며 굿즈 판매존이 함께 운영됩니다.",
        "thumbnailUrl": "https://placehold.co/400x300/0284c7/white?text=Genshin+Cafe+Hongdae",
        "tags": ["원신", "호요버스", "콜라보카페", "홍대", "나타", "디저트"],
        "sourceUrl": "https://genshin.hoyoverse.com/ko/news/detail/cafe-paris-collab",
    },
    {
        "id": 3,
        "title": "귀멸의 칼날 특별전 -도깨비의 꽃-",
        "category": "애니메이션",
        "subCategory": "귀멸의 칼날",
        "startDate": "2026-09-01",
        "endDate": "2026-10-25",
        "reservationType": "사전예약",
        "reservationUrl": "https://tickets.interpark.com/goods/kimetsu-special-2026",
        "reservationStartDate": "2026-08-10",
        "reservationEndDate": "2026-10-24",
        "venueName": "DDP 동대문디자인플라자",
        "address": "서울특별시 중구 을지로 281 DDP 배움터 디자인전시관",
        "lat": 37.5670,
        "lng": 127.0094,
        "description": "귀멸의 칼날 TV 및 극장판 전 시리즈의 원화와 콘티, 실물 크기 캐릭터 조형물을 감상할 수 있는 대규모 공식 기획전입니다. 한국 한정 오리지널 굿즈샵이 동시 운영됩니다.",
        "thumbnailUrl": "https://placehold.co/400x300/dc2626/white?text=Demon+Slayer+Exhibition",
        "tags": ["귀멸의칼날", "애니메이션", "원화전", "DDP", "동대문", "유포테이블"],
        "sourceUrl": "https://kimetsu.com/exhibition/korea2026",
    },
    {
        "id": 4,
        "title": "나 혼자만 레벨업 웹툰 완결 2주년 팝업스토어",
        "category": "웹툰",
        "subCategory": "나 혼자만 레벨업",
        "startDate": "2026-09-28",
        "endDate": "2026-10-11",
        "reservationType": "현장대기",
        "reservationUrl": "",
        "reservationStartDate": None,
        "reservationEndDate": None,
        "venueName": "잠실 롯데월드몰",
        "address": "서울특별시 송파구 올림픽로 300 롯데월드몰 1F 아트리움",
        "lat": 37.5131,
        "lng": 127.1024,
        "description": "전 세계적인 신드롬을 일으킨 카카오페이지 레전드 웹툰 '나 혼자만 레벨업'의 기념 팝업스토어! 성진우 그림자 군단 디오라마와 아크릴 스탠드, 금속 뱃지, 한정판 아트북을 현장에서 만나보세요.",
        "thumbnailUrl": "https://placehold.co/400x300/4f46e5/white?text=Solo+Leveling+Popup",
        "tags": ["나혼자만레벨업", "웹툰", "카카오페이지", "잠실", "롯데월드몰", "성진우"],
        "sourceUrl": "https://page.kakao.com/events/sololeveling-popup",
    },

    # =========================================================================
    # 2. 곧 예약 오픈 또는 예약 진행 중인 행사 (Reservation Opening Soon)
    # =========================================================================
    {
        "id": 5,
        "title": "주술회전 × 애니메이트 카페",
        "category": "애니메이션",
        "subCategory": "주술회전",
        "startDate": "2026-10-15",
        "endDate": "2026-11-15",
        "reservationType": "네이버예약",
        "reservationUrl": "https://booking.naver.com/booking/12/bizes/jujutsu-cafe",
        "reservationStartDate": "2026-10-02",
        "reservationEndDate": "2026-10-12",
        "venueName": "애니메이트 홍대",
        "address": "서울특별시 마포구 양화로 188 AK플라자 홍대 5층 애니메이트 카페존",
        "lat": 37.5562,
        "lng": 126.9263,
        "description": "시부야 사변 & 회옥·옥절 에피소드를 테마로 한 공식 애니메이트 콜라보레이션 카페. 고죠 사토루, 게토 스구루, 이타도리 유지의 시그니처 메뉴와 캔뱃지, 엽서 증정 이벤트가 운영됩니다.",
        "thumbnailUrl": "https://placehold.co/400x300/1e293b/white?text=Jujutsu+Kaisen+Cafe",
        "tags": ["주술회전", "애니메이트", "콜라보카페", "홍대", "고죠사토루", "AK플라자"],
        "sourceUrl": "https://animatecafe.co.kr/event/jujutsu-2026",
    },
    {
        "id": 6,
        "title": "스텔라이브 2nd 단독 콘서트 & 전시회",
        "category": "버튜버",
        "subCategory": "스텔라이브",
        "startDate": "2026-10-30",
        "endDate": "2026-11-01",
        "reservationType": "사전예약",
        "reservationUrl": "https://stellive.kr/event/concert2026",
        "reservationStartDate": "2026-10-03",
        "reservationEndDate": "2026-10-25",
        "venueName": "아케이드 성수",
        "address": "서울특별시 성동구 아차산로 68 아케이드 성수 지하1층",
        "lat": 37.5445,
        "lng": 127.0560,
        "description": "버추얼 아이돌 기업 스텔라이브(StelLive)의 두 번째 단독 오프라인 콘서트 및 기념 전시회. 미스틱과 유니버스 멤버들의 미공개 콘셉트 아트 및 라이브 전용 공식 응원봉, 굿즈 컬렉션이 판매됩니다.",
        "thumbnailUrl": "https://placehold.co/400x300/a855f7/white?text=StelLive+2nd+Concert",
        "tags": ["스텔라이브", "버튜버", "강지", "성수", "아케이드성수", "콘서트"],
        "sourceUrl": "https://stellive.kr/notice/2nd-concert",
    },
    {
        "id": 7,
        "title": "우마무스메 프리티더비 팝업스토어",
        "category": "게임",
        "subCategory": "우마무스메",
        "startDate": "2026-10-16",
        "endDate": "2026-10-31",
        "reservationType": "네이버예약",
        "reservationUrl": "https://booking.naver.com/booking/12/bizes/umamusume-popup",
        "reservationStartDate": "2026-10-05",
        "reservationEndDate": "2026-10-14",
        "venueName": "용산 아이파크몰",
        "address": "서울특별시 용산구 한강대로23길 55 용산 아이파크몰 테마파크 6층",
        "lat": 37.5297,
        "lng": 126.9654,
        "description": "카카오게임즈의 모바일 육성 시뮬레이션 게임 '우마무스메 프리티 더비' 오피셜 팝업스토어! 승부복 아크릴 스탠드, 트레이너 저지, 위닝 라이브 응원봉 등 신규 굿즈가 대거 발매됩니다.",
        "thumbnailUrl": "https://placehold.co/400x300/10b981/white?text=Umamusume+Popup",
        "tags": ["우마무스메", "말딸", "카카오게임즈", "사이게임즈", "용산아이파크몰", "팝업스토어"],
        "sourceUrl": "https://umamusume.kakaogames.com/event/popup-2026",
    },
    {
        "id": 8,
        "title": "굿스마일 피규어 엑스포 2026 서울",
        "category": "피규어/굿즈",
        "subCategory": "굿스마일",
        "startDate": "2026-11-20",
        "endDate": "2026-11-22",
        "reservationType": "사전예약",
        "reservationUrl": "https://goodsmile.kr/expo2026",
        "reservationStartDate": "2026-10-05",
        "reservationEndDate": "2026-11-15",
        "venueName": "코엑스 (삼성)",
        "address": "서울특별시 강남구 영동대로 513 코엑스 전시장 Hall B",
        "lat": 37.5117,
        "lng": 127.0593,
        "description": "굿스마일 컴퍼니의 넨도로이드, 스케일 피규어, 프라모델 신작 원형 대공개! 원더 페스티벌 출품작 한국 최초 전시 및 행사 한정 넨도로이드 현장 특별 판매가 진행됩니다.",
        "thumbnailUrl": "https://placehold.co/400x300/e11d48/white?text=GoodSmile+Expo+2026",
        "tags": ["굿스마일", "넨도로이드", "피규어", "코엑스", "프라모델", "전시회"],
        "sourceUrl": "https://goodsmile.info/event/expo2026-seoul",
    },
    {
        "id": 9,
        "title": "Fate/Grand Order 8주년 기념 전시회",
        "category": "게임",
        "subCategory": "Fate/Grand Order",
        "startDate": "2026-11-05",
        "endDate": "2026-11-18",
        "reservationType": "캐치테이블",
        "reservationUrl": "https://app.catchtable.co.kr/ct/shop/fgo_8th_exhibition",
        "reservationStartDate": "2026-10-08",
        "reservationEndDate": "2026-11-04",
        "venueName": "더현대 서울 (여의도)",
        "address": "서울특별시 영등포구 여의대로 108 더현대 서울 5F 에픽서울",
        "lat": 37.5256,
        "lng": 126.9289,
        "description": "페이트/그랜드 오더 서비스 8주년을 축하하는 대규모 인터랙티브 전시회. 보구 연출 미디어아트 존, 성우 특별 음성 가이드, 한국 서비스 한정 공식 메모리얼 굿즈가 제공됩니다.",
        "thumbnailUrl": "https://placehold.co/400x300/3b82f6/white?text=Fate+Grand+Order+8th",
        "tags": ["FGO", "페그오", "Fate", "넷마블", "더현대서울", "전시회"],
        "sourceUrl": "https://fgo.netmarble.com/news/notice/8th-anniversary",
    },
    {
        "id": 10,
        "title": "홀로라이브 5th 페스 한국 팬미팅",
        "category": "버튜버",
        "subCategory": "홀로라이브",
        "startDate": "2026-11-07",
        "endDate": "2026-11-08",
        "reservationType": "사전예약",
        "reservationUrl": "https://ticketlink.co.kr/hololive-fanmeeting-2026",
        "reservationStartDate": "2026-10-10",
        "reservationEndDate": "2026-10-20",
        "venueName": "코엑스 (삼성)",
        "address": "서울특별시 강남구 영동대로 513 코엑스 오디토리움",
        "lat": 37.5117,
        "lng": 127.0593,
        "description": "커버 주식회사 주최, 홀로라이브 프로덕션 버추얼 탤런트들과 함께하는 한국 오프라인 팬미팅 및 뷰잉 이벤트입니다. 스페셜 게스트 토크쇼, 오피셜 굿즈 사전 예약 판매가 준비되어 있습니다.",
        "thumbnailUrl": "https://placehold.co/400x300/06b6d4/white?text=Hololive+5th+Fes",
        "tags": ["홀로라이브", "버튜버", "커버", "코엑스", "팬미팅", "라이브뷰잉"],
        "sourceUrl": "https://hololive.hololivepro.com/events/korea-fanmeeting-2026",
    },

    # =========================================================================
    # 3. 예정된 행사 (Upcoming Events - starting Oct-Nov 2026)
    # =========================================================================
    {
        "id": 11,
        "title": "체인소 맨 POP UP STORE",
        "category": "애니메이션",
        "subCategory": "체인소 맨",
        "startDate": "2026-10-20",
        "endDate": "2026-11-03",
        "reservationType": "현장대기",
        "reservationUrl": "",
        "reservationStartDate": None,
        "reservationEndDate": None,
        "venueName": "에스팩토리 (성수)",
        "address": "서울특별시 성동구 연무장15길 11 에스팩토리 D동",
        "lat": 37.5437,
        "lng": 127.0569,
        "description": "MAPPA 제작 애니메이션 '체인소 맨'의 다크하고 스타일리시한 세계관을 재현한 팝업스토어. 덴지, 파워, 마키마, 아키의 포치타 룸 및 오리지널 어패럴 라인업이 공개됩니다.",
        "thumbnailUrl": "https://placehold.co/400x300/ea580c/white?text=Chainsaw+Man+Popup",
        "tags": ["체인소맨", "MAPPA", "성수", "에스팩토리", "포치타", "굿즈"],
        "sourceUrl": "https://chainsawman.dog/popup-korea",
    },
    {
        "id": 12,
        "title": "전지적 독자 시점 공식 굿즈 팝업스토어",
        "category": "웹툰",
        "subCategory": "전지적 독자 시점",
        "startDate": "2026-10-23",
        "endDate": "2026-11-08",
        "reservationType": "자유입장",
        "reservationUrl": "",
        "reservationStartDate": None,
        "reservationEndDate": None,
        "venueName": "팝업스토어 성수",
        "address": "서울특별시 성동구 연무장길 35 팝업스토어 성수 1-2F",
        "lat": 37.5449,
        "lng": 127.0568,
        "description": "웹툰 전지적 독자 시점의 성수 팝업스토어 오픈! 김독자 컴퍼니 오피스 콘셉트의 포토존과 주인공 김독자, 유중혁의 향수, 메탈 키링, 회중시계 한정판 패키지가 공개됩니다.",
        "thumbnailUrl": "https://placehold.co/400x300/312e81/white?text=ORV+Popup+Seongsu",
        "tags": ["전독시", "전지적독자시점", "웹툰", "성수동", "김독자", "유중혁"],
        "sourceUrl": "https://comic.naver.com/popup/orv-2026",
    },
    {
        "id": 13,
        "title": "서울 코믹월드 2026 가을",
        "category": "동인행사",
        "subCategory": "코믹월드",
        "startDate": "2026-10-24",
        "endDate": "2026-10-25",
        "reservationType": "사전예약",
        "reservationUrl": "https://comicw.co.kr/tickets/autumn2026",
        "reservationStartDate": "2026-09-20",
        "reservationEndDate": "2026-10-23",
        "venueName": "킨텍스 (일산)",
        "address": "경기도 고양시 일산서구 킨텍스로 217-60 킨텍스 제1전시장 4-5홀",
        "lat": 37.6694,
        "lng": 126.7464,
        "description": "국내 최대 종합 아마추어 만화 및 서브컬처 동인 축제 서울 코믹월드! 수백 명의 동인 크리에이터 부스, 코스프레 무대 런웨이, 우타이테 라이브 콘서트가 펼쳐집니다.",
        "thumbnailUrl": "https://placehold.co/400x300/f59e0b/white?text=Comic+World+Autumn+2026",
        "tags": ["코믹월드", "서코", "동인행사", "킨텍스", "코스프레", "회지"],
        "sourceUrl": "https://comicw.co.kr/notice/2026-fall",
    },
    {
        "id": 14,
        "title": "하이큐!! THE FINAL 극장판 기념 팝업",
        "category": "애니메이션",
        "subCategory": "하이큐!!",
        "startDate": "2026-11-12",
        "endDate": "2026-11-26",
        "reservationType": "네이버예약",
        "reservationUrl": "https://booking.naver.com/booking/12/bizes/haikyu-final-popup",
        "reservationStartDate": "2026-10-28",
        "reservationEndDate": "2026-11-10",
        "venueName": "AK플라자 홍대",
        "address": "서울특별시 마포구 양화로 188 AK플라자 홍대 4층",
        "lat": 37.5577,
        "lng": 126.9244,
        "description": "극장판 하이큐!! 쓰레기장의 결전 흥행을 기념하는 공식 팝업스토어. 카라스노 고교와 네코마 고교의 라이벌 대결 명장면 포토존, 유니폼 레플리카 및 캐릭터 슬로건 타월을 판매합니다.",
        "thumbnailUrl": "https://placehold.co/400x300/f97316/white?text=Haikyu+Final+Popup",
        "tags": ["하이큐", "극장판", "AK플라자", "홍대", "카라스노", "네코마"],
        "sourceUrl": "https://haikyu.jp/movie/korea-popup",
    },
    {
        "id": 15,
        "title": "VCR 게임즈 데이 2026 (배틀그라운드/발로란트)",
        "category": "게임",
        "subCategory": "VCR 게임즈",
        "startDate": "2026-11-28",
        "endDate": "2026-11-29",
        "reservationType": "사전예약",
        "reservationUrl": "https://vcr-gamesday.kr/tickets",
        "reservationStartDate": "2026-10-15",
        "reservationEndDate": "2026-11-20",
        "venueName": "킨텍스 (일산)",
        "address": "경기도 고양시 일산서구 킨텍스로 217-60 킨텍스 제2전시장 7홀",
        "lat": 37.6694,
        "lng": 126.7464,
        "description": "인기 스트리머와 버튜버들이 총출동하는 국내 최대 인비테이셔널 e스포츠 축제! 배틀그라운드와 발로란트 오프라인 매치 및 현장 관람객 참여형 이벤트 매치가 진행됩니다.",
        "thumbnailUrl": "https://placehold.co/400x300/059669/white?text=VCR+Games+Day+2026",
        "tags": ["VCR", "배틀그라운드", "발로란트", "스트리머", "킨텍스", "e스포츠"],
        "sourceUrl": "https://vcr-gamesday.kr/2026",
    },

    # =========================================================================
    # 4. 종료된 행사 (Past Events - ended in Sep 2026)
    # =========================================================================
    {
        "id": 16,
        "title": "초속5센티미터 × 너의 이름은 마코토 신카이 특별전",
        "category": "애니메이션",
        "subCategory": "신카이 마코토",
        "startDate": "2026-08-15",
        "endDate": "2026-09-20",
        "reservationType": "사전예약",
        "reservationUrl": "https://tickets.interpark.com/shinkai-special-2026",
        "reservationStartDate": "2026-08-01",
        "reservationEndDate": "2026-09-18",
        "venueName": "DDP 동대문디자인플라자",
        "address": "서울특별시 중구 을지로 281 DDP 뮤지엄",
        "lat": 37.5670,
        "lng": 127.0094,
        "description": "신카이 마코토 감독의 대표작들을 조명하는 대규모 회고전. 빛과 풍경의 마술사로 불리는 신카이 월드의 배경 미술 원화, 음악 체험관, 영화 OST 한정 바이닐 LP가 전시/판매되었습니다.",
        "thumbnailUrl": "https://placehold.co/400x300/0ea5e9/white?text=Shinkai+Makoto+Exhibition",
        "tags": ["신카이마코토", "너의이름은", "초속5센티미터", "DDP", "애니메이션", "원화전"],
        "sourceUrl": "https://shinkaimakoto-exhibition.kr",
    },
    {
        "id": 17,
        "title": "리그 오브 레전드 월드 챔피언십 2026 팬파크",
        "category": "게임",
        "subCategory": "리그 오브 레전드",
        "startDate": "2026-09-10",
        "endDate": "2026-09-24",
        "reservationType": "자유입장",
        "reservationUrl": "",
        "reservationStartDate": None,
        "reservationEndDate": None,
        "venueName": "킨텍스 (일산)",
        "address": "경기도 고양시 일산서구 킨텍스로 217-60 킨텍스 야외광장",
        "lat": 37.6694,
        "lng": 126.7464,
        "description": "LCK 팬들을 위한 대규모 페스티벌! 팀별 응원 부스, 코스프레 콘테스트, 전설의 전당 미니 뮤지엄 및 인플루언서 초청 쇼매치가 성황리에 열렸습니다.",
        "thumbnailUrl": "https://placehold.co/400x300/1e3a8a/white?text=LoL+Worlds+FanPark",
        "tags": ["롤", "리그오브레전드", "LCK", "롤드컵", "킨텍스", "팬파크"],
        "sourceUrl": "https://lolesports.com/news/worlds2026-fanpark",
    },
    {
        "id": 18,
        "title": "스파이×패밀리 시크릿 카페",
        "category": "애니메이션",
        "subCategory": "스파이×패밀리",
        "startDate": "2026-08-20",
        "endDate": "2026-09-25",
        "reservationType": "네이버예약",
        "reservationUrl": "https://booking.naver.com/booking/12/bizes/spyfamily-cafe",
        "reservationStartDate": "2026-08-05",
        "reservationEndDate": "2026-08-18",
        "venueName": "용산 아이파크몰",
        "address": "서울특별시 용산구 한강대로23길 55 용산 아이파크몰 리빙파크 6층 팝콘D스퀘어",
        "lat": 37.5297,
        "lng": 126.9654,
        "description": "로이드, 요르, 아냐의 포저 일가와 본드가 함께한 테마 카페. 아냐의 땅콩 파르페와 키메라 장난감 굿즈 등 온 가족과 팬들이 함께 즐긴 콜라보 카페 행사였습니다.",
        "thumbnailUrl": "https://placehold.co/400x300/f43f5e/white?text=Spy+Family+Cafe",
        "tags": ["스파이패밀리", "아냐", "용산아이파크몰", "팝콘D스퀘어", "콜라보카페", "애니메이션"],
        "sourceUrl": "https://spy-family.net/cafe-korea-2026",
    },
]


def get_all_events() -> List[Dict[str, Any]]:
    """Return all events."""
    return EVENTS


def get_event_by_id(event_id: int) -> Optional[Dict[str, Any]]:
    """Find and return an event by its ID."""
    for event in EVENTS:
        if event["id"] == event_id:
            return event
    return None


def get_events_by_category(category: str) -> List[Dict[str, Any]]:
    """Filter events by category."""
    return [event for event in EVENTS if event["category"] == category]


def get_events_by_status(status: str, ref_date: str = CURRENT_DATE) -> List[Dict[str, Any]]:
    """Filter events by status relative to reference date.
    
    Status can be:
    - 'ongoing': event is currently taking place
    - 'upcoming': event starts after ref_date
    - 'past': event ended before ref_date
    """
    if status == "ongoing":
        return [
            event for event in EVENTS
            if event["startDate"] <= ref_date <= event["endDate"]
        ]
    elif status == "upcoming":
        return [
            event for event in EVENTS
            if event["startDate"] > ref_date
        ]
    elif status == "past":
        return [
            event for event in EVENTS
            if event["endDate"] < ref_date
        ]
    return EVENTS
