"""Digest events (continuous-local-run R9, R46): small, durable records the daily digest reads."""
from __future__ import annotations

import json
import os
from datetime import date, datetime, timedelta, timezone

import psycopg


def emit(conn: psycopg.Connection, kind: str, detail: dict | None = None, *, run_id: str | None = None) -> None:
    with conn.cursor() as cur:
        cur.execute("INSERT INTO digest_events (run_id, kind, detail) VALUES (%s,%s,%s::jsonb)", (run_id or os.environ.get("CAMPUS_RUN_ID"), kind, json.dumps(detail or {}, default=str)))
    conn.commit()


def for_day(conn: psycopg.Connection, day: date | None = None) -> list[dict]:
    day = day or datetime.now(timezone.utc).date()
    start = datetime(day.year, day.month, day.day, tzinfo=timezone.utc)
    with conn.cursor() as cur:
        cur.execute("SELECT created_at, run_id, kind, detail FROM digest_events WHERE created_at >= %s AND created_at < %s ORDER BY created_at", (start, start + timedelta(days=1)))
        return [dict(r) for r in cur.fetchall()]
