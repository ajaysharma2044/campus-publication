"""Query expansion from the versioned pattern library (continuous-local-run R19, R33; AT20).

Deterministic: every harvested entity × applicable patterns → hypotheses (never observed demand). The library is
mirrored in docs/strategy/query-patterns.md; PATTERN_VERSION changes when a pattern changes.
"""
from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

import psycopg

from .discovery import QuestionInput, ingest

PATTERN_VERSION = "v1"
AUDIENCE_PHRASE = {"prospective_transfer": "transfer students", "international": "international students", "grad": "grad students",
                   "parent": "parents", "undergrad": "students", "alumni": "alumni", "faculty_staff": "staff", "resident": "residents", "visitor": "visitors"}


@dataclass(frozen=True)
class Pattern:
    key: str
    template: str
    entity_types: tuple[str, ...]
    audiences: tuple[str, ...] = ()
    pair: bool = False                  # <other> from the same type + group
    topic_prefixes: tuple[str, ...] = ()  # restrict to entities whose topic key starts with one of these


PATTERNS: tuple[Pattern, ...] = (
    Pattern("review", "{entity} review", ("residence_hall", "dining_location", "gym", "program", "club", "neighborhood", "park", "employer")),
    Pattern("vs", "{entity} vs {other}", ("residence_hall", "dining_location", "program", "neighborhood", "bus_route"), pair=True),
    Pattern("room_size", "{entity} room size", ("residence_hall",)),
    Pattern("cost", "{entity} cost", ("residence_hall", "dining_location", "parking_lot", "gym", "program", "bus_route", "course", "employer")),
    Pattern("good_for_transfers", "is {entity} good for transfers", ("residence_hall", "program", "club"), ("prospective_transfer",)),
    Pattern("parking", "{entity} parking", ("residence_hall", "library", "gym", "dining_location", "park", "event", "office")),
    Pattern("how_to_get_to", "how to get to {entity}", ("residence_hall", "library", "dining_location", "gym", "park", "trail", "office", "event")),
    Pattern("hours", "{entity} hours", ("dining_location", "library", "gym", "student_service", "town_service", "office")),
    Pattern("prereq", "{entity} prerequisites", ("course", "program")),
    Pattern("schedule", "{entity} schedule", ("bus_route", "event", "course")),
    Pattern("apply", "how to apply {entity}", ("program", "transfer_pathway", "student_service", "employer", "club")),
    Pattern("requirements", "{entity} requirements", ("program", "transfer_pathway", "course")),
    Pattern("safety", "{entity} safety rules", ("park", "trail")),
    Pattern("audience_entity", "{entity} for {audience}", tuple(), ("prospective_transfer", "international", "grad", "parent")),
    Pattern("alumni_benefit", "{school} alumni {entity}", tuple(), ("alumni",), topic_prefixes=("alumni_",)),
    Pattern("parent_task", "{school} parent {entity}", tuple(), ("parent",), topic_prefixes=("parents_",)),
    Pattern("student_jobs", "{school} student jobs {entity}", tuple(), ("undergrad",), topic_prefixes=("jobs_student", "careers")),
    Pattern("jobs_at", "jobs at {school} {entity}", tuple(), ("faculty_staff",), topic_prefixes=("jobs_university",)),
)
TOWN_PATTERNS: tuple[Pattern, ...] = (
    Pattern("town_jobs_for", "{town} jobs for {audience}", tuple(), ("undergrad", "grad", "resident", "international"), topic_prefixes=("town_jobs",)),
)


def _applies(p: Pattern, entity_type: str, topic_key: str) -> bool:
    if p.topic_prefixes:
        return any(topic_key.startswith(pre) for pre in p.topic_prefixes)
    return (not p.entity_types) or entity_type in p.entity_types


def queries_for_entity(entity: dict, *, school_name: str | None, siblings: list[dict] | None = None) -> list[tuple[str, str, str | None]]:
    """[(query, pattern_key, audience)] for one entity row {name, entity_type, topic_key, attributes}. Pure."""
    out: list[tuple[str, str, str | None]] = []
    name = entity["name"]
    for p in PATTERNS:
        if not _applies(p, entity["entity_type"], entity.get("topic_key") or ""):
            continue
        if p.key == "audience_entity" and p.entity_types == () and entity["entity_type"] in ("course",):
            continue  # courses: audience variants are noise
        if p.pair:
            group = (entity.get("attributes") or {}).get("group")
            for s in siblings or []:
                if s["slug"] == entity["slug"] or s["entity_type"] != entity["entity_type"]:
                    continue
                if group is None or (s.get("attributes") or {}).get("group") != group:
                    continue
                if s["slug"] < entity["slug"]:
                    continue  # each unordered pair once
                out.append((p.template.format(entity=name, other=s["name"]), p.key, None))
            continue
        if p.audiences:
            for aud in p.audiences:
                q = p.template.format(entity=name, audience=AUDIENCE_PHRASE.get(aud, aud), school=school_name or "")
                out.append((q.strip(), p.key, aud))
        else:
            out.append((p.template.format(entity=name, school=school_name or "").strip(), p.key, None))
    return out


def expand_scope(conn: psycopg.Connection, *, institution_id: UUID | None = None, place_id: UUID | None = None, campus_id: UUID | None = None,
                 school_name: str | None = None, town_name: str | None = None, limit_per_entity: int = 40) -> dict:
    """Generate hypotheses for every active entity in the scope. Idempotent through the occurrence key."""
    if (institution_id is None) == (place_id is None):
        raise ValueError("exactly one of institution_id / place_id")
    scope_col, scope_id = ("institution_id", institution_id) if institution_id else ("place_id", place_id)
    with conn.cursor() as cur:
        cur.execute(f"""SELECT e.id, e.name, e.slug, e.entity_type, e.attributes, t.key AS topic_key FROM entities e JOIN topics t ON t.id=e.topic_id
                        WHERE e.{scope_col}=%s AND e.status IN ('active','synthetic_fixture') ORDER BY e.entity_type, e.slug""", (scope_id,))
        ents = [dict(r) for r in cur.fetchall()]
    by_type: dict[str, list[dict]] = {}
    for e in ents:
        by_type.setdefault(e["entity_type"], []).append(e)
    items: list[QuestionInput] = []
    for e in ents:
        for q, pkey, aud in queries_for_entity(e, school_name=school_name, siblings=by_type.get(e["entity_type"]))[:limit_per_entity]:
            scope_tag = f"i:{institution_id}" if institution_id else f"p:{place_id}"
            items.append(QuestionInput(raw_text=q, origin="hypothesis", institution_id=institution_id, campus_id=campus_id, place_id=place_id,
                                       topic_key=e["topic_key"], entity_id=e["id"], is_hypothesis=True,
                                       source_ref=f"hyp:{scope_tag}:{e['slug']}:{pkey}:{aud or '-'}", pattern_key=pkey, pattern_version=PATTERN_VERSION,
                                       constraints=[f"audience:{aud}"] if aud else []))
    if place_id and town_name:
        for p in TOWN_PATTERNS:
            for aud in p.audiences:
                q = p.template.format(town=town_name, audience=AUDIENCE_PHRASE.get(aud, aud))
                items.append(QuestionInput(raw_text=q, origin="hypothesis", place_id=place_id, topic_key="town_jobs", is_hypothesis=True,
                                           source_ref=f"hyp:p:{place_id}:town:{p.key}:{aud}", pattern_key=p.key, pattern_version=PATTERN_VERSION, constraints=[f"audience:{aud}"]))
    res = ingest(conn, items)
    res["generated"] = len(items)
    res["entities"] = len(ents)
    res["pattern_version"] = PATTERN_VERSION
    return res


def hypothesis_stats(conn: psycopg.Connection) -> dict:
    with conn.cursor() as cur:
        cur.execute("""SELECT count(*) FILTER (WHERE is_hypothesis) AS hypotheses, count(*) FILTER (WHERE NOT is_hypothesis) AS observed,
                              count(DISTINCT pattern_key) FILTER (WHERE is_hypothesis) AS patterns FROM questions""")
        return dict(cur.fetchone())
