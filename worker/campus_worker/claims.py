"""Claim store: typed atomic claims, provenance, supersession and conflicts (SPEC §13).

Rules enforced here:
- A claim is scoped by institution, campus, entity, field, academic_year, room_type, audience.
- Storing a new claim for the same scope supersedes the previous one only when it comes from the
  same source family or a more specific/newer effective date; otherwise an open conflict is
  recorded and BOTH claims are marked `conflicted`. Critical conflicts block publication.
- Nothing here resolves a conflict automatically. resolve_conflict() records a human/role decision.
- Deterministic extraction from retained tables for housing rates lives in extract_rate_table().
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from uuid import UUID

import psycopg

from .collectors.pdf import find_academic_years, parse_money_minor
from .types import ClaimRecord

CRITICAL_FIELD_PREFIXES = ("rate.", "cost.", "fee.", "deadline.", "eligibility.", "prerequisite.", "agreement.", "accessibility.", "route.")


def is_critical_field(field: str) -> bool:
    return field.startswith(CRITICAL_FIELD_PREFIXES)


def _scope_key(c: ClaimRecord) -> tuple:
    return (str(c.institution_id), str(c.campus_id), str(c.entity_id), c.field, c.academic_year, c.room_type,
            tuple(sorted(c.audience_applicability)), c.billing_period, c.price_basis)


def _values_equal(a: dict, b: ClaimRecord) -> bool:
    if a["value_type"] != b.value_type:
        return False
    if b.value_type in ("money", "integer", "decimal", "range_money", "duration"):
        return (a["value_number"] is not None and b.value_number is not None and float(a["value_number"]) == float(b.value_number)
                and (a["value_number_high"] is None) == (b.value_number_high is None)
                and (a["value_number_high"] is None or float(a["value_number_high"]) == float(b.value_number_high)))
    if b.value_type == "boolean":
        return a["value_bool"] == b.value_bool
    if b.value_type == "date":
        return a["value_date"] == b.value_date
    return (a["value_text"] or "").strip().lower() == (b.value_text or "").strip().lower()


def _insert_claim(cur, c: ClaimRecord, evidence_category: str | None = None) -> UUID:
    cur.execute(
        """INSERT INTO claims (institution_id, campus_id, entity_id, topic_id, field, value_type, value_text, value_number,
           value_number_high, value_bool, value_date, unit, currency, billing_period, price_basis, room_type, audience_applicability,
           academic_year, term, effective_from, effective_to, evidence_category, is_critical, extraction_method, extraction_model,
           extraction_confidence, retrieved_at, verification_due_at)
           VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) RETURNING id""",
        (c.institution_id, c.campus_id, c.entity_id, c.topic_id, c.field, c.value_type, c.value_text, c.value_number,
         c.value_number_high, c.value_bool, c.value_date, c.unit, c.currency, c.billing_period, c.price_basis, c.room_type,
         c.audience_applicability, c.academic_year, c.term, c.effective_from, c.effective_to,
         evidence_category or c.evidence_category, c.is_critical or is_critical_field(c.field), c.extraction_method,
         c.extraction_model, c.extraction_confidence, c.retrieved_at,
         c.verification_due_at or (c.retrieved_at + timedelta(days=90))),
    )
    return cur.fetchone()["id"]


@dataclass
class StoreResult:
    claim_id: UUID
    action: str          # 'created' | 'confirmed' | 'superseded' | 'conflict'
    conflict_id: UUID | None = None
    superseded_id: UUID | None = None


def store_claim(conn: psycopg.Connection, c: ClaimRecord, *, snapshot_id: UUID | None, excerpt: str | None = None,
                locator: str | None = None, source_family: str | None = None) -> StoreResult:
    with conn.cursor() as cur:
        cur.execute(
            """SELECT c.*, (SELECT array_agg(DISTINCT r.source_family) FROM claim_sources cs JOIN fetch_snapshots s ON s.id=cs.snapshot_id
                       JOIN source_registry r ON r.id=s.source_id WHERE cs.claim_id=c.id) AS families
               FROM claims c WHERE c.institution_id=%s AND c.campus_id IS NOT DISTINCT FROM %s AND c.entity_id IS NOT DISTINCT FROM %s
               AND c.field=%s AND c.academic_year IS NOT DISTINCT FROM %s AND c.room_type IS NOT DISTINCT FROM %s
               AND c.audience_applicability=%s AND c.billing_period IS NOT DISTINCT FROM %s AND c.price_basis IS NOT DISTINCT FROM %s
               AND c.superseded_by_id IS NULL ORDER BY c.retrieved_at DESC""",
            (c.institution_id, c.campus_id, c.entity_id, c.field, c.academic_year, c.room_type, c.audience_applicability,
             c.billing_period, c.price_basis),
        )
        existing = cur.fetchall()
        if not existing:
            cid = _insert_claim(cur, c)
            _link(cur, cid, snapshot_id, excerpt, locator)
            conn.commit()
            return StoreResult(cid, "created")
        current = existing[0]
        weak_current = current["evidence_category"] in ("estimate", "unknown") and current["conflict_status"] != "open"
        if _values_equal(current, c):
            # same value from another source: add provenance, refresh retrieved_at/verification due
            _link(cur, current["id"], snapshot_id, excerpt, locator)
            cur.execute("UPDATE claims SET retrieved_at=GREATEST(retrieved_at,%s), verification_due_at=%s WHERE id=%s",
                        (c.retrieved_at, c.retrieved_at + timedelta(days=90), current["id"]))
            if weak_current and c.evidence_category == "verified_fact":
                # an opened primary source confirms a snippet estimate: the claim is now verified (continuous-local-run S4)
                cur.execute("UPDATE claims SET evidence_category='verified_fact', extraction_method=%s, extraction_model=%s, extraction_confidence=%s WHERE id=%s",
                            (c.extraction_method, c.extraction_model, c.extraction_confidence, current["id"]))
                conn.commit()
                return StoreResult(current["id"], "verified")
            conn.commit()
            return StoreResult(current["id"], "confirmed")
        same_family = source_family is not None and current["families"] and source_family in (current["families"] or [])
        newer_effective = (c.effective_from is not None and current["effective_from"] is not None and c.effective_from > current["effective_from"])
        # an opened primary source beats a snippet estimate outright: supersede, never a conflict between a guess and a fact
        if same_family or newer_effective or (weak_current and c.evidence_category == "verified_fact"):
            cid = _insert_claim(cur, c)
            _link(cur, cid, snapshot_id, excerpt, locator)
            cur.execute("UPDATE claims SET superseded_by_id=%s, evidence_category=CASE WHEN evidence_category='verified_fact' THEN 'stale' ELSE evidence_category END WHERE id=%s", (cid, current["id"]))
            conn.commit()
            return StoreResult(cid, "superseded", superseded_id=current["id"])
        # Different value, different source family, same scope: conflict. Neither wins silently.
        cid = _insert_claim(cur, c, evidence_category="conflicted")
        _link(cur, cid, snapshot_id, excerpt, locator)
        cur.execute("UPDATE claims SET evidence_category='conflicted', conflict_status='open' WHERE id=%s", (current["id"],))
        cur.execute("UPDATE claims SET conflict_status='open' WHERE id=%s", (cid,))
        cur.execute(
            """INSERT INTO conflicts (institution_id, claim_a_id, claim_b_id, conflict_type) VALUES (%s,%s,%s,'value') RETURNING id""",
            (c.institution_id, current["id"], cid),
        )
        conflict_id = cur.fetchone()["id"]
        conn.commit()
        return StoreResult(cid, "conflict", conflict_id=conflict_id)


def _link(cur, claim_id: UUID, snapshot_id: UUID | None, excerpt: str | None, locator: str | None) -> None:
    if snapshot_id is None:
        return
    cur.execute(
        """INSERT INTO claim_sources (claim_id, snapshot_id, excerpt, locator) VALUES (%s,%s,%s,%s)
           ON CONFLICT DO NOTHING""",
        (claim_id, snapshot_id, (excerpt or "")[:1000] or None, locator),
    )


def resolve_conflict(conn: psycopg.Connection, conflict_id: UUID, *, winner_claim_id: UUID | None, resolution: str, scoped_unresolved: bool = False) -> None:
    """Record a resolution. If winner is given, the loser is superseded and the winner restored to
    verified_fact. If scoped_unresolved, both stay visible as 'conflicted' but the page may state the
    discrepancy explicitly."""
    with conn.cursor() as cur:
        cur.execute("SELECT claim_a_id, claim_b_id FROM conflicts WHERE id=%s", (conflict_id,))
        c = cur.fetchone()
        if scoped_unresolved:
            cur.execute("UPDATE conflicts SET status='scoped_unresolved', resolution=%s, resolved_at=now() WHERE id=%s", (resolution, conflict_id))
            cur.execute("UPDATE claims SET conflict_status='scoped_unresolved' WHERE id IN (%s,%s)", (c["claim_a_id"], c["claim_b_id"]))
        else:
            loser = c["claim_b_id"] if winner_claim_id == c["claim_a_id"] else c["claim_a_id"]
            cur.execute("UPDATE conflicts SET status='resolved', resolution=%s, resolved_claim_id=%s, resolved_at=now() WHERE id=%s", (resolution, winner_claim_id, conflict_id))
            cur.execute("UPDATE claims SET evidence_category='verified_fact', conflict_status='resolved' WHERE id=%s", (winner_claim_id,))
            cur.execute("UPDATE claims SET superseded_by_id=%s, conflict_status='resolved', evidence_category='stale' WHERE id=%s", (winner_claim_id, loser))
    conn.commit()


def blocking_claims(conn: psycopg.Connection, claim_ids: list[UUID]) -> list[dict]:
    """Critical claims that cannot be published: open conflicts, stale, unknown, or superseded."""
    if not claim_ids:
        return []
    with conn.cursor() as cur:
        cur.execute(
            """SELECT id, field, evidence_category, conflict_status, superseded_by_id FROM claims WHERE id = ANY(%s)
               AND is_critical AND (conflict_status='open' OR evidence_category IN ('stale','unknown','conflicted','estimate') OR superseded_by_id IS NOT NULL)""",
            (claim_ids,),
        )
        return cur.fetchall()


def current_claims_for_entity(conn: psycopg.Connection, entity_id: UUID) -> list[dict]:
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM claims WHERE entity_id=%s AND superseded_by_id IS NULL ORDER BY field, academic_year DESC, room_type", (entity_id,))
        return cur.fetchall()


def mark_stale_for_source(conn: psycopg.Connection, source_id: UUID) -> list[UUID]:
    """When a source disappears, downgrade current claims that depend solely on it."""
    with conn.cursor() as cur:
        cur.execute(
            """WITH affected AS (
                 SELECT DISTINCT cs.claim_id FROM claim_sources cs JOIN fetch_snapshots s ON s.id=cs.snapshot_id WHERE s.source_id=%s)
               UPDATE claims c SET evidence_category='stale' FROM affected a WHERE c.id=a.claim_id AND c.superseded_by_id IS NULL
               AND c.evidence_category='verified_fact'
               AND NOT EXISTS (SELECT 1 FROM claim_sources cs2 JOIN fetch_snapshots s2 ON s2.id=cs2.snapshot_id
                               JOIN source_registry r2 ON r2.id=s2.source_id WHERE cs2.claim_id=c.id AND r2.id<>%s AND r2.health<>'gone')
               RETURNING c.id""",
            (source_id, source_id),
        )
        ids = [r["id"] for r in cur.fetchall()]
    conn.commit()
    return ids


# ------------------------------------------------------------------ deterministic extraction
ROOM_TYPE_WORDS = ("single", "double", "triple", "quad", "suite", "apartment", "studio", "efficiency", "one-bedroom", "two-bedroom")
PERIOD_WORDS = {
    "per_academic_year": ("academic year", "per year", "annual", "/year", "yearly", "2 semesters"),
    "per_semester": ("per semester", "semester", "/semester", "per term"),
    "per_month": ("per month", "monthly", "/month", "/mo"),
}


def detect_period(*texts: str) -> str:
    blob = " ".join(t.lower() for t in texts if t)
    for period, words in PERIOD_WORDS.items():
        if any(w in blob for w in words):
            return period
    return "unknown"


def detect_basis(*texts: str) -> str:
    blob = " ".join(t.lower() for t in texts if t)
    if "per person" in blob or "per student" in blob or "per resident" in blob or "per bed" in blob:
        return "per_person"
    if "per unit" in blob or "per apartment" in blob or "whole unit" in blob or "per room (not per person)" in blob:
        return "per_unit"
    return "unknown"


def extract_rate_table(table: dict, *, institution_id: UUID, campus_id: UUID | None, topic_id: UUID, entity_id: UUID | None,
                       retrieved_at: datetime, context_text: str = "", default_academic_year: str | None = None) -> tuple[list[ClaimRecord], list[str]]:
    """Deterministically extract money claims from an HTML/PDF table with a room-type column and
    one or more money columns whose headers may carry academic years. Returns (claims, warnings).
    Ambiguities (no year, unknown period/basis) are preserved as explicit 'unknown', never guessed."""
    warnings: list[str] = []
    headers = table.get("headers") or []
    rows = table.get("rows") or []
    caption = table.get("caption") or ""
    if not rows:
        return [], ["empty_table"]
    if not headers and rows:
        headers, rows = rows[0], rows[1:]
    period = detect_period(caption, context_text, *headers)
    basis = detect_basis(caption, context_text, *headers)
    if period == "unknown":
        warnings.append("billing_period_unknown")
    if basis == "unknown":
        warnings.append("price_basis_unknown")
    year_cols: dict[int, str | None] = {}
    for i, h in enumerate(headers):
        ys = find_academic_years(h)
        if ys:
            year_cols[i] = ys[0]
        elif parse_money_minor(" ".join(r[i] for r in rows if i < len(r))) is not None:
            year_cols[i] = default_academic_year or find_academic_years(caption + " " + context_text)[:1][0] if (default_academic_year or find_academic_years(caption + " " + context_text)) else None
    if not year_cols:
        return [], warnings + ["no_money_columns"]
    claims: list[ClaimRecord] = []
    for r in rows:
        label = (r[0] or "").strip() if r else ""
        if not label:
            continue
        room_type = next((w for w in ROOM_TYPE_WORDS if w in label.lower()), None) or label[:60]
        for col, ay in year_cols.items():
            if col >= len(r):
                continue
            minor = parse_money_minor(r[col])
            if minor is None:
                continue
            if ay is None:
                warnings.append(f"academic_year_unknown:{label}")
            claims.append(ClaimRecord(
                institution_id=institution_id, campus_id=campus_id, entity_id=entity_id, topic_id=topic_id,
                field="rate.room", value_type="money", value_number=minor, unit="minor_units", currency="USD",
                billing_period=period, price_basis=basis, room_type=room_type, academic_year=ay,
                evidence_category="verified_fact" if ay else "estimate", extraction_method="deterministic",
                retrieved_at=retrieved_at,
            ))
    return claims, warnings
