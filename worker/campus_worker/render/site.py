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


# ---------------------------------------------------------------------------------------------- site shell (R8 local publish)
POLICY_DIR = Path(__file__).parent / "content" / "policies"


def _shell_ctx(path: str, template_name: str, section: str, *, environment: str, publication_name: str, base_url: str, **extra) -> dict:
    ctx = engine.site_defaults(publication_name=publication_name, environment=environment, base_url=base_url)
    ctx.update(canonical_path=path, template_name=template_name, static_prefix="/static/", today=datetime.now(timezone.utc).date(), noindex=(environment != "production"),
               compact_masthead=template_name not in ("home",), current_section=section, ad_slots={}, related=[])
    ctx.update(extra)
    return ctx


def published_pages(conn: psycopg.Connection) -> list[dict]:
    """Pages in the local build: every page whose current version passed the editorial gate and is not held (R8 publishes each at once)."""
    with conn.cursor() as cur:
        cur.execute("""SELECT p.id, p.path, p.page_format, p.audience, p.status, p.local_published_at, p.first_published_at, p.last_material_update_at, p.institution_id, p.place_id, p.topic_id,
                              v.headline, v.deck, v.byline, v.created_at AS version_created_at, v.change_summary,
                              i.canonical_name AS school_name, i.slug AS school_slug, t.key AS topic_key, t.label AS topic_label
                       FROM pages p JOIN page_versions v ON v.id=p.current_version_id LEFT JOIN institutions i ON i.id=p.institution_id LEFT JOIN topics t ON t.id=p.topic_id
                       WHERE v.gate_status='passed' AND (p.status NOT IN ('held','redirected','retired','planned') OR (p.status='held' AND p.revalidation_reason LIKE 'seo_gate failed%%'))
                       ORDER BY COALESCE(p.last_material_update_at, p.local_published_at, v.created_at) DESC""")
        return [dict(r) for r in cur.fetchall()]


def render_shell(conn: psycopg.Connection, *, out_root: Path = OUT_DEFAULT, environment: str = "staging", publication_name: str = "The Campus Ledger (working title)",
                 base_url: str = "") -> list[Path]:
    """Home, schools index, school and topic hubs, policies, search and 404 for the local build, from the database (never fixtures).
    Hubs link every published page, which is where a page's first inbound link comes from (R45 no-orphan rule)."""
    import shutil

    out_root.mkdir(parents=True, exist_ok=True)
    static_out = out_root / "static"
    if static_out.exists():
        shutil.rmtree(static_out)
    shutil.copytree(engine.STATIC_DIR, static_out)
    pages = published_pages(conn)
    kw = dict(environment=environment, publication_name=publication_name, base_url=base_url)
    written: list[Path] = []

    def emit(rel: str, template: str, ctx: dict) -> None:
        p = out_root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(engine.render(template, **ctx))
        written.append(p)

    with conn.cursor() as cur:
        cur.execute("SELECT count(*) AS n FROM institutions WHERE identity_status IN ('verified','pending_verification')")
        registry_count = cur.fetchone()["n"]
        cur.execute("SELECT id, canonical_name, slug, city, state_code, institution_type, control, identity_status FROM institutions WHERE id = ANY(%s) ORDER BY canonical_name",
                    (list({p["institution_id"] for p in pages if p["institution_id"]}),))
        schools = [dict(r) for r in cur.fetchall()]
        cur.execute("SELECT id, key, label, description, sort_order FROM topics WHERE scope='school' AND NOT auto_created ORDER BY sort_order, key")
        topics = [dict(r) for r in cur.fetchall()]
    by_school: dict = {}
    for p in pages:
        by_school.setdefault(p["institution_id"], []).append(p)
    type_label = lambda t: (t or "institution").replace("_", " ").capitalize()
    for s in schools:
        sp = by_school.get(s["id"], [])
        by_topic: dict = {}
        for p in sp:
            by_topic.setdefault(p["topic_id"], []).append(p)
        school_href = f"/schools/{s['slug']}/"
        topic_rows = []
        for t in topics:
            n = len(by_topic.get(t["id"], []))
            topic_rows.append({"label": t["label"], "applicability": "applicable" if n else "unknown", "href": f"{school_href}{t['key']}/" if n else "#", "page_count": n})
        changes = [{"href": p["path"], "headline": p["headline"], "change": p["change_summary"] or "published", "date": p["last_material_update_at"] or p["local_published_at"] or p["version_created_at"]} for p in sp[:5]]
        school = {"name": s["canonical_name"], "city": s["city"], "state": s["state_code"], "type_label": type_label(s["institution_type"]), "control": (s["control"] or "").replace("_", " "),
                  "identity_status": s["identity_status"], "identity_note": "" if s["identity_status"] == "verified" else "Identity pending verification against the NCES institution registry.",
                  "coverage_note": f"{len(sp)} published guide{'s' if len(sp) != 1 else ''}", "coverage_status": "pilot" if sp else "onboarding",
                  "topics": topic_rows, "guides": [{"topic": p["topic_label"], "href": p["path"], "headline": p["headline"], "deck": p["deck"]} for p in sp], "tools": [], "changes": changes,
                  "topics_applicable": [t["label"].lower() for t in topic_rows if t["page_count"]]}
        emit(f"schools/{s['slug']}/index.html", "school_hub.html", _shell_ctx(school_href, "school_hub", "/schools/", school=school, **kw))
        for t in topics:
            tp = by_topic.get(t["id"], [])
            if not tp:
                continue
            topic = {"label": t["label"], "description": t["description"] or f"{t['label']} at {s['canonical_name']}: verified facts from official pages, with the date we checked.", "applicability": "applicable",
                     "key_fact_label": None, "profiles": [{"name": p["headline"], "href": p["path"], "key_fact": "", "verified_at": p["local_published_at"] or p["version_created_at"]} for p in tp if p["page_format"] in ("entity_profile", "profile")],
                     "guides": [{"href": p["path"], "headline": p["headline"], "deck": p["deck"]} for p in tp if p["page_format"] not in ("entity_profile", "profile")], "tools": [], "unknowns": [], "empty_note": ""}
            emit(f"schools/{s['slug']}/{t['key']}/index.html", "topic_hub.html", _shell_ctx(f"{school_href}{t['key']}/", "topic_hub", f"/topics/{t['key']}/", school={"name": s["canonical_name"], "href": school_href}, topic=topic, **kw))
    school_cards = [{"name": s["canonical_name"], "href": f"/schools/{s['slug']}/", "city": s["city"], "state": s["state_code"], "type_label": type_label(s["institution_type"]), "pages": len(by_school.get(s["id"], []))} for s in schools]
    emit("schools/index.html", "schools_index.html", _shell_ctx("/schools/", "schools_index", "/schools/", registry_count=registry_count, release="NCES HD2024", schools=school_cards, **kw))
    lead = None
    supporting = []
    if pages:
        p = pages[0]
        lead = {"section": f"{p['topic_label']} · {p['school_name']}", "section_href": _hub_for(p["path"])[0], "href": p["path"], "headline": p["headline"], "deck": p["deck"], "byline": p["byline"],
                "updated": p["last_material_update_at"] or p["local_published_at"] or p["version_created_at"]}
        supporting = [{"section": q["topic_label"], "href": q["path"], "headline": q["headline"], "deck": q["deck"]} for q in pages[1:4]]
    updates = [{"href": p["path"], "headline": p["headline"], "change": p["change_summary"] or "published", "date": p["last_material_update_at"] or p["local_published_at"] or p["version_created_at"]} for p in pages[:5]]
    emit("index.html", "home.html", _shell_ctx("/", "home", "/", lead=lead, supporting=supporting, coverage={"schools_with_coverage": len(schools), "registry_count": registry_count}, tools=[],
                                              schools=[{"name": c["name"], "href": c["href"], "pages": c["pages"]} for c in school_cards], updates=updates, **kw))
    for key in ("methods", "corrections", "privacy", "independence"):
        md_path = POLICY_DIR / f"{key}.md"
        if not md_path.exists():
            continue
        md = md_path.read_text()
        title, _, body = md.partition("\n")
        emit(f"about/{key}/index.html", "policy.html", _shell_ctx(f"/about/{key}/", "policy", "/about/methods/", policy={"title": title.lstrip("# ").strip(), "summary": body.strip().split("\n")[0], "body_markdown": body, "updated_at": datetime.now(timezone.utc).date()}, **kw))
    emit("404.html", "not_found.html", _shell_ctx("/404", "not_found", "/", **kw))
    return written
