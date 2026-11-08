"""Entity harvesting — the "always finding data" lane (continuous-local-run R18, R34; AT19, AT34).

Deterministic, no model. A harvest rule names an official directory page (a registered source), the entity type
and topic it lists, and how to pick entities out of the page: links under a path prefix and/or list items under a
heading, with exclusions. Harvesting a snapshot upserts entities with source URL and first/last-seen dates; a hall
that appears on a later run is added, one that disappears is marked inactive (never deleted: pages may cite it).
School entities carry institution_id; town entities carry place_id and never an institution_id (R34).
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from urllib.parse import urljoin, urlsplit
from uuid import UUID

import psycopg
from bs4 import BeautifulSoup

from .collectors.html import register_source
from .registry import slugify

ENTITY_TYPES = ("residence_hall", "dining_location", "library", "bus_route", "parking_lot", "gym", "program", "transfer_pathway", "student_service",
                "course", "club", "park", "trail", "town_service", "neighborhood", "employer", "event", "office")


@dataclass(frozen=True)
class HarvestRule:
    key: str
    source_url: str
    entity_type: str
    topic_key: str
    link_prefix: str | None = None            # keep links whose path starts with this
    link_regex: str | None = None             # or whose href matches this regex
    heading_regex: str | None = None          # only list items / links under a heading matching this (case-insensitive)
    item_selector: str | None = None          # CSS selector for items (default: anchors)
    exclude_regex: str | None = None          # drop names matching this
    include_regex: str | None = None          # keep only names matching this
    min_name_len: int = 3
    attributes: dict = field(default_factory=dict)
    publisher: str | None = None
    group_from_heading: bool = False          # store the nearest heading text as attributes.group (for vs-pairs, R19)
    name_split_regex: str | None = None       # for text items: keep the text BEFORE the first match (e.g. " – in Toni Morrison Hall")
    detail_from_split: str | None = None      # attribute name for the text AFTER the split (e.g. "located_in")

    def as_json(self) -> dict:
        return {k: v for k, v in self.__dict__.items()}


def _nearest_heading(node) -> str | None:
    cur = node
    while cur is not None:
        prev = cur.find_previous(re.compile(r"^h[1-4]$"))
        return prev.get_text(" ", strip=True) if prev else None
    return None


def extract_entities(html: bytes | str, rule: HarvestRule) -> list[dict]:
    """Return [{name, slug, url, group}] found by the rule. Pure function of (html, rule)."""
    soup = BeautifulSoup(html, "lxml")
    for t in soup(["script", "style", "noscript"]):
        t.decompose()
    base = rule.source_url
    found: dict[str, dict] = {}
    heading_re = re.compile(rule.heading_regex, re.I) if rule.heading_regex else None
    link_re = re.compile(rule.link_regex, re.I) if rule.link_regex else None
    excl = re.compile(rule.exclude_regex, re.I) if rule.exclude_regex else None
    nodes = soup.select(rule.item_selector) if rule.item_selector else soup.find_all("a", href=True)
    split_re = re.compile(rule.name_split_regex) if rule.name_split_regex else None
    for node in nodes:
        a = node if node.name == "a" else node.find("a", href=True)
        raw_text = (a.get_text(" ", strip=True) if (a and not split_re) else node.get_text(" ", strip=True)) or ""
        raw_text = raw_text.replace("\xa0", " ")
        detail = None
        if split_re:
            m = split_re.search(raw_text)
            if not m:
                continue  # text items must match the split pattern (e.g. "<name> – in <building>")
            name, detail = raw_text[:m.start()], raw_text[m.end():].strip(" .")
        else:
            name = raw_text
        name = re.sub(r"\s+", " ", name).strip(" -–—:·|!")
        if len(name) < rule.min_name_len or len(name) > 120:
            continue
        href = urljoin(base, a["href"]) if a else None
        if a is not None:
            path = urlsplit(href).path
            if rule.link_prefix and not path.startswith(rule.link_prefix):
                continue
            if link_re and not link_re.search(href):
                continue
            if urlsplit(href).netloc != urlsplit(base).netloc and rule.link_prefix:
                continue
        elif rule.link_prefix or link_re:
            continue
        if heading_re:
            h = _nearest_heading(node)
            if not h or not heading_re.search(h):
                continue
        if excl and excl.search(name):
            continue
        if rule.include_regex and not re.search(rule.include_regex, name, re.I):
            continue
        slug = slugify(name)
        if not slug or slug in found:
            continue
        group = _nearest_heading(node) if rule.group_from_heading else None
        found[slug] = {"name": name, "slug": slug, "url": href, "group": group, "detail": detail}
    return list(found.values())


def register_rule(conn: psycopg.Connection, rule: HarvestRule, *, institution_id: UUID | None, campus_id: UUID | None = None,
                  place_id: UUID | None = None, source_kind: str = "official_html") -> UUID:
    sid = register_source(conn, canonical_url=rule.source_url, institution_id=institution_id, campus_id=campus_id, source_kind=source_kind,
                          publisher=rule.publisher, reliability="official", source_family=f"harvest:{rule.key}", place_id=place_id)
    with conn.cursor() as cur:
        # one harvest source per rule key: a rule whose URL moved must not leave a stale row that re-harvests the old address
        cur.execute("DELETE FROM harvest_sources h USING source_registry r WHERE h.source_id=r.id AND h.rule_key=%s AND r.canonical_url<>%s", (rule.key, rule.source_url))
        cur.execute(
            """INSERT INTO harvest_sources (source_id, rule_key, entity_type, topic_key, rule) VALUES (%s,%s,%s,%s,%s::jsonb)
               ON CONFLICT (source_id, rule_key) DO UPDATE SET entity_type=EXCLUDED.entity_type, topic_key=EXCLUDED.topic_key, rule=EXCLUDED.rule RETURNING id""",
            (sid, rule.key, rule.entity_type, rule.topic_key, json.dumps(rule.as_json())),
        )
        hid = cur.fetchone()["id"]
    conn.commit()
    return hid


def harvest_html(conn: psycopg.Connection, rule: HarvestRule, html: bytes | str, *, institution_id: UUID | None, place_id: UUID | None = None,
                 campus_id: UUID | None = None, snapshot_url: str | None = None, now: datetime | None = None) -> dict:
    """Upsert the entities a page lists. Returns counts; never deletes (missing entities become inactive)."""
    if institution_id is None and place_id is None:
        raise ValueError("harvest needs an institution_id or a place_id")
    if institution_id is not None and place_id is not None:
        raise ValueError("an entity is school-scoped or town-scoped, never both (R34)")
    now = now or datetime.now(timezone.utc)
    items = extract_entities(html, rule)
    src_url = snapshot_url or rule.source_url
    created = updated = 0
    seen_slugs = []
    with conn.cursor() as cur:
        cur.execute("SELECT id FROM topics WHERE key=%s", (rule.topic_key,))
        r = cur.fetchone()
        if not r:
            raise LookupError(f"unknown topic {rule.topic_key}")
        topic_id = r["id"]
        cur.execute("SELECT id FROM source_registry WHERE canonical_url=%s", (rule.source_url,))
        srow = cur.fetchone()
        source_id = srow["id"] if srow else None
        for it in items:
            attrs = dict(rule.attributes)
            if it.get("group"):
                attrs["group"] = it["group"]
            if it.get("url"):
                attrs["official_url"] = it["url"]
            if it.get("detail") and rule.detail_from_split:
                attrs[rule.detail_from_split] = it["detail"]
            seen_slugs.append(it["slug"])
            if institution_id is not None:
                cur.execute(
                    """INSERT INTO entities (institution_id, campus_id, topic_id, entity_type, name, slug, attributes, status, source_id, source_url, first_seen_at, last_seen_at, harvest_rule)
                       VALUES (%s,%s,%s,%s,%s,%s,%s::jsonb,'active',%s,%s,%s,%s,%s)
                       ON CONFLICT (institution_id, topic_id, slug) DO UPDATE SET name=EXCLUDED.name, attributes=entities.attributes || EXCLUDED.attributes,
                         status='active', source_id=COALESCE(EXCLUDED.source_id, entities.source_id), source_url=EXCLUDED.source_url, last_seen_at=EXCLUDED.last_seen_at,
                         first_seen_at=COALESCE(entities.first_seen_at, EXCLUDED.first_seen_at), harvest_rule=EXCLUDED.harvest_rule
                       RETURNING (xmax = 0) AS inserted""",
                    (institution_id, campus_id, topic_id, rule.entity_type, it["name"], it["slug"], json.dumps(attrs), source_id, src_url, now, now, rule.key),
                )
            else:
                cur.execute("SELECT id FROM entities WHERE place_id=%s AND topic_id=%s AND slug=%s", (place_id, topic_id, it["slug"]))
                ex = cur.fetchone()
                if ex:
                    cur.execute("""UPDATE entities SET name=%s, attributes=attributes || %s::jsonb, status='active', source_id=COALESCE(%s, source_id), source_url=%s,
                                   last_seen_at=%s, harvest_rule=%s WHERE id=%s""", (it["name"], json.dumps(attrs), source_id, src_url, now, rule.key, ex["id"]))
                    updated += 1
                    continue
                cur.execute(
                    """INSERT INTO entities (institution_id, campus_id, topic_id, entity_type, name, slug, attributes, status, source_id, source_url, first_seen_at, last_seen_at, harvest_rule, place_id)
                       VALUES (NULL,NULL,%s,%s,%s,%s,%s::jsonb,'active',%s,%s,%s,%s,%s,%s) RETURNING (xmax = 0) AS inserted""",
                    (topic_id, rule.entity_type, it["name"], it["slug"], json.dumps(attrs), source_id, src_url, now, now, rule.key, place_id),
                )
            if cur.fetchone()["inserted"]:
                created += 1
            else:
                updated += 1
        # entities from this rule not seen this time → inactive (kept for citations)
        scope_sql = "institution_id=%s" if institution_id is not None else "place_id=%s"
        cur.execute(f"""UPDATE entities SET status='inactive' WHERE {scope_sql} AND topic_id=%s AND harvest_rule=%s AND status='active' AND NOT (slug = ANY(%s))""",
                    (institution_id if institution_id is not None else place_id, topic_id, rule.key, seen_slugs or ["__none__"]))
        deactivated = cur.rowcount
        if source_id:
            cur.execute("UPDATE harvest_sources SET last_harvested_at=%s, last_count=%s WHERE source_id=%s AND rule_key=%s", (now, len(items), source_id, rule.key))
            cur.execute("UPDATE source_registry SET last_fetched_at=%s, next_refresh_at=%s + make_interval(hours => refresh_interval_hours) WHERE id=%s", (now, now, source_id))
    conn.commit()
    return {"rule": rule.key, "entity_type": rule.entity_type, "found": len(items), "created": created, "updated": updated, "deactivated": deactivated,
            "source_url": src_url, "harvested_at": now.isoformat()}


def harvest_source(conn: psycopg.Connection, fetcher, harvest_source_id: UUID) -> dict:
    """Fetch a registered harvest source through the safe fetcher and harvest it."""
    with conn.cursor() as cur:
        cur.execute("""SELECT h.rule, r.canonical_url, r.institution_id, r.campus_id, r.place_id FROM harvest_sources h JOIN source_registry r ON r.id=h.source_id WHERE h.id=%s""", (harvest_source_id,))
        row = cur.fetchone()
    if not row:
        raise LookupError("harvest source not found")
    if (row["rule"] or {}).get("kind") == "gtfs":
        from .collectors.gtfs import parse_routes, store_routes
        res = fetcher.fetch(row["canonical_url"], expected_types=("application/zip", "application/octet-stream", "application/x-zip-compressed"), use_conditional=False)
        if res.status >= 400 or not res.body:
            return {"rule": row["rule"]["key"], "outcome": f"http_{res.status}", "found": 0}
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM source_registry WHERE canonical_url=%s", (row["canonical_url"],))
            sid = cur.fetchone()["id"]
        return store_routes(conn, parse_routes(res.body), place_id=row["place_id"], source_url=row["canonical_url"], source_id=sid, rule_key=row["rule"]["key"])
    rule = HarvestRule(**row["rule"])
    res = fetcher.fetch(row["canonical_url"], expected_types=("text/html", "application/xhtml+xml"))
    if res.status >= 400 or not res.body:
        return {"rule": rule.key, "outcome": f"http_{res.status}", "found": 0}
    return harvest_html(conn, rule, res.body, institution_id=row["institution_id"], campus_id=row["campus_id"], place_id=row["place_id"], snapshot_url=res.final_url)


def due_harvest_sources(conn: psycopg.Connection, *, now: datetime | None = None, force: bool = False) -> list[dict]:
    now = now or datetime.now(timezone.utc)
    with conn.cursor() as cur:
        cur.execute("""SELECT h.id, h.rule_key, h.entity_type, h.topic_key, r.canonical_url, r.institution_id, r.place_id, h.last_harvested_at
                       FROM harvest_sources h JOIN source_registry r ON r.id=h.source_id
                       WHERE %s OR h.last_harvested_at IS NULL OR r.next_refresh_at IS NULL OR r.next_refresh_at <= %s ORDER BY h.last_harvested_at NULLS FIRST""", (force, now))
        return [dict(r) for r in cur.fetchall()]


def entity_counts(conn: psycopg.Connection) -> list[dict]:
    with conn.cursor() as cur:
        cur.execute("""SELECT COALESCE(i.slug, p.slug) AS scope, t.key AS topic, e.entity_type, count(*) FILTER (WHERE e.status='active') AS active
                       FROM entities e LEFT JOIN institutions i ON i.id=e.institution_id LEFT JOIN places p ON p.id=e.place_id JOIN topics t ON t.id=e.topic_id
                       GROUP BY 1,2,3 ORDER BY 1,2,3""")
        return [dict(r) for r in cur.fetchall()]
