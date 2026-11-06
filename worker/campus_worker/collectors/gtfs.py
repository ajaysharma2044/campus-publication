"""GTFS feed collector (continuous-local-run R34): bus routes from a transit agency's published GTFS zip.

Used for TCAT (Ithaca): the agency website blocks automated agents (robots.txt disallows Claude crawlers and returns 403),
but its GTFS feed is a published data product. Only routes.txt is read; no stop-level personal data exists in GTFS.
"""
from __future__ import annotations

import csv
import io
import json
import zipfile
from datetime import datetime, timezone
from uuid import UUID

import psycopg

from ..registry import slugify


def parse_routes(zip_bytes: bytes) -> list[dict]:
    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as z:
        names = {n.lower(): n for n in z.namelist()}
        if "routes.txt" not in names:
            raise ValueError("GTFS zip has no routes.txt")
        rows = list(csv.DictReader(io.TextIOWrapper(z.open(names["routes.txt"]), encoding="utf-8-sig")))
        agency = {}
        if "agency.txt" in names:
            ag = list(csv.DictReader(io.TextIOWrapper(z.open(names["agency.txt"]), encoding="utf-8-sig")))
            agency = ag[0] if ag else {}
    out = []
    for r in rows:
        short = (r.get("route_short_name") or "").strip()
        long_ = (r.get("route_long_name") or "").strip()
        if not short and not long_:
            continue
        name = f"Route {short}: {long_}" if short and long_ else (f"Route {short}" if short else long_)
        out.append({"name": name[:120], "slug": slugify(f"route-{short or long_}"), "attributes": {"route_id": r.get("route_id"), "route_short_name": short, "route_long_name": long_,
                                                                                                    "route_type": r.get("route_type"), "route_color": r.get("route_color"), "agency": agency.get("agency_name"), "agency_url": agency.get("agency_url")}})
    return out


def store_routes(conn: psycopg.Connection, routes: list[dict], *, place_id: UUID, source_url: str, source_id: UUID | None, topic_key: str = "town_transit_local",
                 rule_key: str = "gtfs_routes", now: datetime | None = None) -> dict:
    now = now or datetime.now(timezone.utc)
    created = updated = 0
    with conn.cursor() as cur:
        cur.execute("SELECT id FROM topics WHERE key=%s", (topic_key,))
        topic_id = cur.fetchone()["id"]
        seen = []
        for r in routes:
            seen.append(r["slug"])
            cur.execute("SELECT id FROM entities WHERE place_id=%s AND topic_id=%s AND slug=%s", (place_id, topic_id, r["slug"]))
            ex = cur.fetchone()
            if ex:
                cur.execute("UPDATE entities SET name=%s, attributes=attributes || %s::jsonb, status='active', source_url=%s, source_id=COALESCE(%s, source_id), last_seen_at=%s, harvest_rule=%s WHERE id=%s",
                            (r["name"], json.dumps(r["attributes"]), source_url, source_id, now, rule_key, ex["id"]))
                updated += 1
            else:
                cur.execute("""INSERT INTO entities (institution_id, campus_id, topic_id, entity_type, name, slug, attributes, status, source_id, source_url, first_seen_at, last_seen_at, harvest_rule, place_id)
                               VALUES (NULL,NULL,%s,'bus_route',%s,%s,%s::jsonb,'active',%s,%s,%s,%s,%s,%s)""",
                            (topic_id, r["name"], r["slug"], json.dumps(r["attributes"]), source_id, source_url, now, now, rule_key, place_id))
                created += 1
        cur.execute("UPDATE entities SET status='inactive' WHERE place_id=%s AND topic_id=%s AND harvest_rule=%s AND status='active' AND NOT (slug = ANY(%s))", (place_id, topic_id, rule_key, seen or ["__none__"]))
        deactivated = cur.rowcount
        if source_id:
            cur.execute("UPDATE harvest_sources SET last_harvested_at=%s, last_count=%s WHERE source_id=%s", (now, len(routes), source_id))
            cur.execute("UPDATE source_registry SET last_fetched_at=%s, next_refresh_at=%s + make_interval(hours => refresh_interval_hours), health='healthy' WHERE id=%s", (now, now, source_id))
    conn.commit()
    return {"rule": rule_key, "entity_type": "bus_route", "found": len(routes), "created": created, "updated": updated, "deactivated": deactivated, "source_url": source_url}
