"""Writer's brief builder (SPEC §16).

A brief is assembled deterministically from database state: the cluster (reader question), the
entity's current claims (evidence), the opportunity decision (contribution), and existing pages
(overlap). The planner role may refine wording, but the critical-claim list, unresolved facts and
overlap are facts from the database, not model output. A keyword list is never a brief.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from uuid import UUID

import psycopg

from .claims import blocking_claims, current_claims_for_entity


@dataclass
class Brief:
    institution_id: UUID
    campus_id: UUID | None
    cluster_id: UUID | None
    opportunity_id: UUID | None
    page_format: str
    audience: str
    reader_decision: str
    verified_answer: str
    unique_contribution: str
    critical_claim_ids: list[UUID]
    supporting_claim_ids: list[UUID]
    unresolved_facts: list[str]
    exceptions: list[str]
    structure: list[dict]
    allowed_subjective_evidence: list[str]
    next_tasks: list[str]
    overlap_page_ids: list[UUID]
    evidence_packet: list[dict] = field(default_factory=list)   # claims as the writer may see them (no secrets, no raw source text)
    blocked_by: list[str] = field(default_factory=list)

    @property
    def ready(self) -> bool:
        return not self.blocked_by


def format_claim_for_packet(c: dict) -> dict:
    """Public-safe claim view for the writer: typed value, scope, category; no excerpts."""
    val = None
    if c["value_type"] in ("money", "range_money"):
        val = {"amount_minor": int(c["value_number"]) if c["value_number"] is not None else None,
               "amount_high_minor": int(c["value_number_high"]) if c["value_number_high"] is not None else None,
               "currency": c["currency"], "billing_period": c["billing_period"], "price_basis": c["price_basis"]}
    elif c["value_type"] == "boolean":
        val = c["value_bool"]
    elif c["value_type"] in ("integer", "decimal", "duration"):
        val = float(c["value_number"]) if c["value_number"] is not None else None
    elif c["value_type"] == "date":
        val = c["value_date"].isoformat() if c["value_date"] else None
    else:
        val = c["value_text"]
    return {"claim_id": str(c["id"]), "field": c["field"], "value_type": c["value_type"], "value": val, "unit": c["unit"],
            "room_type": c["room_type"], "academic_year": c["academic_year"], "audience_applicability": list(c["audience_applicability"] or []),
            "evidence_category": c["evidence_category"], "is_critical": c["is_critical"], "conflict_status": c["conflict_status"],
            "effective_from": c["effective_from"].isoformat() if c["effective_from"] else None,
            "retrieved_at": c["retrieved_at"].isoformat()}


def build_entity_profile_brief(conn: psycopg.Connection, *, entity_id: UUID, audience: str = "first_year", cluster_id: UUID | None = None,
                               opportunity_id: UUID | None = None, required_fields: tuple[str, ...] = ("rate.room",),
                               optional_fields: tuple[str, ...] = ("amenity.air_conditioning", "amenity.kitchen", "eligibility.audience", "location.distance_note")) -> Brief:
    with conn.cursor() as cur:
        cur.execute("SELECT e.*, i.canonical_name, t.key AS topic_key FROM entities e JOIN institutions i ON i.id=e.institution_id JOIN topics t ON t.id=e.topic_id WHERE e.id=%s", (entity_id,))
        ent = cur.fetchone()
        if not ent:
            raise LookupError("entity not found")
        cur.execute("SELECT id, path FROM pages WHERE entity_id=%s AND status IN ('staged','published')", (entity_id,))
        overlap = [r["id"] for r in cur.fetchall()]
    claims = current_claims_for_entity(conn, entity_id)
    critical = [c for c in claims if c["is_critical"]]
    supporting = [c for c in claims if not c["is_critical"]]
    present_fields = {c["field"] for c in claims}
    unresolved = []
    blocked = []
    for f in required_fields:
        if f not in present_fields:
            blocked.append(f"missing_evidence:{f}")
    for f in optional_fields:
        if f not in present_fields:
            unresolved.append(f"{f}: unknown (no source found yet)")
    blocking = blocking_claims(conn, [c["id"] for c in critical])
    if blocking:
        blocked.append("critical_claims_conflicted_or_stale:" + ",".join(str(b["id"]) for b in blocking))
    not_applicable = [c["field"] for c in claims if c["evidence_category"] == "not_applicable"]
    years = sorted({c["academic_year"] for c in critical if c["academic_year"]}, reverse=True)
    rate_lines = []
    for c in critical:
        if c["field"] == "rate.room" and c["value_number"] is not None:
            rate_lines.append(f"{c['room_type']}: ${int(c['value_number']) / 100:,.0f} {c['billing_period'].replace('_', ' ')} {c['price_basis'].replace('_', ' ')} ({c['academic_year'] or 'year unknown'})")
    verified_answer = (f"{ent['name']} at {ent['canonical_name']}. Verified rates: " + "; ".join(rate_lines)) if rate_lines else f"{ent['name']}: rates not yet verified."
    structure = [
        {"heading": "The short answer", "purpose": "state the decision-relevant facts first: cost basis, who can live here, what is unknown", "claim_ids": [str(c["id"]) for c in critical]},
        {"heading": "What the room rate includes", "purpose": "billing period, per-person vs per-unit, what is excluded", "claim_ids": [str(c["id"]) for c in critical if c["field"].startswith("rate.")]},
        {"heading": "Building facts", "purpose": "fact table rendered from shared claims; unknowns shown as unknown", "claim_ids": [str(c["id"]) for c in supporting]},
        {"heading": "Tradeoffs", "purpose": "what this building optimises for versus comparable options, grounded in claims only"},
        {"heading": "What we could not verify", "purpose": "explicit list of unknowns and how to confirm with the institution"},
        {"heading": "Next steps", "purpose": "compare, calculate total cost, check eligibility"},
    ]
    return Brief(
        institution_id=ent["institution_id"], campus_id=ent["campus_id"], cluster_id=cluster_id, opportunity_id=opportunity_id,
        page_format="entity_profile", audience=audience,
        reader_decision=f"Should I choose {ent['name']} and what will it actually cost me for {years[0] if years else 'the coming year'}?",
        verified_answer=verified_answer,
        unique_contribution="One verified fact table per building with explicit billing period and per-person basis, explicit unknowns, and a link to equivalent-period comparison.",
        critical_claim_ids=[c["id"] for c in critical], supporting_claim_ids=[c["id"] for c in supporting],
        unresolved_facts=unresolved, exceptions=[f"not applicable: {f}" for f in not_applicable],
        structure=structure, allowed_subjective_evidence=[], next_tasks=["compare with a second building", "total-cost calculator", "eligibility check"],
        overlap_page_ids=overlap, evidence_packet=[format_claim_for_packet(c) for c in claims], blocked_by=blocked,
    )


def persist_brief(conn: psycopg.Connection, b: Brief) -> UUID:
    with conn.cursor() as cur:
        cur.execute(
            """INSERT INTO briefs (institution_id, campus_id, cluster_id, opportunity_id, page_format, audience, reader_decision, verified_answer,
               unique_contribution, critical_claim_ids, unresolved_facts, exceptions, structure, allowed_subjective_evidence, next_tasks, overlap_page_ids, status)
               VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s::jsonb,%s,%s,%s,%s) RETURNING id""",
            (b.institution_id, b.campus_id, b.cluster_id, b.opportunity_id, b.page_format, b.audience, b.reader_decision, b.verified_answer,
             b.unique_contribution, b.critical_claim_ids, b.unresolved_facts, b.exceptions, json.dumps(b.structure), b.allowed_subjective_evidence,
             b.next_tasks, b.overlap_page_ids, "approved" if b.ready else "draft"),
        )
        bid = cur.fetchone()["id"]
    conn.commit()
    return bid


def audience_guide_justified(conn: psycopg.Connection, *, entity_id: UUID | None, institution_id: UUID, topic_id: UUID, audience: str) -> tuple[bool, str]:
    """A separate audience guide is justified only when at least one current claim differs materially
    for that audience (eligibility/steps/cost) — SPEC §12, exercise 3."""
    with conn.cursor() as cur:
        cur.execute(
            """SELECT field, value_text, value_bool, value_number, audience_applicability FROM claims
               WHERE institution_id=%s AND topic_id=%s AND superseded_by_id IS NULL AND (entity_id=%s OR %s::uuid IS NULL)
               AND (field LIKE 'eligibility.%%' OR field LIKE 'deadline.%%' OR field LIKE 'process.%%' OR field LIKE 'rate.%%')""",
            (institution_id, topic_id, entity_id, entity_id),
        )
        rows = cur.fetchall()
    aud_specific = [r for r in rows if audience in (r["audience_applicability"] or [])]
    general = [r for r in rows if not r["audience_applicability"]]
    if not aud_specific:
        return False, f"no {audience}-specific eligibility, deadline, process or rate claims exist; improve the general page instead"
    differing = []
    for a in aud_specific:
        g = next((x for x in general if x["field"] == a["field"]), None)
        if g is None or (g["value_text"], g["value_bool"], g["value_number"]) != (a["value_text"], a["value_bool"], a["value_number"]):
            differing.append(a["field"])
    if differing:
        return True, f"{audience} rules differ on: {', '.join(sorted(set(differing)))}"
    return False, f"{audience}-scoped claims exist but match the general rules; no separate guide"
