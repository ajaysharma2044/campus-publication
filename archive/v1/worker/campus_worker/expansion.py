"""Sequential multi-school expansion (continuous-local-run R43; AT42).

Expansion starts automatically once the Cornell + Ithaca opportunity map is complete AND 10 pages have passed the
competitor-beat review. Schools come from CAMPUS_EXPANSION_LIST (comma-separated) or the default order below, one at a
time: onboarding (school_config), IPEDS identity verification, then a sweep (R41), then production. The school after
the one in progress waits.
"""
from __future__ import annotations

import os
from dataclasses import dataclass
from uuid import UUID

import psycopg

from . import sweep
from .registry import disambiguate

DEFAULT_ORDER = ["Northwestern University", "Columbia University in the City of New York", "University of Virginia-Main Campus", "University of Michigan-Ann Arbor",
                 "University of Pennsylvania", "University of Southern California", "New York University", "University of California-Berkeley", "University of California-Los Angeles",
                 "Georgetown University", "Duke University", "Vanderbilt University", "University of Notre Dame", "Emory University", "University of North Carolina at Chapel Hill",
                 "Georgia Institute of Technology-Main Campus", "The University of Texas at Austin", "Carnegie Mellon University", "Boston College", "Rice University", "Tufts University",
                 "Washington University in St Louis", "Brown University", "Dartmouth College"]
MIN_BEAT_REVIEW_PASSES = 10


@dataclass
class Readiness:
    ready: bool
    map_complete: bool
    beat_review_passes: int
    in_progress: str | None
    reason: str


def expansion_list() -> list[str]:
    raw = os.environ.get("CAMPUS_EXPANSION_LIST", "").strip()
    return [s.strip() for s in raw.split(",") if s.strip()] if raw else list(DEFAULT_ORDER)


def beat_review_passes(conn: psycopg.Connection) -> int:
    with conn.cursor() as cur:
        cur.execute("SELECT count(*) AS n FROM page_versions WHERE (beat_review->>'passed')::boolean IS TRUE")
        return int(cur.fetchone()["n"])


def in_progress_school(conn: psycopg.Connection) -> dict | None:
    with conn.cursor() as cur:
        cur.execute("""SELECT i.id, i.canonical_name, i.identity_status, sc.coverage_status FROM school_configs sc JOIN institutions i ON i.id=sc.institution_id
                       WHERE sc.coverage_status IN ('onboarding') AND i.identity_status <> 'synthetic_fixture' ORDER BY sc.created_at LIMIT 1""")
        r = cur.fetchone()
    return dict(r) if r else None


def readiness(conn: psycopg.Connection, *, map_complete: bool | None = None) -> Readiness:
    mc = sweep.status(conn)["complete"] if map_complete is None else map_complete
    passes = beat_review_passes(conn)
    ip = in_progress_school(conn)
    if ip:
        return Readiness(False, mc, passes, ip["canonical_name"], f"{ip['canonical_name']} is still onboarding/sweeping; the next school waits (sequential, R43)")
    if not mc:
        return Readiness(False, mc, passes, None, "opportunity map not complete yet")
    if passes < MIN_BEAT_REVIEW_PASSES:
        return Readiness(False, mc, passes, None, f"{passes} pages passed the competitor-beat review; need {MIN_BEAT_REVIEW_PASSES}")
    return Readiness(True, mc, passes, None, "map complete and 10 pages passed the beat review")


def next_school(conn: psycopg.Connection) -> dict | None:
    """First school in the list that has no school_config yet; resolved through the registry (never by name alone)."""
    with conn.cursor() as cur:
        cur.execute("SELECT i.canonical_name FROM school_configs sc JOIN institutions i ON i.id=sc.institution_id")
        done = {r["canonical_name"].lower() for r in cur.fetchall()}
    for name in expansion_list():
        if name.lower() in done:
            continue
        cands = [c for c in disambiguate(conn, name) if not c["is_system"]]
        exact = [c for c in cands if c["canonical_name"].lower() == name.lower()]
        if len(exact) == 1:
            return {"name": name, "institution_id": exact[0]["id"], "candidates": len(cands)}
        return {"name": name, "institution_id": None, "candidates": len(cands), "hold": "identity ambiguous or missing in the registry; owner must resolve by UNITID"}
    return None


def onboard(conn: psycopg.Connection, institution_id: UUID, *, verify_with_checksum: str | None = None) -> dict:
    """Create the school_config (onboarding) and record identity verification when an NCES checksum is supplied."""
    with conn.cursor() as cur:
        cur.execute("SELECT id FROM campuses WHERE institution_id=%s AND is_main LIMIT 1", (institution_id,))
        c = cur.fetchone()
        campus_id = c["id"] if c else None
        if campus_id is None:
            cur.execute("INSERT INTO campuses (institution_id, name, slug, is_main, status) VALUES (%s,'Main campus','main',TRUE,'active') RETURNING id", (institution_id,))
            campus_id = cur.fetchone()["id"]
        cur.execute("""INSERT INTO school_configs (institution_id, campus_id, coverage_status, audiences) VALUES (%s,%s,'onboarding','{prospective_transfer,undergrad}')
                       ON CONFLICT (institution_id, campus_id) DO UPDATE SET coverage_status='onboarding' RETURNING id""", (institution_id, campus_id))
        cfg = cur.fetchone()["id"]
        if verify_with_checksum:
            cur.execute("UPDATE institutions SET identity_status='verified', notes=COALESCE(notes,'') || %s, updated_at=now() WHERE id=%s",
                        (f" | NCES HD release verified sha256={verify_with_checksum}", institution_id))
    conn.commit()
    return {"school_config_id": str(cfg), "campus_id": str(campus_id), "verified": bool(verify_with_checksum)}


def step(conn: psycopg.Connection, *, map_complete: bool | None = None, verify_with_checksum: str | None = None, run_sweep=None) -> dict:
    """One expansion step: if ready, onboard + verify + sweep the next school; otherwise report why not."""
    r = readiness(conn, map_complete=map_complete)
    if not r.ready:
        return {"expanded": False, "readiness": r.__dict__}
    nxt = next_school(conn)
    if not nxt:
        return {"expanded": False, "readiness": r.__dict__, "reason": "expansion list exhausted"}
    if not nxt.get("institution_id"):
        return {"expanded": False, "readiness": r.__dict__, "next": nxt}
    ob = onboard(conn, nxt["institution_id"], verify_with_checksum=verify_with_checksum)
    sw = (run_sweep or (lambda c, iid: sweep.next_step(c)))(conn, nxt["institution_id"])
    return {"expanded": True, "school": nxt["name"], "institution_id": str(nxt["institution_id"]), "onboarding": ob, "sweep": sw, "readiness": r.__dict__}


def mark_active(conn: psycopg.Connection, institution_id: UUID) -> None:
    """Called when a school's sweep completes: production may start and the next school becomes eligible."""
    with conn.cursor() as cur:
        cur.execute("UPDATE school_configs SET coverage_status='active', updated_at=now() WHERE institution_id=%s", (institution_id,))
    conn.commit()
