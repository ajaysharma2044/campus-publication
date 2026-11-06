"""Cornell Class Roster API collector (continuous-local-run R46, R47; AT46).

Public JSON API: https://classes.cornell.edu/api/2.0 — rosters, subjects, classes with prerequisites and term offerings.
Registered as api_authorized (no credential). Courses are stored as entities (entity_type 'course', topic 'courses')
with source URL and date; prerequisite text and term go into attributes. Deterministic; fixture-tested.
"""
from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from uuid import UUID

import psycopg

from ..registry import slugify

BASE = "https://classes.cornell.edu/api/2.0"


class ClassRosterClient:
    def __init__(self, fetch_json=None):
        """fetch_json(url) -> dict. Default uses the safe fetcher's permission check + httpx; tests inject fixtures."""
        self._fetch = fetch_json or self._default_fetch

    @staticmethod
    def _default_fetch(url: str) -> dict:
        import httpx

        with httpx.Client(timeout=30.0, headers={"User-Agent": "CampusPublicationBot/0.1 (+editorial research)"}) as c:
            r = c.get(url)
            r.raise_for_status()
            return r.json()

    def rosters(self) -> list[dict]:
        return (self._fetch(f"{BASE}/config/rosters.json").get("data") or {}).get("rosters") or []

    def subjects(self, roster: str) -> list[dict]:
        return (self._fetch(f"{BASE}/config/subjects.json?roster={roster}").get("data") or {}).get("subjects") or []

    def classes(self, roster: str, subject: str) -> list[dict]:
        return (self._fetch(f"{BASE}/search/classes.json?roster={roster}&subject={subject}").get("data") or {}).get("classes") or []


def course_record(cls: dict, *, roster: str) -> dict:
    subject = cls.get("subject") or ""
    nbr = str(cls.get("catalogNbr") or "")
    groups = cls.get("enrollGroups") or []
    units = sorted({(g.get("unitsMinimum"), g.get("unitsMaximum")) for g in groups if g.get("unitsMinimum") is not None})
    sections = sum(len(g.get("classSections") or []) for g in groups)
    return {
        "name": f"{subject} {nbr}: {cls.get('titleLong') or cls.get('titleShort') or ''}".strip(": "),
        "slug": slugify(f"{subject}-{nbr}"),
        "attributes": {
            "subject": subject, "catalog_nbr": nbr, "title": cls.get("titleLong") or cls.get("titleShort"),
            "term": roster, "description": (cls.get("description") or "")[:1500],
            "prerequisites": (cls.get("catalogPrereqCoreq") or "").strip() or None,
            "when_offered": (cls.get("catalogWhenOffered") or "").strip() or None,
            "distribution": (cls.get("catalogDistr") or "").strip() or None,
            "units": [list(u) for u in units], "sections": sections,
            "crseId": cls.get("crseId"),
        },
    }


def store_courses(conn: psycopg.Connection, *, institution_id: UUID, roster: str, subject: str, classes: list[dict],
                  campus_id: UUID | None = None, now: datetime | None = None) -> dict:
    now = now or datetime.now(timezone.utc)
    url = f"{BASE}/search/classes.json?roster={roster}&subject={subject}"
    created = updated = 0
    with conn.cursor() as cur:
        cur.execute("SELECT id FROM topics WHERE key='courses'")
        topic_id = cur.fetchone()["id"]
        for cls in classes:
            rec = course_record(cls, roster=roster)
            cur.execute(
                """INSERT INTO entities (institution_id, campus_id, topic_id, entity_type, name, slug, attributes, status, source_url, first_seen_at, last_seen_at, harvest_rule)
                   VALUES (%s,%s,%s,'course',%s,%s,%s::jsonb,'active',%s,%s,%s,'class_roster_api')
                   ON CONFLICT (institution_id, topic_id, slug) DO UPDATE SET name=EXCLUDED.name,
                     attributes = entities.attributes || EXCLUDED.attributes, last_seen_at=EXCLUDED.last_seen_at, source_url=EXCLUDED.source_url
                   RETURNING (xmax = 0) AS inserted""",
                (institution_id, campus_id, topic_id, rec["name"], rec["slug"], json.dumps(rec["attributes"]), url, now, now),
            )
            if cur.fetchone()["inserted"]:
                created += 1
            else:
                updated += 1
    conn.commit()
    return {"roster": roster, "subject": subject, "created": created, "updated": updated, "source_url": url}


def harvest_subject(conn: psycopg.Connection, client: ClassRosterClient, *, institution_id: UUID, roster: str, subject: str) -> dict:
    return store_courses(conn, institution_id=institution_id, roster=roster, subject=subject, classes=client.classes(roster, subject))


def latest_roster(client: ClassRosterClient) -> str | None:
    rs = client.rosters()
    if not rs:
        return None
    # rosters are listed oldest → newest; prefer the last one whose status is published/active
    for r in reversed(rs):
        if (r.get("status") or "").lower() not in ("archived",):
            return r.get("slug")
    return rs[-1].get("slug")


_PREREQ_COURSE = re.compile(r"\b([A-Z]{2,6})\s?(\d{4})\b")


def prerequisite_course_codes(text: str | None) -> list[str]:
    """Deterministic extraction of course codes from a prerequisite sentence, for process graphs (R47)."""
    if not text:
        return []
    return sorted({f"{a} {b}" for a, b in _PREREQ_COURSE.findall(text)})
