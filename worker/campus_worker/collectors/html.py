"""Official-HTML collector.

Pipeline: source_registry row → SafeFetcher → material-text extraction (navigation, header,
footer, scripts, cookie banners stripped) → content hash of material text → compare with the
previous snapshot → fetch_snapshots row with outcome and material_change flag. Tables are
retained as structured rows (list of lists) so deterministic claim extraction can run on them.

Material change is judged on the material text hash, so a navigation or footer edit does not
mark every dependent article for re-verification (SPEC §08).
"""
from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from uuid import UUID

import psycopg
from bs4 import BeautifulSoup

from ..fetcher import FetchRefused, FetchResult, SafeFetcher

NOISE_TAGS = ("script", "style", "noscript", "nav", "header", "footer", "aside", "form", "iframe", "svg", "button")
NOISE_SELECTORS = (
    "[role=navigation]", "[role=banner]", "[role=contentinfo]", ".cookie", "#cookie", ".cookie-banner",
    ".breadcrumb", ".breadcrumbs", ".menu", ".sidebar", ".site-header", ".site-footer", ".skip-link",
)


@dataclass
class Extracted:
    title: str | None
    material_text: str
    tables: list[dict]           # [{"caption": str|None, "headers": [...], "rows": [[...]]}]
    headings: list[str]
    links: list[str]
    content_hash: str


def extract_material(html: bytes | str) -> Extracted:
    soup = BeautifulSoup(html, "lxml")
    title = soup.title.get_text(strip=True) if soup.title else None
    # Pick the content root FIRST, then strip noise inside it. Stripping first can delete the root itself when a site
    # wraps <main> in a <header>/<nav> container (observed on scl.cornell.edu, 2026-11-06), leaving only the <title>.
    root = soup.find("main") or soup.find(attrs={"role": "main"}) or soup.find("article") or soup.body or soup
    keep = {id(root)} | {id(p) for p in root.parents}
    for tag in root.find_all(NOISE_TAGS):
        if id(tag) not in keep:
            tag.decompose()
    for sel in NOISE_SELECTORS:
        for el in root.select(sel):
            if id(el) not in keep:
                el.decompose()
    tables = []
    for t in root.find_all("table"):
        cap = t.find("caption")
        headers = [th.get_text(" ", strip=True) for th in t.find_all("th")]
        rows = []
        for tr in t.find_all("tr"):
            cells = [td.get_text(" ", strip=True) for td in tr.find_all(["td"])]
            if cells:
                rows.append(cells)
        tables.append({"caption": cap.get_text(" ", strip=True) if cap else None, "headers": headers, "rows": rows})
    headings = [h.get_text(" ", strip=True) for h in root.find_all(["h1", "h2", "h3"])]
    links = [a.get("href") for a in root.find_all("a", href=True)]
    text = root.get_text("\n", strip=True)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{2,}", "\n", text).strip()
    digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
    return Extracted(title, text, tables, headings, links, digest)


def _previous_hash(conn: psycopg.Connection, source_id: UUID) -> str | None:
    with conn.cursor() as cur:
        cur.execute("SELECT content_hash FROM fetch_snapshots WHERE source_id=%s AND outcome IN ('ok','unchanged') ORDER BY fetched_at DESC LIMIT 1", (source_id,))
        r = cur.fetchone()
    return r["content_hash"] if r else None


def record_snapshot(conn: psycopg.Connection, source_id: UUID, *, final_url: str, status: int | None, content_type: str | None,
                    content_hash: str, raw_hash: str | None, byte_size: int | None, etag: str | None, last_modified: str | None,
                    confidence: float | None, retained_text: str | None, retained_tables: list | None,
                    material_change: bool | None, outcome: str, error_detail: str | None = None) -> UUID:
    with conn.cursor() as cur:
        cur.execute(
            """INSERT INTO fetch_snapshots (source_id, final_url, http_status, content_type, content_hash, raw_hash, byte_size,
               etag, last_modified, extraction_confidence, retained_text, retained_tables, material_change, outcome, error_detail)
               VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s::jsonb,%s,%s,%s) RETURNING id""",
            (source_id, final_url, status, content_type, content_hash, raw_hash, byte_size, etag, last_modified, confidence,
             retained_text, json.dumps(retained_tables) if retained_tables is not None else None, material_change, outcome, error_detail),
        )
        sid = cur.fetchone()["id"]
        ok = outcome in ("ok", "unchanged")
        cur.execute(
            """UPDATE source_registry SET last_fetched_at=now(),
                 last_changed_at = CASE WHEN %s THEN now() ELSE last_changed_at END,
                 consecutive_failures = CASE WHEN %s THEN 0 ELSE consecutive_failures + 1 END,
                 health = CASE WHEN %s THEN 'healthy' WHEN %s = 'blocked' THEN 'blocked'
                               WHEN consecutive_failures + 1 >= 5 THEN 'degraded' ELSE health END,
                 next_refresh_at = now() + make_interval(hours => refresh_interval_hours)
               WHERE id=%s""",
            (bool(material_change), ok, ok, outcome, source_id),
        )
    conn.commit()
    return sid


def collect_html_source(conn: psycopg.Connection, fetcher: SafeFetcher, source_id: UUID, *, force: bool = False) -> dict:
    """Fetch one registered HTML source and record a snapshot. Returns a summary dict. force=True skips conditional
    headers (re-extract after an extractor fix even when the page itself did not change)."""
    with conn.cursor() as cur:
        cur.execute("SELECT r.canonical_url, p.retention_policy FROM source_registry r LEFT JOIN source_permissions p ON p.id=r.permission_id WHERE r.id=%s", (source_id,))
        src = cur.fetchone()
    if not src:
        raise LookupError("source not found")
    url = src["canonical_url"]
    retention = src["retention_policy"] or "excerpts_only"
    try:
        res: FetchResult = fetcher.fetch(url, expected_types=("text/html", "application/xhtml+xml"), use_conditional=not force)
    except FetchRefused as e:
        outcome = {"permission_denied": "blocked", "redirect_permission_denied": "redirect_rejected", "private_address": "redirect_rejected",
                   "oversized": "oversized", "unexpected_content_type": "unexpected_type", "robots_disallow": "blocked"}.get(e.reason, "error")
        sid = record_snapshot(conn, source_id, final_url=url, status=None, content_type=None, content_hash="", raw_hash=None, byte_size=None,
                              etag=None, last_modified=None, confidence=None, retained_text=None, retained_tables=None,
                              material_change=None, outcome=outcome, error_detail=str(e))
        return {"snapshot_id": str(sid), "outcome": outcome, "error": str(e)}
    if res.unchanged:
        prev = _previous_hash(conn, source_id) or ""
        sid = record_snapshot(conn, source_id, final_url=res.final_url, status=304, content_type=None, content_hash=prev, raw_hash=None,
                              byte_size=0, etag=res.etag, last_modified=res.last_modified, confidence=None, retained_text=None,
                              retained_tables=None, material_change=False, outcome="unchanged")
        return {"snapshot_id": str(sid), "outcome": "unchanged", "material_change": False}
    if res.status >= 400:
        outcome = "blocked" if res.status in (401, 403, 429) else "error"
        sid = record_snapshot(conn, source_id, final_url=res.final_url, status=res.status, content_type=res.content_type, content_hash="",
                              raw_hash=None, byte_size=0, etag=None, last_modified=None, confidence=None, retained_text=None,
                              retained_tables=None, material_change=None, outcome=outcome, error_detail=f"HTTP {res.status}")
        if res.status in (404, 410):
            with conn.cursor() as cur:
                cur.execute("UPDATE source_registry SET health='gone' WHERE id=%s", (source_id,))
            conn.commit()
        return {"snapshot_id": str(sid), "outcome": outcome, "status": res.status, "retry_after": res.retry_after_seconds}
    ex = extract_material(res.body)
    prev = _previous_hash(conn, source_id)
    material_change = prev is not None and prev != ex.content_hash
    if len(ex.material_text) < 40:
        outcome, confidence = "parse_failed", 0.0
    else:
        outcome, confidence = "ok", min(1.0, 0.5 + min(len(ex.material_text), 4000) / 8000 + (0.1 if ex.tables else 0))
    retained_text = ex.material_text if retention in ("full_text", "excerpts_only") else None
    retained_tables = ex.tables if retention in ("full_text", "excerpts_only") else None
    if ex.title:
        with conn.cursor() as cur:
            cur.execute("UPDATE source_registry SET title=%s WHERE id=%s", (ex.title[:300], source_id))
    sid = record_snapshot(conn, source_id, final_url=res.final_url, status=res.status, content_type=res.content_type,
                          content_hash=ex.content_hash, raw_hash=hashlib.sha256(res.body).hexdigest(), byte_size=len(res.body),
                          etag=res.etag, last_modified=res.last_modified, confidence=confidence, retained_text=retained_text,
                          retained_tables=retained_tables, material_change=material_change if prev is not None else None, outcome=outcome)
    return {"snapshot_id": str(sid), "outcome": outcome, "material_change": material_change, "first_fetch": prev is None,
            "tables": len(ex.tables), "title": ex.title, "confidence": confidence}


def register_source(conn: psycopg.Connection, *, canonical_url: str, institution_id: UUID | None, campus_id: UUID | None,
                    source_kind: str, publisher: str | None, reliability: str = "official", refresh_interval_hours: int = 168,
                    source_family: str | None = None, place_id: UUID | None = None) -> UUID:
    from ..permissions import check_url

    d = check_url(conn, canonical_url)
    with conn.cursor() as cur:
        cur.execute(
            """INSERT INTO source_registry (institution_id, campus_id, canonical_url, publisher, source_kind, permission_id, reliability,
               source_family, refresh_interval_hours, next_refresh_at, place_id)
               VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,now(),%s)
               ON CONFLICT (canonical_url) DO UPDATE SET publisher=EXCLUDED.publisher, reliability=EXCLUDED.reliability,
                 place_id=COALESCE(EXCLUDED.place_id, source_registry.place_id) RETURNING id""",
            (institution_id, campus_id, canonical_url, publisher, source_kind, d.permission_id, reliability, source_family, refresh_interval_hours, place_id),
        )
        sid = cur.fetchone()["id"]
    conn.commit()
    return sid


def refresh_titles(conn: psycopg.Connection, fetcher: SafeFetcher, source_ids: list[UUID] | None = None) -> dict:
    """Fill `source_registry.title` for official HTML sources that have none (backfill for pages fetched before 0006).
    A plain fetch of the page's <title>: no snapshot is recorded and nothing else changes."""
    with conn.cursor() as cur:
        if source_ids:
            cur.execute("SELECT id, canonical_url FROM source_registry WHERE id = ANY(%s::uuid[]) AND title IS NULL", (source_ids,))
        else:
            cur.execute("SELECT id, canonical_url FROM source_registry WHERE title IS NULL AND source_kind LIKE 'official%%' AND health <> 'gone' ORDER BY canonical_url")
        rows = cur.fetchall()
    out = {"checked": len(rows), "titled": 0, "failed": []}
    for r in rows:
        try:
            res = fetcher.fetch(r["canonical_url"], expected_types=("text/html", "application/xhtml+xml"), use_conditional=False)
        except FetchRefused as e:
            out["failed"].append({"url": r["canonical_url"], "reason": e.reason})
            continue
        if res.status >= 400 or not res.body:
            out["failed"].append({"url": r["canonical_url"], "reason": f"HTTP {res.status}"})
            continue
        title = extract_material(res.body).title
        if title:
            with conn.cursor() as cur:
                cur.execute("UPDATE source_registry SET title=%s WHERE id=%s", (title[:300], r["id"]))
            conn.commit()
            out["titled"] += 1
    return out
