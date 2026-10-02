# -*- coding: utf-8 -*-
"""
카카오 Geocoding API 연동 모듈

텍스트 주소를 위도/경도 좌표로 변환합니다.
- 카카오 Local API (주소 검색) 사용
- API 키는 환경변수 KAKAO_REST_API_KEY 또는 .env 파일에서 로드
"""

import os
import json
from typing import Optional, Tuple

try:
    import requests
except ImportError:
    requests = None


def _load_api_key() -> Optional[str]:
    """
    카카오 REST API 키를 환경변수 또는 .env 파일에서 로드합니다.
    """
    # 1. 환경변수에서 먼저 탐색
    key = os.environ.get("KAKAO_REST_API_KEY")
    if key:
        return key

    # 2. 프로젝트 루트의 .env 파일에서 탐색
    env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line.startswith("#") or "=" not in line:
                    continue
                k, v = line.split("=", 1)
                k = k.strip()
                v = v.strip().strip('"').strip("'")
                if k == "KAKAO_REST_API_KEY":
                    return v

    return None


def geocode(address: str) -> Tuple[Optional[float], Optional[float]]:
    """
    주소 텍스트를 위도/경도 좌표로 변환합니다.
    
    Args:
        address: 변환할 주소 문자열 (예: "서울특별시 강남구 영동대로 513")
    
    Returns:
        (lat, lng) 튜플. 변환 실패 시 (None, None).
    """
    if not requests:
        print("[Geocoder] requests 라이브러리가 없습니다.")
        return None, None

    api_key = _load_api_key()
    if not api_key:
        # API 키 없이도 프로그램이 중단되지 않도록 graceful 처리
        return None, None

    url = "https://dapi.kakao.com/v2/local/search/address.json"
    headers = {"Authorization": f"KakaoAK {api_key}"}
    params = {"query": address}

    try:
        response = requests.get(url, headers=headers, params=params, timeout=5)
        if response.status_code == 200:
            data = response.json()
            documents = data.get("documents", [])
            if documents:
                doc = documents[0]
                lat = float(doc.get("y", 0))
                lng = float(doc.get("x", 0))
                if lat and lng:
                    return lat, lng

        # 주소 검색 실패 시, 키워드 검색으로 재시도
        url_keyword = "https://dapi.kakao.com/v2/local/search/keyword.json"
        response = requests.get(url_keyword, headers=headers, params=params, timeout=5)
        if response.status_code == 200:
            data = response.json()
            documents = data.get("documents", [])
            if documents:
                doc = documents[0]
                lat = float(doc.get("y", 0))
                lng = float(doc.get("x", 0))
                if lat and lng:
                    return lat, lng

    except requests.exceptions.RequestException as e:
        print(f"[Geocoder] API 요청 실패: {e}")

    return None, None


def geocode_event(event: dict) -> dict:
    """
    이벤트 딕셔너리에 좌표가 없으면 주소를 기반으로 좌표를 채웁니다.
    이미 좌표가 있으면 그대로 반환합니다.
    """
    if event.get("lat") and event.get("lng"):
        return event

    address = event.get("address", "") or event.get("venueName", "")
    if address:
        lat, lng = geocode(address)
        if lat and lng:
            event["lat"] = lat
            event["lng"] = lng

    return event


# ==============================================================================
# 테스트 (직접 실행 시)
# ==============================================================================
if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding='utf-8')

    api_key = _load_api_key()
    if not api_key:
        print("=" * 60)
        print("  Geocoder 테스트")
        print("=" * 60)
        print()
        print("  [!] 카카오 REST API 키가 설정되지 않았습니다.")
        print()
        print("  .env 파일에 아래 내용을 추가해 주세요:")
        print('  KAKAO_REST_API_KEY=여기에_발급받은_키_입력')
        print()
        print("  또는 환경변수로 설정:")
        print('  $env:KAKAO_REST_API_KEY="여기에_발급받은_키_입력"')
    else:
        print("=" * 60)
        print("  Geocoder 테스트 (API 키 감지됨)")
        print("=" * 60)

        test_addresses = [
            "서울특별시 강남구 영동대로 513",
            "서울특별시 영등포구 여의대로 108",
            "경기도 고양시 일산서구 킨텍스로 217-60",
        ]

        for addr in test_addresses:
            lat, lng = geocode(addr)
            status = f"({lat}, {lng})" if lat else "실패"
            print(f"  {addr} -> {status}")
