"""Process navigator (continuous-local-run R47): pick where you are and where you want to go; see the exact steps,
requirements, deadlines and offices, rendered from the process graph. Deterministic; no doorway pages.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from uuid import UUID

import psycopg

from ..processes import effective_rules


@dataclass
class Answer:
    found: bool
    path_nodes: list[dict] = field(default_factory=list)      # L1 (+ L2/L3 that apply) in order
    steps: list[str] = field(default_factory=list)
    prerequisites: list[str] = field(default_factory=list)
    course_requirements: list[str] = field(default_factory=list)
    gpa_min: str | None = None
    deadlines: list[str] = field(default_factory=list)
    forms: list[str] = field(default_factory=list)
    offices: list[str] = field(default_factory=list)
    exceptions: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)
    source_urls: list[str] = field(default_factory=list)
    claim_ids: list[str] = field(default_factory=list)
    message: str | None = None


def options(conn: psycopg.Connection, graph_id: UUID) -> dict:
    with conn.cursor() as cur:
        cur.execute("SELECT DISTINCT from_state FROM process_nodes WHERE graph_id=%s AND layer=1 AND from_state IS NOT NULL ORDER BY 1", (graph_id,))
        froms = [r["from_state"] for r in cur.fetchall()]
        cur.execute("SELECT DISTINCT to_state FROM process_nodes WHERE graph_id=%s AND layer=1 AND to_state IS NOT NULL ORDER BY 1", (graph_id,))
        tos = [r["to_state"] for r in cur.fetchall()]
        cur.execute("SELECT DISTINCT situation FROM process_nodes WHERE graph_id=%s AND layer IN (2,3) AND situation IS NOT NULL ORDER BY 1", (graph_id,))
        sits = [r["situation"] for r in cur.fetchall()]
    return {"from_states": froms, "to_states": tos, "situations": sits}


def answer(conn: psycopg.Connection, graph_id: UUID, *, from_state: str, to_state: str, situations: list[str] | None = None, major: str | None = None) -> Answer:
    """Resolve the L1 transition, then layer on every L2/L3 node whose situation/major matches."""
    situations = [s.lower() for s in (situations or [])]
    with conn.cursor() as cur:
        cur.execute("SELECT id, key, label, source_urls FROM process_nodes WHERE graph_id=%s AND layer=1 AND lower(from_state)=lower(%s) AND lower(to_state)=lower(%s)", (graph_id, from_state, to_state))
        l1 = cur.fetchone()
        if not l1:
            cur.execute("SELECT count(*) AS n FROM process_nodes WHERE graph_id=%s AND layer=1", (graph_id,))
            return Answer(False, message=f"No documented path from {from_state} to {to_state} on the official pages we hold ({cur.fetchone()['n']} documented transitions). Ask the receiving college's advising office.")
        cur.execute("""WITH RECURSIVE sub AS (SELECT * FROM process_nodes WHERE parent_id=%s UNION ALL SELECT n.* FROM process_nodes n JOIN sub ON n.parent_id=sub.id)
                       SELECT id, key, label, layer, situation, source_urls FROM sub ORDER BY layer, key""", (l1["id"],))
        children = [dict(r) for r in cur.fetchall()]
    applicable = [l1]
    for c in children:
        sit = (c.get("situation") or "").lower()
        if sit and (sit in situations or (major and major.lower() in sit)):
            applicable.append(c)
    a = Answer(True, path_nodes=[{"key": n["key"], "label": n["label"]} for n in applicable])
    merged: dict = {}
    urls: list[str] = []
    claims: list[str] = []
    with conn.cursor() as cur:
        for n in applicable:
            merged.update(effective_rules(conn, n["id"]))
            urls += [u for u in (n.get("source_urls") or []) if u not in urls]
            cur.execute("SELECT claim_id FROM process_node_claims WHERE node_id=%s", (n["id"],))
            claims += [str(r["claim_id"]) for r in cur.fetchall()]
    a.steps = list(merged.get("steps") or [])
    a.prerequisites = list(merged.get("prerequisites") or [])
    a.course_requirements = list(merged.get("course_requirements") or [])
    a.gpa_min = merged.get("gpa_min")
    a.deadlines = list(merged.get("deadlines") or [])
    a.forms = list(merged.get("forms") or [])
    a.offices = list(merged.get("offices") or [])
    a.exceptions = list(merged.get("exceptions") or [])
    a.notes = list(merged.get("notes") or [])
    a.source_urls = urls
    a.claim_ids = sorted(set(claims))
    return a


def as_dict(a: Answer) -> dict:
    return a.__dict__.copy()
