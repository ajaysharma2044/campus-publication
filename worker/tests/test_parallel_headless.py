"""Parallel headless fallback (specs/bulk-mode.md section 3, last bullet; acceptance B5: 4 workers, 20 pages, no file conflicts).

No `claude -p` runs here: the script's --dry-run does everything else (page list, shards, prompts, fake worker replies, the serial merge);
the merge is also fed hand-made worker folders (a planted double write, a real CLI envelope with a pipeline report), and the page-list fallback
`campus_worker.lean queue --json` runs against the test database.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "parallel_headless.sh"
MERGE = ROOT / "scripts" / "merge_headless_shards.py"
PY = ROOT / "worker" / ".venv" / "bin" / "python"
if not PY.exists():
    PY = Path(sys.executable)


def _pages(n: int = 20) -> list[dict]:
    return [{"question_id": f"q{i:03d}", "path": f"/schools/fixture-state/housing/question-{i:02d}/", "page_type": "question_guide",
             "question": f"fixture question {i}", "cluster_id": (f"00000000-0000-4000-8000-{i:012d}" if i % 5 else None)} for i in range(n)]


def _env(tmp_path: Path) -> dict:
    return dict(os.environ, CAMPUS_HEADLESS_ROOT=str(tmp_path / "headless"), CAMPUS_RUN_DIR=str(tmp_path / "run"), CAMPUS_NO_CAFFEINATE="1")


def test_dry_run_four_workers_twenty_pages_no_conflicts(tmp_path):
    pages_file = tmp_path / "pages.json"
    pages_file.write_text(json.dumps(_pages(20)))
    p = subprocess.run(["bash", str(SCRIPT), "4", "--pages", str(pages_file), "--dry-run", "--run", "t1"], env=_env(tmp_path), cwd=str(ROOT),
                       capture_output=True, text=True, timeout=120)
    assert p.returncode == 0, p.stdout + p.stderr
    run_dir = tmp_path / "headless" / "t1"
    workers = sorted(d for d in run_dir.iterdir() if d.name.startswith("worker-"))
    assert [d.name for d in workers] == [f"worker-{i}" for i in range(4)]
    shards = {i: json.loads((d / "pages.json").read_text()) for i, d in enumerate(workers)}
    assert [len(s) for s in shards.values()] == [5, 5, 5, 5]
    seen = [pg["path"] for s in shards.values() for pg in s]
    assert len(seen) == 20 and len(set(seen)) == 20 and set(seen) == {pg["path"] for pg in _pages(20)}  # every page exactly once
    for i, d in enumerate(workers):
        prompt = (d / "prompt.md").read_text()
        assert f"worker {i} of 4" in prompt and f"worker-{i}/" in prompt and "--until verify --path" in prompt
        assert "Never run git" in prompt and "Never publish" in prompt and '{"worker": %d, "done":' % i in prompt
        for pg in shards[i]:
            assert pg["path"] in prompt and pg["worker"] == i and pg["slug"] == pg["path"].strip("/").replace("/", "-")
            if pg["cluster_id"]:
                assert f"pipeline run {pg['cluster_id']} --until verify --path {pg['path']}" in prompt
        for j, other in shards.items():  # only its own pages are in a worker's prompt
            if j != i:
                assert not any(pg["path"] in prompt for pg in other)
        out = json.loads((d / "out.json").read_text())  # the dry-run stand-in for the worker's reply
        assert out["worker"] == i and out["done"] == [] and [s["path"] for s in out["skipped"]] == [pg["path"] for pg in shards[i]]
        assert all(s["reason"] == "dry-run" for s in out["skipped"])
        assert not (d / "err.txt").exists()  # claude -p never ran
    merged = json.loads((run_dir / "merged.json").read_text())
    assert merged["ok"] is True and merged["conflicts"] == [] and merged["workers"] == 4
    assert merged["done"] == [] and len(merged["skipped"]) == 20 and len(merged["assigned"]) == 20 and merged["unaccounted"] == []
    assert {s["worker"] for s in merged["skipped"]} == {0, 1, 2, 3} and merged["skipped_reasons"] == {"dry-run": 20}
    assert "conflicts=0" in p.stdout and "DONE" in p.stdout
    assert not (tmp_path / "run" / "lock").exists()  # a dry run takes no run lock


def test_merge_fails_loudly_on_a_path_two_workers_both_wrote(tmp_path):
    run_dir = tmp_path / "headless" / "t2"
    dup = "/schools/fixture-state/housing/question-07/"
    for i, done in ((0, [dup, "/schools/fixture-state/housing/question-00/"]), (1, [dup]), (2, [])):
        d = run_dir / f"worker-{i}"
        d.mkdir(parents=True)
        (d / "out.json").write_text(json.dumps({"worker": i, "done": done, "skipped": []}))
    p = subprocess.run([str(PY), str(MERGE), str(run_dir), "--pipeline-reports", str(tmp_path / "no-reports")], cwd=str(ROOT), capture_output=True, text=True, timeout=60)
    assert p.returncode == 1, p.stdout + p.stderr
    text = p.stdout + p.stderr
    assert "CONFLICT" in text and dup in text and "workers 0, 1" in text and "conflicts=1" in text
    merged = json.loads((run_dir / "merged.json").read_text())  # the conflict is on record, and nothing is marked ok
    assert merged["ok"] is False and merged["conflicts"] == [{"path": dup, "workers": [0, 1], "kind": "produced by more than one worker"}]


def test_merge_reads_the_cli_envelope_and_lists_version_ids(tmp_path):
    run_dir = tmp_path / "headless" / "t3"
    d = run_dir / "worker-0"
    d.mkdir(parents=True)
    path, other = "/schools/fixture-state/housing/question-01/", "/schools/fixture-state/housing/question-02/"
    cid, vid = "00000000-0000-4000-8000-000000000001", "11111111-2222-4333-8444-555555555555"
    (d / "pages.json").write_text(json.dumps([{"path": path, "cluster_id": cid, "question": "q1", "page_type": "question_guide", "question_id": "q001", "slug": "s1", "worker": 0},
                                              {"path": other, "cluster_id": None, "question": "q2", "page_type": "question_guide", "question_id": "q002", "slug": "s2", "worker": 0}]))
    (d / "done.json").write_text(json.dumps([{"path": path, "cluster_id": cid, "version_id": vid, "outcome": "gate_passed"}]))
    reply = 'Produced one page, skipped one.\n{"worker": 0, "done": ["%s"], "skipped": [{"path": "%s", "reason": "no cluster id"}]}' % (path, other)
    (d / "out.json").write_text("warning: something the CLI printed first\n" + json.dumps({"type": "result", "subtype": "success", "is_error": False, "num_turns": 9, "result": reply}) + "\n")
    (d / "exit_code").write_text("0\n")
    (d / "s1.json").write_text(json.dumps({"headline": "h" * 20, "deck": "d" * 30, "body_markdown": "b" * 300, "fact_table": [], "next_actions": [{"text": "t", "target": "/x/"}], "claim_refs": []}))
    reports = tmp_path / "pipeline"
    reports.mkdir()
    (reports / "00000000.json").write_text(json.dumps({"cluster_id": cid, "run_id": "headless-t3", "started": "2026-11-06T00:00:00+00:00", "page_path": path, "version_id": vid, "outcome": "gate_passed", "stages": {}}))
    p = subprocess.run([str(PY), str(MERGE), str(run_dir), "--pipeline-reports", str(reports)], cwd=str(ROOT), capture_output=True, text=True, timeout=60)
    assert p.returncode == 0, p.stdout + p.stderr
    merged = json.loads((run_dir / "merged.json").read_text())
    assert merged["ok"] is True and merged["conflicts"] == [] and merged["unaccounted"] == []
    assert merged["done"] == [{"path": path, "worker": 0, "cluster_id": cid, "version_id": vid, "outcome": "gate_passed", "report": "build/runs/pipeline/00000000.json"}]
    assert merged["skipped"] == [{"path": other, "worker": 0, "reason": "no cluster id"}]
    assert merged["versions"] == [{"version_id": vid, "path": path, "worker": 0, "outcome": "gate_passed"}] and merged["publishable"] == [vid]
    assert merged["drafts"] == {"0": ["s1.json"]} and merged["worker_reports"][0]["reported"] is True and merged["worker_reports"][0]["exit_code"] == 0
    assert "done=1 skipped=1" in p.stdout and "conflicts=0" in p.stdout and f"pipeline publish {vid}" in p.stdout


def test_print_argv_shows_run_sh_flags_without_the_git_write_shapes(tmp_path):
    p = subprocess.run(["bash", str(SCRIPT), "4", "--print-argv", "--max-turns", "60"], env=_env(tmp_path), cwd=str(ROOT), capture_output=True, text=True, timeout=60)
    assert p.returncode == 0, p.stdout + p.stderr
    argv = p.stdout.splitlines()
    assert argv[:2] == ["claude", "-p"] and "--output-format" in argv and argv[argv.index("--output-format") + 1] == "json"
    assert argv[argv.index("--permission-mode") + 1] == "dontAsk" and argv[argv.index("--max-turns") + 1] == "60"
    allowed = argv[argv.index("--allowedTools") + 1].split(",")
    run_sh = [l.strip() for l in (ROOT / "scripts" / "iteration_tools.txt").read_text().splitlines() if l.strip()]
    assert "Bash(worker/.venv/bin/python -m campus_worker.*)" in allowed and "Bash(worker/.venv/bin/python scripts/*)" in allowed and "Bash(git status*)" in allowed
    assert not any(a.startswith(("Bash(git add", "Bash(git commit", "Bash(git push")) for a in allowed)  # workers never commit
    assert set(allowed) == {a for a in run_sh if not a.startswith(("Bash(git add", "Bash(git commit", "Bash(git push"))}  # otherwise run.sh's list
    assert not (tmp_path / "headless").exists()  # nothing written


def test_lean_queue_cli_prints_planned_pages(clean_conn, migrated_url, monkeypatch):
    from tests.helpers import make_school
    from tests.test_lean import _cluster, _verified_claim
    monkeypatch.setenv("CAMPUS_LEAN_MODE", "1")
    inst, campus, topics = make_school(clean_conn)
    with clean_conn.cursor() as cur:
        cur.execute("UPDATE institutions SET identity_status='verified' WHERE id=%s", (inst,))
    clean_conn.commit()
    cid = _cluster(clean_conn, inst, campus, topics["housing"], "fixture hall laundry", agi=4, niche=30)
    _cluster(clean_conn, inst, campus, topics["housing"], "fixture hall address", agi=1, niche=50)  # strong incumbent: never in the queue
    _verified_claim(clean_conn, inst, campus, topics["housing"])
    clean_conn.commit()
    env = dict(os.environ, DATABASE_URL=migrated_url, CAMPUS_LEAN_MODE="1")
    p = subprocess.run([str(PY), "-m", "campus_worker.lean", "queue", "--limit", "5", "--json"], cwd=str(ROOT), env=env, capture_output=True, text=True, timeout=60)
    assert p.returncode == 0, p.stderr
    pages = json.loads(p.stdout)
    assert [pg["cluster_id"] for pg in pages] == [str(cid)]
    assert set(pages[0]) >= {"question_id", "path", "page_type", "question", "cluster_id"}
    assert pages[0]["question_id"] is None and pages[0]["question"] == "fixture hall laundry" and pages[0]["page_type"] == "guide"
    assert pages[0]["path"].startswith("/schools/fixture-state/housing/") and pages[0]["path"].endswith("/") and pages[0]["queue"]["label"] == "fixture hall laundry"
    usage = subprocess.run([str(PY), "-m", "campus_worker.lean"], cwd=str(ROOT), env=env, capture_output=True, text=True, timeout=60)
    assert usage.returncode == 2 and "queue" in usage.stdout
