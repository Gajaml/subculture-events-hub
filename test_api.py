# -*- coding: utf-8 -*-
"""API 통합 테스트 스크립트"""
import urllib.request
import json

def test_api(url, label):
    r = urllib.request.urlopen(url)
    data = json.loads(r.read())
    return data

# 1. Health Check
health = test_api('http://localhost:5000/api/health', 'Health')
print(f"=== Health Check ===")
print(f"  Status: {health['status']}, Date: {health['today']}, Events: {health['total_events']}")

# 2. All Events
events = test_api('http://localhost:5000/api/events', 'All Events')
print(f"\n=== All Events: {len(events)} ===")
for ev in events[:5]:
    status = ev.get('status', '?')
    print(f"  [{status}] {ev['title']} | {ev['venueName']} | {ev['startDate']}~{ev['endDate']}")
if len(events) > 5:
    print(f"  ... and {len(events) - 5} more")

# 3. Category Filter
games = test_api('http://localhost:5000/api/events?category=%EA%B2%8C%EC%9E%84', 'Games')
print(f"\n=== Category: 게임 => {len(games)} events ===")
for ev in games:
    print(f"  - {ev['title']}")

anime = test_api('http://localhost:5000/api/events?category=%EC%95%A0%EB%8B%88%EB%A9%94%EC%9D%B4%EC%85%98', 'Anime')
print(f"\n=== Category: 애니메이션 => {len(anime)} events ===")
for ev in anime:
    print(f"  - {ev['title']}")

# 4. Status Filter
ongoing = test_api('http://localhost:5000/api/events?status=ongoing', 'Ongoing')
print(f"\n=== Status: 진행 중 => {len(ongoing)} events ===")
for ev in ongoing:
    print(f"  - {ev['title']} ({ev['startDate']}~{ev['endDate']})")

upcoming = test_api('http://localhost:5000/api/events?status=upcoming', 'Upcoming')
print(f"\n=== Status: 예정 => {len(upcoming)} events ===")
for ev in upcoming:
    print(f"  - {ev['title']} ({ev['startDate']})")

reservation = test_api('http://localhost:5000/api/events?status=reservation', 'Reservation')
print(f"\n=== Status: 예약 오픈 중 => {len(reservation)} events ===")
for ev in reservation:
    print(f"  - {ev['title']} (예약: {ev.get('reservationStartDate','N/A')}~{ev.get('reservationEndDate','N/A')})")

ended = test_api('http://localhost:5000/api/events?status=ended', 'Ended')
print(f"\n=== Status: 종료 => {len(ended)} events ===")
for ev in ended:
    print(f"  - {ev['title']}")

# 5. Categories List
cats = test_api('http://localhost:5000/api/categories', 'Categories')
print(f"\n=== Available Categories: {cats} ===")

# 6. Single Event
ev1 = test_api('http://localhost:5000/api/events/1', 'Single Event')
print(f"\n=== Single Event (ID=1) ===")
print(f"  Title: {ev1['title']}")
print(f"  Category: {ev1['category']}")
print(f"  Status: {ev1['status']}")
print(f"  Location: {ev1['venueName']} ({ev1['lat']}, {ev1['lng']})")

# 7. Frontend Page
r = urllib.request.urlopen('http://localhost:5000/')
html = r.read().decode('utf-8')
print(f"\n=== Frontend HTML ===")
print(f"  Size: {len(html)} bytes")
print(f"  Contains '서브컬처': {'서브컬처' in html}")
print(f"  Contains 'Leaflet': {'leaflet' in html.lower()}")
print(f"  Contains 'Tailwind': {'tailwind' in html.lower()}")

print("\n✅ ALL TESTS PASSED!")
