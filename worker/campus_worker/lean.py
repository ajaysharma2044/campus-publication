"""LEAN MODE (owner decision 2026-11-06, logged in STATE.md; overrides specs/continuous-local-run.md where they conflict).

CAMPUS_LEAN_MODE=1 (the default) switches on:
  - demand evidence and sweet-spot scores only order the work: any observed cluster that is not navigational and has no strong
    dedicated incumbent (AGI ≥ 2) gets a page once its scope has at least one verified fact (funnel.qualify, lanes.production_item);
  - information-gain minimum 1 verified, claim-linked item (quality.check_information_gain);
  - tier-2 profiles need 4 verified claims instead of 6 (tier2);
  - the competitor-beat review runs on every 10th produced page as a spot check; the others get the editor pass only (pipeline.run_r16);
  - the sweep intel cap defaults to 5000 so every deferred cluster gets observed (sweep.sweep_cap).
Unchanged: verified, sourced, dated facts; access modes and robots; no fake reviews or copied text; the editorial gates and rubric;
the critical-claim rule; the SEO gate; the 60% overlap rule. CAMPUS_LEAN_MODE=0 restores the spec's thresholds (the test suite runs that way
for the spec's acceptance tests, plus tests/test_lean.py for this mode).

CLI:  python -m campus_worker.lean queue [--limit N] [--json]   the lean production queue as planned pages (question_id, path, page_type,
      question, cluster_id): the page-list fallback of scripts/parallel_headless.sh when no `campus_worker.bulk plan` output is given (specs/bulk-mode.md section 3).
"""
from __future__ import annotations

import os
from uuid import UUID

import psycopg

MIN_GAIN_ITEMS_LEAN = 1
TIER2_MIN_CLAIMS_LEAN = 4
BEAT_REVIEW_EVERY = 10
STRONG_INCUMBENT_AGI = 1           # AGI 0 or 1: a dedicated, current, sourced page already answers it
SWEEP_INTEL_CAP_LEAN = 5000
MAX_VERIFIER_ROUNDS = 3           # owner decision 2026-11-06 (reader-first, efficiency): after 3 verifier rounds, cut the unverifiable claim and publish, or skip the page


def enabled() -> bool:
    return (os.environ.get("CAMPUS_LEAN_MODE", "1") or "1").strip().lower() not in ("0", "false", "no", "off")


def verified_claims_in_scope(conn: psycopg.Connection, *, institution_id: UUID | None, place_id: UUID | None, topic_id: UUID | None, entity_id: UUID | None = None) -> int:
    """Current verified facts for the cluster's scope: an entity cluster needs facts about that entity; a topic cluster needs facts for the
    school-or-town + topic (topic-less claims count for every topic of the scope)."""
    with conn.cursor() as cur:
        if entity_id:
            cur.execute("""SELECT count(*) AS n FROM claims WHERE entity_id=%s AND evidence_category='verified_fact' AND superseded_by_id IS NULL AND conflict_status <> 'open'""", (entity_id,))
            return int(cur.fetchone()["n"])
        if institution_id:
            cur.execute("""SELECT count(*) AS n FROM claims WHERE institution_id=%s AND (topic_id=%s OR topic_id IS NULL) AND evidence_category='verified_fact'
                           AND superseded_by_id IS NULL AND conflict_status <> 'open'""", (institution_id, topic_id))
        elif place_id:
            cur.execute("""SELECT count(*) AS n FROM claims c JOIN entities e ON e.id=c.entity_id WHERE e.place_id=%s AND (c.topic_id=%s OR c.topic_id IS NULL)
                           AND c.evidence_category='verified_fact' AND c.superseded_by_id IS NULL AND c.conflict_status <> 'open'""", (place_id, topic_id))
        else:
            return 0
        return int(cur.fetchone()["n"])


# owner decision 2026-11-06 (reader-first, topic choice): practical, high-traffic questions first; a lower rank wins the queue before niche_score
PRACTICAL_TOPIC_RANK = {"costs_aid": 0, "parents_billing": 0, "admissions": 1, "housing": 1, "daily_life": 2, "dining": 2, "transportation": 3, "town_transit_local": 3,
                        "town_transit_intercity": 3, "town_offcampus_housing": 3, "parents_calendar": 4, "parents_prep": 4, "parents_logistics": 4, "parents_visitors": 4, "transfer": 4,
                        "courses": 5, "programs": 5, "services": 6, "health_wellbeing": 6, "accessibility": 6}
PRACTICAL_TOPIC_DEFAULT_RANK = 9


def topic_rank(topic_key: str | None) -> int:
    return PRACTICAL_TOPIC_RANK.get(topic_key or "", PRACTICAL_TOPIC_DEFAULT_RANK)


def production_queue(conn: psycopg.Connection, *, limit: int = 20) -> list[dict]:
    """Lean production order: every observed, non-navigational cluster without a strong incumbent that has a verified fact in scope,
    practical topics first (costs, deadlines, housing, dining, transit, parents: owner decision 2026-11-06), then best niche_score.
    in_production/done clusters are excluded; D only orders."""
    with conn.cursor() as cur:
        cur.execute("""SELECT c.id AS cluster_id, c.label, c.best_variant, c.d_score AS d, c.agi, c.g_est AS g, c.e_est AS e, c.niche_score, c.capture_format,
                              c.queue_state, c.institution_id, c.place_id, c.topic_id, t.key AS topic_key
                       FROM intent_clusters c LEFT JOIN topics t ON t.id=c.topic_id
                       WHERE c.last_intel_at IS NOT NULL AND c.queue_state IN ('sweet_spot','watch','reject') AND c.agi IS NOT NULL AND c.agi > %s
                       ORDER BY c.niche_score DESC NULLS LAST, c.agi DESC, c.d_score DESC NULLS LAST, c.updated_at LIMIT %s""", (STRONG_INCUMBENT_AGI, limit * 5))
        rows = [dict(r) for r in cur.fetchall()]
    rows.sort(key=lambda r: (topic_rank(r.get("topic_key")), -(r.get("niche_score") or 0)))
    out = []
    for r in rows:
        # an entity cluster enters the queue without facts: the pipeline researches the entity's own official page first (ensure_research);
        # a topic cluster needs a verified fact in its scope (there is no single page to research for it)
        if r.get("entity_id") or verified_claims_in_scope(conn, institution_id=r["institution_id"], place_id=r["place_id"], topic_id=r["topic_id"]) >= 1:
            out.append(r)
            if len(out) >= limit:
                break
    return out


def spot_check_due(pages_produced_before: int) -> bool:
    """The competitor-beat review runs on the 10th, 20th, … produced page (and the very first, so the review path is exercised)."""
    return pages_produced_before == 0 or (pages_produced_before + 1) % BEAT_REVIEW_EVERY == 0


def pages_produced(conn: psycopg.Connection) -> int:
    with conn.cursor() as cur:
        cur.execute("SELECT count(DISTINCT page_id) AS n FROM page_versions WHERE writer_model LIKE 'agent:writer%%'")
        return int(cur.fetchone()["n"])


def covered_by_existing_page(conn: psycopg.Connection, *, cluster_id: UUID) -> str | None:
    """The path of a page in the same scope whose title, headings, primary query or planned secondary questions already carry every content
    word of the cluster's question (the 60% overlap rule's cheap front door: no second page for a question an existing page answers)."""
    import re
    from .seo_gate import _contains_query
    with conn.cursor() as cur:
        cur.execute("SELECT label, best_variant, institution_id, place_id, topic_id FROM intent_clusters WHERE id=%s", (cluster_id,))
        c = cur.fetchone()
        cur.execute("""SELECT p.path, p.primary_query, v.headline, v.body_markdown FROM pages p LEFT JOIN page_versions v ON v.id=p.current_version_id
                       WHERE p.institution_id IS NOT DISTINCT FROM %s AND p.place_id IS NOT DISTINCT FROM %s AND p.topic_id=%s AND p.status NOT IN ('redirected','retired')""",
                    (c["institution_id"], c["place_id"], c["topic_id"]))
        pages = [dict(r) for r in cur.fetchall()]
        cur.execute("SELECT page_path, query_norm FROM query_targets")
        targets = [dict(r) for r in cur.fetchall()]
    questions = [q for q in (c["label"], c["best_variant"]) if q]
    for pg in pages:
        texts = [pg.get("headline") or "", pg.get("primary_query") or ""] + re.findall(r"^#{1,3} (.+)$", pg.get("body_markdown") or "", re.M)
        texts += [t["query_norm"] for t in targets if t["page_path"] == pg["path"]]
        for q in questions:
            if any(_contains_query(t, q) for t in texts if t):
                return pg["path"]
    return None


def default_page_path(conn: psycopg.Connection, *, cluster_id: UUID) -> str:
    """LEAN MODE: a page path for a cluster no strategist win plan named: /schools|towns/<scope>/<topic>/<slug-of-the-question>/."""
    import re
    with conn.cursor() as cur:
        cur.execute("""SELECT c.label, c.best_variant, t.key AS topic_key, i.slug AS school_slug, p.slug AS place_slug FROM intent_clusters c
                       LEFT JOIN topics t ON t.id=c.topic_id LEFT JOIN institutions i ON i.id=c.institution_id LEFT JOIN places p ON p.id=c.place_id WHERE c.id=%s""", (cluster_id,))
        c = cur.fetchone()
    text = re.sub(r"[\u2019']s\b", "", (c["best_variant"] or c["label"] or "").lower())  # possessives: "cornell's" → "cornell"
    stop = {"a", "an", "the", "of", "at", "in", "on", "for", "to", "is", "are", "do", "does", "did", "what", "when", "where", "how", "can", "i", "my", "and", "or", "be", "with", "by", "it", "its", "there", "any", "have", "has", "will", "should", "you", "your"}
    words = [w for w in re.findall(r"[a-z0-9]+", text) if w not in stop]
    slug = "-".join(words)[:60].strip("-") or "guide"
    scope = f"/schools/{c['school_slug']}/" if c["school_slug"] else f"/towns/{c['place_slug']}/"
    return f"{scope}{c['topic_key']}/{slug}/"


def synthetic_win_plan(conn: psycopg.Connection, *, cluster_id: UUID, page_path: str) -> dict:
    """LEAN MODE: the minimal plan a cluster gets when no strategist win plan names it — the page answers the observed question from
    verified facts; an entity cluster becomes a factual profile (never a review: no resident experience without an allowed source)."""
    with conn.cursor() as cur:
        cur.execute("""SELECT c.label, c.best_variant, c.entity_id, e.name AS entity_name, e.entity_type, i.canonical_name AS school, p.name AS place FROM intent_clusters c
                       LEFT JOIN entities e ON e.id=c.entity_id LEFT JOIN institutions i ON i.id=c.institution_id LEFT JOIN places p ON p.id=c.place_id WHERE c.id=%s""", (cluster_id,))
        c = cur.fetchone()
    scope = c["school"] or c["place"] or ""
    query = unservable_intent_stripped(c["best_variant"] or c["label"])
    if c["entity_id"]:
        title = f"{c['entity_name']} at {scope}: facts from the official page"[:60] if len(f"{c['entity_name']} at {scope}") <= 40 else f"{c['entity_name']}: the official facts"[:60]
        fmt, h1 = "entity_profile", f"{c['entity_name']} ({scope})"
        contribution = f"the verified facts about {c['entity_name']} from its official page, on one page, with the date checked; no ratings and no unattributed resident experience"
    else:
        title = query[:60]
        fmt, h1 = "guide", query
        contribution = "a dated, sourced answer from the official pages, with what they do not say stated plainly"
    return {"page_path": page_path, "primary_query": query, "target_title": title, "h1": h1, "page_format": fmt, "lean": True,
            "contribution": contribution, "answer_first_intro": "", "snippet_formats": ["table"], "faq_real_questions": [], "secondary_questions": [], "beats": [],
            "note": "LEAN MODE synthetic plan (owner decision 2026-11-06): no strategist win plan exists for this cluster; plan from the claims and this plan; a missing strategist plan is not a reason to hold."}


UNSERVABLE_INTENT = ("review", "reviews", "rating", "ratings", "reddit", "opinions", "experience", "experiences")


def unservable_intent_stripped(query: str) -> str:
    """A factual page never carries resident reviews or ratings (no allowed source), so a 'review' intent word is not a content word the
    title must promise: 'Barbara McClintock Hall review Cornell' → 'Barbara McClintock Hall Cornell'."""
    import re
    words = [w for w in re.findall(r"\S+", query or "") if w.lower().strip("?.,!") not in UNSERVABLE_INTENT]
    return " ".join(words).strip() or (query or "")


def verifier_rounds(conn, page_id) -> int:
    """How many verifier dispatches this page has consumed across all of its versions (one per saved verifier reply)."""
    import json as _json
    from .pipeline import RUNS_DIR
    with conn.cursor() as cur:
        cur.execute("SELECT id FROM page_versions WHERE page_id=%s", (page_id,))
        vids = {str(r["id"]) for r in cur.fetchall()}
    n = 0
    for f in (RUNS_DIR / "agent-output").glob("*-verifier-*.json"):
        try:
            doc = _json.loads(f.read_text()).get("doc") or {}
        except (ValueError, OSError):
            continue
        if set(doc.get("input_ids") or []) & vids:
            n += 1
    return n


def last_verified_rubric(conn, page_id) -> dict | None:
    """The most recent verifier rubric recorded on any passed version of this page (carried when no further verifier round is spent)."""
    with conn.cursor() as cur:
        cur.execute("SELECT rubric FROM page_versions WHERE page_id=%s AND rubric IS NOT NULL AND gate_status='passed' ORDER BY version_no DESC LIMIT 1", (page_id,))
        row = cur.fetchone()
    return dict(row["rubric"]) if row and row["rubric"] else None


def queue_pages(conn: psycopg.Connection, *, limit: int = 20) -> list[dict]:
    """`production_queue` as planned pages, the shape `campus_worker.bulk plan --json` prints and scripts/parallel_headless.sh shards
    (question_id, path, page_type, question, cluster_id; the queue row itself under `queue`). The path is what `pipeline run <cluster_id>` would
    use: the cluster's existing page, else lean.default_page_path. A lean queue row has no question id (it is a cluster, not a dossier question)."""
    from .pipeline import _page_for_cluster
    pages = []
    for r in production_queue(conn, limit=limit):
        existing = _page_for_cluster(conn, r["cluster_id"])
        pages.append({"question_id": None, "path": (existing or {}).get("path") or default_page_path(conn, cluster_id=r["cluster_id"]), "page_type": "guide",
                      "question": r.get("best_variant") or r.get("label"), "cluster_id": str(r["cluster_id"]), "queue": dict(r)})
    return pages


def main(argv: list[str]) -> int:
    """python -m campus_worker.lean queue [--limit N] [--json]"""
    import json
    from .config import get_settings
    from .db import connect
    if not argv or argv[0] != "queue" or "-h" in argv or "--help" in argv:
        print("usage: python -m campus_worker.lean queue [--limit N] [--json]   the lean production queue as planned pages (scripts/parallel_headless.sh)")
        return 2
    limit = int(argv[argv.index("--limit") + 1]) if "--limit" in argv else 20
    conn = connect(get_settings().database_url)
    try:
        pages = queue_pages(conn, limit=limit)
    finally:
        conn.close()
    if "--json" in argv:
        print(json.dumps(pages, indent=1, default=str))
    else:
        for p in pages:
            print(f"{p['cluster_id'][:8]}  {p['path']}  {p['question']}")
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main(sys.argv[1:]))
