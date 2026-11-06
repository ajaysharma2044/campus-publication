"""Agent team (specs/continuous-local-run.md R11, R16, R28; AT10).

Default tests use fixture runners (no model calls). `pytest -m live` dispatches each agent once through the real
CLI (needs `claude auth login`); it is opt-in via CAMPUS_LIVE_TESTS=1.
"""
import json
import os
import threading
import time

import pytest

from campus_worker.agents import dispatch as d
from tests.agent_fixtures import OUTPUTS, cli_stdout, envelope

EXPECTED = {"skill-scout": ("skill_scout", "opus"), "search-intel": ("search_intel", "sonnet"), "search-strategist": ("search_strategist", "opus"),
            "onboarding": ("onboarding", "sonnet"), "discovery": ("discovery", "sonnet"), "opportunity": ("opportunity", "sonnet"), "researcher": ("researcher", "sonnet"),
            "planner": ("planner", "sonnet"), "writer": ("writer", "sonnet"), "editor": ("editor", "opus"), "verifier": ("verifier", "opus"), "seo": ("seo", "sonnet"),
            "tool-engineer": ("tool_engineer", "sonnet"), "ad-ops": ("ad_ops", "haiku"), "analyst": ("analyst", "sonnet")}


def test_fifteen_agent_files_parse_and_declare_contracts():
    specs = d.load_agents()
    assert set(specs) == set(EXPECTED), set(specs) ^ set(EXPECTED)
    for name, (role, model) in EXPECTED.items():
        s = specs[name]
        assert s.role == role and s.model == model and s.max_turns > 0 and s.reference.endswith(".md")
        assert (d.REPO_ROOT / "skills" / "national-college-publishing" / "references" / s.reference).exists()
        assert (d.REPO_ROOT / "worker" / "campus_worker" / "contracts" / "schemas" / f"{s.schema}.json").exists()
    # R28: opus is reserved for editor, verifier, skill-scout, strategist
    assert {n for n, s in specs.items() if s.model == "opus"} == {"editor", "verifier", "skill-scout", "search-strategist"}
    # only writer and tool-engineer may change files
    assert {n for n, s in specs.items() if not s.read_only} == {"writer", "tool-engineer"}


def test_every_agent_returns_a_valid_contract_against_a_fixture_packet(tmp_path):
    specs = d.load_agents()
    log = tmp_path / "dispatch.jsonl"
    for name, spec in specs.items():
        packet = d.build_packet(task_id="AT10", run_id="run-fixture-0001", objective="fixture", input_ids=["b1"], turn_budget=spec.max_turns)
        res = d.dispatch(spec, packet, runner=lambda a, p: (0, cli_stdout(a.role), ""), log_path=log)
        assert res.status == "ok", (name, res.errors)
        assert res.doc["role"] == spec.role and res.doc["output"] == OUTPUTS[spec.role]
    lines = [json.loads(l) for l in log.read_text().splitlines()]
    assert len(lines) == 15 and all(l["status"] == "ok" and l["agent"] for l in lines)


def test_partial_and_invalid_and_usage_outcomes_are_not_retried(tmp_path):
    specs = d.load_agents()
    calls = []

    def runner_partial(a, p):
        calls.append(a.name)
        return 0, cli_stdout(a.role, text='{"schema_version": "1.0", "role": "writer", "output": {"headline": "cut off'), ""
    r = d.dispatch(specs["writer"], d.build_packet(task_id="t", run_id="r", objective="o", input_ids=[]), runner=runner_partial, log_path=tmp_path / "l.jsonl")
    assert r.status == "partial" and calls == ["writer"] and "cut off" in r.raw
    bad = envelope("writer", {"headline": "too short"})
    r = d.dispatch(specs["writer"], d.build_packet(task_id="t", run_id="r", objective="o", input_ids=[]), runner=lambda a, p: (0, cli_stdout(a.role, text=json.dumps(bad)), ""), log_path=tmp_path / "l.jsonl")
    assert r.status == "invalid" and any("body_markdown" in e for e in r.errors)
    r = d.dispatch(specs["seo"], d.build_packet(task_id="t", run_id="r", objective="o", input_ids=[]), runner=lambda a, p: (1, cli_stdout(a.role, text="You've hit your usage limit", is_error=True), ""), log_path=tmp_path / "l.jsonl")
    assert r.status == "failed" and r.usage_limit
    hold = envelope("researcher", OUTPUTS["researcher"], decision="hold", hold={"reason": "turn_budget", "retry_condition": "larger packet split"})
    r = d.dispatch(specs["researcher"], d.build_packet(task_id="t", run_id="r", objective="o", input_ids=[]), runner=lambda a, p: (0, cli_stdout(a.role, text=json.dumps(hold)), ""), log_path=tmp_path / "l.jsonl")
    assert r.status == "hold"


def test_read_only_agents_run_in_parallel_and_writers_serialize(tmp_path):
    specs = d.load_agents()
    lock = threading.Lock(); active = {"n": 0, "peak": 0}

    def runner(a, p):
        with lock:
            active["n"] += 1; active["peak"] = max(active["peak"], active["n"])
        time.sleep(0.2)
        with lock:
            active["n"] -= 1
        return 0, cli_stdout(a.role), ""
    items = [(specs[n], d.build_packet(task_id="p", run_id="r", objective="o", input_ids=[])) for n in ("search-intel", "discovery", "researcher", "opportunity", "planner", "writer", "tool-engineer")]
    t0 = time.monotonic()
    res = d.dispatch_many(items, runner=runner, log_path=tmp_path / "l.jsonl", max_parallel=4)
    assert all(r.status == "ok" for r in res) and len(res) == 7
    assert 2 <= active["peak"] <= 4
    assert [r.agent for r in res][-2:] == ["writer", "tool-engineer"]  # writers after the read-only batch, one at a time
    assert time.monotonic() - t0 < 1.6  # 5 read-only at ≤4 parallel (~0.4s) + 2 serial (0.4s)


def test_packet_refuses_secrets_and_caps_excerpts():
    with pytest.raises(ValueError):
        d.build_packet(task_id="t", run_id="r", objective="o", input_ids=[], extra={"note": "app_password=abcdef123456"})
    p = d.build_packet(task_id="t", run_id="r", objective="o", input_ids=["s1"], evidence=[{"id": "s1", "excerpt": "x" * 5000}])
    assert len(p["evidence"][0]["excerpt"]) == 1501


@pytest.mark.live
@pytest.mark.skipif(not os.environ.get("CAMPUS_LIVE_TESTS"), reason="set CAMPUS_LIVE_TESTS=1 to dispatch agents through the real CLI (uses subscription)")
def test_live_dispatch_each_agent_once(tmp_path):
    specs = d.load_agents()
    out = {}
    for name, spec in specs.items():
        packet = d.build_packet(task_id="AT10-live", run_id="run-live", objective=f"Smoke test: return a minimal but schema-valid {spec.schema} envelope using only the packet. Do not search or fetch.",
                                input_ids=["fixture"], evidence=[{"id": "fixture", "excerpt": "SYNTHETIC FIXTURE: Fixture Hall double room $12,042 per person 2026-27."}], turn_budget=min(spec.max_turns, 6))
        r = d.dispatch(spec, packet, runner=lambda a, p: d.cli_runner(a, p, timeout_s=600), log_path=tmp_path / "live.jsonl")
        out[name] = (r.status, r.errors[:2], r.turns)
    (d.REPO_ROOT / "build" / "runs").mkdir(parents=True, exist_ok=True)
    (d.REPO_ROOT / "build" / "runs" / "at10-live.json").write_text(json.dumps(out, indent=2))
    assert all(v[0] in ("ok", "hold") for v in out.values()), out
