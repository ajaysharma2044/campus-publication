"""Volume reporting (continuous-local-run R44; AT43): ready/live/held by tier, school and topic, and the projected days
to 1,000 and 5,000 ready pages at the current throughput."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

import psycopg

TARGETS = (1000, 5000)


def counts(conn: psycopg.Connection) -> dict:
    with conn.cursor() as cur:
        cur.execute("""SELECT p.tier, COALESCE(i.slug, pl.slug, '(none)') AS scope, COALESCE(t.key, '(none)') AS topic,
                              count(*) FILTER (WHERE p.ready_at IS NOT NULL AND p.first_published_at IS NULL) AS ready,
                              count(*) FILTER (WHERE p.first_published_at IS NOT NULL) AS live,
                              count(*) FILTER (WHERE p.status='held') AS held,
                              count(*) AS total
                       FROM pages p LEFT JOIN institutions i ON i.id=p.institution_id LEFT JOIN places pl ON pl.id=p.place_id LEFT JOIN topics t ON t.id=p.topic_id
                       WHERE p.status <> 'redirected' GROUP BY 1,2,3 ORDER BY 1,2,3""")
        rows = [dict(r) for r in cur.fetchall()]
        cur.execute("""SELECT count(*) FILTER (WHERE ready_at IS NOT NULL AND first_published_at IS NULL) AS ready, count(*) FILTER (WHERE first_published_at IS NOT NULL) AS live,
                              count(*) FILTER (WHERE status='held') AS held, count(*) FILTER (WHERE ready_at IS NOT NULL) AS ever_ready FROM pages WHERE status <> 'redirected'""")
        tot = dict(cur.fetchone())
    by_tier = {}
    for r in rows:
        d = by_tier.setdefault(r["tier"], {"ready": 0, "live": 0, "held": 0})
        for k in d:
            d[k] += r[k]
    return {"rows": rows, "totals": tot, "by_tier": by_tier}


def throughput(conn: psycopg.Connection, *, days: int = 7, now: datetime | None = None) -> dict:
    """Ready pages per day over the window, from pages.ready_at (actual run throughput, not a plan)."""
    now = now or datetime.now(timezone.utc)
    since = now - timedelta(days=days)
    with conn.cursor() as cur:
        cur.execute("SELECT count(*) AS n, min(ready_at) AS first FROM pages WHERE ready_at >= %s", (since,))
        r = cur.fetchone()
    n = int(r["n"])
    span_days = max(1.0, (now - r["first"]).total_seconds() / 86400) if r["first"] else float(days)
    return {"window_days": days, "ready_in_window": n, "per_day": round(n / span_days, 3), "since": since.isoformat()}


def projection(conn: psycopg.Connection, *, now: datetime | None = None) -> dict:
    tp = throughput(conn, now=now)
    c = counts(conn)
    ever = int(c["totals"]["ever_ready"])
    out = {"ready_total": ever, "per_day": tp["per_day"], "throughput": tp, "projected_days": {}}
    for target in TARGETS:
        remaining = max(0, target - ever)
        out["projected_days"][str(target)] = None if tp["per_day"] <= 0 else (0 if remaining == 0 else round(remaining / tp["per_day"]))
    out["note"] = "projection from actual ready_at throughput over the last 7 days; null when no page became ready in the window"
    return out


def report(conn: psycopg.Connection) -> dict:
    return {"counts": counts(conn), "projection": projection(conn)}
