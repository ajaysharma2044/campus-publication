"""Stages 1-2 (code only): plan the page list from the ranked question map, then gather each page's facts and source quotes from the
dossier (the database), never from the web. Existing pages are skipped unless their sources changed (sources hash)."""
from __future__ import annotations

import hashlib
import json
from uuid import UUID

import psycopg

from ..seo_gate import _contains_query, _hubs_for
from .dossier import human_value
from .util import slugify


def _stems(text: str) -> set[str]:
    import re
    from ..seo_gate import STOP
    out = set()
    for w in re.findall(r"[a-z0-9']+", (text or "").lower().replace("\u2019", "'")):
        w = w.replace("'s", "")
        if w in STOP or len(w) < 2:
            continue
        for suf in ("ing", "ies", "ed", "es", "s"):
            if len(w) > 4 and w.endswith(suf):
                w = w[: -len(suf)] + ("y" if suf == "ies" else "")
                break
        out.add(w)
    return out


def covered_by(existing: list[dict], primary_query: str, question: str) -> str | None:
    """The path of a live or planned page that asks the same question: stemmed content words of the two primary queries overlap at least
    85% (paraphrases: "Is housing guaranteed for transfers at Cornell?" / "Does Cornell guarantee housing for transfer students?"), or a
    specific question (4+ content words) whose words all sit in an existing title. A broad hub ("Cornell housing deadlines") is never
    swallowed by a narrower page, and an audience variant keeps its own page."""
    mine = _stems(primary_query) | (_stems(question) if not primary_query else set())
    if not mine:
        return None
    for e in existing:
        theirs = _stems(e.get("primary_query") or e.get("headline") or "")
        if theirs:
            j = len(mine & theirs) / len(mine | theirs)
            if j >= 0.85:
                return e["path"]
        title = _stems(e.get("headline") or "")
        if len(mine) >= 4 and mine <= title:
            return e["path"]
    return None


TEMPLATES = {
    "question_guide": ["answer", "details", "costs_and_dates", "steps_if_any", "not_confirmed", "next_steps"],
    "entity_guide": ["answer", "at_a_glance", "what_is_there", "who_and_placement", "rules_and_costs", "how_to_apply", "contact", "not_confirmed", "next_steps"],
    "process_guide": ["answer", "steps", "deadlines", "exceptions", "contact", "not_confirmed", "next_steps"],
    "comparison": ["answer", "comparison_table", "differences", "not_confirmed", "next_steps"],
}
TOWN_TOPICS = {"town_services", "town_transit_local", "town_transit_intercity", "town_neighborhoods", "town_offcampus_housing", "town_food", "town_outdoors", "town_weather", "town_jobs", "town_government"}
MAX_FACTS = 40


def path_for(q: dict, *, school_slug: str, place_slug: str | None) -> str:
    topic = (q.get("topic_key") or "housing").replace("_", "-")
    if q.get("topic_key") in TOWN_TOPICS and place_slug:
        scope = f"/towns/{place_slug}"
        topic = topic.replace("town-", "")
    else:
        scope = f"/schools/{school_slug}"
    if q["page_type"] == "entity_guide" and q.get("entity_slug"):
        slug = q["entity_slug"]
    elif q.get("answer_key", "").startswith("hub:"):
        slug = slugify(q.get("stored_pq") or q["question"], keep_stop=False)   # /schools/cornell-university/housing/cornell-housing-deadlines/
    else:
        slug = slugify(q["question"])
        if (q.get("audience") or "general") not in ("general", None) and q["page_type"] != "entity_guide":
            slug = f"{slug}-{slugify(q['audience'])}"
    return f"{scope}/{topic}/{slug}/"


def short_school_name(name: str) -> str:
    """'Cornell University' → 'Cornell'; 'Fixture State University' → 'Fixture State': the words a searcher types."""
    import re
    return re.sub(r"\b(University|College|Institute|of Technology|the)\b", "", name).strip(" ,-") or name


def primary_query_for(q: dict, *, school_name: str) -> str:
    """The query whose content words the title must carry (R45): the question itself, or for an entity guide the entity plus the school's short name."""
    if q["page_type"] == "entity_guide" and q.get("entity_name"):
        return f"{q['entity_name']} {short_school_name(school_name)}"
    return q["question"]


def plan_pages(conn: psycopg.Connection, *, institution_id: UUID, limit: int, run_id: str, include_existing: bool = False) -> dict:
    with conn.cursor() as cur:
        cur.execute("SELECT slug, canonical_name FROM institutions WHERE id=%s", (institution_id,))
        inst_row = cur.fetchone()
        school_slug, school_name = inst_row["slug"], inst_row["canonical_name"]
        cur.execute("SELECT slug FROM places WHERE kind IN ('city','town') ORDER BY name LIMIT 1")
        place_slug = (cur.fetchone() or {}).get("slug")
        cur.execute("""SELECT q.id, q.question, q.audience, q.page_type, q.answer_key, q.entity_id, q.topic_id, q.cluster_id, q.win_note, q.incumbent_class, q.tier, q.order_rank, q.primary_query AS stored_pq,
                              t.key AS topic_key, e.slug AS entity_slug, e.name AS entity_name
                       FROM bulk_questions q LEFT JOIN topics t ON t.id=q.topic_id LEFT JOIN entities e ON e.id=q.entity_id
                       WHERE q.institution_id=%s AND q.status='queued' ORDER BY q.order_rank NULLS LAST, q.created_at""", (institution_id,))
        qs = [dict(r) for r in cur.fetchall()]
        cur.execute("SELECT path FROM pages")
        existing = {r["path"] for r in cur.fetchall()}
        cur.execute("SELECT path FROM bulk_pages")
        planned_paths = {r["path"] for r in cur.fetchall()}
        cur.execute("""SELECT p.path, p.primary_query, v.headline FROM pages p JOIN page_versions v ON v.id=p.current_version_id
                       WHERE p.institution_id=%s AND v.gate_status='passed' AND p.status NOT IN ('held','retired','redirected','unpublished')""", (institution_id,))
        live = [dict(r) for r in cur.fetchall()]
        cur.execute("SELECT path, plan->>'primary_query' AS primary_query, plan->>'question' AS headline FROM bulk_pages WHERE stage IN ('planned','gathered','written','checked','verified')")
        live += [dict(r) for r in cur.fetchall()]
    planned, skipped = [], []
    for q in qs:
        if len(planned) >= limit:
            break
        path = path_for(q, school_slug=school_slug, place_slug=place_slug)
        pq = q.get("stored_pq") or primary_query_for(q, school_name=school_name)
        dup = covered_by(live, pq, q["question"])
        if (path in existing and not include_existing) or path in planned_paths or dup:
            skipped.append({"question": q["question"], "path": path, "reason": f"answered by {dup}" if dup else ("page exists" if path in existing else "already planned")})
            with conn.cursor() as cur:
                cur.execute("UPDATE bulk_questions SET status='skipped', updated_at=now() WHERE id=%s", (q["id"],))
            continue
        live.append({"path": path, "primary_query": pq, "headline": q["question"]})
        plan = {"question": q["question"], "primary_query": q.get("stored_pq") or primary_query_for(q, school_name=school_name), "audience": q["audience"], "page_type": q["page_type"], "sections": TEMPLATES[q["page_type"]], "topic_key": q["topic_key"], "entity_id": str(q["entity_id"]) if q["entity_id"] else None,
                "entity_name": q.get("entity_name"), "answer_key": q["answer_key"], "win_note": q.get("win_note"), "incumbent_class": q.get("incumbent_class"), "hubs": list(_hubs_for(path)), "order_rank": q.get("order_rank")}
        with conn.cursor() as cur:
            cur.execute("""INSERT INTO bulk_pages (question_id, path, page_type, stage, plan, run_id) VALUES (%s, %s, %s, 'planned', %s::jsonb, %s)
                           ON CONFLICT (path) DO NOTHING RETURNING id""", (q["id"], path, q["page_type"], json.dumps(plan), run_id))
            row = cur.fetchone()
            if row:
                cur.execute("UPDATE bulk_questions SET status='planned', updated_at=now() WHERE id=%s", (q["id"],))
                planned.append({"bulk_page_id": str(row["id"]), "question_id": str(q["id"]), "path": path, "page_type": q["page_type"], "question": q["question"], "cluster_id": str(q["cluster_id"]) if q["cluster_id"] else None})
                planned_paths.add(path)
        conn.commit()
    return {"planned": planned, "skipped": skipped}


def _families_for(answer_key: str, page_type: str) -> list[str]:
    if answer_key.startswith("entity:") and ":" in answer_key[7:]:
        fam = answer_key.rsplit(":", 1)[-1]
        return [] if fam == "guide" else fam.split("+")
    if answer_key.startswith("claim:"):
        return [answer_key[6:].split(".", 1)[0]]
    return []


def gather(conn: psycopg.Connection, bulk_page: dict, *, institution_id: UUID) -> dict:
    """The page's facts with their verbatim quotes, source URLs, dates and snapshot ids, plus internal link targets."""
    plan = bulk_page["plan"]
    entity_id = UUID(plan["entity_id"]) if plan.get("entity_id") else None
    families = _families_for(plan.get("answer_key") or "", plan["page_type"])
    with conn.cursor() as cur:
        cur.execute("SELECT id FROM topics WHERE key=%s", (plan.get("topic_key") or "housing",))
        topic_id = (cur.fetchone() or {}).get("id")
        cur.execute("""SELECT c.id, c.entity_id, c.field, c.value_type, c.value_text, c.value_number, c.value_bool, c.value_date, c.billing_period, c.price_basis, c.room_type, c.audience_applicability,
                              c.academic_year, c.is_critical, c.topic_id, e.name AS entity_name,
                              (SELECT json_build_object('url', COALESCE(s.final_url, r.canonical_url), 'fetched_at', s.fetched_at, 'excerpt', cs.excerpt, 'snapshot_id', s.id, 'title', r.title, 'content_hash', s.content_hash)
                                 FROM claim_sources cs JOIN fetch_snapshots s ON s.id=cs.snapshot_id JOIN source_registry r ON r.id=s.source_id
                                 WHERE cs.claim_id=c.id AND cs.excerpt IS NOT NULL AND cs.excerpt <> '' AND r.source_kind LIKE 'official%%' ORDER BY s.fetched_at DESC LIMIT 1) AS source
                       FROM claims c LEFT JOIN entities e ON e.id=c.entity_id
                       WHERE c.institution_id=%s AND c.superseded_by_id IS NULL AND c.evidence_category='verified_fact' AND c.conflict_status IS DISTINCT FROM 'conflicted'
                         AND (c.entity_id=%s OR (c.entity_id IS NULL AND c.topic_id=%s))
                       ORDER BY (c.entity_id IS NOT NULL) DESC, c.is_critical DESC, c.field""", (institution_id, entity_id, topic_id))
        rows = [dict(r) for r in cur.fetchall() if r["source"]]
    def score(c):
        fam = c["field"].split(".", 1)[0]
        return (0 if c["entity_id"] else 1, 0 if (families and fam in families) else 1, 0 if c["is_critical"] else 1)
    rows.sort(key=score)
    facts = []
    for c in rows[:MAX_FACTS]:
        facts.append({"id": str(c["id"]), "field": c["field"], "value": human_value(c), "academic_year": c.get("academic_year"), "audience": c.get("audience_applicability") or [], "entity": c.get("entity_name"),
                      "is_critical": c["is_critical"], "quote": c["source"]["excerpt"], "source_url": c["source"]["url"], "source_title": c["source"].get("title"), "fetched_at": str(c["source"]["fetched_at"])[:10],
                      "snapshot_id": str(c["source"]["snapshot_id"]), "content_hash": c["source"].get("content_hash")})
    with conn.cursor() as cur:
        cur.execute("""SELECT p.path, v.headline FROM pages p JOIN page_versions v ON v.id=p.current_version_id WHERE p.institution_id=%s AND v.gate_status='passed' AND p.status NOT IN ('held','retired','redirected')
                       ORDER BY p.last_material_update_at DESC NULLS LAST LIMIT 12""", (institution_id,))
        links = [{"path": r["path"], "anchor_hint": r["headline"]} for r in cur.fetchall() if r["path"] != bulk_page["path"]]
        cur.execute("SELECT path, plan->>'question' AS question FROM bulk_pages WHERE stage IN ('planned','gathered','written','checked','verified','published') AND path <> %s AND run_id=%s LIMIT 12", (bulk_page["path"], bulk_page.get("run_id")))
        links += [{"path": r["path"], "anchor_hint": r["question"]} for r in cur.fetchall()]
    sources_hash = hashlib.sha256("|".join(sorted({f["content_hash"] or "" for f in facts})).encode()).hexdigest()
    gathered = {"facts": facts, "link_targets": links[:10], "hubs": plan.get("hubs") or list(_hubs_for(bulk_page["path"])), "sources_hash": sources_hash, "fact_count": len(facts),
                "entity_fact_count": sum(1 for f in facts if f["entity"]), "has_money": any("$" in f["value"] for f in facts), "has_dates": any(f["field"].startswith("deadline") or ", 20" in f["value"] for f in facts)}
    with conn.cursor() as cur:
        cur.execute("UPDATE bulk_pages SET gathered=%s::jsonb, sources_hash=%s, stage=CASE WHEN %s >= 1 THEN 'gathered' ELSE 'skipped' END, skip_reason=CASE WHEN %s >= 1 THEN NULL ELSE 'no verified fact with a quote in scope' END, updated_at=now() WHERE id=%s",
                    (json.dumps(gathered), sources_hash, len(facts), len(facts), bulk_page["id"]))
    conn.commit()
    return gathered
