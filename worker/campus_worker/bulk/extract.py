"""D2: typed claims with verbatim quotes from every crawled page, one Message Batches request per page.

The model only proposes claims; code decides what is kept: a claim survives only if its quote appears verbatim in the page text
(whitespace- and quote-insensitive), its field maps onto the claim taxonomy, and its value parses into the typed record. Storing
goes through claims.store_claim, which dedupes and supersedes by scope (institution, entity, field, year, audience...), so the same
fee on two pages becomes one claim with two sources. Entities the pages name (halls, dining rooms, offices, programs) are created
when they do not exist yet, so later questions and pages can hang off them.
"""
from __future__ import annotations

import json
import re
from datetime import date, datetime, timezone
from uuid import UUID

import psycopg

from .. import claims as cm
from ..pipeline import canonical_field
from ..types import ClaimRecord
from .batch_client import BatchRequest, BatchResult, usage_minor
from .util import json_default, parse_json_object, quote_in_text, slugify

PAGE_TEXT_LIMIT = 24_000       # chars per page sent to the model (about 6k tokens)
MAX_OUTPUT_TOKENS = 4_000
ENTITY_TYPES = ("residence_hall", "dining_location", "library", "building", "office", "program", "major", "bus_route", "parking_lot", "town_service", "park", "meal_plan", "course")
FIELD_FAMILIES = ("fee", "rate", "cost", "deadline", "eligibility", "policy", "process", "contact", "hours", "location", "capacity", "amenity", "placement", "route",
                  "program", "requirement", "prerequisite", "agreement", "accessibility", "timeline", "housing", "address")

EXTRACTION_SYSTEM = """You extract facts from one official web page of a US college or its town for a reference publication. Return ONE JSON object and nothing else:
{"claims": [...], "entities": [...], "processes": [...]}

A claim: {"field": "<family>.<specific_name>", "value_type": "money|integer|decimal|boolean|text|date", "value": <number in minor units for money, integer, decimal, true/false, text, or ISO date>,
 "unit": null, "currency": "USD" (money only), "billing_period": "per_semester|per_academic_year|per_month|per_year|one_time|per_term|per_week|per_day|null",
 "price_basis": "per_person|per_unit|per_bed|null", "academic_year": "YYYY-YY or null", "audience": ["first_year","transfer","graduate","international","parent","alumni","staff","resident","all"] (as the page says, else []),
 "entity_name": "<the hall, dining room, office, program, route or service the fact is about, exactly as named on the page, or null when the fact is institution-wide>",
 "entity_type": "residence_hall|dining_location|library|building|office|program|major|bus_route|parking_lot|town_service|park|meal_plan|course|null",
 "quote": "<the exact sentence or table cell from the page, copied verbatim, that states this fact>", "is_critical": true/false, "confidence": 0.0-1.0}

Field families: fee, rate, cost, deadline, eligibility, policy, process, contact, hours, location, capacity, amenity, placement, route, program, requirement, prerequisite, accessibility, timeline.
Examples: fee.housing_application, rate.room.double, deadline.housing_application, eligibility.residency_requirement, policy.cancellation, contact.email, hours.weekday, location.campus_area, capacity.residents, amenity.elevator, process.change_major.

Rules:
- Only facts the page states. No inference, no outside knowledge, no summaries of opinions. Skip marketing language.
- The quote must be copied character for character from the page text: same words, numbers, punctuation, dashes, capitalization and number formatting; never retype a phone number, email, date or range in another format, and never join two sentences. Use a whole sentence or a whole table cell of at least 12 characters. A claim whose quote is not verbatim on the page is discarded by code.
- Dates: value as ISO date (YYYY-MM-DD) when a full date is stated; a month-only or relative date goes in value_type "text".
- Money: value in minor units (cents) as an integer; include the billing period and basis only when the page states them.
- One fact per claim. Prefer specific fields over generic ones. At most 60 claims per page; pick the ones a student, parent, transfer, alum or job seeker would act on (fees, deadlines, rules, eligibility, locations, contacts, steps, hours).
- entities: every named hall, dining room, library, office, program, major, route, parking lot or service the page is about or lists, as {"name", "entity_type"}.
- processes: step-by-step procedures the page describes, as {"name": "<verb phrase, e.g. apply for housing>", "steps": ["...", "..."], "quote": "<verbatim sentence introducing or stating the steps>", "deadline_claim_fields": []}.
- If the page has no usable facts, return {"claims": [], "entities": [], "processes": []}."""


def pending_snapshots(conn: psycopg.Connection, *, institution_id: UUID | None, place_ids: list[UUID] | None, limit: int, only_crawled: bool = True) -> list[dict]:
    with conn.cursor() as cur:
        cur.execute("""SELECT DISTINCT ON (s.source_id) s.id, s.source_id, s.fetched_at, s.retained_text, COALESCE(s.final_url, r.canonical_url) AS url, r.crawl_section, r.source_family,
                              r.institution_id, r.place_id, r.publisher
                       FROM fetch_snapshots s JOIN source_registry r ON r.id=s.source_id
                       WHERE s.outcome='ok' AND s.retained_text IS NOT NULL AND length(s.retained_text) >= 80 AND s.extracted_at IS NULL AND r.source_kind LIKE 'official%%'
                         AND (r.institution_id = %s OR r.place_id = ANY(%s::uuid[]))
                         AND (%s = FALSE OR r.source_family LIKE 'crawl:%%' OR r.crawl_section IS NOT NULL)
                       ORDER BY s.source_id, s.fetched_at DESC""", (institution_id, place_ids or [], only_crawled))
        rows = [dict(r) for r in cur.fetchall()]
    return rows[:limit]


def section_topic(conn: psycopg.Connection, cfg: dict) -> dict[str, UUID]:
    """crawl section key → topic id (from the school config), with 'default' = housing."""
    with conn.cursor() as cur:
        cur.execute("SELECT id, key FROM topics")
        by_key = {r["key"]: r["id"] for r in cur.fetchall()}
    out = {sec["key"]: by_key.get(sec["topic"]) for sec in cfg.get("sections", []) if by_key.get(sec["topic"])}
    out["default"] = by_key.get("housing")
    return out


def build_requests(snapshots: list[dict], *, model: str, topic_by_section: dict) -> list[BatchRequest]:
    reqs = []
    for s in snapshots:
        section = s.get("crawl_section") or "default"
        user = (f"PAGE URL: {s['url']}\nPUBLISHER: {s.get('publisher') or ''}\nSECTION: {section}\nFETCHED: {s['fetched_at'].date().isoformat() if s.get('fetched_at') else ''}\n\nPAGE TEXT:\n"
                + (s["retained_text"] or "")[:PAGE_TEXT_LIMIT])
        reqs.append(BatchRequest(custom_id=f"extract:{s['id']}", model=model, system=EXTRACTION_SYSTEM, user=user, max_tokens=MAX_OUTPUT_TOKENS, temperature=0.0))
    return reqs


def _entity_id(conn: psycopg.Connection, *, institution_id: UUID | None, place_id: UUID | None, topic_id: UUID, name: str | None, entity_type: str | None, cache: dict, create: bool = True) -> UUID | None:
    if not name or not institution_id:
        return None
    key = (slugify(name, keep_stop=True), (entity_type or "").lower())
    if key in cache:
        return cache[key]
    slug = key[0]
    with conn.cursor() as cur:
        cur.execute("SELECT id, slug, name, entity_type FROM entities WHERE institution_id=%s AND (slug=%s OR lower(name)=lower(%s))", (institution_id, slug, name))
        rows = cur.fetchall()
        hit = next((r for r in rows if not entity_type or r["entity_type"] == entity_type), rows[0] if rows else None)
        if hit:
            cache[key] = hit["id"]
            return hit["id"]
        if not create or entity_type not in ENTITY_TYPES:
            cache[key] = None
            return None
        cur.execute("""INSERT INTO entities (institution_id, campus_id, topic_id, entity_type, name, slug, attributes)
                       VALUES (%s, (SELECT id FROM campuses WHERE institution_id=%s AND is_main LIMIT 1), %s, %s, %s, %s, '{}'::jsonb)
                       ON CONFLICT (institution_id, topic_id, slug) DO UPDATE SET name=EXCLUDED.name RETURNING id""", (institution_id, institution_id, topic_id, entity_type, name.strip()[:160], slug))
        eid = cur.fetchone()["id"]
    cache[key] = eid
    return eid


def _record(c: dict, *, institution_id: UUID | None, campus_id: UUID | None, entity_id: UUID | None, topic_id: UUID, fetched_at: datetime, model: str) -> ClaimRecord | None:
    field = canonical_field(str(c.get("field") or "").strip().lower().replace(" ", "_"))
    if "." not in field or field.split(".", 1)[0] not in FIELD_FAMILIES:
        return None
    vt = (c.get("value_type") or "text").lower()
    val = c.get("value")
    kw: dict = dict(institution_id=institution_id, campus_id=campus_id, entity_id=entity_id, topic_id=topic_id, field=field, evidence_category="verified_fact",
                    extraction_method="model", extraction_model=f"batch:{model}", extraction_confidence=min(1.0, max(0.0, float(c.get("confidence") or 0.8))),
                    retrieved_at=fetched_at, academic_year=c.get("academic_year") if re.fullmatch(r"\d{4}-\d{2}", str(c.get("academic_year") or "")) else None,
                    audience_applicability=[str(a) for a in (c.get("audience") or []) if a][:6],
                    billing_period=(c.get("billing_period") or ("unknown" if vt == "money" else None)), price_basis=(c.get("price_basis") or ("unknown" if vt == "money" else None)),
                    room_type=c.get("room_type") or None, is_critical=bool(c.get("is_critical")) or cm.is_critical_field(field))
    try:
        if vt == "money":
            kw.update(value_type="money", value_number=int(round(float(val))), unit="minor_units", currency=c.get("currency") or "USD")
        elif vt == "integer":
            kw.update(value_type="integer", value_number=int(round(float(val))))
        elif vt == "decimal":
            kw.update(value_type="decimal", value_number=float(val))
        elif vt == "boolean":
            kw.update(value_type="boolean", value_bool=(val if isinstance(val, bool) else str(val).strip().lower() in ("true", "yes", "1")))
        elif vt == "date":
            kw.update(value_type="date", value_date=date.fromisoformat(str(val)[:10]))
        else:
            text = str(val if val is not None else "").strip()
            if not text:
                return None
            kw.update(value_type="text", value_text=text[:600])
        return ClaimRecord(**kw)
    except (TypeError, ValueError):
        return None


def process_results(conn: psycopg.Connection, results: list[BatchResult], *, model: str, topic_by_section: dict, batch_id: str, default_institution_id: UUID | None = None) -> dict:
    """Store the claims whose quotes are verbatim on their page; mark each snapshot extracted; return counts and cost."""
    stats = {"pages": 0, "claims_proposed": 0, "claims_stored": 0, "claims_dropped_no_quote": 0, "claims_dropped_invalid": 0, "entities_created": 0, "processes": 0, "errors": 0, "cost_minor": 0}
    cache: dict = {}
    for res in results:
        if not res.custom_id.startswith("extract:"):
            continue
        sid = UUID(res.custom_id.split(":", 1)[1])
        stats["pages"] += 1
        if res.ok and res.usage:
            stats["cost_minor"] += usage_minor(res.model or model, res.usage)
        with conn.cursor() as cur:
            cur.execute("""SELECT s.retained_text, s.fetched_at, r.institution_id, r.place_id, r.crawl_section, r.source_family,
                                  (SELECT id FROM campuses WHERE institution_id=r.institution_id AND is_main LIMIT 1) AS campus_id
                           FROM fetch_snapshots s JOIN source_registry r ON r.id=s.source_id WHERE s.id=%s""", (sid,))
            snap = cur.fetchone()
        if not snap:
            continue
        doc = parse_json_object(res.text or "") if res.ok else None
        if doc is None:
            stats["errors"] += 1
            with conn.cursor() as cur:
                cur.execute("UPDATE fetch_snapshots SET extracted_at=now(), extraction_batch_id=%s WHERE id=%s", (batch_id + ":error", sid))
            conn.commit()
            continue
        topic_id = topic_by_section.get(snap["crawl_section"] or "default") or topic_by_section.get("default")
        if snap["institution_id"] is None and default_institution_id is not None:
            snap["institution_id"] = default_institution_id   # town pages: claims live under the school (claims.institution_id is NOT NULL), scoped by their town topic
            with conn.cursor() as cur:
                cur.execute("SELECT id FROM campuses WHERE institution_id=%s AND is_main LIMIT 1", (default_institution_id,))
                snap["campus_id"] = (cur.fetchone() or {}).get("id")
        text = snap["retained_text"] or ""
        n_before = len(cache)
        for e in doc.get("entities") or []:
            if isinstance(e, dict) and e.get("name") and (e.get("entity_type") in ENTITY_TYPES):
                _entity_id(conn, institution_id=snap["institution_id"], place_id=snap["place_id"], topic_id=topic_id, name=e["name"], entity_type=e["entity_type"], cache=cache)
        for c in doc.get("claims") or []:
            if not isinstance(c, dict):
                continue
            stats["claims_proposed"] += 1
            quote = str(c.get("quote") or "")
            if not quote_in_text(quote, text):
                stats["claims_dropped_no_quote"] += 1
                continue
            eid = _entity_id(conn, institution_id=snap["institution_id"], place_id=snap["place_id"], topic_id=topic_id, name=c.get("entity_name"), entity_type=c.get("entity_type"), cache=cache)
            rec = _record(c, institution_id=snap["institution_id"], campus_id=snap["campus_id"], entity_id=eid, topic_id=topic_id, fetched_at=snap["fetched_at"] or datetime.now(timezone.utc), model=model)
            if rec is None or rec.institution_id is None:
                stats["claims_dropped_invalid"] += 1
                continue
            try:
                cm.store_claim(conn, rec, snapshot_id=sid, excerpt=quote[:500], locator="bulk-extract", source_family=snap["source_family"])
                stats["claims_stored"] += 1
            except Exception as e:  # noqa: BLE001 — a malformed record is a count, never a crash of the batch
                conn.rollback()
                stats["claims_dropped_invalid"] += 1
                stats.setdefault("store_errors", []).append(f"{rec.field}: {type(e).__name__}: {str(e)[:100]}")
        for p in doc.get("processes") or []:
            if isinstance(p, dict) and p.get("name") and p.get("steps") and quote_in_text(str(p.get("quote") or ""), text) and snap["institution_id"]:
                rec = ClaimRecord(institution_id=snap["institution_id"], campus_id=snap["campus_id"], entity_id=None, topic_id=topic_id, field=f"process.{slugify(p['name'], keep_stop=True)[:60].replace('-', '_')}",
                                  value_type="text", value_text=json.dumps({"name": p["name"], "steps": [str(x)[:300] for x in p["steps"]][:12]}), evidence_category="verified_fact",
                                  extraction_method="model", extraction_model=f"batch:{model}", extraction_confidence=0.8, retrieved_at=snap["fetched_at"] or datetime.now(timezone.utc), is_critical=False)
                try:
                    cm.store_claim(conn, rec, snapshot_id=sid, excerpt=str(p["quote"])[:500], locator="bulk-extract:process", source_family=snap["source_family"])
                    stats["processes"] += 1
                except Exception:  # noqa: BLE001
                    conn.rollback()
        stats["entities_created"] += sum(1 for v in list(cache.values())[n_before:] if v)
        with conn.cursor() as cur:
            cur.execute("UPDATE fetch_snapshots SET extracted_at=now(), extraction_batch_id=%s WHERE id=%s", (batch_id, sid))
        conn.commit()
    return stats


def unextracted_count(conn: psycopg.Connection, *, institution_id: UUID | None, place_ids: list[UUID] | None) -> int:
    return len(pending_snapshots(conn, institution_id=institution_id, place_ids=place_ids, limit=100_000))
