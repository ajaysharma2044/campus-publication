"""Execution mode (specs/continuous-local-run.md R7; AT8).

Session mode: dollar caps never block work, and the ledger still records one unpriced usage entry per
iteration and per agent dispatch. API mode: caps behave exactly as before (test_budget.py covers them).
"""
import dataclasses
from datetime import datetime, timezone

import pytest

from campus_worker import budget as budgetmod
from campus_worker import queue as q
from campus_worker.config import Budget, Settings, get_settings
from campus_worker.scheduler import run_once
from campus_worker.types import JobRecord, UsageEntry


def _overspend(conn, budget: Budget):
    """Record priced spend above the daily cap directly (as reconciled actuals)."""
    now = datetime.now(timezone.utc)
    with conn.cursor() as cur:
        cur.execute("INSERT INTO usage_ledger (occurred_at, day, month, provider, kind, amount_minor, priced) VALUES (%s,%s,%s,'anthropic','actual',%s,TRUE)",
                    (now, now.date(), now.strftime("%Y-%m"), budget.daily_cap_minor + 100))
    conn.commit()


def test_session_mode_never_pauses_on_dollar_caps(clean_conn):
    b = Budget(daily_cap_minor=300, monthly_cap_minor=6000)
    _overspend(clean_conn, b)
    api = budgetmod.status(clean_conn, b, execution_mode="api")
    assert api["paused"] is True
    sess = budgetmod.status(clean_conn, b, execution_mode="session")
    assert sess["paused"] is False and sess["cap_reached_but_not_enforced"] is True and sess["execution_mode"] == "session"


def test_session_usage_entries_are_recorded_unpriced(clean_conn):
    rid = budgetmod.record_session_usage(clean_conn, kind="iteration", task_id="S4", agent=None, duration_s=12.5, turns=3, iteration=1)
    budgetmod.record_session_usage(clean_conn, kind="dispatch", task_id="S4", agent="researcher", duration_s=4.0, turns=2, iteration=1)
    with clean_conn.cursor() as cur:
        cur.execute("SELECT provider, kind, amount_minor, priced, detail FROM usage_ledger WHERE id=%s", (rid,))
        r = cur.fetchone()
    assert r["provider"] == "session" and r["amount_minor"] == 0 and r["priced"] is False and r["detail"]["task_id"] == "S4" and r["detail"]["turns"] == 3
    s = budgetmod.session_usage_summary(clean_conn)
    assert s["iterations"] == 1 and s["dispatches"] == 1 and s["turns"] == 5 and s["seconds"] == 16.5
    # unpriced session usage never counts toward the priced caps
    assert budgetmod.spent(clean_conn)["day_minor"] == 0
    with pytest.raises(ValueError):
        budgetmod.record_session_usage(clean_conn, kind="other", task_id=None, agent=None, duration_s=1, turns=None)


def test_scheduler_tick_in_session_mode_is_not_usage_paused_over_cap(clean_conn, monkeypatch):
    b = Budget(daily_cap_minor=300, monthly_cap_minor=6000)
    _overspend(clean_conn, b)
    base = get_settings()
    api_settings = dataclasses.replace(base, budget=b, execution_mode="api")
    r = run_once(clean_conn, api_settings)
    assert r["status"] == "usage_paused" and r["exit_code"] == 20
    sess_settings = dataclasses.replace(base, budget=b, execution_mode="session")
    r = run_once(clean_conn, sess_settings)
    assert r["status"] == "waiting" and r["exit_code"] == 10 and r["budget"]["paused"] is False
    q.enqueue(clean_conn, JobRecord(job_type="noop", idempotency_key="session-noop"))
    r = run_once(clean_conn, sess_settings)
    assert r["status"] == "completed"


def test_settings_default_mode_is_session_and_env_validated(monkeypatch):
    monkeypatch.delenv("CAMPUS_EXECUTION_MODE", raising=False)
    s = Settings.from_env()
    assert s.execution_mode == "session" and s.auth_mode()["mode"] == "session" and s.auth_mode()["connected"] is True
    monkeypatch.setenv("CAMPUS_EXECUTION_MODE", "api")
    assert Settings.from_env().execution_mode == "api"
    monkeypatch.setenv("CAMPUS_EXECUTION_MODE", "cloud")
    with pytest.raises(ValueError):
        Settings.from_env()
