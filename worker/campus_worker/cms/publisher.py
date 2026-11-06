"""Publish a gated page version to the CMS, idempotently (SPEC §25, §28).

Rules:
- Only versions with gate_status='passed' are publishable; anything else raises NotPublishable.
- external_id = pages.id (immutable). The CMS stores content_hash; a repeat publish of the same
  version is a no-op (changed=False) and never creates a duplicate.
- Staging publishes with status 'draft' unless auto_publish is enabled AND environment is
  production AND the daily quota allows it.
- Path changes register a redirect from the previous path.
- After success, pages.cms_external_id / cms_content_hash / status are updated and the
  publication is recorded as a 'publish' usage of the daily new-page quota.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from uuid import UUID

import psycopg

from ..adapters.cms import PublishRequest, PublishResult
from ..render import engine

POST_TYPE_BY_FORMAT = {"guide": "campus_guide", "entity_profile": "campus_profile", "comparison": "campus_comparison", "tool": "campus_tool",
                       "topic_hub": "campus_topic", "school_hub": "campus_school", "explainer": "campus_guide", "policy": "campus_policy", "home": "campus_policy"}


class NotPublishable(Exception):
    pass


class QuotaExceeded(Exception):
    pass


@dataclass
class PublishOutcome:
    page_id: UUID
    version_id: UUID
    cms_id: str
    created: bool
    changed: bool
    status: str
    redirect_from: str | None = None


def _sources_for_version(conn: psycopg.Connection, version_id: UUID) -> list[dict]:
    with conn.cursor() as cur:
        cur.execute(
            """SELECT DISTINCT r.canonical_url AS url, r.publisher, r.source_kind AS kind, max(s.fetched_at) AS retrieved_at
               FROM page_claims pc JOIN claim_sources cs ON cs.claim_id=pc.claim_id JOIN fetch_snapshots s ON s.id=cs.snapshot_id
               JOIN source_registry r ON r.id=s.source_id WHERE pc.page_version_id=%s GROUP BY r.canonical_url, r.publisher, r.source_kind ORDER BY 1""",
            (version_id,),
        )
        return [dict(r, retrieved_at=r["retrieved_at"].isoformat()) for r in cur.fetchall()]


def new_pages_published_today(conn: psycopg.Connection) -> int:
    with conn.cursor() as cur:
        cur.execute("SELECT count(*) AS n FROM pages WHERE first_published_at >= date_trunc('day', now())")
        return cur.fetchone()["n"]


def build_request(conn: psycopg.Connection, version_id: UUID, *, status: str) -> tuple[PublishRequest, dict, dict]:
    with conn.cursor() as cur:
        cur.execute("""SELECT v.*, p.path, p.slug, p.page_format, p.institution_id, p.campus_id, p.entity_id, p.audience, p.cms_external_id, p.cms_content_hash,
                              p.status AS page_status, t.key AS topic_key FROM page_versions v JOIN pages p ON p.id=v.page_id
                       LEFT JOIN topics t ON t.id=p.topic_id WHERE v.id=%s""", (version_id,))
        v = cur.fetchone()
    if v is None:
        raise LookupError("version not found")
    if v["gate_status"] != "passed":
        raise NotPublishable(f"version gate_status={v['gate_status']}; only 'passed' versions publish")
    body_html = engine.md_to_html(v["body_markdown"])
    structured = dict(v["structured"])
    structured.setdefault("fact_table_caption", f"{v['headline']} — verified facts")
    meta = {"institution_id": str(v["institution_id"]) if v["institution_id"] else "", "campus_id": str(v["campus_id"]) if v["campus_id"] else "",
            "topic_key": v["topic_key"] or "", "entity_id": str(v["entity_id"]) if v["entity_id"] else "", "version_no": str(v["version_no"]),
            "byline": v["byline"], "production_note": v["production_note"] or "", "deck": v["deck"] or "", "audience": v["audience"] or "",
            "structured": structured, "sources": _sources_for_version(conn, version_id), "next_actions": structured.get("next_actions", []),
            "material_updated_at": v["created_at"].isoformat() if v["is_material_change"] else "", "noindex": "0"}  # deterministic: hash must be stable
    req = PublishRequest(external_id=str(v["page_id"]), post_type=POST_TYPE_BY_FORMAT[v["page_format"]], title=v["headline"], slug=v["slug"],
                         path=v["path"], content_html=body_html, status=status, meta=meta)
    return req, dict(v), meta


def publish_version(conn: psycopg.Connection, cms, version_id: UUID, *, environment: str, auto_publish: bool,
                    live_allowance: int | None = None, niche_score: float | None = None) -> PublishOutcome:
    """Push a passed version to the CMS. status='publish' only in production with auto_publish; otherwise 'draft'
    (staging/local, never quota'd — continuous-local-run R8). `live_allowance` is the ramp's remaining NEW pages
    for today (None = unlimited); updates to already-live pages are never capped."""
    status = "publish" if (auto_publish and environment == "production") else "draft"
    req, v, _ = build_request(conn, version_id, status=status)
    page_id = v["page_id"]
    first_time = v["cms_external_id"] is None
    going_live_new = status == "publish" and v["page_status"] != "published"
    if going_live_new and live_allowance is not None and live_allowance <= 0:
        raise QuotaExceeded("live ramp allowance for today is exhausted; the page stays ready and goes live on a later day (R8)")
    if v["cms_content_hash"] == req.content_hash and not first_time:
        return PublishOutcome(page_id, version_id, v["cms_external_id"], False, False, status)
    # path change → redirect old path
    redirect_from = None
    with conn.cursor() as cur:
        cur.execute("SELECT redirect_to_path FROM pages WHERE id=%s", (page_id,))
    res: PublishResult = cms.upsert(req)
    with conn.cursor() as cur:
        cur.execute(
            """UPDATE pages SET cms_external_id=%s, cms_content_hash=%s, current_version_id=%s,
               status = CASE WHEN %s='publish' THEN 'published' ELSE 'staged' END,
               first_published_at = CASE WHEN %s='publish' AND first_published_at IS NULL THEN now() ELSE first_published_at END,
               last_material_update_at = CASE WHEN %s THEN now() ELSE last_material_update_at END WHERE id=%s""",
            (res.cms_id, res.content_hash, version_id, status, status, v["is_material_change"] and res.changed, page_id),
        )
    conn.commit()
    if status == "publish":
        from .. import ramp
        ramp.record_release(conn, page_id, version_id, kind="new" if going_live_new else "update", niche_score=niche_score)
    return PublishOutcome(page_id, version_id, res.cms_id, res.created, res.changed, status, redirect_from)


def publish_local(conn: psycopg.Connection, cms, version_id: UUID, *, settings, out_root=None) -> dict:
    """R8 before a live domain exists: render the passed version to build/site/, upsert it as a draft to the
    local staging CMS when one is connected, mark the page ready and locally published. No quota, ever."""
    from .. import ramp
    from ..render import site

    out = site.render_version(conn, version_id, out_root=out_root or site.OUT_DEFAULT, environment="staging",
                              publication_name=settings.publication_name)
    with conn.cursor() as cur:
        cur.execute("SELECT page_id FROM page_versions WHERE id=%s", (version_id,))
        page_id = cur.fetchone()["page_id"]
    cms_outcome = None
    if cms is not None and cms.capability().state in ("connected", "fixture"):
        cms_outcome = publish_version(conn, cms, version_id, environment="staging", auto_publish=False)
    ramp.mark_ready(conn, page_id)
    with conn.cursor() as cur:
        cur.execute("UPDATE pages SET local_published_at=now(), current_version_id=%s, status=CASE WHEN status IN ('planned','drafting','held') THEN 'staged' ELSE status END WHERE id=%s",
                    (version_id, page_id))
    conn.commit()
    return {"page_id": str(page_id), "version_id": str(version_id), "site_path": str(out), "cms": (cms_outcome.__dict__ if cms_outcome else None)}


def release_live(conn: psycopg.Connection, cms, *, settings, now=None) -> dict:
    """R8 with a live domain: take ready pages best niche_score first and publish up to today's ramp allowance.
    Pages left over stay ready. Never called without settings.is_live."""
    from .. import ramp

    if not settings.is_live:
        return {"released": [], "skipped": "no live domain", "allowance": None}
    today = ramp._today(now)
    ramp.ensure_live_since(conn, today)
    allow = ramp.allowance(conn, settings.quotas.live_ramp, now=now)
    released = []
    remaining = allow["remaining"]
    for row in ramp.ready_queue(conn):
        if remaining <= 0:
            break
        o = publish_version(conn, cms, row["version_id"], environment="production", auto_publish=True, live_allowance=remaining,
                            niche_score=float(row["niche_score"]) if row["niche_score"] is not None else None)
        released.append({"page_id": str(o.page_id), "path": row["path"], "niche_score": row["niche_score"]})
        remaining -= 1
    allow_after = ramp.allowance(conn, settings.quotas.live_ramp, now=now)
    return {"released": released, "allowance": allow_after, "still_ready": len(ramp.ready_queue(conn))}


def move_page(conn: psycopg.Connection, cms, page_id: UUID, new_path: str, new_slug: str) -> None:
    """Rename a page's path (e.g. building renamed) keeping its immutable id; CMS gets a redirect."""
    with conn.cursor() as cur:
        cur.execute("SELECT path FROM pages WHERE id=%s", (page_id,))
        old = cur.fetchone()["path"]
        if old == new_path:
            return
        cur.execute("UPDATE pages SET path=%s, slug=%s, cms_content_hash=NULL WHERE id=%s", (new_path, new_slug, page_id))
        cur.execute("INSERT INTO pages (page_format, slug, path, status, redirect_to_path) VALUES ('explainer', %s, %s, 'redirected', %s) ON CONFLICT (path) DO UPDATE SET status='redirected', redirect_to_path=EXCLUDED.redirect_to_path",
                    (old.strip("/").split("/")[-1] + "-redirect", old, new_path))
    conn.commit()
    cms.add_redirect(old, new_path)
