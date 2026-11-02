import pytest
from campus_worker import budget as b
from campus_worker.config import Budget
from campus_worker.types import UsageEntry


def test_reservation_blocks_when_cap_exceeded(clean_conn):
    cfg = Budget(daily_cap_minor=300, monthly_cap_minor=6000, headroom_pct=10)  # usable 270/day
    r1 = b.reserve(clean_conn, cfg, UsageEntry(provider="anthropic", kind="reservation", amount_minor=200))
    with pytest.raises(b.BudgetExceeded):
        b.reserve(clean_conn, cfg, UsageEntry(provider="anthropic", kind="reservation", amount_minor=100))
    b.reconcile(clean_conn, r1, 50)  # actual was much lower → room again
    assert b.spent(clean_conn)["day_minor"] == 50
    b.reserve(clean_conn, cfg, UsageEntry(provider="anthropic", kind="reservation", amount_minor=100))
    st = b.status(clean_conn, cfg)
    assert st["daily_remaining_minor"] == 270 - 150 and st["paused"] is False


def test_unpriced_cannot_reserve_but_is_visible(clean_conn):
    cfg = Budget()
    with pytest.raises(b.Unpriced):
        b.reserve(clean_conn, cfg, UsageEntry(provider="search", kind="reservation", amount_minor=0))
    b.record_unpriced_usage(clean_conn, UsageEntry(provider="search", kind="actual", amount_minor=0, priced=False, detail={"calls": 3}))
    assert b.spent(clean_conn)["unpriced_month_minor"] == 0
    with clean_conn.cursor() as cur:
        cur.execute("SELECT count(*) AS n FROM usage_ledger WHERE NOT priced")
        assert cur.fetchone()["n"] == 1


def test_monthly_cap_enforced(clean_conn):
    cfg = Budget(daily_cap_minor=100000, monthly_cap_minor=1000, headroom_pct=0)
    b.reserve(clean_conn, cfg, UsageEntry(provider="anthropic", kind="reservation", amount_minor=900))
    with pytest.raises(b.BudgetExceeded, match="monthly"):
        b.reserve(clean_conn, cfg, UsageEntry(provider="anthropic", kind="reservation", amount_minor=200))


def test_estimate_rounds_up_and_unknown_model_unpriced():
    assert b.estimate_model_call_minor("claude-haiku-5-5", 1000, 1000) == 1
    assert b.estimate_model_call_minor("claude-opus-5-5", 100_000, 4_000) == 180
    with pytest.raises(b.Unpriced):
        b.estimate_model_call_minor("claude-ancient-1", 10, 10)
