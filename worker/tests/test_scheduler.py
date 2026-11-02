from campus_worker import queue as q
from campus_worker.config import Budget, Settings, get_settings
from campus_worker.scheduler import plan_daily, run_once
from campus_worker.types import JobRecord
import dataclasses


def _settings(**over):
    s = get_settings()
    return dataclasses.replace(s, **over)


def test_tick_waiting_then_completes_and_retries(clean_conn):
    r = run_once(clean_conn, _settings())
    assert r["status"] == "waiting" and r["exit_code"] == 10
    a, _ = q.enqueue(clean_conn, JobRecord(job_type="noop", idempotency_key="tick-noop"))
    b, _ = q.enqueue(clean_conn, JobRecord(job_type="fail_once_then_succeed", idempotency_key="tick-flaky", depends_on=[a]))
    r = run_once(clean_conn, _settings())
    assert r["status"] == "completed" and [x["result"] for x in r["ran"]] == ["succeeded", "retry_wait"]
    with clean_conn.cursor() as cur:
        cur.execute("UPDATE jobs SET not_before=now() WHERE id=%s", (b,))
    clean_conn.commit()
    r = run_once(clean_conn, _settings())
    assert [x["result"] for x in r["ran"]] == ["succeeded"] and q.counts(clean_conn) == {"succeeded": 2}
    with clean_conn.cursor() as cur:
        cur.execute("SELECT last_status, last_success_at FROM heartbeats WHERE component='scheduler'")
        hb = cur.fetchone()
        cur.execute("SELECT count(*) AS n FROM runs WHERE status='succeeded'")
        assert cur.fetchone()["n"] == 2
    assert hb["last_status"] == "completed" and hb["last_success_at"]


def test_unknown_job_type_dead_letters_and_unpriced_paid_is_held(clean_conn):
    q.enqueue(clean_conn, JobRecord(job_type="deploy_everything", idempotency_key="evil-job"))
    q.enqueue(clean_conn, JobRecord(job_type="write_draft", idempotency_key="unpriced-draft", is_paid=True, estimated_cost_minor=None))
    r = run_once(clean_conn, _settings())
    assert len(r["held_unpriced"]) == 1
    states = q.counts(clean_conn)
    assert states == {"dead_letter": 1, "held": 1}


def test_model_job_holds_on_missing_credential_and_tick_reports_blocked(clean_conn, monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    q.enqueue(clean_conn, JobRecord(job_type="write_draft", idempotency_key="draft-1", is_paid=True, estimated_cost_minor=50))
    r = run_once(clean_conn, _settings())
    assert r["ran"][0]["result"] == "held:provider_auth"
    r2 = run_once(clean_conn, _settings())
    assert r2["status"] == "blocked" and r2["exit_code"] == 30


def test_budget_pause_blocks_paid_jobs_but_not_deterministic_ones(clean_conn):
    from campus_worker import budget as b
    from campus_worker.types import UsageEntry
    paused = Budget(daily_cap_minor=10, monthly_cap_minor=1000, headroom_pct=0)
    b.reserve(clean_conn, paused, UsageEntry(provider="anthropic", kind="reservation", amount_minor=10))
    q.enqueue(clean_conn, JobRecord(job_type="write_draft", idempotency_key="paid-x", is_paid=True, estimated_cost_minor=5))
    q.enqueue(clean_conn, JobRecord(job_type="noop", idempotency_key="free-x"))
    r = run_once(clean_conn, _settings(budget=paused))
    assert [x["job_type"] for x in r["ran"]] == ["noop"] and r["budget"]["paused"]
    r2 = run_once(clean_conn, _settings(budget=paused))
    assert r2["status"] == "usage_paused" and r2["exit_code"] == 20


def test_interrupt_and_resume_without_duplicate_work(clean_conn):
    """Simulate a crash mid-tick: job leased, process dies (lease expires), next tick reclaims and completes once."""
    a, _ = q.enqueue(clean_conn, JobRecord(job_type="noop", idempotency_key="resume-1"))
    j = q.lease(clean_conn, "crashed-worker", lease_seconds=0)
    import time; time.sleep(0.05)
    r = run_once(clean_conn, _settings())
    assert r["reclaimed"] == [str(a)] and r["ran"][0]["result"] == "succeeded"
    with clean_conn.cursor() as cur:
        cur.execute("SELECT attempts, state FROM jobs WHERE id=%s", (a,))
        row = cur.fetchone()
    assert row["state"] == "succeeded" and row["attempts"] == 2
    assert run_once(clean_conn, _settings())["ran"] == []  # nothing duplicated


def test_lock_prevents_overlap(clean_conn, migrated_url):
    from campus_worker import db as dbmod
    other = dbmod.connect(migrated_url)
    try:
        with other.cursor() as cur:
            cur.execute("SELECT pg_advisory_lock(hashtext('campus_scheduler_tick'))")
        r = run_once(clean_conn, _settings())
        assert r["status"] == "locked"
        with other.cursor() as cur:
            cur.execute("SELECT pg_advisory_unlock(hashtext('campus_scheduler_tick'))")
    finally:
        other.close()


def test_plan_daily_respects_exploration_share(clean_conn):
    from tests.helpers import make_school, make_source
    inst, campus, topics = make_school(clean_conn)
    inst2, campus2, _ = make_school(clean_conn, name="Riverbend CC", slug="rcc", itype="community_college", unitid="900003")
    with clean_conn.cursor() as cur:
        cur.execute("INSERT INTO school_configs (institution_id, campus_id, is_underserved) VALUES (%s,%s,FALSE),(%s,%s,TRUE)", (inst, campus, inst2, campus2))
    clean_conn.commit()
    for i in range(30):
        make_source(clean_conn, inst, campus, f"https://www.example.edu/big{i}")
    for i in range(5):
        make_source(clean_conn, inst2, campus2, f"https://www.example.edu/cc{i}")
    out = plan_daily(clean_conn, _settings())
    assert out["enqueued"] == 20 and out["due_sources"] == 35
    with clean_conn.cursor() as cur:
        cur.execute("SELECT institution_id, count(*) AS n FROM jobs GROUP BY institution_id")
        by = {r["institution_id"]: r["n"] for r in cur.fetchall()}
    assert by[inst2] == 4 and by[inst] == 16  # 20% exploration share for the underserved school
