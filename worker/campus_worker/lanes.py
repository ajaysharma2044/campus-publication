"""Lane mix (continuous-local-run R24; R4). `python -m campus_worker.lanes next` prints the lane and its top item.

Each iteration picks the lane with the largest deficit against CAMPUS_LANE_MIX (default 50/30/20 production,
discovery, maintenance), counted per run. A lane with no work passes its share to the next. Failing tests always
come first, but that check is the coordinator's (iteration prompt step 1), not this module's.
"""
from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path

import psycopg

from .config import REPO_ROOT, get_settings

LANES = ("production", "discovery", "maintenance")


def parse_mix(spec: str) -> dict[str, float]:
    parts = [int(p) for p in spec.split(",")]
    if len(parts) != 3 or sum(parts) <= 0 or any(p < 0 for p in parts):
        raise ValueError("CAMPUS_LANE_MIX must be three non-negative integers, e.g. 50,30,20")
    tot = sum(parts)
    return {l: p / tot for l, p in zip(LANES, parts)}


def picks(conn: psycopg.Connection, run_id: str) -> dict[str, int]:
    with conn.cursor() as cur:
        cur.execute("SELECT lane, picks FROM lane_state WHERE run_id=%s", (run_id,))
        return {r["lane"]: r["picks"] for r in cur.fetchall()}


def record_pick(conn: psycopg.Connection, run_id: str, lane: str) -> None:
    with conn.cursor() as cur:
        cur.execute("""INSERT INTO lane_state (run_id, lane, picks) VALUES (%s,%s,1) ON CONFLICT (run_id, lane) DO UPDATE SET picks=lane_state.picks+1, updated_at=now()""", (run_id, lane))
    conn.commit()


def order_by_deficit(mix: dict[str, float], counts: dict[str, int]) -> list[str]:
    total = sum(counts.get(l, 0) for l in LANES)
    # deficit = target share × (total+1) − picks so far; highest deficit first; stable tie order = LANES order
    return sorted(LANES, key=lambda l: (-(mix[l] * (total + 1) - counts.get(l, 0)), LANES.index(l)))


# ---------------------------------------------------------------- work finders (each returns None when the lane has nothing)
def production_item(conn) -> dict | None:
    from . import sweetspot
    q = sweetspot.queue(conn, limit=1)
    if not q:
        return None
    it = q[0]
    return {"kind": "sweet_spot_cluster", "cluster_id": str(it["cluster_id"]), "label": it["label"], "best_variant": it["best_variant"],
            "niche_score": float(it["niche_score"] or 0), "topic_key": it["topic_key"], "capture_format": it["capture_format"],
            "next": "python -m campus_worker.pipeline run <cluster_id>  (R16 chain with the cheapest-first funnel)"}


def discovery_item(conn, settings) -> dict | None:
    from . import harvest
    due = harvest.due_harvest_sources(conn)
    if due:
        return {"kind": "harvest_due", "count": len(due), "first": {"rule": due[0]["rule_key"], "url": due[0]["canonical_url"]}, "next": "python -m campus_worker.sweep harvest"}
    with conn.cursor() as cur:
        cur.execute("SELECT count(*) AS n FROM intent_clusters WHERE queue_state='needs_intel' OR (queue_state='candidate' AND last_intel_at IS NULL)")
        need = cur.fetchone()["n"]
    if need:
        return {"kind": "search_intel_batch", "clusters_needing_intel": int(need), "batch_size": 10, "next": "python -m campus_worker.sweep intel --batch 10"}
    with conn.cursor() as cur:
        cur.execute("SELECT count(*) AS n FROM entities e WHERE e.status='active' AND NOT EXISTS (SELECT 1 FROM questions q WHERE q.entity_id=e.id AND q.is_hypothesis)")
        unexpanded = cur.fetchone()["n"]
    if unexpanded:
        return {"kind": "expand_pending", "entities_without_hypotheses": int(unexpanded), "next": "python -m campus_worker.sweep expand"}
    scout = _skill_scout_due()
    if scout:
        return scout
    return None


def _skill_scout_due() -> dict | None:
    f = REPO_ROOT / "docs" / "ops" / "skill-evaluations.md"
    text = f.read_text() if f.exists() else ""
    m = re.findall(r"last scout run: (\d{4}-\d{2}-\d{2})", text)
    from datetime import date, timedelta
    if not m:
        return {"kind": "skill_scout", "reason": "no scout run recorded yet (R12: once at the first run)", "next": "dispatch skill-scout with docs/ops/skill-eval-set.md"}
    last = date.fromisoformat(m[-1])
    if date.today() - last >= timedelta(days=7):
        return {"kind": "skill_scout", "reason": f"weekly scout due (last {last})", "next": "dispatch skill-scout"}
    return None


def maintenance_item(conn, settings) -> dict | None:
    from . import queue as q
    with conn.cursor() as cur:
        cur.execute("""SELECT id, path FROM pages WHERE first_published_at IS NOT NULL AND revalidation_required ORDER BY last_material_update_at NULLS FIRST LIMIT 1""")
        r = cur.fetchone()
    if r:
        return {"kind": "recheck_due", "page_id": str(r["id"]), "path": r["path"], "next": "dispatch analyst rank re-check (R15)"}
    counts = q.counts(conn)
    if counts.get("queued", 0) or counts.get("retry_wait", 0):
        return {"kind": "db_jobs_due", "queued": counts.get("queued", 0), "retry_wait": counts.get("retry_wait", 0), "next": "python -m campus_worker.cli run-once"}
    item = first_unblocked_backlog_item()
    if item:
        return {"kind": "backlog_item", **item, "next": "implement it; run its acceptance check; commit with the id"}
    return None


def first_unblocked_backlog_item(path: Path | None = None) -> dict | None:
    """Parse BACKLOG.md tables: first row with status `todo` whose dependencies are all `done`."""
    p = path or (REPO_ROOT / "BACKLOG.md")
    if not p.exists():
        return None
    rows = {}
    order = []
    for line in p.read_text().splitlines():
        if not line.startswith("|") or line.startswith("|--") or line.startswith("| ID"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 5:
            continue
        rid, task, deps, _acc, status = cells[0], cells[1], cells[2], cells[3], cells[-1]
        if not re.fullmatch(r"[A-Z]+\d+", rid):
            continue
        rows[rid] = {"id": rid, "task": task, "deps": [d.strip() for d in re.split(r"[,\s]+", deps) if re.fullmatch(r"[A-Z]+\d+", d.strip())], "status": status.lower()}
        order.append(rid)
    for rid in order:
        r = rows[rid]
        if r["status"].startswith("todo") and all(rows.get(d, {}).get("status", "").startswith("done") for d in r["deps"]):
            return {"id": rid, "task": r["task"]}
    return None


def next_lane(conn: psycopg.Connection, settings=None, *, run_id: str | None = None, mode: str | None = None) -> dict:
    settings = settings or get_settings()
    run_id = run_id or os.environ.get("CAMPUS_RUN_ID") or "adhoc"
    mode = mode or os.environ.get("CAMPUS_RUN_MODE") or "normal"
    mix = parse_mix(settings.quotas.lane_mix)
    counts = picks(conn, run_id)
    order = ["discovery"] if mode == "sweep" else order_by_deficit(mix, counts)
    finders = {"production": lambda: production_item(conn), "discovery": lambda: discovery_item(conn, settings), "maintenance": lambda: maintenance_item(conn, settings)}
    tried = []
    for lane in order:
        item = finders[lane]()
        tried.append({"lane": lane, "has_work": item is not None})
        if item is not None:
            record_pick(conn, run_id, lane)
            return {"lane": lane, "item": item, "mix": settings.quotas.lane_mix, "picks": {**counts, lane: counts.get(lane, 0) + 1}, "tried": tried, "mode": mode}
    return {"lane": None, "item": None, "no_work": True, "mix": settings.quotas.lane_mix, "picks": counts, "tried": tried, "mode": mode}


def main(argv: list[str]) -> int:
    from .db import connect
    settings = get_settings()
    conn = connect(settings.database_url)
    try:
        if not argv or argv[0] == "next":
            print(json.dumps(next_lane(conn, settings), indent=2, default=str))
            return 0
        if argv[0] == "status":
            print(json.dumps({"mix": settings.quotas.lane_mix, "picks": picks(conn, os.environ.get("CAMPUS_RUN_ID") or "adhoc")}, indent=2))
            return 0
    finally:
        conn.close()
    print("usage: python -m campus_worker.lanes next|status")
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
