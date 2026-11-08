"""Operational dashboard.

    python -m campus_worker.dashboard.app   → http://127.0.0.1:8090/

Staff-only by design: bind to localhost or put behind the host's auth; it exposes internal
scores, excerpts counts and budget. It never renders raw source excerpts or correction text.
"""
from __future__ import annotations

import html
import json
from datetime import datetime, timezone

from starlette.applications import Starlette
from starlette.responses import HTMLResponse, JSONResponse
from starlette.routing import Route

from .. import budget as budgetmod
from .. import queue as queuemod
from ..cli import integrations_status
from ..config import get_settings
from ..db import connect


def gather(conn, settings) -> dict:
    d = {"generated_at": datetime.now(timezone.utc).isoformat(), "environment": settings.environment, "auth_mode": settings.auth_mode(),
         "budget": budgetmod.status(conn, settings.budget), "queue": queuemod.counts(conn), "held": [dict(r, id=str(r["id"]), age=str(r["age"])) for r in queuemod.held_and_dead(conn)],
         "integrations": integrations_status(settings)}
    with conn.cursor() as cur:
        cur.execute("SELECT component, last_started_at, last_success_at, last_status FROM heartbeats ORDER BY component")
        d["heartbeats"] = [dict(r) for r in cur.fetchall()]
        cur.execute("SELECT health, count(*) AS n FROM source_registry GROUP BY health")
        d["sources"] = {r["health"]: r["n"] for r in cur.fetchall()}
        cur.execute("SELECT count(*) AS n FROM source_registry WHERE next_refresh_at < now() AND health <> 'gone'")
        d["sources_overdue"] = cur.fetchone()["n"]
        cur.execute("SELECT evidence_category, count(*) AS n FROM claims WHERE superseded_by_id IS NULL GROUP BY evidence_category")
        d["claims"] = {r["evidence_category"]: r["n"] for r in cur.fetchall()}
        cur.execute("SELECT count(*) AS n FROM conflicts WHERE status='open'")
        d["open_conflicts"] = cur.fetchone()["n"]
        cur.execute("SELECT decision, count(*) AS n FROM (SELECT DISTINCT ON (cluster_id) decision FROM opportunity_scores ORDER BY cluster_id, scored_at DESC) s GROUP BY decision")
        d["opportunities"] = {r["decision"]: r["n"] for r in cur.fetchall()}
        cur.execute("SELECT status, count(*) AS n FROM pages GROUP BY status")
        d["pages"] = {r["status"]: r["n"] for r in cur.fetchall()}
        cur.execute("SELECT gate_status, count(*) AS n FROM page_versions GROUP BY gate_status")
        d["gates"] = {r["gate_status"]: r["n"] for r in cur.fetchall()}
        cur.execute("SELECT severity, category, message, occurred_at FROM exceptions WHERE resolved_at IS NULL ORDER BY occurred_at DESC LIMIT 20")
        d["exceptions"] = [dict(r, occurred_at=r["occurred_at"].isoformat()) for r in cur.fetchall()]
        cur.execute("SELECT key, area, status, primary_metric FROM experiments ORDER BY created_at DESC LIMIT 10")
        d["experiments"] = [dict(r) for r in cur.fetchall()]
        cur.execute("SELECT count(*) AS n, COALESCE(SUM(earnings_minor),0) AS e FROM revenue_reports")
        r = cur.fetchone()
        d["revenue"] = {"reports": r["n"], "earnings_minor_reported": int(r["e"]), "note": "network-reported, estimated; no reports imported" if not r["n"] else "network-reported, may revise"}
        cur.execute("SELECT count(*) AS n FROM analytics_aggregates")
        d["analytics_rows"] = cur.fetchone()["n"]
        cur.execute("SELECT resolved_model, count(*) AS n FROM runs WHERE resolved_model IS NOT NULL GROUP BY resolved_model")
        d["model_usage"] = {r["resolved_model"]: r["n"] for r in cur.fetchall()}
    # continuous-local-run R29 (efficiency) and R44 (volume) tiles, from the same functions the digest uses
    try:
        from .. import digest as digestmod, sweetspot, volume
        today = datetime.now(timezone.utc).date()
        d["efficiency"] = digestmod.efficiency(conn, today)
        vol = volume.report(conn)
        d["volume"] = {"totals": vol["counts"]["totals"], "by_tier_scope_topic": [f"tier {r['tier']} · {r['scope']} · {r['topic']}: ready {r['ready']} / live {r['live']} / held {r['held']}" for r in vol["counts"]["rows"]],
                       "throughput_per_day": vol["projection"]["per_day"], "projected_days_to_1000": vol["projection"]["projected_days"]["1000"], "projected_days_to_5000": vol["projection"]["projected_days"]["5000"], "note": vol["projection"]["note"]}
        d["sweet_spot_top10"] = [f"{q['label'][:60]} — D {q['d_score']} AGI {q['agi']} G {q['g_est']} E {q['e_est']} niche {q['niche_score']}" for q in sweetspot.queue(conn, limit=10)]
    except Exception as e:  # noqa: BLE001 — the dashboard must render even when a tile's tables are missing
        conn.rollback()
        d["efficiency"] = {"error": f"{type(e).__name__}: {e}"}
        d["volume"] = {"error": f"{type(e).__name__}: {e}"}
        d["sweet_spot_top10"] = []
    return d


def _kv(title: str, obj: dict | list, note: str = "") -> str:
    if isinstance(obj, dict):
        rows = "".join(f"<tr><th scope='row'>{html.escape(str(k))}</th><td>{html.escape(json.dumps(v, default=str) if isinstance(v, (dict, list)) else str(v))}</td></tr>" for k, v in obj.items()) or "<tr><td colspan=2 class='coverage-note'>none</td></tr>"
    else:
        rows = "".join(f"<tr><td colspan=2>{html.escape(json.dumps(v, default=str))}</td></tr>" for v in obj) or "<tr><td colspan=2 class='coverage-note'>none</td></tr>"
    return f"<section><h2 class='section-head'>{html.escape(title)}</h2>{('<p class=coverage-note>' + html.escape(note) + '</p>') if note else ''}<div class='table-wrap'><table class='facts'><tbody>{rows}</tbody></table></div></section>"


def render_html(d: dict) -> str:
    hb = {h["component"]: h for h in d["heartbeats"]}
    sched = hb.get("scheduler")
    status_line = (f"scheduler: <b>{html.escape(sched['last_status'] or '?')}</b>, last success {sched['last_success_at']}" if sched else "scheduler: <b>never run</b>")
    parts = [
        "<!doctype html><html lang=en><head><meta charset=utf-8><meta name=viewport content='width=device-width,initial-scale=1'><meta name=robots content='noindex,nofollow'>",
        "<title>Operations — Footnote Daily</title><link rel=stylesheet href='/static/campus.css'></head><body class='tpl-dashboard'>",
        f"<div class='staging-banner'>Operations dashboard · {html.escape(d['environment'])} · staff only · generated {html.escape(d['generated_at'])}</div>",
        "<main class='container' style='padding-top:24px'><h1>Operating status</h1>",
        f"<p class='deck'>{status_line}. Model credential: <b>{html.escape(d['auth_mode']['mode'])}</b> ({html.escape(d['auth_mode']['billing'])}). "
        f"Budget today {d['budget']['day_minor']}/{d['budget']['daily_cap_minor']}¢, month {d['budget']['month_minor']}/{d['budget']['monthly_cap_minor']}¢"
        f"{' — <b>PAUSED</b>' if d['budget']['paused'] else ''}. Unpriced usage this month: {d['budget']['unpriced_month_minor']}¢.</p>",
        "<div class='grid'><div class='col-12 col-md-6'>",
        _kv("Integrations", {k: f"{v['state']} — {v['reason']}" for k, v in d["integrations"].items()}, "connected = real credential present; fixture/unconnected/disabled are not live services"),
        _kv("Jobs by state", d["queue"]), _kv("Held and dead-letter jobs", d["held"], "owner, reason, retry condition, age"),
        _kv("Heartbeats", {h["component"]: f"{h['last_status']} · started {h['last_started_at']} · last success {h['last_success_at']}" for h in d["heartbeats"]}),
        "</div><div class='col-12 col-md-6'>",
        _kv("Sources by health", dict(d["sources"], overdue=d["sources_overdue"])), _kv("Claims by evidence category", dict(d["claims"], open_conflicts=d["open_conflicts"])),
        _kv("Opportunities (latest decision per cluster)", d["opportunities"]), _kv("Pages by status", d["pages"]), _kv("Draft gates", d["gates"]),
        _kv("Model usage (resolved model → runs)", d["model_usage"]), _kv("Experiments", d["experiments"]),
        _kv("Revenue", d["revenue"]), _kv("Analytics", {"aggregate_rows": d["analytics_rows"]}),
        "</div></div>",
        "<div class='grid'><div class='col-12 col-md-6'>", _kv("Efficiency today (R29)", d.get("efficiency", {}), "turns and minutes per published page, per verified update, per qualified cluster; discovery yield; wasted-work rate"),
        "</div><div class='col-12 col-md-6'>", _kv("Volume (R44)", d.get("volume", {}), "ready/live/held by tier, scope and topic; projected days to 1,000 and 5,000 ready pages from actual throughput"),
        _kv("Sweet-spot queue (top 10)", d.get("sweet_spot_top10", []), "D, AGI, G, E, niche_score; observed via search tool, never measured volume"), "</div></div>",
        _kv("Open exceptions", d["exceptions"]),
        "<p class='coverage-note'>Nothing on this page is a live-service claim unless the integration state says connected and a heartbeat shows a recent success.</p></main></body></html>",
    ]
    return "".join(parts)


async def index(request):
    settings = get_settings()
    conn = connect(settings.database_url)
    try:
        return HTMLResponse(render_html(gather(conn, settings)))
    finally:
        conn.close()


async def status_json(request):
    settings = get_settings()
    conn = connect(settings.database_url)
    try:
        return JSONResponse(json.loads(json.dumps(gather(conn, settings), default=str)))
    finally:
        conn.close()


async def health(request):
    settings = get_settings()
    conn = connect(settings.database_url)
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT last_success_at, last_status FROM heartbeats WHERE component='scheduler'")
            r = cur.fetchone()
        ok = bool(r and r["last_success_at"])
        return JSONResponse({"ok": ok, "scheduler_last_success": r["last_success_at"].isoformat() if ok else None, "status": r["last_status"] if r else "never_run"}, status_code=200 if ok else 503)
    finally:
        conn.close()


from starlette.staticfiles import StaticFiles  # noqa: E402
from ..render.engine import STATIC_DIR  # noqa: E402

app = Starlette(routes=[Route("/", index), Route("/status.json", status_json), Route("/health", health)])
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8090)
