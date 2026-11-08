"""Shared helpers for tests: create a synthetic institution/campus/entity quickly."""
from datetime import datetime, timezone
from uuid import UUID

from campus_worker import permissions


def make_school(conn, *, name="Fixture State University", slug="fixture-state", itype="university", unitid="900001"):
    permissions.seed_defaults(conn)
    with conn.cursor() as cur:
        cur.execute("INSERT INTO institutions (canonical_name, slug, institution_type, identity_status) VALUES (%s,%s,%s,'synthetic_fixture') RETURNING id", (name, slug, itype))
        inst = cur.fetchone()["id"]
        cur.execute("INSERT INTO institution_external_ids (institution_id, system_name, external_id) VALUES (%s,'ipeds_unitid',%s)", (inst, unitid))
        cur.execute("INSERT INTO campuses (institution_id, name, slug, is_main, status) VALUES (%s,'Main','main',TRUE,'synthetic_fixture') RETURNING id", (inst,))
        campus = cur.fetchone()["id"]
        cur.execute("SELECT id, key FROM topics")
        topics = {r["key"]: r["id"] for r in cur.fetchall()}
        cur.execute("INSERT INTO source_permissions (domain_pattern, publisher, connector, access_mode, permission_state, retention_policy, rate_limit_per_minute) VALUES ('*.example.edu','Fixture','official_html','public_http','allowed','excerpts_only',600) ON CONFLICT DO NOTHING")
    conn.commit()
    return inst, campus, topics


def make_entity(conn, inst, campus, topic_id, *, name="Fixture Hall", slug="fixture-hall", etype="residence_hall"):
    with conn.cursor() as cur:
        cur.execute("INSERT INTO entities (institution_id, campus_id, topic_id, entity_type, name, slug, status) VALUES (%s,%s,%s,%s,%s,%s,'synthetic_fixture') RETURNING id",
                    (inst, campus, topic_id, etype, name, slug))
        eid = cur.fetchone()["id"]
    conn.commit()
    return eid


def make_source(conn, inst, campus, url, *, family=None, kind="official_html"):
    from campus_worker.collectors.html import register_source
    return register_source(conn, canonical_url=url, institution_id=inst, campus_id=campus, source_kind=kind, publisher="Fixture", source_family=family)


def make_snapshot(conn, source_id, *, content_hash="h"):
    from campus_worker.collectors.html import record_snapshot
    return record_snapshot(conn, source_id, final_url="x", status=200, content_type="text/html", content_hash=content_hash, raw_hash=None,
                           byte_size=1, etag=None, last_modified=None, confidence=0.9, retained_text=None, retained_tables=None,
                           material_change=None, outcome="ok")


NOW = datetime(2026, 11, 2, 12, 0, tzinfo=timezone.utc)
