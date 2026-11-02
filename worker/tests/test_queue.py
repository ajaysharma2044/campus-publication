import pytest
from campus_worker import queue as q
from campus_worker.types import JobRecord


def test_idempotent_enqueue(clean_conn):
    a, c1 = q.enqueue(clean_conn, JobRecord(job_type="t", idempotency_key="src:v1"))
    b, c2 = q.enqueue(clean_conn, JobRecord(job_type="t", idempotency_key="src:v1"))
    assert a == b and c1 and not c2
    assert q.counts(clean_conn) == {"queued": 1}


def test_lease_is_exclusive_and_respects_dependencies(clean_conn):
    a, _ = q.enqueue(clean_conn, JobRecord(job_type="research", idempotency_key="job-a"))
    b, _ = q.enqueue(clean_conn, JobRecord(job_type="draft", idempotency_key="job-b", depends_on=[a], priority=99))
    j1 = q.lease(clean_conn, "w1")
    assert j1.id == a  # b is blocked despite higher priority
    assert q.lease(clean_conn, "w2") is None
    q.complete(clean_conn, a, "w1")
    j2 = q.lease(clean_conn, "w2")
    assert j2.id == b


def test_expired_lease_is_reclaimed_and_lost_lease_completion_refused(clean_conn):
    a, _ = q.enqueue(clean_conn, JobRecord(job_type="t", idempotency_key="job-exp"))
    j = q.lease(clean_conn, "w1", lease_seconds=0)
    import time; time.sleep(0.05)
    assert q.reclaim_expired_leases(clean_conn) == [a]
    with pytest.raises(q.LeaseLost):
        q.complete(clean_conn, a, "w1")
    with clean_conn.cursor() as cur:
        cur.execute("SELECT count(*) AS n FROM exceptions WHERE job_id=%s", (a,))
        assert cur.fetchone()["n"] == 1
    j2 = q.lease(clean_conn, "w2")
    assert j2.id == a and j2.attempt == 2


def test_three_retries_then_dead_letter(clean_conn):
    a, _ = q.enqueue(clean_conn, JobRecord(job_type="t", idempotency_key="retry"))
    states = []
    for _ in range(3):
        j = q.lease(clean_conn, "w")
        assert j is not None
        states.append(q.fail(clean_conn, a, "w", "boom", retry_after_seconds=0))
    assert states == ["retry_wait", "retry_wait", "dead_letter"]
    assert q.lease(clean_conn, "w") is None
    dl = q.held_and_dead(clean_conn)
    assert dl[0]["state"] == "dead_letter" and dl[0]["hold_owner"] == "owner"


def test_non_retryable_failure_dead_letters_immediately(clean_conn):
    a, _ = q.enqueue(clean_conn, JobRecord(job_type="t", idempotency_key="perm"))
    q.lease(clean_conn, "w")
    assert q.fail(clean_conn, a, "w", "invalid input", retryable=False) == "dead_letter"


def test_hold_requires_reason_and_condition(clean_conn):
    a, _ = q.enqueue(clean_conn, JobRecord(job_type="t", idempotency_key="hold"))
    q.lease(clean_conn, "w")
    with pytest.raises(ValueError):
        q.hold(clean_conn, a, "w", "missing_evidence", "")
    q.hold(clean_conn, a, "w", "missing_evidence", "source snapshot for rates page available")
    held = q.held_and_dead(clean_conn)[0]
    assert held["hold_reason"] == "missing_evidence" and held["hold_retry_condition"]
    q.release_hold(clean_conn, a)
    assert q.lease(clean_conn, "w").id == a


def test_delegation_depth_limit(clean_conn):
    with pytest.raises(ValueError):
        q.enqueue(clean_conn, JobRecord(job_type="t", idempotency_key="deep", delegation_depth=2), max_delegation_depth=1)
