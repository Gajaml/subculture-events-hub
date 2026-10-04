# -*- coding: utf-8 -*-
"""
SQLite 데이터베이스 관리 모듈

이벤트 데이터의 영구 저장 및 조회를 담당합니다.
- 테이블 자동 생성 (CREATE IF NOT EXISTS)
- 이벤트 삽입 (중복 방지: title + startDate + venueName 기준)
- 전체/개별 이벤트 조회
- Mock 데이터 마이그레이션 지원
"""

import os
import sqlite3
from datetime import date
from typing import Any, Dict, List, Optional

# DB 파일 경로: 프로젝트 루트의 data/events.db
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "data", "events.db")

# ==============================================================================
# 테이블 스키마 정의
# ==============================================================================
CREATE_EVENTS_TABLE = """
CREATE TABLE IF NOT EXISTS events (
    id                    INTEGER PRIMARY KEY AUTOINCREMENT,
    title                 TEXT NOT NULL,
    category              TEXT NOT NULL DEFAULT '게임',
    sub_category          TEXT DEFAULT '',
    start_date            TEXT NOT NULL,
    end_date              TEXT NOT NULL,
    reservation_type      TEXT DEFAULT '',
    reservation_url       TEXT DEFAULT '',
    reservation_start_date TEXT,
    reservation_end_date  TEXT,
    venue_name            TEXT DEFAULT '',
    address               TEXT DEFAULT '',
    lat                   REAL,
    lng                   REAL,
    description           TEXT DEFAULT '',
    thumbnail_url         TEXT DEFAULT '',
    tags                  TEXT DEFAULT '[]',
    source_url            TEXT DEFAULT '',
    source                TEXT DEFAULT 'manual',
    created_at            TEXT DEFAULT (datetime('now', 'localtime')),
    updated_at            TEXT DEFAULT (datetime('now', 'localtime')),
    UNIQUE(title, start_date, venue_name)
);
"""

CREATE_INDEX = """
CREATE INDEX IF NOT EXISTS idx_events_dates ON events(start_date, end_date);
CREATE INDEX IF NOT EXISTS idx_events_category ON events(category);
"""


# ==============================================================================
# DB 초기화 및 연결
# ==============================================================================
def get_connection() -> sqlite3.Connection:
    """SQLite 데이터베이스 연결을 반환합니다."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA foreign_keys=ON;")
    return conn


def init_db():
    """데이터베이스 테이블 및 인덱스를 초기화합니다."""
    conn = get_connection()
    try:
        conn.execute(CREATE_EVENTS_TABLE)
        conn.executescript(CREATE_INDEX)
        conn.commit()
        print(f"[DB] 데이터베이스 초기화 완료: {DB_PATH}")
    finally:
        conn.close()


# ==============================================================================
# 이벤트 CRUD 함수
# ==============================================================================
def insert_event(event: Dict[str, Any]) -> Optional[int]:
    """
    이벤트 1건을 DB에 삽입합니다.
    title + start_date + venue_name이 동일한 행이 이미 있으면 무시(중복 방지)합니다.
    
    Returns:
        삽입된 row ID, 또는 중복이면 None
    """
    import json

    tags = event.get("tags", [])
    if isinstance(tags, list):
        tags = json.dumps(tags, ensure_ascii=False)

    conn = get_connection()
    try:
        cursor = conn.execute(
            """
            INSERT OR IGNORE INTO events 
                (title, category, sub_category, start_date, end_date,
                 reservation_type, reservation_url, reservation_start_date, reservation_end_date,
                 venue_name, address, lat, lng, description, thumbnail_url, tags, source_url, source)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                event.get("title", ""),
                event.get("category", "게임"),
                event.get("subCategory", event.get("sub_category", "")),
                event.get("startDate", event.get("start_date", "")),
                event.get("endDate", event.get("end_date", "")),
                event.get("reservationType", event.get("reservation_type", "")),
                event.get("reservationUrl", event.get("reservation_url", "")),
                event.get("reservationStartDate", event.get("reservation_start_date")),
                event.get("reservationEndDate", event.get("reservation_end_date")),
                event.get("venueName", event.get("venue_name", "")),
                event.get("address", ""),
                event.get("lat"),
                event.get("lng"),
                event.get("description", ""),
                event.get("thumbnailUrl", event.get("thumbnail_url", "")),
                tags,
                event.get("sourceUrl", event.get("source_url", "")),
                event.get("source", "manual"),
            ),
        )
        conn.commit()
        return cursor.lastrowid if cursor.rowcount > 0 else None
    finally:
        conn.close()


def insert_events_bulk(events: List[Dict[str, Any]]) -> int:
    """이벤트 목록을 일괄 삽입합니다. 삽입된 건수를 반환합니다."""
    count = 0
    for ev in events:
        result = insert_event(ev)
        if result is not None:
            count += 1
    return count


def get_all_events() -> List[Dict[str, Any]]:
    """DB에 저장된 모든 이벤트를 딕셔너리 리스트로 반환합니다."""
    import json

    conn = get_connection()
    try:
        rows = conn.execute("SELECT * FROM events ORDER BY start_date ASC").fetchall()
        events = []
        for row in rows:
            ev = dict(row)
            # snake_case → camelCase 변환 (프론트엔드 호환)
            ev = _to_camel_case(ev)
            # tags를 JSON 문자열에서 리스트로 복원
            if isinstance(ev.get("tags"), str):
                try:
                    ev["tags"] = json.loads(ev["tags"])
                except (json.JSONDecodeError, TypeError):
                    ev["tags"] = []
            events.append(ev)
        return events
    finally:
        conn.close()


def get_event_by_id(event_id: int) -> Optional[Dict[str, Any]]:
    """특정 ID의 이벤트를 반환합니다."""
    import json

    conn = get_connection()
    try:
        row = conn.execute("SELECT * FROM events WHERE id = ?", (event_id,)).fetchone()
        if row is None:
            return None
        ev = _to_camel_case(dict(row))
        if isinstance(ev.get("tags"), str):
            try:
                ev["tags"] = json.loads(ev["tags"])
            except (json.JSONDecodeError, TypeError):
                ev["tags"] = []
        return ev
    finally:
        conn.close()


def get_event_count() -> int:
    """DB에 저장된 이벤트 총 수를 반환합니다."""
    conn = get_connection()
    try:
        row = conn.execute("SELECT COUNT(*) FROM events").fetchone()
        return row[0]
    except Exception:
        return 0
    finally:
        conn.close()


# ==============================================================================
# 유틸리티
# ==============================================================================
def _to_camel_case(d: Dict[str, Any]) -> Dict[str, Any]:
    """snake_case 키를 camelCase로 변환합니다 (프론트엔드 호환)."""
    mapping = {
        "id": "id",
        "title": "title",
        "category": "category",
        "sub_category": "subCategory",
        "start_date": "startDate",
        "end_date": "endDate",
        "reservation_type": "reservationType",
        "reservation_url": "reservationUrl",
        "reservation_start_date": "reservationStartDate",
        "reservation_end_date": "reservationEndDate",
        "venue_name": "venueName",
        "address": "address",
        "lat": "lat",
        "lng": "lng",
        "description": "description",
        "thumbnail_url": "thumbnailUrl",
        "tags": "tags",
        "source_url": "sourceUrl",
        "source": "source",
        "created_at": "createdAt",
        "updated_at": "updatedAt",
    }
    result = {}
    for key, value in d.items():
        new_key = mapping.get(key, key)
        result[new_key] = value
    return result


# ==============================================================================
# 직접 실행 시: DB 초기화
# ==============================================================================
if __name__ == "__main__":
    init_db()
    print(f"[DB] 총 이벤트 수: {get_event_count()}")
