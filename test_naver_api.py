# -*- coding: utf-8 -*-
"""
네이버 API 인증 테스트 스크립트
secrets.json에서 키를 읽어와 보안 상 안전하게 API를 호출합니다.
"""
import urllib.request
import urllib.parse
import json
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

def load_secrets():
    client_id = os.environ.get("NAVER_CLIENT_ID")
    client_secret = os.environ.get("NAVER_CLIENT_SECRET")
    
    if not client_id or not client_secret:
        print("❌ 환경변수(NAVER_CLIENT_ID, NAVER_CLIENT_SECRET)가 설정되지 않았습니다.")
        return None, None
        
    return client_id, client_secret

def test_naver_search():
    client_id = os.environ.get("NAVER_CLIENT_ID")
    client_secret = os.environ.get("NAVER_CLIENT_SECRET")
    if not client_id:
        return
        
    print("✅ 키 로드 성공. 네이버 클라우드(NCP) 기반 블로그 검색 API 테스트를 시작합니다...\n")
    
    query = urllib.parse.quote("팝업스토어")
    # NCP NAVER API HUB 신규 엔드포인트
    url = f"https://naverapihub.apigw.ntruss.com/search/v1/blog?query={query}&display=3"
    
    req = urllib.request.Request(url)
    
    # NCP 신규 헤더 적용 (Client ID/Secret 또는 API KEY 방식 모두 시도)
    req.add_header("X-NCP-APIGW-API-KEY-ID", client_id)
    req.add_header("X-NCP-APIGW-API-KEY", client_secret)
    # 혹시 모를 하위 호환성을 위해 구형 헤더도 함께 전송
    req.add_header("X-Naver-Client-Id", client_id)
    req.add_header("X-Naver-Client-Secret", client_secret)
    
    try:
        r = urllib.request.urlopen(req)
        response_code = r.getcode()
        
        if response_code == 200:
            print("🎉 [성공] NCP API 연동이 완벽하게 작동합니다!")
            response_body = r.read().decode('utf-8')
            data = json.loads(response_body)
            
            print(f"\n총 검색 결과 수: {data.get('total', 0):,}건")
            print("-" * 50)
            for i, item in enumerate(data.get('items', []), 1):
                title = item.get('title', '').replace('<b>', '').replace('</b>', '')
                print(f"{i}. {title}")
                print(f"   (링크: {item.get('link')})")
            print("-" * 50)
        else:
            print(f"⚠️ [에러] HTTP 응답 코드: {response_code}")
            
    except urllib.error.HTTPError as e:
        print(f"❌ [에러] 인증 실패 또는 권한 오류 (HTTP {e.code})")
        print(f"상세 에러 내용: {e.read().decode('utf-8', errors='ignore')}")
    except Exception as e:
        print(f"❌ [에러] 알 수 없는 오류: {e}")

if __name__ == "__main__":
    test_naver_search()
