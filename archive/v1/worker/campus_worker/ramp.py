"""Unthrottled production, paced go-live (specs/continuous-local-run.md R8; AT9).

- Production never waits: a page that passes every gate is marked ready (`pages.ready_at`).
- Without a live domain, ready pages publish immediately to the local build and staging CMS (no quota).
- With a live domain (settings.is_live), ready pages go live best niche_score first under the ramp
  `CAMPUS_LIVE_RAMP` ("5x14,15" = 5/day for 14 days, then 15/day). Updates to live pages are never capped.
- If the analyst finds >20% of live pages unindexed after 14 days, the ramp holds at its current rate
  and the digest flags it (set_indexing_hold).
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date, datetime, timezone
from uuid import UUID

import psycopg

_STAGE = re.compile(r"^\s*(\d+)\s*(?:x\s*(\d+))?\s*$")


@dataclass(frozen=True)
class Stage:
    per_day: int
    days: int | None  # None = forever


def parse_ramp(spec: str) -> list[Stage]:
    stages: list[Stage] = []
    for i, part in enumerate(spec.split(",")):
        m = _STAGE.match(part)
        if not m:
            raise ValueError(f"bad ramp stage {part!r} in {spec!r}; expected '<per_day>x<days>' or '<per_day>'")
        per_day, days = int(m.group(1)), (int(m.group(2)) if m.group(2) else None)
        if per_day < 0:
            raise ValueError("ramp rate must be >= 0")
        stages.append(Stage(per_day, days))
    if not stages:
        raise ValueError("empty ramp")
    for s in stages[:-1]:
        if s.days is None:
            raise ValueError("only the last ramp stage may be open-ended")
    return stages


def rate_for_day(stages: list[Stage], day_index: int) -> int:
    """Pages/day allowed on the given 0-based day since live_since."""
    if day_index < 0:
        return 0
    cursor = 0
    for s in stages:
        if s.days is None or day_index < cursor + s.days:
            return s.per_day
        cursor += s.days
    return stages[-1].per_day


def _today(now: datetime | None) -> date:
    return (now or datetime.now(timezone.utc)).date()


def ramp_state(conn: psycopg.Connection) -> dict:
    with conn.cursor() as cur:
        cur.execute("SELECT live_since, hold, hold_reason, hold_rate_per_day, updated_at FROM ramp_state WHERE id=1")
        return dict(cur.fetchone())


def ensure_live_since(conn: psycopg.Connection, today: date) -> date:
    with conn.cursor() as cur:
        cur.execute("UPDATE ramp_state SET live_since=COALESCE(live_since,%s), updated_at=now() WHERE id=1 RETURNING live_since", (today,))
        return cur.fetchone()["live_since"]


def allowance(conn: psycopg.Connection, ramp_spec: str, *, now: datetime | None = None) -> dict:
    """How many NEW pages may still go live today."""
    today = _today(now)
    stages = parse_ramp(ramp_spec)
    st = ramp_state(conn)
    live_since = st["live_since"] or today
    day_index = (today - live_since).days
    rate = rate_for_day(stages, day_index)
    if st["hold"] and st["hold_rate_per_day"] is not None:
        rate = min(rate, int(st["hold_rate_per_day"]))
    with conn.cursor() as cur:
        cur.execute("SELECT count(*) AS n FROM live_releases WHERE released_on=%s AND kind='new'", (today,))
        released = cur.fetchone()["n"]
    return {"today": today.isoformat(), "day_index": day_index, "rate": rate, "released_today": released,
            "remaining": max(0, rate - released), "hold": st["hold"], "hold_reason": st["hold_reason"]}


def mark_ready(conn: psycopg.Connection, page_id: UUID, *, niche_score: float | None = None, now: datetime | None = None) -> None:
    with conn.cursor() as cur:
        cur.execute("UPDATE pages SET ready_at=COALESCE(ready_at,%s), niche_score=COALESCE(%s, niche_score) WHERE id=%s",
                    (now or datetime.now(timezone.utc), niche_score, page_id))
    conn.commit()


def ready_queue(conn: psycopg.Connection, *, limit: int | None = None) -> list[dict]:
    """Ready pages not yet live, best niche_score first (NULL last), then oldest ready first."""
    with conn.cursor() as cur:
        cur.execute(
            """SELECT p.id AS page_id, p.current_version_id AS version_id, p.path, p.niche_score, p.ready_at, p.tier, p.status
               FROM pages p WHERE p.ready_at IS NOT NULL AND p.first_published_at IS NULL AND p.status IN ('staged','held','drafting','planned')
                 AND p.current_version_id IS NOT NULL
               ORDER BY p.niche_score DESC NULLS LAST, p.ready_at ASC""" + (f" LIMIT {int(limit)}" if limit else ""))
        return [dict(r) for r in cur.fetchall()]


def record_release(conn: psycopg.Connection, page_id: UUID, version_id: UUID | None, *, kind: str, niche_score: float | None, now: datetime | None = None) -> None:
    with conn.cursor() as cur:
        cur.execute("INSERT INTO live_releases (page_id, version_id, released_on, released_at, niche_score, kind) VALUES (%s,%s,%s,%s,%s,%s)",
                    (page_id, version_id, _today(now), now or datetime.now(timezone.utc), niche_score, kind))
    conn.commit()


def set_indexing_hold(conn: psycopg.Connection, *, live_pages_checked: int, unindexed: int, current_rate: int, threshold: float = 0.20) -> dict:
    """Analyst re-check input (R8/R15): if more than `threshold` of live pages show no sign of indexing after 14 days,
    hold the ramp at the current rate. Clears the hold when the share drops to the threshold or below."""
    share = (unindexed / live_pages_checked) if live_pages_checked else 0.0
    hold = share > threshold
    reason = f"{unindexed}/{live_pages_checked} live pages ({share:.0%}) show no sign of indexing after 14 days" if hold else None
    with conn.cursor() as cur:
        cur.execute("UPDATE ramp_state SET hold=%s, hold_reason=%s, hold_rate_per_day=%s, updated_at=now() WHERE id=1",
                    (hold, reason, current_rate if hold else None))
    conn.commit()
    return {"hold": hold, "share_unindexed": round(share, 3), "reason": reason}


def live_counts(conn: psycopg.Connection) -> dict:
    with conn.cursor() as cur:
        cur.execute("""SELECT count(*) FILTER (WHERE ready_at IS NOT NULL AND first_published_at IS NULL) AS ready,
                              count(*) FILTER (WHERE first_published_at IS NOT NULL) AS live,
                              count(*) FILTER (WHERE status='held') AS held FROM pages""")
        return dict(cur.fetchone())
