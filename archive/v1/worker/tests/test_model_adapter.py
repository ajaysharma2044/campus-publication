import json
import pytest
from campus_worker import budget as b
from campus_worker.adapters.base import ProviderError
from campus_worker.adapters.model import AnthropicProvider, FixtureProvider, HoldJob, ModelRouter
from campus_worker.config import Budget, ModelRouting


def _run(conn):
    with conn.cursor() as cur:
        cur.execute("INSERT INTO jobs (job_type, idempotency_key) VALUES ('t','m1') RETURNING id")
        jid = cur.fetchone()["id"]
        cur.execute("INSERT INTO runs (job_id, attempt, role) VALUES (%s,1,'writer') RETURNING id", (jid,))
        rid = cur.fetchone()["id"]
    conn.commit()
    return jid, rid


def test_unconnected_without_key(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    cap = AnthropicProvider().capability()
    assert cap.state == "unconnected" and not cap.connected


def test_resolved_model_recorded(clean_conn):
    jid, rid = _run(clean_conn)
    prov = FixtureProvider({("claude-sonnet-5-5", "default"): '{"ok":true}'})
    router = ModelRouter(ModelRouting(), Budget(), prov)
    out = router.call(clean_conn, role="writing_model", system="s", user="u", max_tokens=100, max_input_tokens=1000, job_id=jid, run_id=rid)
    assert out.resolved_model == "claude-sonnet-5-5" and out.escalation_level == 0
    with clean_conn.cursor() as cur:
        cur.execute("SELECT requested_model, resolved_model, usage FROM runs WHERE id=%s", (rid,))
        r = cur.fetchone()
    assert r["resolved_model"] == "claude-sonnet-5-5" and r["usage"]["calls"] == 1
    assert b.spent(clean_conn)["day_minor"] >= 0  # reservation released, actual recorded


def test_cheap_tier_escalates_once_within_ceiling(clean_conn):
    jid, rid = _run(clean_conn)
    prov = FixtureProvider({("claude-haiku-5-5", "default"): "weak", ("claude-opus-5-5", "default"): "strong"})
    router = ModelRouter(ModelRouting(), Budget(), prov)
    validate = lambda t: [] if t == "strong" else ["judgment:answer does not resolve the task"]
    out = router.call(clean_conn, role="classification_model", system="s", user="u", max_tokens=50, max_input_tokens=100, job_id=jid, run_id=rid, validate=validate)
    assert out.resolved_model == "claude-opus-5-5" and out.escalation_level == 1
    models = [c["model"] for c in prov.calls]
    assert models == ["claude-haiku-5-5", "claude-haiku-5-5", "claude-opus-5-5"]  # 1 repair, then 1 escalation


def test_escalation_ceiling_then_hold(clean_conn):
    jid, rid = _run(clean_conn)
    prov = FixtureProvider({("claude-haiku-5-5", "default"): "weak", ("claude-opus-5-5", "default"): "still weak"})
    router = ModelRouter(ModelRouting(), Budget(), prov)
    with pytest.raises(HoldJob) as e:
        router.call(clean_conn, role="classification_model", system="s", user="u", max_tokens=50, max_input_tokens=100, job_id=jid, run_id=rid, validate=lambda t: ["judgment:bad"])
    assert e.value.reason == "escalation_exhausted"
    assert len(prov.calls) == 4  # haiku, haiku repair, opus, opus repair — then hold, no more calls


def test_missing_evidence_holds_without_escalation(clean_conn):
    jid, rid = _run(clean_conn)
    prov = FixtureProvider()
    router = ModelRouter(ModelRouting(), Budget(), prov)
    with pytest.raises(HoldJob) as e:
        router.call(clean_conn, role="writing_model", system="s", user="u", max_tokens=50, max_input_tokens=100, job_id=jid, run_id=rid,
                    validate=lambda t: ["evidence:critical claim rate.double has no source"])
    assert e.value.reason == "missing_evidence"
    assert all(c["model"] == "claude-sonnet-5-5" for c in prov.calls) and len(prov.calls) == 2


def test_budget_reservation_failure_prevents_paid_call(clean_conn):
    jid, rid = _run(clean_conn)
    prov = FixtureProvider()
    router = ModelRouter(ModelRouting(), Budget(daily_cap_minor=1, monthly_cap_minor=1, headroom_pct=0), prov)
    with pytest.raises(b.BudgetExceeded):
        router.call(clean_conn, role="editorial_model", system="s", user="u", max_tokens=4000, max_input_tokens=100_000, job_id=jid, run_id=rid)
    assert prov.calls == []  # provider never invoked


def test_outage_is_retryable_not_escalated(clean_conn):
    jid, rid = _run(clean_conn)
    prov = FixtureProvider({("claude-sonnet-5-5", "default"): ProviderError("529 overloaded", retryable=True, kind="outage")})
    router = ModelRouter(ModelRouting(), Budget(), prov)
    with pytest.raises(ProviderError) as e:
        router.call(clean_conn, role="writing_model", system="s", user="u", max_tokens=50, max_input_tokens=100, job_id=jid, run_id=rid)
    assert e.value.retryable and len(prov.calls) == 1
    assert b.spent(clean_conn)["day_minor"] == 0  # reservation released


def test_unavailable_model_uses_preapproved_fallback_else_holds(clean_conn):
    jid, rid = _run(clean_conn)
    prov = FixtureProvider(models={"claude-opus-5-5"})
    router = ModelRouter(ModelRouting(), Budget(), prov)
    out = router.call(clean_conn, role="writing_model", system="s", user="u", max_tokens=50, max_input_tokens=100, job_id=jid, run_id=rid)
    assert out.resolved_model == "claude-opus-5-5" and "fallback" in out.fallback_rationale
    prov2 = FixtureProvider(models={"claude-haiku-5-5"})
    router2 = ModelRouter(ModelRouting(), Budget(), prov2)
    with pytest.raises(HoldJob) as e:
        router2.call(clean_conn, role="editorial_model", system="s", user="u", max_tokens=50, max_input_tokens=100, job_id=jid, run_id=rid)
    assert e.value.reason == "model_unavailable"  # never silently downgrade high-stakes review
