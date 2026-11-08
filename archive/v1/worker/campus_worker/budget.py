"""Budget ledger and enforcement (SPEC §26, §38).

Every paid call reserves a safe upper-bound estimate atomically before the request, then
reconciles to actual usage afterwards. Daily and monthly caps are enforced with headroom.
Unpriced paid work cannot reserve and must be held. Unpriced *usage* (e.g. a provider whose
price is unknown) is still recorded with priced=FALSE so it is visible, never hidden.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import date, datetime, timezone
from uuid import UUID

import psycopg

from .config import Budget
from .types import UsageEntry


class BudgetExceeded(Exception):
    pass


class Unpriced(Exception):
    pass


@dataclass
class Reservation:
    id: UUID
    amount_minor: int
    job_id: UUID | None
    run_id: UUID | None
    provider: str


def _keys(now: datetime | None = None) -> tuple[date, str]:
    now = now or datetime.now(timezone.utc)
    return now.date(), now.strftime("%Y-%m")


def spent(conn: psycopg.Connection, *, now: datetime | None = None) -> dict:
    """Committed spend (reservations + actuals + releases) for today and this month."""
    day, month = _keys(now)
    with conn.cursor() as cur:
        cur.execute("SELECT COALESCE(SUM(amount_minor),0) AS s FROM usage_ledger WHERE day=%s AND priced", (day,))
        d = cur.fetchone()["s"]
        cur.execute("SELECT COALESCE(SUM(amount_minor),0) AS s FROM usage_ledger WHERE month=%s AND priced", (month,))
        m = cur.fetchone()["s"]
        cur.execute("SELECT COALESCE(SUM(amount_minor),0) AS s FROM usage_ledger WHERE month=%s AND NOT priced", (month,))
        unpriced = cur.fetchone()["s"]
    return {"day": day.isoformat(), "day_minor": int(d), "month": month, "month_minor": int(m), "unpriced_month_minor": int(unpriced)}


def reserve(conn: psycopg.Connection, budget: Budget, entry: UsageEntry, *, now: datetime | None = None) -> Reservation:
    """Atomically reserve `entry.amount_minor` (a safe upper bound). Raises BudgetExceeded or Unpriced.

    Uses a transaction-level advisory lock so concurrent workers cannot both pass the check.
    """
    if entry.kind != "reservation":
        raise ValueError("reserve() takes a reservation entry")
    if entry.amount_minor is None or entry.amount_minor <= 0 or not entry.priced:
        raise Unpriced("paid work must carry a positive priced upper-bound estimate before it can run")
    day, month = _keys(now)
    with conn.cursor() as cur:
        cur.execute("SELECT pg_advisory_xact_lock(hashtext('campus_budget'))")
        cur.execute("SELECT COALESCE(SUM(amount_minor),0) AS s FROM usage_ledger WHERE day=%s AND priced", (day,))
        d = int(cur.fetchone()["s"])
        cur.execute("SELECT COALESCE(SUM(amount_minor),0) AS s FROM usage_ledger WHERE month=%s AND priced", (month,))
        m = int(cur.fetchone()["s"])
        day_limit = budget.daily_cap_minor * (100 - budget.headroom_pct) // 100
        month_limit = budget.monthly_cap_minor * (100 - budget.headroom_pct) // 100
        if d + entry.amount_minor > day_limit:
            conn.rollback()
            raise BudgetExceeded(f"daily cap: spent {d} + {entry.amount_minor} > {day_limit} minor units (cap {budget.daily_cap_minor} less {budget.headroom_pct}% headroom)")
        if m + entry.amount_minor > month_limit:
            conn.rollback()
            raise BudgetExceeded(f"monthly cap: spent {m} + {entry.amount_minor} > {month_limit} minor units")
        cur.execute(
            """INSERT INTO usage_ledger (day, month, job_id, run_id, provider, kind, amount_minor, currency, priced, detail)
               VALUES (%s,%s,%s,%s,%s,'reservation',%s,%s,TRUE,%s::jsonb) RETURNING id""",
            (day, month, entry.job_id, entry.run_id, entry.provider, entry.amount_minor, entry.currency, json.dumps(entry.detail)),
        )
        rid = cur.fetchone()["id"]
    conn.commit()
    return Reservation(rid, entry.amount_minor, entry.job_id, entry.run_id, entry.provider)


def reconcile(conn: psycopg.Connection, res: Reservation, actual_minor: int, *, detail: dict | None = None, now: datetime | None = None) -> None:
    """Replace the reservation with actual spend: release the reservation, record the actual."""
    day, month = _keys(now)
    with conn.cursor() as cur:
        cur.execute(
            """INSERT INTO usage_ledger (day, month, job_id, run_id, provider, kind, amount_minor, priced, detail)
               VALUES (%s,%s,%s,%s,%s,'release',%s,TRUE,%s::jsonb)""",
            (day, month, res.job_id, res.run_id, res.provider, -res.amount_minor, json.dumps({"reservation_id": str(res.id)})),
        )
        cur.execute(
            """INSERT INTO usage_ledger (day, month, job_id, run_id, provider, kind, amount_minor, priced, detail)
               VALUES (%s,%s,%s,%s,%s,'actual',%s,TRUE,%s::jsonb)""",
            (day, month, res.job_id, res.run_id, res.provider, actual_minor, json.dumps(detail or {})),
        )
    conn.commit()


def record_unpriced_usage(conn: psycopg.Connection, entry: UsageEntry, *, now: datetime | None = None) -> None:
    """Visibility for usage whose price is unknown. Does not count toward caps but is reported."""
    day, month = _keys(now)
    with conn.cursor() as cur:
        cur.execute(
            """INSERT INTO usage_ledger (day, month, job_id, run_id, provider, kind, amount_minor, priced, detail)
               VALUES (%s,%s,%s,%s,%s,'actual',%s,FALSE,%s::jsonb)""",
            (day, month, entry.job_id, entry.run_id, entry.provider, entry.amount_minor, json.dumps(entry.detail)),
        )
    conn.commit()


def status(conn: psycopg.Connection, budget: Budget, *, now: datetime | None = None, execution_mode: str = "api") -> dict:
    """Budget state. In session mode (continuous-local-run R7) dollar caps never pause work: the
    figures are still reported, `paused` is always False, and session usage is counted separately."""
    s = spent(conn, now=now)
    s.update(
        daily_cap_minor=budget.daily_cap_minor,
        monthly_cap_minor=budget.monthly_cap_minor,
        headroom_pct=budget.headroom_pct,
        daily_remaining_minor=max(0, budget.daily_cap_minor * (100 - budget.headroom_pct) // 100 - s["day_minor"]),
        monthly_remaining_minor=max(0, budget.monthly_cap_minor * (100 - budget.headroom_pct) // 100 - s["month_minor"]),
        execution_mode=execution_mode,
    )
    capped = s["daily_remaining_minor"] == 0 or s["monthly_remaining_minor"] == 0
    s["paused"] = capped if execution_mode == "api" else False
    s["cap_reached_but_not_enforced"] = capped and execution_mode == "session"
    if execution_mode == "session":
        s["session"] = session_usage_summary(conn, now=now)
    return s


SESSION_PROVIDER = "session"


def record_session_usage(conn: psycopg.Connection, *, kind: str, task_id: str | None, agent: str | None, duration_s: float,
                         turns: int | None, iteration: int | None = None, run_id: UUID | None = None, job_id: UUID | None = None,
                         extra: dict | None = None, now: datetime | None = None) -> UUID:
    """Record one unpriced usage entry per iteration or per agent dispatch (R7). amount is 0 and priced=FALSE,
    so it never counts toward dollar caps but is always visible. kind: 'iteration' | 'dispatch'."""
    if kind not in ("iteration", "dispatch"):
        raise ValueError("session usage kind must be 'iteration' or 'dispatch'")
    now = now or datetime.now(timezone.utc)
    day, month = _keys(now)
    detail = {"session_kind": kind, "task_id": task_id, "agent": agent, "duration_s": round(float(duration_s), 3), "turns": turns, "iteration": iteration}
    if extra:
        detail.update(extra)
    with conn.cursor() as cur:
        cur.execute(
            """INSERT INTO usage_ledger (occurred_at, day, month, job_id, run_id, provider, kind, amount_minor, currency, priced, detail)
               VALUES (%s,%s,%s,%s,%s,%s,'actual',0,'USD',FALSE,%s::jsonb) RETURNING id""",
            (now, day, month, job_id, run_id, SESSION_PROVIDER, json.dumps(detail, default=str)),
        )
        rid = cur.fetchone()["id"]
    conn.commit()
    return rid


def session_usage_summary(conn: psycopg.Connection, *, now: datetime | None = None) -> dict:
    day, month = _keys(now)
    with conn.cursor() as cur:
        cur.execute(
            """SELECT count(*) FILTER (WHERE detail->>'session_kind'='iteration') AS iterations,
                      count(*) FILTER (WHERE detail->>'session_kind'='dispatch') AS dispatches,
                      COALESCE(SUM((detail->>'duration_s')::numeric),0) AS seconds,
                      COALESCE(SUM((detail->>'turns')::int),0) AS turns
               FROM usage_ledger WHERE provider=%s AND day=%s""", (SESSION_PROVIDER, day))
        d = dict(cur.fetchone())
        cur.execute("SELECT count(*) AS n FROM usage_ledger WHERE provider=%s AND month=%s", (SESSION_PROVIDER, month))
        d["month_entries"] = cur.fetchone()["n"]
    return {k: (float(v) if k == "seconds" else int(v)) for k, v in d.items()}


# Pricing table for upper-bound estimates (USD per million tokens). These are *estimates for
# reservation only*; actual spend is reconciled from provider usage. Update from the provider's
# current price list before connecting a real key; unknown model → Unpriced.
MODEL_PRICE_PER_MTOK_MINOR = {
    # model id: (input cents per 1M tokens, output cents per 1M tokens)
    "claude-haiku-5-5": (100, 500),
    "claude-sonnet-5-5": (300, 1500),
    "claude-opus-5-5": (1500, 7500),
}


def estimate_model_call_minor(model: str, max_input_tokens: int, max_output_tokens: int) -> int:
    if model not in MODEL_PRICE_PER_MTOK_MINOR:
        raise Unpriced(f"no price entry for model {model}; hold the job until priced")
    cin, cout = MODEL_PRICE_PER_MTOK_MINOR[model]
    est = (max_input_tokens * cin + max_output_tokens * cout) / 1_000_000
    return max(1, int(est + 0.999))  # round up: safe upper bound, never zero
