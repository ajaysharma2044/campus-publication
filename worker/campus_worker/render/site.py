"""Render a gated page version to the local site build (continuous-local-run R8: build/site/).

Deterministic: same version → same HTML. Only versions whose gate passed are rendered here; held drafts
are the preview renderer's job (session_run) and carry a held notice.
"""
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from uuid import UUID

import psycopg

from ..config import REPO_ROOT
from . import engine

OUT_DEFAULT = REPO_ROOT / "build" / "site"
TEMPLATE_BY_FORMAT = {"guide": "article.html", "explainer": "article.html", "entity_profile": "article.html", "comparison": "article.html",
                      "tool": "article.html", "policy": "policy.html"}


def _hub_for(path: str) -> tuple[str, str]:
    parts = [p for p in path.split("/") if p]
    if len(parts) >= 3 and parts[0] in ("schools", "towns"):
        return "/".join(["", parts[0], parts[1], parts[2], ""]), parts[1].replace("-", " ").title() + " · " + parts[2].replace("-", " ").title()
    if len(parts) >= 2:
        return "/" + "/".join(parts[:2]) + "/", parts[1].replace("-", " ").title()
    return "/", ""


def version_context(conn: psycopg.Connection, version_id: UUID, *, environment: str, publication_name: str, base_url: str = "") -> tuple[dict, dict]:
    from ..cms.publisher import _sources_for_version  # local import: publisher imports this module too

    with conn.cursor() as cur:
        cur.execute("""SELECT v.*, p.path, p.page_format, p.audience, p.first_published_at, p.last_material_update_at, p.institution_id
                       FROM page_versions v JOIN pages p ON p.id=v.page_id WHERE v.id=%s""", (version_id,))
        v = cur.fetchone()
    if v is None:
        raise LookupError("version not found")
    if v["gate_status"] != "passed":
        raise ValueError(f"version gate_status={v['gate_status']}; only passed versions render to the site build")
    structured = dict(v["structured"] or {})
    section_href, section = _hub_for(v["path"])
    published = v["first_published_at"] or v["created_at"]
    updated = v["last_material_update_at"] or v["created_at"]
    ctx = engine.site_defaults(publication_name=publication_name, environment=environment, base_url=base_url)
    ctx.update(canonical_path=v["path"], template_name=v["page_format"], static_prefix="/static/", today=datetime.now(timezone.utc).date(),
               noindex=(environment != "production"), compact_masthead=True, current_section=section_href, ad_slots={}, related=[],
               structured_data=structured.get("json_ld", ""))
    ctx["page"] = {"id": str(v["page_id"]), "headline": v["headline"], "deck": v["deck"], "section": section, "section_href": section_href,
                   "byline": v["byline"], "published_at": published, "updated_at": updated,
                   "audience_label": (v["audience"] or "").replace("_", " ") or None, "body_markdown": v["body_markdown"],
                   "fact_table": structured.get("fact_table", []), "fact_table_caption": structured.get("fact_table_caption"),
                   "fact_table_footnote": structured.get("fact_table_footnote"), "next_actions": structured.get("next_actions", []),
                   "production_note": v["production_note"], "sources": _sources_for_version(conn, version_id) or structured.get("sources", []),
                   "held_notice": None, "stale": False}
    return ctx, dict(v)


def render_version(conn: psycopg.Connection, version_id: UUID, *, out_root: Path = OUT_DEFAULT, environment: str = "staging",
                   publication_name: str = "The Campus Ledger (working title)", base_url: str = "") -> Path:
    ctx, v = version_context(conn, version_id, environment=environment, publication_name=publication_name, base_url=base_url)
    html = engine.render(TEMPLATE_BY_FORMAT.get(v["page_format"], "article.html"), **ctx)
    out = out_root / v["path"].strip("/") / "index.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html)
    return out
