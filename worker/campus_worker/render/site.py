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


# ---------------------------------------------------------------------------------------------- process navigator (R47)
def navigator_context(conn: psycopg.Connection, graph_id: UUID, *, school_slug: str, school_name: str, topic_key: str, environment: str = "staging",
                      publication_name: str = "The Campus Ledger (working title)", base_url: str = "", selected: dict | None = None) -> tuple[dict, str]:
    """Server-rendered navigator page context: options, the embedded graph, and the answer for the selected (or first) path."""
    import json as _json
    from ..tools import navigator as nav

    with conn.cursor() as cur:
        cur.execute("SELECT key, name, description, tool_path FROM process_graphs WHERE id=%s", (graph_id,))
        g = cur.fetchone()
        cur.execute("SELECT id, parent_id, layer, key, label, from_state, to_state, situation, rules, inherits_parent, page_decision, page_path, source_urls FROM process_nodes WHERE graph_id=%s ORDER BY layer, key", (graph_id,))
        nodes = [dict(r) for r in cur.fetchall()]
    opts = nav.options(conn, graph_id)
    sel = selected or {}
    from_state = sel.get("from") or (opts["from_states"][0] if opts["from_states"] else "")
    to_state = sel.get("to") or next((n["to_state"] for n in nodes if n["layer"] == 1 and n["from_state"] == from_state), (opts["to_states"][0] if opts["to_states"] else ""))
    sits = sel.get("situations") or []
    a = nav.answer(conn, graph_id, from_state=from_state, to_state=to_state, situations=sits)
    topic_slug = topic_key.replace("_", "-")
    path = g["tool_path"] or f"/schools/{school_slug}/{topic_slug}/tools/{g['key']}-navigator/"
    label = lambda s: s.replace("-", " ").title()
    sources = sorted({u for n in nodes for u in (n.get("source_urls") or [])})
    ctx = engine.site_defaults(publication_name=publication_name, environment=environment, base_url=base_url)
    now = datetime.now(timezone.utc)
    ctx.update(canonical_path=path, template_name="navigator", static_prefix="/static/", today=now.date(), noindex=(environment != "production"), compact_masthead=True,
               current_section=f"/schools/{school_slug}/{topic_slug}/", ad_slots={}, related=[],
               structured_data=_json.dumps([{"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
                   {"@type": "ListItem", "position": 1, "name": school_name, "item": f"{base_url}/schools/{school_slug}/"},
                   {"@type": "ListItem", "position": 2, "name": label(topic_key), "item": f"{base_url}/schools/{school_slug}/{topic_slug}/"},
                   {"@type": "ListItem", "position": 3, "name": g["name"], "item": f"{base_url}{path}"}]},
                   {"@context": "https://schema.org", "@type": "WebPage", "name": f"{g['name']} navigator", "description": g["description"] or "", "url": f"{base_url}{path}"}]))
    answer = {"found": a.found, "heading": " · ".join(n["label"] for n in a.path_nodes) if a.found else "No documented path", "steps": a.steps, "prerequisites": a.prerequisites,
              "course_requirements": a.course_requirements, "gpa_min": a.gpa_min, "deadlines": a.deadlines, "forms": a.forms, "offices": a.offices, "exceptions": a.exceptions, "message": a.message}
    ctx["nav"] = {"id": str(graph_id), "title": f"{g['name']} navigator: {school_name}", "description": (g["description"] or f"Pick where you are and where you want to go at {school_name}; see the exact steps, requirements, deadlines and offices from official pages.")[:155],
                  "answer_first": (f"From {label(from_state)} to {label(to_state)}: {len(a.steps)} steps, minimum GPA {a.gpa_min or 'not stated'}, owned by {', '.join(a.offices) or 'the receiving college'}." if a.found else a.message),
                  "section": f"{school_name} · {label(topic_key)}", "section_href": f"/schools/{school_slug}/{topic_slug}/", "action": path, "academic_year": sel.get("academic_year") or f"{now.year}-{str(now.year + 1)[2:]}",
                  "updated_at": now, "from_states": [{"value": s, "label": label(s)} for s in opts["from_states"]], "to_states": [{"value": s, "label": label(s)} for s in opts["to_states"]],
                  "situations": [{"value": s, "label": s.capitalize()} for s in opts["situations"]], "selected_from": from_state, "selected_to": to_state, "selected_situations": sits, "answer": answer,
                  "graph_json": _json.dumps({"nodes": [{"id": str(n["id"]), "parent_id": str(n["parent_id"]) if n["parent_id"] else None, "layer": n["layer"], "key": n["key"], "label": n["label"],
                                                        "from_state": n["from_state"], "to_state": n["to_state"], "situation": n["situation"], "rules": n["rules"], "inherits_parent": n["inherits_parent"]} for n in nodes]}),
                  "breadcrumbs": [{"href": f"/schools/{school_slug}/", "text": school_name}, {"href": f"/schools/{school_slug}/{topic_slug}/", "text": label(topic_key)}, {"href": path, "text": g["name"]}],
                  "method": "Every path is resolved from a process graph filled from official college, department and registrar pages: the transition you pick, plus any situation-specific rules layered on top. A node whose rules match its parent adds nothing; nothing is generated per combination.",
                  "limitations": "This is a navigator of published rules, not an advising decision. Offices change deadlines and requirements; the source list below is what we verified and when.",
                  "related": [{"href": n["page_path"], "text": n["label"]} for n in nodes if n.get("page_path") and n["page_decision"] == "standalone"][:6],
                  "next_actions": [{"text": f"Read the {g['name'].lower()} overview", "target": next((n["page_path"] for n in nodes if n["layer"] == 0 and n.get("page_path")), f"/schools/{school_slug}/{topic_slug}/")},
                                   {"text": f"{label(topic_key)} at {school_name}", "target": f"/schools/{school_slug}/{topic_slug}/"}],
                  "sources": [{"url": u, "title": u.split("//", 1)[-1][:80], "publisher": school_name, "retrieved_at": now, "kind": "official page"} for u in sources],
                  "production_note": "Rendered from the process graph; rules carry claim ids and source URLs. No human editor reviewed this version unless named in the correction history."}
    return ctx, path


def render_navigator(conn: psycopg.Connection, graph_id: UUID, *, school_slug: str, school_name: str, topic_key: str, out_root: Path = OUT_DEFAULT,
                     environment: str = "staging", selected: dict | None = None, publication_name: str = "The Campus Ledger (working title)", base_url: str = "") -> Path:
    ctx, path = navigator_context(conn, graph_id, school_slug=school_slug, school_name=school_name, topic_key=topic_key, environment=environment, selected=selected,
                                  publication_name=publication_name, base_url=base_url)
    html = engine.render("navigator.html", **ctx)
    out = out_root / path.strip("/") / "index.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html)
    # static assets next to the build so screenshot QA can load CSS/JS
    static_src = Path(__file__).parent / "static"
    static_dst = out_root / "static"
    if not static_dst.exists():
        import shutil
        shutil.copytree(static_src, static_dst)
    return out
