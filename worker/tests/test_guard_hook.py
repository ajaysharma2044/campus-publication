"""Guard hook tests (specs/continuous-local-run.md §7 enforcement; AT17, AT11 hook clause).

Runs .claude/hooks/guard.sh as Claude Code would: hook JSON on stdin, exit 2 + stderr message blocks.
"""
import json
import os
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
HOOK = ROOT / ".claude" / "hooks" / "guard.sh"


def run_hook(tool_name: str, tool_input: dict) -> tuple[int, str]:
    env = dict(os.environ, CLAUDE_PROJECT_DIR=str(ROOT))
    p = subprocess.run(["bash", str(HOOK)], input=json.dumps({"tool_name": tool_name, "tool_input": tool_input, "hook_event_name": "PreToolUse"}),
                       capture_output=True, text=True, env=env, timeout=30)
    return p.returncode, p.stderr


@pytest.mark.parametrize("path", ["SPEC.md", "specs/continuous-local-run.md", str(ROOT / "specs" / "x.md"), ".claude/settings.json"])
def test_owner_only_files_are_blocked(path):
    code, err = run_hook("Edit", {"file_path": path, "old_string": "a", "new_string": "b"})
    assert code == 2 and "BLOCKED" in err, err


def test_write_to_spec_blocked():
    code, err = run_hook("Write", {"file_path": "specs/continuous-local-run.md", "content": "x"})
    assert code == 2 and "owner-only" in err


def test_gate_threshold_edit_blocked_but_other_gates_edits_allowed():
    gates = "worker/campus_worker/editorial/gates.py"
    code, err = run_hook("Edit", {"file_path": gates, "old_string": "MIN_TOTAL = 20", "new_string": "MIN_TOTAL = 10"})
    assert code == 2 and "gate threshold" in err
    code, err = run_hook("Edit", {"file_path": gates, "old_string": "def content_hash(", "new_string": "def content_hash(  # noqa\n"})
    assert code == 0, err
    code, err = run_hook("Write", {"file_path": gates, "content": "MIN_TOTAL = 20\n"})
    assert code == 2


def test_live_ramp_default_protected_in_config():
    cfg = "worker/campus_worker/config.py"
    code, err = run_hook("Edit", {"file_path": cfg, "old_string": 'live_ramp: str = "5x14,15"', "new_string": 'live_ramp: str = "50x1,500"'})
    assert code == 2 and "live-ramp" in err
    code, err = run_hook("Edit", {"file_path": cfg, "old_string": "class Quotas:", "new_string": 'class Quotas:\n    live_ramp: str = "5x14,15"'})
    assert code == 0, err
    code, err = run_hook("Edit", {"file_path": cfg, "old_string": "x", "new_string": "    ads_enabled: bool\n"})
    assert code == 0, err


def test_unlisted_skill_write_blocked_and_baseline_allowed():
    code, err = run_hook("Write", {"file_path": ".claude/skills/some-seo-skill/SKILL.md", "content": "# x"})
    assert code == 2 and "not listed as adopted" in err
    code, err = run_hook("Bash", {"command": "mkdir -p .claude/skills/some-seo-skill && cp -r /tmp/x .claude/skills/some-seo-skill/"})
    assert code == 2
    code, err = run_hook("Write", {"file_path": ".claude/skills/national-college-publishing/README.md", "content": "# baseline"})
    assert code == 0, err


def test_bash_writes_to_protected_paths_blocked_reads_allowed():
    assert run_hook("Bash", {"command": "echo x >> SPEC.md"})[0] == 2
    assert run_hook("Bash", {"command": "sed -i '' 's/a/b/' specs/continuous-local-run.md"})[0] == 2
    assert run_hook("Bash", {"command": "perl -pi -e 's/20/10/' worker/campus_worker/editorial/gates.py"})[0] == 2
    assert run_hook("Bash", {"command": "cat SPEC.md | head"})[0] == 0
    assert run_hook("Bash", {"command": "grep -n MIN_TOTAL worker/campus_worker/editorial/gates.py"})[0] == 0


def test_force_push_blocked_normal_push_allowed():
    assert run_hook("Bash", {"command": "git push --force origin main"})[0] == 2
    assert run_hook("Bash", {"command": "git push -f"})[0] == 2
    assert run_hook("Bash", {"command": "git push -u origin continuous-local-run"})[0] == 0


def test_ordinary_edits_allowed():
    assert run_hook("Edit", {"file_path": "STATE.md", "old_string": "a", "new_string": "b"})[0] == 0
    assert run_hook("Write", {"file_path": "worker/campus_worker/new_module.py", "content": "x = 1\n"})[0] == 0


def test_unparseable_input_is_blocked_not_ignored():
    env = dict(os.environ, CLAUDE_PROJECT_DIR=str(ROOT))
    p = subprocess.run(["bash", str(HOOK)], input="not json", capture_output=True, text=True, env=env, timeout=30)
    assert p.returncode == 2
