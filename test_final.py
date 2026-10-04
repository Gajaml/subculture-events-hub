import urllib.request
import urllib.parse
import urllib.error
import json
import pytest
from datetime import date

BASE_URL = 'http://localhost:5000'

def test_health_check():
    r = urllib.request.urlopen(f'{BASE_URL}/api/health')
    health = json.loads(r.read())
    assert health['status'] == 'healthy'
    assert health['today'] == date.today().isoformat()
    assert health['total_events'] == 18

def test_all_events_api():
    r = urllib.request.urlopen(f'{BASE_URL}/api/events')
    events = json.loads(r.read())
    assert len(events) == 18
    assert all('status' in e for e in events)
    assert all(e['status'] in ('ongoing', 'upcoming', 'ended', 'reservation_open') for e in events)
    assert all('lat' in e and 'lng' in e for e in events)
    assert all('thumbnailUrl' in e for e in events)

def test_category_filter():
    # 실제 DB에 존재하는 카테고리들에 대한 필터링 검증
    r = urllib.request.urlopen(f'{BASE_URL}/api/events')
    all_events = json.loads(r.read())
    categories = list(set(e['category'] for e in all_events if e.get('category')))
    assert len(categories) > 0

    for cat_kr in categories:
        encoded = urllib.parse.quote(cat_kr)
        r = urllib.request.urlopen(f'{BASE_URL}/api/events?category={encoded}')
        data = json.loads(r.read())
        assert len(data) >= 1, f"Category '{cat_kr}' should return at least 1 event"
        assert all(d['category'] == cat_kr for d in data)

def test_status_filter():
    # 진행 중/예정/종료 상태 필터가 정상 동작하는지 검증
    r = urllib.request.urlopen(f'{BASE_URL}/api/events')
    all_events = json.loads(r.read())
    statuses_present = set(e['status'] for e in all_events if e.get('status'))

    for status in statuses_present:
        r = urllib.request.urlopen(f'{BASE_URL}/api/events?status={status}')
        data = json.loads(r.read())
        assert len(data) >= 1
        assert all(d['status'] == status or d.get('event_status') == status for d in data)

def test_single_event():
    r = urllib.request.urlopen(f'{BASE_URL}/api/events/1')
    ev1 = json.loads(r.read())
    assert ev1['id'] == 1
    assert len(ev1['title']) > 0
    assert 37.0 < ev1['lat'] < 38.0
    assert 126.0 < ev1['lng'] < 128.0

def test_frontend_page():
    r = urllib.request.urlopen(f'{BASE_URL}/')
    html = r.read().decode('utf-8')
    assert len(html) > 10000
    assert 'tailwindcss' in html
    assert 'leaflet' in html.lower()
    assert "/api/events" in html
    assert '서브컬처' in html
    assert 'cal-grid' in html
    assert 'view-map' in html
    assert 'view-list' in html
    assert 'event-modal' in html
    assert 'data-val="ongoing"' in html
    assert 'data-val="upcoming"' in html
    assert 'thumbnailUrl' in html

def test_error_handling():
    with pytest.raises(urllib.error.HTTPError) as excinfo:
        urllib.request.urlopen(f'{BASE_URL}/api/events/99999')
    assert excinfo.value.code == 404
