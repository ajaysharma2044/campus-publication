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


def enabled() -> bool:
    return (os.environ.get("CAMPUS_LEAN_MODE", "1") or "1").strip().lower() not in ("0", "false", "no", "off")


def verified_claims_in_scope(conn: psycopg.Connection, *, institution_id: UUID | None, place_id: UUID | None, topic_id: UUID | None) -> int:
    """Current verified facts for the cluster's school-or-town + topic scope (topic-less claims count for every topic of the scope)."""
    with conn.cursor() as cur:
        if institution_id:
            cur.execute("""SELECT count(*) AS n FROM claims WHERE institution_id=%s AND (topic_id=%s OR topic_id IS NULL) AND evidence_category='verified_fact'
                           AND superseded_by_id IS NULL AND conflict_status <> 'open'""", (institution_id, topic_id))
        elif place_id:
            cur.execute("""SELECT count(*) AS n FROM claims c JOIN entities e ON e.id=c.entity_id WHERE e.place_id=%s AND (c.topic_id=%s OR c.topic_id IS NULL)
                           AND c.evidence_category='verified_fact' AND c.superseded_by_id IS NULL AND c.conflict_status <> 'open'""", (place_id, topic_id))
        else:
            return 0
        return int(cur.fetchone()["n"])


def production_queue(conn: psycopg.Connection, *, limit: int = 20) -> list[dict]:
    """Lean production order: every observed, non-navigational cluster without a strong incumbent, best niche_score first, that has a
    verified fact in scope. in_production/done clusters are excluded; D only orders."""
    with conn.cursor() as cur:
        cur.execute("""SELECT c.id AS cluster_id, c.label, c.best_variant, c.d_score AS d, c.agi, c.g_est AS g, c.e_est AS e, c.niche_score, c.capture_format,
                              c.queue_state, c.institution_id, c.place_id, c.topic_id, t.key AS topic_key
                       FROM intent_clusters c LEFT JOIN topics t ON t.id=c.topic_id
                       WHERE c.last_intel_at IS NOT NULL AND c.queue_state IN ('sweet_spot','watch','reject') AND c.agi IS NOT NULL AND c.agi > %s
                       ORDER BY c.niche_score DESC NULLS LAST, c.agi DESC, c.d_score DESC NULLS LAST, c.updated_at LIMIT %s""", (STRONG_INCUMBENT_AGI, limit * 5))
        rows = [dict(r) for r in cur.fetchall()]
    out = []
    for r in rows:
        if verified_claims_in_scope(conn, institution_id=r["institution_id"], place_id=r["place_id"], topic_id=r["topic_id"]) >= 1:
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
    text = (c["best_variant"] or c["label"] or "").lower()
    stop = {"a", "an", "the", "of", "at", "in", "on", "for", "to", "is", "are", "do", "does", "did", "what", "when", "where", "how", "can", "i", "my", "and", "or", "be", "with", "by", "it", "its", "there", "any", "have", "has", "will", "should", "you", "your"}
    words = [w for w in re.findall(r"[a-z0-9]+", text) if w not in stop]
    slug = "-".join(words)[:60].strip("-") or "guide"
    scope = f"/schools/{c['school_slug']}/" if c["school_slug"] else f"/towns/{c['place_slug']}/"
    return f"{scope}{c['topic_key']}/{slug}/"
