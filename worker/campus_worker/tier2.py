"""Tier-2 data profiles (continuous-local-run R42; AT41).

One page per real entity, rendered deterministically from verified claims through the entity_profile template with a
short model-written intro and tradeoffs section. A profile may publish only when ALL hold:
  - the entity has at least 6 verified claims of its own (verified_fact, current, no open conflict)
  - at least 1 observed query targets that entity
  - its fact table shares less than 60% of rows with any other published page (computed here)
  - it passes the existing gates
Comparison pages ("X vs Y") only for pairs with an observed query — never all combinations.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import UUID

import psycopg

from .editorial import checks, gates
from .registry import slugify

MIN_VERIFIED_CLAIMS = 6
MAX_OVERLAP = 0.60


@dataclass
class Eligibility:
    entity_id: UUID
    eligible: bool
    verified_claims: int
    observed_queries: int
    max_overlap: float
    overlap_with: str | None
    reasons: list[str] = field(default_factory=list)


def verified_claims(conn: psycopg.Connection, entity_id: UUID) -> list[dict]:
    with conn.cursor() as cur:
        cur.execute("""SELECT * FROM claims WHERE entity_id=%s AND superseded_by_id IS NULL AND evidence_category='verified_fact' AND conflict_status<>'open'
                       ORDER BY field, room_type, academic_year DESC""", (entity_id,))
        return [dict(r) for r in cur.fetchall()]


def observed_queries(conn: psycopg.Connection, entity_id: UUID) -> int:
    with conn.cursor() as cur:
        cur.execute("SELECT count(DISTINCT COALESCE(source_ref, id::text)) AS n FROM questions WHERE entity_id=%s AND NOT is_hypothesis", (entity_id,))
        return int(cur.fetchone()["n"])


def _display_value(c: dict) -> str:
    if c["value_type"] == "money" and c["value_number"] is not None:
        amt = int(c["value_number"]) / 100
        per = {"per_academic_year": "per academic year", "per_semester": "per semester", "per_month": "per month", "one_time": "one-time", "per_year": "per year"}.get(c.get("billing_period") or "", c.get("billing_period") or "")
        basis = {"per_person": "per person", "per_unit": "per unit", "per_bed": "per bed"}.get(c.get("price_basis") or "", "")
        return f"${amt:,.0f} {per} {basis}".strip()
    if c["value_type"] == "boolean":
        return "Yes" if c["value_bool"] else "No"
    if c["value_type"] == "date" and c["value_date"]:
        return c["value_date"].isoformat()
    if c["value_number"] is not None:
        return f"{c['value_number']} {c.get('unit') or ''}".strip()
    return c.get("value_text") or "Unknown"


def fact_rows(claims_: list[dict]) -> list[dict]:
    rows = []
    for c in claims_:
        label = c["field"].replace(".", " ").replace("_", " ")
        if c.get("room_type"):
            label += f" ({c['room_type']})"
        if c.get("academic_year"):
            label += f", {c['academic_year']}"
        rows.append({"label": label[:1].upper() + label[1:], "value": _display_value(c), "status": "verified", "verified_at": c["retrieved_at"].isoformat() if c.get("retrieved_at") else None, "claim_id": str(c["id"]),
                     "numeric": c["value_type"] in ("money", "integer", "decimal"), "row_key": f"{c['field']}|{c.get('room_type') or ''}|{c.get('academic_year') or ''}|{_display_value(c)}"})
    return rows


def overlap_with_published(conn: psycopg.Connection, rows: list[dict], *, exclude_page_id: UUID | None = None) -> tuple[float, str | None]:
    """Share of this fact table's rows that also appear in any other published/staged page's fact table."""
    keys = {r["row_key"] for r in rows}
    if not keys:
        return 0.0, None
    worst, worst_path = 0.0, None
    with conn.cursor() as cur:
        cur.execute("""SELECT p.id, p.path, v.structured FROM pages p JOIN page_versions v ON v.id=p.current_version_id
                       WHERE p.status IN ('staged','published') AND (%s::uuid IS NULL OR p.id<>%s)""", (exclude_page_id, exclude_page_id))
        for r in cur.fetchall():
            other = {x.get("row_key") for x in (r["structured"] or {}).get("fact_table", []) if x.get("row_key")}
            if not other:
                continue
            share = len(keys & other) / len(keys)
            if share > worst:
                worst, worst_path = share, r["path"]
    return round(worst, 3), worst_path


def eligibility(conn: psycopg.Connection, entity_id: UUID, *, exclude_page_id: UUID | None = None) -> Eligibility:
    cl = verified_claims(conn, entity_id)
    oq = observed_queries(conn, entity_id)
    ov, ov_path = overlap_with_published(conn, fact_rows(cl), exclude_page_id=exclude_page_id)
    reasons = []
    if len(cl) < MIN_VERIFIED_CLAIMS:
        reasons.append(f"{len(cl)} verified claims < {MIN_VERIFIED_CLAIMS}")
    if oq < 1:
        reasons.append("no observed query targets this entity")
    if ov >= MAX_OVERLAP:
        reasons.append(f"fact table overlaps {ov:.0%} with {ov_path} (limit {MAX_OVERLAP:.0%})")
    return Eligibility(entity_id, not reasons, len(cl), oq, ov, ov_path, reasons)


def build_profile(conn: psycopg.Connection, entity_id: UUID, *, intro_md: str, tradeoffs_md: str, rubric: dict | None, headline: str | None = None,
                  deck: str | None = None, byline: str = "Publication desk", primary_query: str | None = None) -> dict:
    """Create (or refresh) the tier-2 page + version for an entity and run the gates. Publishing is the publisher's job."""
    with conn.cursor() as cur:
        cur.execute("""SELECT e.*, i.slug AS school_slug, p.slug AS place_slug, t.key AS topic_key, i.canonical_name AS school_name FROM entities e
                       LEFT JOIN institutions i ON i.id=e.institution_id LEFT JOIN places p ON p.id=e.place_id JOIN topics t ON t.id=e.topic_id WHERE e.id=%s""", (entity_id,))
        e = cur.fetchone()
    if not e:
        raise LookupError("entity not found")
    el = eligibility(conn, entity_id)
    if not el.eligible:
        return {"entity_id": str(entity_id), "built": False, "reasons": el.reasons, "eligibility": el.__dict__}
    cl = verified_claims(conn, entity_id)
    rows = fact_rows(cl)
    scope = f"/schools/{e['school_slug']}" if e["school_slug"] else f"/towns/{e['place_slug']}"
    topic_slug = e["topic_key"].replace("_", "-")  # URL policy: lowercase, hyphenated (R45)
    path = f"{scope}/{topic_slug}/{e['slug']}/"
    headline = headline or f"{e['name']}: verified facts"
    body = f"{intro_md.strip()}\n\n## Facts\n\n[[fact-table]]\n\n## Tradeoffs\n\n{tradeoffs_md.strip()}\n\n## What we could not verify\n\nAnything not in the table above has no verified source yet. Unknown is a value, not a no.\n"
    with conn.cursor() as cur:
        cur.execute("""INSERT INTO pages (institution_id, campus_id, topic_id, entity_id, page_format, slug, path, audience, status, tier, place_id, primary_query)
                       VALUES (%s,%s,%s,%s,'entity_profile',%s,%s,NULL,'drafting',2,%s,%s)
                       ON CONFLICT (path) DO UPDATE SET status=CASE WHEN pages.status IN ('published','staged') THEN pages.status ELSE 'drafting' END, tier=2, primary_query=COALESCE(EXCLUDED.primary_query, pages.primary_query) RETURNING id""",
                    (e["institution_id"], e["campus_id"], e["topic_id"], entity_id, e["slug"], path, e["place_id"], primary_query))
        pid = cur.fetchone()["id"]
    conn.commit()
    hub = f"{scope}/{topic_slug}/"
    next_actions = [{"text": f"See every {e['topic_key'].replace('_', ' ')} entry for {e.get('school_name') or e.get('place_slug') or 'this scope'}", "target": hub}]
    structured = {"fact_table": rows, "fact_table_caption": f"{e['name']} — verified facts", "fact_table_footnote": "Every row is a verified claim with a primary source; unknown means no verified source states it.",
                  "claim_refs": [str(c["id"]) for c in cl], "next_actions": next_actions, "tier": 2}
    vid = gates.create_version(conn, pid, brief_id=None, headline=headline, deck=deck or f"Verified facts about {e['name']}, with sources.", body_md=body, body_html=None, structured=structured,
                               byline=byline, production_note="Tier-2 data profile rendered from verified claims; the intro and tradeoffs are model-written from those claims only (R42).",
                               claim_ids=[c["id"] for c in cl], writer_model="tier2:deterministic", editor_model=None, verifier_model=None, change_summary="tier-2 profile")
    det = checks.run_all(headline=headline, deck=deck or "", body_md=body, byline=byline, fact_table=rows, body_claim_ids=[str(c["id"]) for c in cl],
                         critical_ids=[str(c["id"]) for c in cl if c["is_critical"]], approved_ids={str(c["id"]) for c in cl}, institution_name=e.get("school_name") or "",
                         other_institution_names=[], academic_year=next((c["academic_year"] for c in cl if c.get("academic_year")), None), next_actions=next_actions, existing_bodies=[])
    gate = gates.gate_version(conn, vid, det, rubric)
    return {"entity_id": str(entity_id), "built": True, "page_id": str(pid), "version_id": str(vid), "path": path, "gate": gate.as_dict(), "eligibility": el.__dict__, "rows": len(rows)}


def comparison_pairs_with_demand(conn: psycopg.Connection, *, institution_id: UUID | None = None, place_id: UUID | None = None) -> list[dict]:
    """Entity pairs that have an OBSERVED 'X vs Y' question (never all combinations)."""
    scope_sql, scope_id = ("q.institution_id=%s", institution_id) if institution_id else ("q.place_id=%s", place_id)
    with conn.cursor() as cur:
        cur.execute(f"SELECT DISTINCT raw_text FROM questions q WHERE {scope_sql} AND NOT is_hypothesis AND lower(raw_text) LIKE '%% vs %%'", (scope_id,))
        texts = [r["raw_text"] for r in cur.fetchall()]
        scope_e, scope_eid = ("institution_id=%s", institution_id) if institution_id else ("place_id=%s", place_id)
        cur.execute(f"SELECT id, name, slug, entity_type FROM entities WHERE {scope_e} AND status IN ('active','synthetic_fixture')", (scope_eid,))
        ents = [dict(r) for r in cur.fetchall()]
    pairs = []
    for t in texts:
        left, _, right = t.lower().partition(" vs ")
        a = next((e for e in ents if e["name"].lower() in left), None)
        b = next((e for e in ents if e["name"].lower() in right), None)
        if a and b and a["id"] != b["id"] and a["entity_type"] == b["entity_type"]:
            key = tuple(sorted([a["slug"], b["slug"]]))
            if key not in {tuple(sorted([p["a"]["slug"], p["b"]["slug"]])) for p in pairs}:
                pairs.append({"a": a, "b": b, "query": t, "path": f"compare/{key[0]}-vs-{key[1]}/"})
    return pairs
