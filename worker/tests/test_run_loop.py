"""Run loop tests (specs/continuous-local-run.md R2–R6, R10; AT3–AT7) using fixture iterations — no model calls.

AT3 (real `claude -p` iterations) is verified live by the owner-visible run; here the loop mechanics are proven:
log lines with every R10 field, stop file, lock, consecutive failures, usage pause without retry, no_work.
"""
import json
import os
import signal
import subprocess
import time
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
RUN = ROOT / "scripts" / "run.sh"
STOP = ROOT / "scripts" / "stop.sh"
STUB = ROOT / "scripts" / "fixtures" / "iteration_stub.sh"
R10_FIELDS = {"iteration", "start", "end", "task_id", "agents_dispatched", "result", "checks", "commit", "stop_reason"}


def _env(tmp_path, **extra):
    env = dict(os.environ, CAMPUS_RUN_DIR=str(tmp_path / "run"), CAMPUS_RUN_LOG_DIR=str(tmp_path / "logs"), CAMPUS_RUN_NO_GIT="1",
               CAMPUS_NO_CAFFEINATE="1", CAMPUS_ITERATION_CMD=str(STUB), CAMPUS_STUB_MARK_FILE=str(tmp_path / "marks.txt"))
    env.pop("DATABASE_URL", None)  # ledger write is skipped and noted; the loop must not depend on the DB
    env.update(extra)
    return env


def _lines(tmp_path):
    logs = list((tmp_path / "logs").glob("*.jsonl"))
    assert len(logs) == 1, logs
    return [json.loads(l) for l in logs[0].read_text().splitlines() if l.strip()]


def test_max_three_iterations_write_three_full_log_lines(tmp_path):
    p = subprocess.run(["bash", str(RUN), "--max", "3"], env=_env(tmp_path, CAMPUS_STUB_SEQUENCE="ok,ok,ok"), capture_output=True, text=True, timeout=120)
    assert p.returncode == 12, p.stdout + p.stderr
    lines = _lines(tmp_path)
    iters = [l for l in lines if "iteration" in l]
    assert [l["iteration"] for l in iters] == [1, 2, 3]
    for l in iters:
        assert R10_FIELDS <= set(l), l
        assert l["result"] == "succeeded" and l["task_id"] == "FIX-001" and l["agents_dispatched"] == ["analyst"] and l["checks"][0]["pass"] is True
        assert l["start"] <= l["end"] and l["commit"]
    assert lines[-1]["stop_reason"] == "max_iterations" and lines[-1]["iterations"] == 3


def test_no_work_stops_with_exit_zero(tmp_path):
    p = subprocess.run(["bash", str(RUN)], env=_env(tmp_path, CAMPUS_STUB_SEQUENCE="ok,nowork"), capture_output=True, text=True, timeout=120)
    assert p.returncode == 0
    lines = _lines(tmp_path)
    assert [l.get("result") for l in lines if "iteration" in l] == ["succeeded", "no_work"] and lines[-1]["stop_reason"] == "no_work"


def test_stop_file_mid_iteration_finishes_current_and_starts_no_new_one(tmp_path):
    env = _env(tmp_path, CAMPUS_STUB_SEQUENCE="slow,ok,ok", CAMPUS_STUB_SLEEP="3")
    proc = subprocess.Popen(["bash", str(RUN)], env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    time.sleep(1.0)
    s = subprocess.run(["bash", str(STOP)], env=env, capture_output=True, text=True)
    assert "STOP file created" in s.stdout
    out, _ = proc.communicate(timeout=60)
    assert proc.returncode == 0, out
    lines = _lines(tmp_path)
    iters = [l for l in lines if "iteration" in l]
    assert len(iters) == 1 and iters[0]["result"] == "succeeded" and iters[0]["duration_s"] >= 2
    assert lines[-1]["stop_reason"] == "stop_file"
    marks = (tmp_path / "marks.txt").read_text().splitlines()
    assert len(marks) == 1  # the stub was started exactly once


def test_sigint_behaves_like_stop(tmp_path):
    env = _env(tmp_path, CAMPUS_STUB_SEQUENCE="slow,ok", CAMPUS_STUB_SLEEP="3")
    proc = subprocess.Popen(["bash", str(RUN)], env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    time.sleep(1.0)
    proc.send_signal(signal.SIGINT)
    out, _ = proc.communicate(timeout=60)
    assert proc.returncode == 0, out
    lines = _lines(tmp_path)
    assert [l["result"] for l in lines if "iteration" in l] == ["succeeded"] and lines[-1]["stop_reason"] == "stop_file"


def test_second_run_while_active_exits_locked(tmp_path):
    env = _env(tmp_path, CAMPUS_STUB_SEQUENCE="slow,nowork", CAMPUS_STUB_SLEEP="4")
    proc = subprocess.Popen(["bash", str(RUN)], env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    time.sleep(1.0)
    second = subprocess.run(["bash", str(RUN), "--max", "1"], env=env, capture_output=True, text=True, timeout=30)
    assert second.returncode == 11 and "locked" in second.stdout
    subprocess.run(["bash", str(STOP)], env=env, capture_output=True)
    proc.communicate(timeout=60)
    assert not (tmp_path / "run" / "lock").exists()  # lock released on exit


def test_three_consecutive_failures_stop_the_loop(tmp_path):
    p = subprocess.run(["bash", str(RUN), "--force-fail"], env=_env(tmp_path), capture_output=True, text=True, timeout=120)
    assert p.returncode == 1
    lines = _lines(tmp_path)
    assert [l["result"] for l in lines if "iteration" in l] == ["failed", "failed", "failed"] and lines[-1]["stop_reason"] == "consecutive_failures"


def test_failures_counter_resets_after_a_success(tmp_path):
    p = subprocess.run(["bash", str(RUN), "--max", "6"], env=_env(tmp_path, CAMPUS_STUB_SEQUENCE="fail,fail,ok,fail,fail,ok"), capture_output=True, text=True, timeout=120)
    assert p.returncode == 12
    assert len([l for l in _lines(tmp_path) if "iteration" in l]) == 6


def test_usage_limit_exits_20_with_no_retry_inside_60s(tmp_path):
    t0 = time.time()
    p = subprocess.run(["bash", str(RUN), "--simulate-usage-limit"], env=_env(tmp_path), capture_output=True, text=True, timeout=120)
    elapsed = time.time() - t0
    assert p.returncode == 20, p.stdout
    lines = _lines(tmp_path)
    iters = [l for l in lines if "iteration" in l]
    assert len(iters) == 1 and iters[0]["result"] == "usage_paused" and "usage limit" in iters[0]["error"].lower()
    assert lines[-1]["stop_reason"] == "usage_paused" and elapsed < 60
    assert len((tmp_path / "marks.txt").read_text().splitlines()) == 1  # no retry at all


def test_auth_error_exits_30(tmp_path):
    p = subprocess.run(["bash", str(RUN)], env=_env(tmp_path, CAMPUS_STUB_SEQUENCE="auth"), capture_output=True, text=True, timeout=120)
    assert p.returncode == 30 and _lines(tmp_path)[-1]["stop_reason"] == "auth_error"


def test_runlog_classifier_direct():
    import importlib.util
    spec = importlib.util.spec_from_file_location("runlog", ROOT / "scripts" / "runlog.py")
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    assert m.classify({"is_error": True, "result": "You've hit your usage limit"}, "", "", 1)[0] == "usage_paused"
    assert m.classify({"is_error": True, "result": "Not logged in · Please run /login"}, "", "", 1)[0] == "auth_error"
    assert m.classify({"is_error": False, "result": 'done {"iteration_summary": {"task_id": "S4", "result": "held"}}'}, "", "", 0) == ("held", {"task_id": "S4", "result": "held"})
    assert m.classify(None, "garbage", "", 0)[0] == "failed"
    assert m.extract_summary('x {"a": {"iteration_summary": {"task_id": "T"}}} y')["task_id"] == "T"


def test_allowlist_reaches_the_cli_as_one_comma_joined_argument():
    """A pattern with spaces (Bash(python -m campus_worker.*)) must not be word-split into a stray -m option (AT3 live failure 2026-11-06)."""
    import subprocess
    r = subprocess.run(["bash", str(ROOT / "scripts" / "run.sh"), "--print-argv", "--max", "1"], capture_output=True, text=True, timeout=60, cwd=str(ROOT),
                       env=dict(os.environ, CAMPUS_NO_CAFFEINATE="1", CAMPUS_RUN_DIR=str(ROOT / "build" / "runs" / "argv-test")))
    assert r.returncode == 0, r.stderr[-500:]
    argv = r.stdout.splitlines()
    assert argv[0] == "claude" and "--allowedTools" in argv
    allowed = argv[argv.index("--allowedTools") + 1]
    assert allowed == argv[-1] and "Bash(python -m campus_worker.*)" in allowed.split(",") and "-m" not in argv
