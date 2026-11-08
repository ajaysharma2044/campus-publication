"""Daily digest (continuous-local-run R9, R29, R44; AT16, AT26, AT43).

    python -m campus_worker.digest --reason run_end|midnight|manual [--date YYYY-MM-DD]

Writes docs/digest/YYYY-MM-DD.md with every R9 section, the R29 efficiency metrics computed from the ledger and the
dispatch log, and the R44 volume report. Idempotent for a day: re-running rewrites the same file from current state.
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

import psycopg

from . import events, sweetspot, volume
from .agents.dispatch import DISPATCH_LOG_DEFAULT
from .config import REPO_ROOT, get_settings

DIGEST_DIR = REPO_ROOT / "docs" / "digest"
RUNS_DIR = REPO_ROOT / "build" / "runs"


def _day_bounds(day: date) -> tuple[datetime, datetime]:
    start = datetime(day.year, day.month, day.day, tzinfo=timezone.utc)
    return start, start + timedelta(days=1)


def tasks_done(day: date) -> list[dict]:
    """Commits of the day (ids from the commit subject) plus run-log lines."""
    start, end = _day_bounds(day)
    out = []
    try:
        log = subprocess.run(["git", "log", f"--since={start.isoformat()}", f"--until={end.isoformat()}", "--format=%h|%s"], cwd=REPO_ROOT, capture_output=True, text=True, timeout=30).stdout
        for line in log.splitlines():
            sha, _, subject = line.partition("|")
            m = re.match(r"^([A-Z]+\d+(?:/[A-Z]+\d+)*|M\d+(?:/M\d+)*|S\d+)[:\s]", subject)
            out.append({"commit": sha, "task_id": m.group(1) if m else None, "subject": subject[:140]})
    except Exception:  # noqa: BLE001
        pass
    for p in sorted(RUNS_DIR.glob("*.jsonl")) if RUNS_DIR.exists() else []:
        if p.name == "dispatch.jsonl":
            continue
        for line in p.read_text().splitlines():
            try:
                e = json.loads(line)
            except json.JSONDecodeError:
                continue
            if e.get("start", "")[:10] == day.isoformat() and e.get("iteration"):
                out.append({"run": p.stem, "iteration": e["iteration"], "task_id": e.get("task_id"), "result": e.get("result"), "commit": e.get("commit"), "lane": e.get("lane")})
    return out


def pages_section(conn: psycopg.Connection, day: date) -> dict:
    start, end = _day_bounds(day)
    with conn.cursor() as cur:
        cur.execute("SELECT path, local_published_at, first_published_at, tier FROM pages WHERE (local_published_at >= %s AND local_published_at < %s) OR (first_published_at >= %s AND first_published_at < %s) ORDER BY path", (start, end, start, end))
        published = [dict(r) for r in cur.fetchall()]
        cur.execute("SELECT path, revalidation_reason, status FROM pages WHERE status='held' ORDER BY path")
        held = [dict(r) for r in cur.fetchall()]
    return {"published": published, "held": held}


def claims_section(conn: psycopg.Connection, day: date) -> dict:
    start, end = _day_bounds(day)
    with conn.cursor() as cur:
        cur.execute("""SELECT count(*) FILTER (WHERE evidence_category='verified_fact') AS verified, count(*) FILTER (WHERE superseded_by_id IS NOT NULL) AS superseded,
                              count(*) FILTER (WHERE evidence_category='estimate') AS estimates FROM claims WHERE retrieved_at >= %s AND retrieved_at < %s""", (start, end))
        row = dict(cur.fetchone())
        cur.execute("""SELECT i.canonical_name, c.field, c.room_type, c.evidence_category FROM claims c JOIN institutions i ON i.id=c.institution_id
                       WHERE c.retrieved_at >= %s AND c.retrieved_at < %s AND c.evidence_category='verified_fact' ORDER BY c.field LIMIT 40""", (start, end))
        row["examples"] = [dict(r) for r in cur.fetchall()]
    return row


def skills_section() -> dict:
    p = REPO_ROOT / "docs" / "ops" / "skill-evaluations.md"
    if not p.exists():
        return {"note": "no skill evaluations yet"}
    text = p.read_text()
    return {"last_run": (re.search(r"last scout run: (\S+)", text) or [None, None])[1] if re.search(r"last scout run: (\S+)", text) else None,
            "candidates": len(re.findall(r"^\| `[^`]+` \| (?:skill|plugin|mcp_server|reference) \|", text, re.M)),
            "accepted": len(re.findall(r"\*\*accept\*\*", text)), "rejected": len(re.findall(r"\*\*reject\*\*", text)),
            "adopted": len(re.findall(r"^\| `[^`]+` \| adopted \|", text, re.M))}


def intel_section(conn: psycopg.Connection, day: date) -> dict:
    start, end = _day_bounds(day)
    with conn.cursor() as cur:
        cur.execute("SELECT count(*) AS n FROM serp_observations WHERE observed_at >= %s AND observed_at < %s", (start, end))
        obs = cur.fetchone()["n"]
        cur.execute("SELECT count(*) AS n FROM strategies WHERE created_at >= %s AND created_at < %s", (start, end))
        strategies = cur.fetchone()["n"]
        cur.execute("SELECT count(*) AS n FROM topics WHERE auto_created")
        auto = cur.fetchone()["n"]
        cur.execute("""SELECT count(*) FILTER (WHERE queue_state='sweet_spot') AS sweet_spot, count(*) FILTER (WHERE queue_state='watch') AS watch,
                              count(*) FILTER (WHERE queue_state='reject') AS reject, count(*) FILTER (WHERE queue_state='navigational') AS navigational, count(*) AS clusters FROM intent_clusters""")
        q = dict(cur.fetchone())
        cur.execute("""SELECT c.label, t.key AS topic, c.d_score, c.agi, c.g_est, c.e_est, c.niche_score, c.audience, COALESCE(i.slug, p.slug) AS scope FROM intent_clusters c LEFT JOIN topics t ON t.id=c.topic_id
                       LEFT JOIN institutions i ON i.id=c.institution_id LEFT JOIN places p ON p.id=c.place_id WHERE c.queue_state='sweet_spot' ORDER BY c.niche_score DESC NULLS LAST LIMIT 10""")
        top = [dict(r) for r in cur.fetchall()]
        cur.execute("""SELECT t.key AS topic, t.scope, count(*) FILTER (WHERE c.queue_state IN ('sweet_spot','watch')) AS candidates FROM intent_clusters c JOIN topics t ON t.id=c.topic_id
                       WHERE c.queue_state IN ('sweet_spot','watch') GROUP BY t.key, t.scope ORDER BY candidates DESC""")
        by_topic = [dict(r) for r in cur.fetchall()]
    return {"observations_today": obs, "strategies_today": strategies, "auto_topics": auto, "queue": q, "top_sweet_spot": top, "by_topic": by_topic}


def failures_section(conn: psycopg.Connection, day: date) -> dict:
    start, end = _day_bounds(day)
    with conn.cursor() as cur:
        cur.execute("SELECT severity, message FROM exceptions WHERE occurred_at >= %s AND occurred_at < %s AND resolved_at IS NULL ORDER BY occurred_at DESC LIMIT 20", (start, end))
        exc = [dict(r) for r in cur.fetchall()]
        cur.execute("SELECT job_type, hold_reason, count(*) AS n FROM jobs WHERE state IN ('held','dead_letter') GROUP BY job_type, hold_reason ORDER BY n DESC LIMIT 20")
        held = [dict(r) for r in cur.fetchall()]
    failed_iters = [t for t in tasks_done(day) if t.get("result") in ("failed", "usage_paused", "auth_error")]
    refused = [e for e in _dispatch_entries(day) if e.get("status") in ("failed", "invalid", "partial") and not e.get("usage_limit")]
    blockers = [l.strip("- ").strip() for l in (REPO_ROOT / "STATE.md").read_text().splitlines() if l.strip().startswith("- Current blockers")]
    return {"exceptions": exc, "held_jobs": held, "failed_iterations": failed_iters, "agent_failures": len(refused), "blockers": blockers}


def _dispatch_entries(day: date) -> list[dict]:
    if not DISPATCH_LOG_DEFAULT.exists():
        return []
    out = []
    for line in DISPATCH_LOG_DEFAULT.read_text().splitlines():
        try:
            e = json.loads(line)
        except json.JSONDecodeError:
            continue
        if (e.get("ts") or "")[:10] == day.isoformat():
            out.append(e)
    return out


def efficiency(conn: psycopg.Connection, day: date) -> dict:
    """R29 metrics from the ledger (session usage rows) and the dispatch log."""
    start, end = _day_bounds(day)
    with conn.cursor() as cur:
        cur.execute("""SELECT COALESCE(SUM((detail->>'turns')::int),0) AS turns, COALESCE(SUM((detail->>'duration_s')::numeric),0) AS seconds,
                              count(*) FILTER (WHERE detail->>'session_kind'='dispatch') AS dispatches, count(*) FILTER (WHERE detail->>'session_kind'='iteration') AS iterations
                       FROM usage_ledger WHERE provider='session' AND occurred_at >= %s AND occurred_at < %s""", (start, end))
        u = dict(cur.fetchone())
        cur.execute("SELECT count(*) AS n FROM pages WHERE (local_published_at >= %s AND local_published_at < %s) OR (first_published_at >= %s AND first_published_at < %s)", (start, end, start, end))
        published = cur.fetchone()["n"]
        cur.execute("SELECT count(*) AS n FROM page_versions v JOIN pages p ON p.id=v.page_id WHERE v.created_at >= %s AND v.created_at < %s AND v.version_no > 1 AND v.gate_status='passed'", (start, end))
        updates = cur.fetchone()["n"]
        cur.execute("SELECT count(*) AS n FROM intent_clusters WHERE queue_state='sweet_spot' AND updated_at >= %s AND updated_at < %s", (start, end))
        qualified = cur.fetchone()["n"]
        cur.execute("SELECT count(*) AS n FROM intent_clusters WHERE last_intel_at >= %s AND last_intel_at < %s", (start, end))
        tested = cur.fetchone()["n"]
        cur.execute("SELECT count(*) AS n FROM usage_ledger WHERE provider='search' AND occurred_at >= %s AND occurred_at < %s AND (detail->>'cached')::boolean IS FALSE", (start, end))
        searches = cur.fetchone()["n"]
    entries = _dispatch_entries(day)
    expensive = {"researcher", "planner", "writer", "editor", "verifier", "seo", "tool-engineer", "search-strategist"}
    wasted = 0
    ran_expensive = [e for e in entries if e.get("agent") in expensive and e.get("status") in ("ok", "hold", "partial", "invalid")]
    with conn.cursor() as cur:
        for e in ran_expensive:
            cid = (e.get("task_id") or "").split(":")[-1][:8]
            if not cid:
                continue
            cur.execute("SELECT 1 FROM intent_clusters WHERE id::text LIKE %s AND queue_state IN ('reject','navigational','watch') LIMIT 1", (cid + "%",))
            if cur.fetchone():
                wasted += 1
    turns, seconds = int(u["turns"]), float(u["seconds"])
    per = lambda n: {"turns": round(turns / n, 1), "minutes": round(seconds / 60 / n, 1)} if n else None
    return {"turns_total": turns, "minutes_total": round(seconds / 60, 1), "dispatches": int(u["dispatches"]), "iterations": int(u["iterations"]), "searches_new": int(searches),
            "per_published_page": per(published), "per_verified_update": per(updates), "per_qualified_cluster": per(qualified),
            "discovery_yield": (round(qualified / tested, 3) if tested else None), "qualified": qualified, "hypotheses_tested": tested,
            "wasted_work_rate": (round(wasted / len(ran_expensive), 3) if ran_expensive else 0.0), "expensive_stages_run": len(ran_expensive), "expensive_on_rejected": wasted}


def next_tasks(conn: psycopg.Connection) -> list[str]:
    from . import lanes
    out = []
    q = sweetspot.queue(conn, limit=1)
    if q:
        out.append(f"production: {q[0]['label']} (niche {q[0]['niche_score']}) via the R16 pipeline")
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT count(*) AS n FROM intent_clusters c WHERE c.last_intel_at IS NULL AND c.queue_state IN ('candidate','needs_intel') AND (c.hypothesis_count > 0 OR c.independent_occurrences >= 2)")
            n = cur.fetchone()["n"]
        if n:
            out.append(f"discovery: search intel for {n} clusters still waiting (batches of 10/25)")
    except psycopg.Error:
        conn.rollback()
    item = lanes.first_unblocked_backlog_item()
    if item:
        out.append(f"maintenance: BACKLOG {item['id']} — {item['task'][:80]}")
    return out[:3] or ["no unblocked work"]


def render(day: date, reason: str, data: dict) -> str:
    L = [f"# Daily digest — {day.isoformat()}", "", f"Written {datetime.now(timezone.utc).isoformat(timespec='seconds')} ({reason}). Everything below is read from the database, the run log and the dispatch log; nothing here is a measured rank or volume.", ""]
    L += ["## Tasks done (IDs, commits)", ""]
    L += [f"- {t.get('task_id') or '—'} · `{t.get('commit')}` · {t.get('subject') or (str(t.get('run')) + ' it.' + str(t.get('iteration')) + ' ' + str(t.get('result')))}" for t in data["tasks"]] or ["- none"]
    p = data["pages"]
    L += ["", "## Pages published, held and why", ""]
    L += [f"- published (local/live): `{x['path']}` tier {x['tier']}" for x in p["published"]] or ["- published: none"]
    L += [f"- held: `{x['path']}` — {x['revalidation_reason'] or 'no reason recorded'}" for x in p["held"]] or ["- held: none"]
    c = data["claims"]
    L += ["", "## Claims verified or superseded", "", f"- verified facts recorded today: {c['verified']}; superseded today: {c['superseded']}; still estimates (today's retrievals): {c['estimates']}"]
    L += [f"  - {x['canonical_name']}: {x['field']}{(' (' + x['room_type'] + ')') if x.get('room_type') else ''}" for x in c["examples"][:12]]
    s = data["skills"]
    L += ["", "## Skills evaluated, adopted or rejected", "", f"- last scout run {s.get('last_run')}; candidates {s.get('candidates')}, accepted {s.get('accepted')}, rejected {s.get('rejected')}, adopted {s.get('adopted')} (docs/ops/skill-evaluations.md)"]
    i = data["intel"]
    L += ["", "## Search intel and strategy changes", "", f"- observations stored today: {i['observations_today']}; strategies stored today: {i['strategies_today']}; auto-created topics: {i['auto_topics']}",
          f"- queue: {i['queue']['sweet_spot']} sweet-spot · {i['queue']['watch']} watch · {i['queue']['reject']} reject · {i['queue']['navigational']} navigational of {i['queue']['clusters']} clusters", "",
          "| # | scope | topic | cluster | D | AGI | G | E | niche_score |", "|---|---|---|---|---|---|---|---|---|"]
    L += [f"| {n} | {x['scope']} | {x['topic']} | {x['label'][:70]} | {x['d_score']} | {x['agi']} | {x['g_est']} | {x['e_est']} | {x['niche_score']} |" for n, x in enumerate(i["top_sweet_spot"], 1)] or ["| — | | | no sweet-spot clusters | | | | | |"]
    L += ["", "sweet-spot/watch candidates by topic: " + (", ".join(f"{b['topic']} ({b['candidates']})" for b in i["by_topic"]) or "none")]
    f = data["failures"]
    L += ["", "## Failures and blockers", ""]
    L += [f"- iteration {t.get('iteration')} ({t.get('run')}): {t.get('result')}" for t in f["failed_iterations"]] + [f"- held/dead-letter jobs: {h['job_type']} × {h['n']} ({h['hold_reason']})" for h in f["held_jobs"]]
    L += [f"- open exception ({e['severity']}): {e['message'][:160]}" for e in f["exceptions"]] + [f"- agent dispatches that failed/invalid/partial today: {f['agent_failures']}"] + [f"- {b}" for b in f["blockers"]]
    e = data["efficiency"]
    L += ["", "## Efficiency (R29)", "", f"- turns {e['turns_total']} · minutes {e['minutes_total']} · dispatches {e['dispatches']} · iterations {e['iterations']} · new searches {e['searches_new']}",
          f"- per published page: {e['per_published_page']}", f"- per verified update: {e['per_verified_update']}", f"- per qualified cluster: {e['per_qualified_cluster']}",
          f"- discovery yield: {e['discovery_yield']} ({e['qualified']} qualified / {e['hypotheses_tested']} tested)", f"- wasted-work rate: {e['wasted_work_rate']} ({e['expensive_on_rejected']} expensive stages on later-rejected clusters / {e['expensive_stages_run']})"]
    v = data["volume"]
    L += ["", "## Volume (R44)", "", f"- ready {v['counts']['totals']['ready']} · live {v['counts']['totals']['live']} · held {v['counts']['totals']['held']}", "", "| tier | scope | topic | ready | live | held |", "|---|---|---|---|---|---|"]
    L += [f"| {r['tier']} | {r['scope']} | {r['topic']} | {r['ready']} | {r['live']} | {r['held']} |" for r in v["counts"]["rows"]] or ["| — | | | 0 | 0 | 0 |"]
    pj = v["projection"]
    L += ["", f"- throughput: {pj['per_day']} ready pages/day over the last {pj['throughput']['window_days']} days; projected days to 1,000: {pj['projected_days']['1000']}, to 5,000: {pj['projected_days']['5000']} ({pj['note']})"]
    L += ["", "## Next 3 tasks", ""] + [f"{n}. {t}" for n, t in enumerate(data["next"], 1)]
    L.append("")
    return "\n".join(L)


def write(conn: psycopg.Connection, *, reason: str, day: date | None = None, out_dir: Path | None = None) -> Path:
    day = day or datetime.now(timezone.utc).date()
    data = {"tasks": tasks_done(day), "pages": pages_section(conn, day), "claims": claims_section(conn, day), "skills": skills_section(), "intel": intel_section(conn, day),
            "failures": failures_section(conn, day), "efficiency": efficiency(conn, day), "volume": volume.report(conn), "next": next_tasks(conn)}
    out_dir = out_dir or DIGEST_DIR
    out_dir.mkdir(parents=True, exist_ok=True)
    p = out_dir / f"{day.isoformat()}.md"
    p.write_text(render(day, reason, data))
    events.emit(conn, "digest_written", {"path": str(p), "reason": reason})
    return p


def main(argv: list[str]) -> int:
    from .db import connect
    reason = argv[argv.index("--reason") + 1] if "--reason" in argv else "manual"
    day = date.fromisoformat(argv[argv.index("--date") + 1]) if "--date" in argv else None
    conn = connect(get_settings().database_url)
    try:
        print(write(conn, reason=reason, day=day))
        return 0
    finally:
        conn.close()


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
