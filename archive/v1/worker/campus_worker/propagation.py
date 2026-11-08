"""Source-change propagation through dependency records (SPEC §08, §13, §28).

- register(): claim/source/entity/tool → page/page_version/tool/comparison edges.
- on_claim_changed(): finds every downstream output, flags pages `revalidation_required`, and
  enqueues idempotent `revalidate_page` jobs (one per page per upstream change).
- on_source_gone(): marks dependent claims stale and propagates.
- regression_guard(): if a collector run extracts zero claims across many pages that previously
  produced claims, stop propagation instead of blanking published content.
"""
from __future__ import annotations

import json
from uuid import UUID

import psycopg

from . import queue as q
from .types import JobRecord


def register(conn: psycopg.Connection, *, upstream_type: str, upstream_id: UUID, downstream_type: str, downstream_id: UUID) -> None:
    with conn.cursor() as cur:
        cur.execute(
            """INSERT INTO dependencies (upstream_type, upstream_id, downstream_type, downstream_id) VALUES (%s,%s,%s,%s)
               ON CONFLICT DO NOTHING""",
            (upstream_type, upstream_id, downstream_type, downstream_id),
        )
    conn.commit()


def downstream_of(conn: psycopg.Connection, upstream_type: str, upstream_id: UUID) -> list[dict]:
    with conn.cursor() as cur:
        cur.execute("SELECT downstream_type, downstream_id FROM dependencies WHERE upstream_type=%s AND upstream_id=%s", (upstream_type, upstream_id))
        return cur.fetchall()


def _page_ids_for(conn: psycopg.Connection, items: list[dict]) -> set[UUID]:
    pages: set[UUID] = set()
    with conn.cursor() as cur:
        for it in items:
            if it["downstream_type"] == "page":
                pages.add(it["downstream_id"])
            elif it["downstream_type"] == "page_version":
                cur.execute("SELECT page_id FROM page_versions WHERE id=%s", (it["downstream_id"],))
                r = cur.fetchone()
                if r:
                    pages.add(r["page_id"])
            elif it["downstream_type"] in ("tool_config", "comparison"):
                cur.execute("SELECT downstream_id FROM dependencies WHERE upstream_type='tool_config' AND upstream_id=%s AND downstream_type='page'", (it["downstream_id"],))
                pages.update(r["downstream_id"] for r in cur.fetchall())
    return pages


def on_claim_changed(conn: psycopg.Connection, old_claim_id: UUID, new_claim_id: UUID | None, *, reason: str) -> dict:
    """Flag affected pages and enqueue revalidation. The new claim inherits the old claim's edges."""
    items = downstream_of(conn, "claim", old_claim_id)
    pages = _page_ids_for(conn, items)
    enqueued = []
    with conn.cursor() as cur:
        for pid in pages:
            cur.execute("UPDATE pages SET revalidation_required=TRUE, revalidation_reason=%s WHERE id=%s", (reason, pid))
        if new_claim_id:
            for it in items:
                cur.execute(
                    """INSERT INTO dependencies (upstream_type, upstream_id, downstream_type, downstream_id) VALUES ('claim',%s,%s,%s)
                       ON CONFLICT DO NOTHING""",
                    (new_claim_id, it["downstream_type"], it["downstream_id"]),
                )
    conn.commit()
    for pid in pages:
        jid, created = q.enqueue(conn, JobRecord(job_type="revalidate_page", idempotency_key=f"revalidate:{pid}:{new_claim_id or old_claim_id}",
                                                 payload={"page_id": str(pid), "claim_id": str(new_claim_id or old_claim_id), "reason": reason}, priority=70))
        enqueued.append({"job_id": str(jid), "created": created, "page_id": str(pid)})
    return {"affected_pages": [str(p) for p in pages], "jobs": enqueued, "downstream": len(items)}


def on_source_gone(conn: psycopg.Connection, source_id: UUID) -> dict:
    from .claims import mark_stale_for_source

    stale = mark_stale_for_source(conn, source_id)
    results = [on_claim_changed(conn, cid, None, reason="source_gone") for cid in stale]
    with conn.cursor() as cur:
        cur.execute("UPDATE source_registry SET health='gone' WHERE id=%s", (source_id,))
    conn.commit()
    return {"stale_claims": [str(c) for c in stale], "propagations": results}


def regression_guard(conn: psycopg.Connection, *, source_ids: list[UUID], extracted_counts: dict[UUID, int], min_sources: int = 5) -> dict:
    """Return {'halt': bool, 'reason': ...}. Halts when ≥ min_sources sources that previously yielded
    claims now yield zero — a parser regression, not a world change."""
    if len(source_ids) < min_sources:
        return {"halt": False, "reason": "too few sources to judge"}
    with conn.cursor() as cur:
        cur.execute(
            """SELECT s.source_id, count(DISTINCT cs.claim_id) AS n FROM fetch_snapshots s JOIN claim_sources cs ON cs.snapshot_id=s.id
               WHERE s.source_id = ANY(%s) GROUP BY s.source_id""", (source_ids,))
        prior = {r["source_id"]: r["n"] for r in cur.fetchall()}
    regressed = [sid for sid in source_ids if prior.get(sid, 0) > 0 and extracted_counts.get(sid, 0) == 0]
    if len(regressed) >= min_sources or (prior and len(regressed) >= 0.8 * len([s for s in source_ids if prior.get(s, 0) > 0]) and len(regressed) >= 3):
        with conn.cursor() as cur:
            cur.execute(
                """INSERT INTO exceptions (severity, category, message, detail) VALUES ('critical','source',
                   'collector regression: zero claims across sources that previously produced claims; propagation halted', %s::jsonb)""",
                (json.dumps({"regressed": [str(s) for s in regressed]}),))
        conn.commit()
        return {"halt": True, "reason": "zero_fact_regression", "regressed": [str(s) for s in regressed]}
    return {"halt": False, "reason": "ok", "regressed": [str(s) for s in regressed]}
