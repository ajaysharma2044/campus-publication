"""Mass sweep mode and the opportunity map (continuous-local-run R40, R41, R46; AT40, AT22, AT33, AT45).

  python -m campus_worker.sweep harvest          deterministic: harvest every due source (school + town), no model
  python -m campus_worker.sweep expand           deterministic: hypotheses for every entity from the pattern library
  python -m campus_worker.sweep next             what the coordinator should do now (harvest / expand / intel batch / score / complete)
  python -m campus_worker.sweep intel --batch N  the next N clusters needing search observation (cheapest first)
  python -m campus_worker.sweep run-intel [--batch N]  dispatch one search-intel batch (<=25), ingest it, then score
  python -m campus_worker.sweep score            score every cluster (D, AGI, G, E, niche_score, decision) + auto-topics (R46)
  python -m campus_worker.sweep map              write docs/strategy/opportunity-map.md and build/opportunity-map.csv
  python -m campus_worker.sweep status           {complete: bool, ...}

The sweep is complete when no cluster still needs search observation and every cluster has a decision. The run loop
switches from sweep mode to the normal lane mix on `sweep_complete` (R41). Batches: 25 in sweep mode, 10 in normal.
"""
from __future__ import annotations

import csv
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from uuid import UUID

import psycopg

from . import discovery, expand, harvest, sweetspot
from .config import REPO_ROOT, get_settings

MAP_MD = REPO_ROOT / "docs" / "strategy" / "opportunity-map.md"
MAP_CSV = REPO_ROOT / "build" / "opportunity-map.csv"
BATCH_SWEEP, BATCH_NORMAL = 25, 10


def scopes(conn: psycopg.Connection, *, include_fixtures: bool = False) -> dict:
    """Schools and towns in scope. Synthetic fixture institutions are never searched or published live (SPEC fixtures rule);
    tests pass include_fixtures=True."""
    with conn.cursor() as cur:
        cur.execute("""SELECT i.id, i.canonical_name, i.slug, i.place_id, c.id AS campus_id FROM institutions i
                       LEFT JOIN school_configs sc ON sc.institution_id=i.id LEFT JOIN campuses c ON c.institution_id=i.id AND c.is_main
                       WHERE NOT i.is_system AND COALESCE(sc.coverage_status, 'onboarding') <> 'paused'
                         AND (%s OR i.identity_status <> 'synthetic_fixture')
                         AND (sc.id IS NOT NULL OR EXISTS (SELECT 1 FROM entities e WHERE e.institution_id=i.id))
                       ORDER BY i.canonical_name""", (include_fixtures,))
        schools = [dict(r) for r in cur.fetchall()]
        cur.execute("SELECT id, name, slug FROM places WHERE kind IN ('city','town','village') ORDER BY name")
        towns = [dict(r) for r in cur.fetchall()]
    return {"schools": schools, "towns": towns}


def run_harvest(conn: psycopg.Connection, fetcher=None, *, force: bool = False) -> dict:
    from .fetcher import SafeFetcher
    fetcher = fetcher or SafeFetcher(conn)
    out = []
    for src in harvest.due_harvest_sources(conn, force=force):
        try:
            out.append(harvest.harvest_source(conn, fetcher, src["id"]))
        except Exception as e:  # noqa: BLE001 — one bad source never stops the sweep; it is reported
            out.append({"rule": src["rule_key"], "outcome": f"error: {type(e).__name__}: {str(e)[:160]}", "found": 0})
    return {"harvested": out, "entities": harvest.entity_counts(conn)}


def run_expand(conn: psycopg.Connection, *, include_fixtures: bool = False) -> dict:
    sc = scopes(conn, include_fixtures=include_fixtures)
    out = []
    for s in sc["schools"]:
        out.append(dict(expand.expand_scope(conn, institution_id=s["id"], campus_id=s["campus_id"], school_name=_short_name(s["canonical_name"])), scope=s["slug"]))
        out.append(dict(expand.expand_topics(conn, institution_id=s["id"], campus_id=s["campus_id"], school_name=_short_name(s["canonical_name"])), scope=s["slug"], kind="topics"))
    for t in sc["towns"]:
        out.append(dict(expand.expand_scope(conn, place_id=t["id"], town_name=t["name"]), scope=t["slug"]))
        out.append(dict(expand.expand_topics(conn, place_id=t["id"], town_name=t["name"]), scope=t["slug"], kind="topics"))
    return {"expanded": out, "stats": expand.hypothesis_stats(conn)}


def _short_name(name: str) -> str:
    return name.replace(" University", "").replace("University of ", "").strip() if name else name


# A cluster earns a search-observation round when it came from the pattern library (a hypothesis) or has at least two
# independent observed occurrences. A lone follow-up question waits for a second occurrence (watch), so the sweep converges.
ELIGIBLE = "(c.hypothesis_count > 0 OR c.independent_occurrences >= 2)"


PRIORITY_PATTERNS = ("topic_seed", "review", "cost", "vs", "good_for_transfers", "hours", "schedule", "apply", "requirements", "prereq")
SWEEP_INTEL_CAP_DEFAULT = 300


def sweep_cap() -> int:
    return int(os.environ.get("CAMPUS_SWEEP_INTEL_CAP", SWEEP_INTEL_CAP_DEFAULT))


def _priority_sql() -> str:
    cases = " ".join(f"WHEN q.pattern_key='{p}' THEN {i}" for i, p in enumerate(PRIORITY_PATTERNS))
    return f"(SELECT min(CASE {cases} ELSE 50 END) FROM questions q WHERE q.cluster_id=c.id)"


def intel_batch(conn: psycopg.Connection, *, batch: int) -> list[dict]:
    """Clusters needing search observation, cheapest/most valuable first: observed demand, then topic-seed and high-value
    patterns (review, cost, vs, …), then everything else, oldest first."""
    with conn.cursor() as cur:
        # topic breadth first (R41/AT40: the map must cover every R33 topic inside the intel cap): the best cluster of every topic
        # comes before the second-best of any topic; within a topic, observed demand, then priority, then hypotheses, then age.
        cur.execute(f"""WITH ranked AS (
                          SELECT c.id AS cluster_id, c.label, c.best_variant, t.key AS topic_key, c.observed_count, c.hypothesis_count, c.institution_id, c.place_id,
                                 row_number() OVER (PARTITION BY c.topic_id ORDER BY c.observed_count DESC, {_priority_sql()} ASC, c.hypothesis_count DESC, c.created_at) AS rk
                          FROM intent_clusters c LEFT JOIN topics t ON t.id=c.topic_id
                          WHERE c.last_intel_at IS NULL AND c.queue_state IN ('candidate','needs_intel') AND {ELIGIBLE})
                        SELECT * FROM ranked ORDER BY rk, observed_count DESC, hypothesis_count DESC LIMIT %s""", (batch,))
        return [dict(r) for r in cur.fetchall()]


def defer_beyond_cap(conn: psycopg.Connection, *, cap: int | None = None) -> int:
    """R41 bounded sweep: clusters beyond the intel cap (lowest priority first) are decided 'watch' with a deferral reason and
    observed later in the normal discovery lane. Returns how many were deferred."""
    cap = sweep_cap() if cap is None else cap
    with conn.cursor() as cur:
        cur.execute(f"""WITH ranked AS (
                          SELECT c.id, c.observed_count, c.hypothesis_count,
                                 row_number() OVER (PARTITION BY c.topic_id ORDER BY c.observed_count DESC, {_priority_sql()} ASC, c.hypothesis_count DESC, c.created_at) AS rk
                          FROM intent_clusters c WHERE c.last_intel_at IS NULL AND c.queue_state IN ('candidate','needs_intel') AND {ELIGIBLE})
                        SELECT id FROM ranked ORDER BY rk, observed_count DESC, hypothesis_count DESC""")
        ids = [r["id"] for r in cur.fetchall()]
        cur.execute("SELECT count(*) AS n FROM intent_clusters WHERE last_intel_at IS NOT NULL")
        observed = cur.fetchone()["n"]
        room = max(0, cap - int(observed))
        deferred = ids[room:]
        if deferred:
            cur.execute("""UPDATE intent_clusters SET queue_state='watch', queue_reason='deferred: beyond the sweep intel cap; the discovery lane observes it later (R41)', updated_at=now()
                           WHERE id = ANY(%s)""", (deferred,))
        # a cluster with one observed occurrence and no hypothesis is not eligible for search intel yet (R20: hypotheses are never demand,
        # one occurrence is not independent evidence); its decision is 'watch' until a second occurrence arrives, so the map can complete
        cur.execute(f"""UPDATE intent_clusters c SET queue_state='watch', queue_reason='waiting for a second independent occurrence (R20)', updated_at=now()
                        WHERE c.last_intel_at IS NULL AND c.queue_state IN ('candidate','needs_intel') AND NOT {ELIGIBLE}""")
        waiting = cur.rowcount
    conn.commit()
    return len(deferred) + waiting


def run_score(conn: psycopg.Connection, *, run_id: str | None = None) -> dict:
    auto = discovery.auto_create_topics(conn, run_id=run_id)
    scored = sweetspot.score_all(conn)
    by = {}
    for cs in scored:
        by[cs.decision] = by.get(cs.decision, 0) + 1
    return {"scored": len(scored), "by_decision": by, "auto_topics": auto}


def status(conn: psycopg.Connection) -> dict:
    with conn.cursor() as cur:
        cur.execute(f"""SELECT count(*) AS clusters, count(*) FILTER (WHERE c.last_intel_at IS NULL AND c.queue_state IN ('candidate','needs_intel') AND {ELIGIBLE}) AS need_intel,
                              count(*) FILTER (WHERE queue_state='sweet_spot') AS sweet_spot, count(*) FILTER (WHERE queue_state='watch') AS watch,
                              count(*) FILTER (WHERE queue_state='reject') AS reject, count(*) FILTER (WHERE queue_state='navigational') AS navigational,
                              count(*) FILTER (WHERE queue_state IN ('candidate','needs_intel')) AS undecided,
                              count(*) FILTER (WHERE c.last_intel_at IS NULL AND c.queue_state IN ('candidate','needs_intel') AND NOT {ELIGIBLE}) AS waiting_second_occurrence,
                              count(*) FILTER (WHERE c.queue_state='watch' AND c.queue_reason LIKE 'deferred:%%') AS deferred FROM intent_clusters c""")
        c = dict(cur.fetchone())
        cur.execute("SELECT count(*) AS n FROM entities WHERE status='active'")
        c["entities"] = cur.fetchone()["n"]
        cur.execute("SELECT count(*) AS n FROM topics WHERE auto_created")
        c["auto_topics"] = cur.fetchone()["n"]
    c["harvest_due"] = len(harvest.due_harvest_sources(conn))
    c["complete"] = c["clusters"] > 0 and c["need_intel"] == 0 and c["undecided"] == 0 and c["harvest_due"] == 0
    return c


def next_step(conn: psycopg.Connection, *, batch: int = BATCH_SWEEP) -> dict:
    st = status(conn)
    if st["harvest_due"]:
        return {"step": "harvest", "detail": {"due": st["harvest_due"]}, "command": "worker/.venv/bin/python -m campus_worker.sweep harvest", "status": st}
    with conn.cursor() as cur:
        cur.execute("SELECT count(*) AS n FROM entities e WHERE e.status='active' AND NOT EXISTS (SELECT 1 FROM questions q WHERE q.entity_id=e.id AND q.is_hypothesis)")
        unexpanded = cur.fetchone()["n"]
    if unexpanded:
        return {"step": "expand", "detail": {"entities_without_hypotheses": int(unexpanded)}, "command": "worker/.venv/bin/python -m campus_worker.sweep expand", "status": st}
    if st["need_intel"]:
        defer_beyond_cap(conn)
        st = status(conn)
    if st["need_intel"]:
        b = intel_batch(conn, batch=batch)
        return {"step": "intel", "detail": {"batch": [{"cluster_id": str(x["cluster_id"]), "label": x["label"], "topic": x["topic_key"]} for x in b], "remaining": st["need_intel"]},
                "command": "worker/.venv/bin/python -m campus_worker.sweep run-intel --batch 25   (one search-intel batch dispatch, ingest, then score; then run sweep next again)", "status": st}
    if st["undecided"]:
        return {"step": "score", "detail": {"undecided": st["undecided"]}, "command": "worker/.venv/bin/python -m campus_worker.sweep score && worker/.venv/bin/python -m campus_worker.sweep map", "status": st}
    return {"step": "complete", "sweep_complete": True, "command": "worker/.venv/bin/python -m campus_worker.sweep map", "status": st}


def write_map(conn: psycopg.Connection, *, md_path: Path | None = None, csv_path: Path | None = None) -> dict:
    with conn.cursor() as cur:
        cur.execute("""SELECT c.id, COALESCE(t.key,'(none)') AS topic, t.scope, e.name AS entity, c.label, c.best_variant, c.d_score, c.agi, c.g_est, c.e_est, c.niche_score,
                              c.queue_state, c.queue_reason, c.capture_format, COALESCE(i.slug, p.slug) AS scope_slug, c.audience
                       FROM intent_clusters c LEFT JOIN topics t ON t.id=c.topic_id LEFT JOIN entities e ON e.id=c.entity_id
                       LEFT JOIN institutions i ON i.id=c.institution_id LEFT JOIN places p ON p.id=c.place_id
                       ORDER BY (c.queue_state='sweet_spot') DESC, c.niche_score DESC NULLS LAST, c.queue_state, t.key, c.label""")
        rows = [dict(r) for r in cur.fetchall()]
    md_path = md_path or MAP_MD
    csv_path = csv_path or MAP_CSV
    md_path.parent.mkdir(parents=True, exist_ok=True); csv_path.parent.mkdir(parents=True, exist_ok=True)
    with csv_path.open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["cluster_id", "scope", "topic", "entity", "best_query_variant", "D", "AGI", "G", "E", "niche_score", "decision", "reason", "capture_format", "audience"])
        for r in rows:
            w.writerow([r["id"], r["scope_slug"], r["topic"], r["entity"] or "", r["best_variant"] or r["label"], r["d_score"], r["agi"], r["g_est"], r["e_est"],
                        r["niche_score"], r["queue_state"], r["queue_reason"], r["capture_format"] or "", r["audience"] or ""])
    st = status(conn)
    by_topic: dict[str, dict] = {}
    for r in rows:
        d = by_topic.setdefault(r["topic"], {"sweet_spot": 0, "watch": 0, "reject": 0, "navigational": 0, "undecided": 0})
        d[r["queue_state"] if r["queue_state"] in d else "undecided"] += 1
    lines = ["# Opportunity map (specs/continuous-local-run.md R41, R22)", "",
             f"Generated {datetime.now(timezone.utc).isoformat(timespec='seconds')} from database state. Scores are deterministic (D from recorded demand evidence, AGI from observed results, "
             "G and E estimates from the authority gap and the source map); priority (SPEC §11) is recorded but not the advance rule for this lane. Sortable CSV: `build/opportunity-map.csv`.", "",
             f"Clusters: {st['clusters']} · sweet-spot: {st['sweet_spot']} · watch: {st['watch']} · reject: {st['reject']} · navigational: {st['navigational']} · undecided: {st['undecided']} · entities: {st['entities']} · auto-created topics: {st['auto_topics']} · complete: {st['complete']}", "",
             "## Top sweet-spot clusters", "", "| # | scope | topic | entity | best query variant | D | AGI | G | E | niche_score | format |", "|---|---|---|---|---|---|---|---|---|---|---|"]
    ss = [r for r in rows if r["queue_state"] == "sweet_spot"]
    for i, r in enumerate(ss[:100], 1):
        lines.append(f"| {i} | {r['scope_slug']} | {r['topic']} | {r['entity'] or ''} | {r['best_variant'] or r['label']} | {r['d_score']} | {r['agi']} | {r['g_est']} | {r['e_est']} | {r['niche_score']} | {r['capture_format'] or ''} |")
    if not ss:
        lines.append("| — | | | | no sweet-spot clusters yet | | | | | | |")
    lines += ["", "## Coverage by topic", "", "| topic | sweet-spot | watch | reject | navigational | undecided |", "|---|---|---|---|---|---|"]
    for k in sorted(by_topic):
        d = by_topic[k]
        lines.append(f"| {k} | {d['sweet_spot']} | {d['watch']} | {d['reject']} | {d['navigational']} | {d['undecided']} |")
    lines += ["", "## Every cluster", "", "| scope | topic | entity | best query | D | AGI | G | E | niche | decision | reason |", "|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in rows:
        lines.append(f"| {r['scope_slug']} | {r['topic']} | {r['entity'] or ''} | {(r['best_variant'] or r['label'])[:80]} | {r['d_score']} | {r['agi']} | {r['g_est']} | {r['e_est']} | {r['niche_score']} | {r['queue_state']} | {(r['queue_reason'] or '')[:120]} |")
    md_path.write_text("\n".join(lines) + "\n")
    return {"md": str(md_path), "csv": str(csv_path), "rows": len(rows), "status": st, "by_topic": by_topic}


def run_intel(conn: psycopg.Connection, *, batch: int, run_id: str | None = None, settings=None, runner=None, log_path=None) -> dict:
    """One search-intel batch dispatch (<=25 clusters, R27/R41) through search_intel.run_batch, which validates and ingests the
    agent output, followed by deterministic scoring. Lets a coordinator restricted to `python -m campus_worker.*` run the lane."""
    from . import search_intel
    settings = settings or get_settings()
    picked = intel_batch(conn, batch=min(batch, BATCH_SWEEP))
    if not picked:
        return {"status": "empty", "batch": 0}
    kw = {"runner": runner} if runner else {}
    if log_path is None:
        from .agents.dispatch import DISPATCH_LOG_DEFAULT
        log_path = DISPATCH_LOG_DEFAULT  # the loop's dispatches must reach the dispatch log (R10, R29 metrics)
    res = search_intel.run_batch(conn, [UUID(str(x["cluster_id"])) for x in picked], settings=settings, run_id=run_id, log_path=log_path, **kw)
    from .db import ensure_conn
    conn = ensure_conn(conn)  # run_batch may have outlived the caller's connection
    scored = run_score(conn, run_id=run_id)
    summary = {k: v for k, v in res.items() if k != "results"}
    summary["clusters"] = len(picked)
    summary["by_status"] = {}
    for r in (res.get("results") or {}).values():
        summary["by_status"][r.get("status")] = summary["by_status"].get(r.get("status"), 0) + 1
    return {"intel": summary, "score": scored}


def main(argv: list[str]) -> int:
    from .db import connect
    settings = get_settings()
    conn = connect(settings.database_url)
    try:
        cmd = argv[0] if argv else "next"
        batch = BATCH_SWEEP if os.environ.get("CAMPUS_RUN_MODE") == "sweep" else BATCH_NORMAL
        if "--batch" in argv:
            batch = int(argv[argv.index("--batch") + 1])
        if cmd == "harvest":
            out = run_harvest(conn, force="--force" in argv)
        elif cmd == "expand":
            out = run_expand(conn)
        elif cmd == "intel":
            out = {"batch": intel_batch(conn, batch=batch)}
        elif cmd == "run-intel":
            out = run_intel(conn, batch=batch, run_id=os.environ.get("CAMPUS_RUN_ID"))
        elif cmd == "score":
            out = run_score(conn, run_id=os.environ.get("CAMPUS_RUN_ID"))
        elif cmd == "map":
            out = write_map(conn)
        elif cmd == "status":
            out = status(conn)
        else:
            out = next_step(conn, batch=batch)
        print(json.dumps(out, indent=2, default=str))
        return 0
    finally:
        conn.close()


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
