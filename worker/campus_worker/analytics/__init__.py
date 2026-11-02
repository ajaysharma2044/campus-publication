"""Analytics contracts (SPEC §24): event dictionary, validation, deduplication, aggregation.

No personal data: events never carry email, addresses, raw query text, precise location or raw
correction text. Identifiers are short-lived session tokens. Consent category per event.
"""
from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from uuid import UUID

import psycopg

EVENT_DICTIONARY: dict[str, dict] = {
    "page_view":           {"purpose": "reach and task entry", "trigger": "once per page load; not on filter/sort changes", "consent": "necessary", "retention_days": 90, "owner": "analyst"},
    "related_link_click":  {"purpose": "do next-task links help", "trigger": "click on a next-actions or related link", "consent": "necessary", "retention_days": 90, "owner": "analyst"},
    "comparison_start":    {"purpose": "comparison usage", "trigger": "comparison table rendered with ≥2 entities", "consent": "necessary", "retention_days": 90, "owner": "tools"},
    "comparison_complete": {"purpose": "task completion", "trigger": "user changes basis/room type or clicks a profile from the table", "consent": "necessary", "retention_days": 90, "owner": "tools"},
    "calculator_start":    {"purpose": "calculator usage", "trigger": "first input change", "consent": "necessary", "retention_days": 90, "owner": "tools"},
    "calculator_complete": {"purpose": "task completion", "trigger": "result rendered after a user edit", "consent": "necessary", "retention_days": 90, "owner": "tools"},
    "source_click":        {"purpose": "do readers verify sources", "trigger": "click in the sources list", "consent": "necessary", "retention_days": 90, "owner": "editorial"},
    "correction_submit":   {"purpose": "error rate signal (count only)", "trigger": "correction form submitted; no text", "consent": "necessary", "retention_days": 90, "owner": "editorial"},
    "school_select":       {"purpose": "disambiguation quality", "trigger": "pick from a disambiguation list", "consent": "necessary", "retention_days": 90, "owner": "search"},
    "audience_select":     {"purpose": "voluntary situation choice", "trigger": "user picks an audience toggle", "consent": "necessary", "retention_days": 90, "owner": "editorial"},
}
COMMON_PROPS = {"page_id", "page_version", "template", "institution_id", "topic", "device_class", "experiment", "audience", "session_token", "ts"}
FORBIDDEN_PROPS = {"email", "address", "query", "q", "search_text", "lat", "lon", "latitude", "longitude", "ip", "correction_text", "name", "phone", "user_id", "fingerprint"}
DEVICE_CLASSES = {"phone", "tablet", "desktop", "bot", "unknown"}
TEMPLATES = {"home", "school_hub", "topic_hub", "guide", "entity_profile", "comparison", "tool", "search", "policy", "not_found"}
PII_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}|\b\d{3}[-. ]\d{3}[-. ]\d{4}\b")


@dataclass
class Event:
    name: str
    props: dict
    ts: datetime


def validate_event(ev: dict) -> list[str]:
    errs = []
    name = ev.get("name")
    if name not in EVENT_DICTIONARY:
        errs.append(f"unknown event {name}")
    props = ev.get("props") or {}
    bad = set(props) & FORBIDDEN_PROPS
    if bad:
        errs.append(f"forbidden personal-data properties: {sorted(bad)}")
    unknown = set(props) - COMMON_PROPS
    if unknown:
        errs.append(f"properties outside the dictionary: {sorted(unknown)}")
    if props.get("device_class") not in (None, *DEVICE_CLASSES):
        errs.append("device_class must be coarse")
    if props.get("template") not in (None, *TEMPLATES):
        errs.append("unknown template")
    for v in props.values():
        if isinstance(v, str) and PII_RE.search(v):
            errs.append("property value looks like personal data")
            break
    if not ev.get("ts"):
        errs.append("missing ts")
    return errs


def dedupe_key(ev: dict) -> str:
    """Same session + page + event within the same minute is one event (SPA re-renders, retries)."""
    p = ev.get("props") or {}
    minute = str(ev.get("ts", ""))[:16]
    return hashlib.sha1(f"{ev.get('name')}|{p.get('session_token')}|{p.get('page_id')}|{minute}".encode()).hexdigest()


def _uuid_or_none(v):
    try:
        return UUID(str(v)) if v else None
    except ValueError:
        return None


def is_bot(user_agent: str | None) -> bool:
    ua = (user_agent or "").lower()
    return any(b in ua for b in ("bot", "crawl", "spider", "slurp", "headless", "lighthouse", "pingdom", "preview"))


def aggregate(conn: psycopg.Connection, events: list[dict], *, day: date, source: str = "first_party") -> dict:
    """Validate, dedupe, drop bots and write daily aggregates. Raw events are not stored here
    (the raw store, if any, is a separate 90-day table owned by the deployment)."""
    seen: set[str] = set()
    counts: dict[tuple, int] = {}
    rejected = 0
    for ev in events:
        if validate_event(ev) or is_bot((ev.get("props") or {}).get("user_agent")):
            rejected += 1
            continue
        k = dedupe_key(ev)
        if k in seen:
            continue
        seen.add(k)
        p = ev["props"]
        key = (_uuid_or_none(p.get("page_id")), p.get("template"), _uuid_or_none(p.get("institution_id")), ev["name"], p.get("device_class") or "unknown", p.get("experiment") or "")
        counts[key] = counts.get(key, 0) + 1
    with conn.cursor() as cur:
        for (page_id, template, inst, name, device, exp), n in counts.items():
            cur.execute(
                """INSERT INTO analytics_aggregates (day, page_id, template, institution_id, event_name, device_class, experiment_key, count, source)
                   VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
                   ON CONFLICT (day, page_id, event_name, device_class, experiment_key, source) DO UPDATE SET count = analytics_aggregates.count + EXCLUDED.count""",
                (day, page_id, template, inst, name, device, exp, n, source),
            )
    conn.commit()
    return {"accepted": sum(counts.values()), "deduped": len(events) - rejected - sum(counts.values()), "rejected": rejected}


def purge_expired(conn: psycopg.Connection, *, aggregate_months: int = 13) -> int:
    with conn.cursor() as cur:
        cur.execute("DELETE FROM analytics_aggregates WHERE day < (CURRENT_DATE - make_interval(months => %s)) RETURNING id", (aggregate_months,))
        n = len(cur.fetchall())
    conn.commit()
    return n


def analytics_tag(enabled: bool, environment: str, consent_granted: bool) -> str:
    """The only analytics loader. Empty unless enabled, production and consented (analytics
    category). Staging never emits it (SPEC §27)."""
    if not (enabled and environment == "production" and consent_granted):
        return ""
    return '<script src="/static/campus-analytics.js" defer data-endpoint="/wp-json/campus/v1/event"></script>'
