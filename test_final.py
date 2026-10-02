# -*- coding: utf-8 -*-
"""최종 통합 테스트 - API 응답 및 프론트엔드 연동 확인"""
import urllib.request
import json
import sys

# Windows 콘솔 인코딩 문제 해결
sys.stdout.reconfigure(encoding='utf-8')

errors = []

def test(label, condition, detail=""):
    status = "PASS" if condition else "FAIL"
    print(f"  [{status}] {label}" + (f" - {detail}" if detail else ""))
    if not condition:
        errors.append(label)

print("=" * 60)
print("  서브컬처 이벤트 애그리게이터 - 통합 테스트")
print("=" * 60)

# 1. Health Check
print("\n1. Health Check API")
r = urllib.request.urlopen('http://localhost:5000/api/health')
health = json.loads(r.read())
test("서버 상태 healthy", health['status'] == 'healthy')
test("오늘 날짜 반환", health['today'] == '2026-10-01')
test("이벤트 18개 로드", health['total_events'] == 18)

# 2. All Events API
print("\n2. 전체 이벤트 목록 API")
r = urllib.request.urlopen('http://localhost:5000/api/events')
events = json.loads(r.read())
test("전체 이벤트 반환", len(events) == 18, f"returned {len(events)}")
test("status 필드 존재", all('status' in e for e in events))
test("유효한 status 값", all(e['status'] in ('ongoing','upcoming','ended','reservation_open') for e in events))
test("lat/lng 좌표 존재", all('lat' in e and 'lng' in e for e in events))
test("thumbnailUrl 존재", all('thumbnailUrl' in e for e in events))

# 3. Category Filter
print("\n3. 카테고리 필터링")
for cat_kr, expected_min in [('게임', 3), ('애니메이션', 3), ('버튜버', 1)]:
    encoded = urllib.parse.quote(cat_kr)
    r = urllib.request.urlopen(f'http://localhost:5000/api/events?category={encoded}')
    data = json.loads(r.read())
    test(f"카테고리 '{cat_kr}' 필터", len(data) >= expected_min, f"{len(data)}개")

# 4. Status Filter
print("\n4. 상태 필터링")
for status, label in [('ongoing', '진행 중'), ('upcoming', '예정'), ('ended', '종료')]:
    r = urllib.request.urlopen(f'http://localhost:5000/api/events?status={status}')
    data = json.loads(r.read())
    test(f"상태 '{label}' 필터", len(data) >= 1, f"{len(data)}개")
    test(f"'{label}' status 값 일관성", all(
        d['status'] == status or d['event_status'] == status for d in data
    ))

# 5. Single Event
print("\n5. 단일 이벤트 조회")
r = urllib.request.urlopen('http://localhost:5000/api/events/1')
ev1 = json.loads(r.read())
test("ID=1 이벤트 조회", ev1['id'] == 1)
test("이벤트 title 존재", len(ev1['title']) > 0, ev1['title'])
test("좌표 유효", 37.0 < ev1['lat'] < 38.0 and 126.0 < ev1['lng'] < 128.0)

# 6. Frontend Page
print("\n6. 프론트엔드 HTML 서빙")
r = urllib.request.urlopen('http://localhost:5000/')
html = r.read().decode('utf-8')
test("HTML 렌더링 성공", len(html) > 10000, f"{len(html)} bytes")
test("Tailwind CSS 포함", 'tailwindcss' in html)
test("Leaflet 포함", 'leaflet' in html.lower())
test("fetch('/api/events') 호출 포함", "/api/events" in html)
test("한글 UI 포함", '서브컬처' in html)
test("캘린더 뷰 포함", 'cal-grid' in html)
test("지도 뷰 포함", 'view-map' in html)
test("리스트 뷰 포함", 'view-list' in html)
test("이벤트 모달 포함", 'event-modal' in html)
test("영문 status 필터 값 (ongoing)", 'data-val="ongoing"' in html)
test("영문 status 필터 값 (upcoming)", 'data-val="upcoming"' in html)
test("thumbnailUrl 사용", 'thumbnailUrl' in html)

# 7. 404 for missing event
print("\n7. 에러 핸들링")
try:
    urllib.request.urlopen('http://localhost:5000/api/events/99999')
    test("존재하지 않는 이벤트 404", False)
except urllib.error.HTTPError as e:
    test("존재하지 않는 이벤트 404", e.code == 404, f"HTTP {e.code}")

# Summary
print("\n" + "=" * 60)
if errors:
    print(f"  FAILED: {len(errors)} tests")
    for err in errors:
        print(f"    - {err}")
else:
    print("  ALL TESTS PASSED! (모든 테스트 통과)")
print("=" * 60)
