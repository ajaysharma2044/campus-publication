"""Subagent dispatch (specs/continuous-local-run.md R11, R16, R25, R26, R28; AT10, AT23).

- Agent definitions live in .claude/agents/<name>.md (frontmatter: name, description, tools, model, maxTurns).
- A dispatch sends a small packet (artifact ids + excerpts) and expects ONE JSON envelope back, validated
  against the role contract. Partial output (turn budget exhausted, invalid JSON) is returned as status
  'partial' with the raw text kept; it is never silently retried on a bigger model.
- Read-only agents (no Write/Edit tools) may run in parallel, up to settings.quotas.parallel_readonly_agents;
  file-changing agents run one at a time.
- Every dispatch is appended to the dispatch log (build/runs/dispatch.jsonl) and, when a DB connection is
  given, recorded as an unpriced session usage entry (R7).

The default runner shells out to `claude -p --agent <name>`; tests inject a fixture runner.
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

from ..config import REPO_ROOT
from ..contracts.validate import SCHEMA_DIR, parse_model_json, validate_envelope

AGENTS_DIR = REPO_ROOT / ".claude" / "agents"
DISPATCH_LOG_DEFAULT = REPO_ROOT / "build" / "runs" / "dispatch.jsonl"
WRITE_TOOLS = ("Write", "Edit", "MultiEdit", "NotebookEdit")
VALID_MODELS = {"sonnet", "opus", "haiku", "inherit", "fable"}
_FM = re.compile(r"^---\n(.*?)\n---\n(.*)$", re.S)


@dataclass(frozen=True)
class AgentSpec:
    name: str
    description: str
    tools: tuple[str, ...]
    model: str
    max_turns: int
    role: str          # contract role in the envelope
    schema: str        # schema file name without .json
    reference: str     # skills/national-college-publishing/references/<file>
    path: Path

    @property
    def read_only(self) -> bool:
        return not any(t.split("(")[0].strip() in WRITE_TOOLS for t in self.tools)


def parse_agent_file(path: Path) -> AgentSpec:
    text = path.read_text(encoding="utf-8")
    m = _FM.match(text)
    if not m:
        raise ValueError(f"{path.name}: no YAML frontmatter")
    fm: dict[str, str] = {}
    for line in m.group(1).splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            fm[k.strip()] = v.strip()
    for k in ("name", "description", "tools", "model"):
        if not fm.get(k):
            raise ValueError(f"{path.name}: frontmatter missing {k}")
    if fm["name"] != path.stem:
        raise ValueError(f"{path.name}: name {fm['name']!r} must equal the file stem")
    if fm["model"] not in VALID_MODELS and not fm["model"].startswith("claude-"):
        raise ValueError(f"{path.name}: model {fm['model']!r} not valid")
    body = m.group(2)
    role = re.search(r"Role contract: `([a-z_]+)`", body)
    schema = re.search(r"schemas/([a-z_]+)\.json", body)
    ref = re.search(r"references/([a-z0-9-]+\.md)", body)
    if not (role and schema and ref):
        raise ValueError(f"{path.name}: body must name the role contract, the schema file and the reference it follows")
    # split tools on commas outside parentheses
    tools = tuple(t.strip() for t in re.split(r",(?![^()]*\))", fm["tools"]) if t.strip())
    return AgentSpec(fm["name"], fm["description"], tools, fm["model"], int(fm.get("maxTurns", "25")), role.group(1), schema.group(1), ref.group(1), path)


def load_agents(agents_dir: Path = AGENTS_DIR) -> dict[str, AgentSpec]:
    specs = {}
    for p in sorted(agents_dir.glob("*.md")):
        s = parse_agent_file(p)
        specs[s.name] = s
    return specs


# ---------------------------------------------------------------------------------------------- packets
def build_packet(*, task_id: str, run_id: str, objective: str, input_ids: list[str], evidence: list[dict] | None = None,
                 institution_id: str | None = None, campus_id: str | None = None, place_id: str | None = None,
                 constraints: list[str] | None = None, acceptance_checks: list[str] | None = None, turn_budget: int | None = None,
                 extra: dict | None = None) -> dict:
    """Small, id-based packet (SPEC §37). Excerpts are capped so no agent receives whole files."""
    ev = []
    for e in evidence or []:
        e = dict(e)
        if isinstance(e.get("excerpt"), str) and len(e["excerpt"]) > 1500:
            e["excerpt"] = e["excerpt"][:1500] + "…"
        ev.append(e)
    packet = {"task_id": task_id, "run_id": run_id, "objective": objective, "input_ids": input_ids, "evidence": ev,
              "institution_id": institution_id, "campus_id": campus_id, "place_id": place_id,
              "constraints": constraints or [], "acceptance_checks": acceptance_checks or [], "turn_budget": turn_budget}
    if extra:
        packet.update(extra)
    _assert_no_secrets(packet)
    return packet


_SECRET = re.compile(r"(password|app_password|api_key|secret|token)\s*[=:]\s*\S{6,}", re.I)


def _assert_no_secrets(obj) -> None:
    s = json.dumps(obj, default=str)
    if _SECRET.search(s):
        raise ValueError("packet contains what looks like a secret; refuse to dispatch")


# ---------------------------------------------------------------------------------------------- runners
Runner = Callable[[AgentSpec, str], tuple[int, str, str]]  # (exit_code, stdout, stderr)


def cli_runner(agent: AgentSpec, prompt: str, *, timeout_s: int = 1800) -> tuple[int, str, str]:
    """Run the agent headlessly: `claude -p --agent <name>` applies its tools, model and maxTurns."""
    cmd = ["claude", "-p", prompt, "--agent", agent.name, "--output-format", "json", "--permission-mode", "dontAsk",
           "--model", agent.model if agent.model != "inherit" else os.environ.get("CAMPUS_COORDINATOR_MODEL", "sonnet"),
           "--max-turns", str(agent.max_turns)]
    env = dict(os.environ)
    env["PATH"] = f"{Path.home()}/.local/bin:" + env.get("PATH", "")
    try:
        p = subprocess.run(cmd, cwd=REPO_ROOT, capture_output=True, text=True, timeout=timeout_s, env=env, stdin=subprocess.DEVNULL)
        return p.returncode, p.stdout, p.stderr
    except subprocess.TimeoutExpired as e:
        return 124, (e.stdout or "") if isinstance(e.stdout, str) else "", f"timeout after {timeout_s}s"


def _cli_result_text(stdout: str) -> tuple[dict | None, str]:
    for line in reversed(stdout.strip().splitlines()):
        line = line.strip()
        if line.startswith("{"):
            try:
                d = json.loads(line)
                return d, d.get("result") if isinstance(d.get("result"), str) else stdout
            except json.JSONDecodeError:
                continue
    return None, stdout


# ---------------------------------------------------------------------------------------------- dispatch
@dataclass
class DispatchResult:
    agent: str
    role: str
    task_id: str | None
    status: str                       # ok | hold | partial | invalid | failed
    doc: dict | None = None
    errors: list[str] = field(default_factory=list)
    raw: str = ""
    duration_s: float = 0.0
    turns: int | None = None
    exit_code: int | None = None
    usage_limit: bool = False
    repaired: bool = False

    def as_dict(self) -> dict:
        d = {k: v for k, v in self.__dict__.items() if k not in ("doc", "raw")}
        d["decision"] = (self.doc or {}).get("decision")
        return d


_USAGE = re.compile(r"(usage limit|hit your limit|rate limit|too many requests|\b429\b|not logged in|please run /login)", re.I)


def contract_for(agent: AgentSpec) -> dict:
    """The exact shapes the agent must return: envelope keys, next_jobs item shape, and the role's output schema."""
    env = json.loads((SCHEMA_DIR / "envelope.json").read_text())
    out_schema = json.loads((SCHEMA_DIR / f"{agent.schema}.json").read_text())
    return {"envelope_required_keys": env["required"], "decision_values": env["properties"]["decision"]["enum"],
            "hold_shape": {"reason": "snake_case_reason", "retry_condition": "what must change"},
            "next_jobs_item_shape": {"job_type": env["properties"]["next_jobs"]["items"]["properties"]["job_type"]["enum"], "payload": {}, "rationale": "string ≤400", "priority": "0-100"},
            "output_schema": out_schema, "note": "output must validate against output_schema exactly (field names, enums, required keys); next_jobs may be an empty list"}


def _prompt(agent: AgentSpec, packet: dict, *, repair: tuple[str, list[str]] | None = None) -> str:
    base = "#packet\n" + json.dumps(packet, default=str, indent=1) + "\n\n#contract\n" + json.dumps(contract_for(agent), default=str) + \
           "\n\nReturn ONE JSON envelope for role " + agent.role + " whose `output` validates against #contract.output_schema, and nothing else."
    if repair:
        prev, errs = repair
        base += ("\n\n#repair\nYour previous reply did not validate. Fix ONLY the JSON shape (keep the observations); errors:\n- " + "\n- ".join(errs[:12]) +
                 "\n\nPrevious reply (truncated):\n" + prev[:6000])
    return base


def dispatch(agent: AgentSpec, packet: dict, *, runner: Runner = cli_runner, conn=None, log_path: Path | None = None,
             iteration: int | None = None, repair_once: bool = True) -> DispatchResult:
    """One dispatch, plus at most ONE same-tier repair when the reply is well-formed JSON that fails the contract
    (SPEC §15/§36 bounded repair). Never escalates to a bigger model."""
    _assert_no_secrets(packet)
    res = _dispatch_once(agent, packet, _prompt(agent, packet), runner=runner)
    if res.status == "invalid" and repair_once:
        again = _dispatch_once(agent, packet, _prompt(agent, packet, repair=(res.raw, res.errors)), runner=runner)
        again.duration_s = round(res.duration_s + again.duration_s, 3)
        again.turns = (res.turns or 0) + (again.turns or 0) if (res.turns or again.turns) else None
        again.errors = (["repaired after: " + "; ".join(res.errors[:3])] if again.status in ("ok", "hold") else again.errors)
        res = again
        res.repaired = True
    _log(res, log_path or DISPATCH_LOG_DEFAULT, iteration=iteration)
    if conn is not None:
        try:
            from .. import budget
            budget.record_session_usage(conn, kind="dispatch", task_id=res.task_id, agent=agent.name, duration_s=res.duration_s, turns=res.turns, iteration=iteration,
                                        extra={"status": res.status, "role": agent.role, "repaired": res.repaired})
        except Exception as e:  # noqa: BLE001 — ledger problems never lose the agent's output
            res.errors.append(f"ledger: {type(e).__name__}: {e}")
    return res


def _dispatch_once(agent: AgentSpec, packet: dict, prompt: str, *, runner: Runner) -> DispatchResult:
    t0 = time.monotonic()
    code, out, err = runner(agent, prompt)
    dur = time.monotonic() - t0
    cli, text = _cli_result_text(out)
    turns = (cli or {}).get("num_turns")
    res = DispatchResult(agent.name, agent.role, packet.get("task_id"), "failed", raw=text or out, duration_s=round(dur, 3), turns=turns, exit_code=code)
    if _USAGE.search((text or "") + (err or "")):
        res.status, res.usage_limit, res.errors = "failed", True, ["usage or auth limit reported by the CLI"]
    elif code != 0 and (cli is None or cli.get("is_error")):
        res.errors = [f"exit {code}: {(text or err or '')[:300]}"]
    else:
        doc, perrs = parse_model_json(text or "")
        if perrs or doc is None:
            res.status, res.errors = "partial", perrs or ["no JSON object"]
        else:
            verrs = validate_envelope(doc, agent.role)
            res.doc = doc
            if verrs:
                res.status, res.errors = "invalid", verrs
            else:
                res.status = "hold" if doc.get("decision") == "hold" else "ok"
    return res


def _log(res: DispatchResult, path: Path, *, iteration: int | None) -> None:
    """One JSON line per dispatch, plus the full reply saved next to the log (agent-output/<ts>-<agent>-<task>.json) so a
    failure after the dispatch (ingest, DB) never loses the agent's work."""
    path.parent.mkdir(parents=True, exist_ok=True)
    ts = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
    entry = dict(res.as_dict(), ts=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), iteration=iteration, run_id=os.environ.get("CAMPUS_RUN_ID"))
    try:
        outdir = path.parent / "agent-output"
        outdir.mkdir(parents=True, exist_ok=True)
        safe_task = re.sub(r"[^A-Za-z0-9_.-]+", "_", str(res.task_id or "task"))[:60]
        outfile = outdir / f"{ts}-{res.agent}-{safe_task}.json"
        outfile.write_text(json.dumps({"agent": res.agent, "task_id": res.task_id, "status": res.status, "errors": res.errors, "doc": res.doc, "raw": (res.raw or "")[:200000]}, default=str))
        entry["output_file"] = str(outfile)
    except OSError:
        pass
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry, default=str) + "\n")


def dispatch_many(items: list[tuple[AgentSpec, dict]], *, runner: Runner = cli_runner, conn=None, log_path: Path | None = None,
                  max_parallel: int = 4, iteration: int | None = None) -> list[DispatchResult]:
    """Read-only agents run concurrently (≤ max_parallel); file-changing agents run one at a time, after them."""
    ro = [(a, p) for a, p in items if a.read_only]
    rw = [(a, p) for a, p in items if not a.read_only]
    results: list[DispatchResult] = []
    if ro:
        with ThreadPoolExecutor(max_workers=max(1, min(max_parallel, len(ro)))) as ex:
            results += list(ex.map(lambda ap: dispatch(ap[0], ap[1], runner=runner, conn=None, log_path=log_path, iteration=iteration), ro))
    for a, p in rw:
        results.append(dispatch(a, p, runner=runner, conn=None, log_path=log_path, iteration=iteration))
    if conn is not None:
        from .. import budget
        for r in results:
            budget.record_session_usage(conn, kind="dispatch", task_id=r.task_id, agent=r.agent, duration_s=r.duration_s, turns=r.turns, iteration=iteration,
                                        extra={"status": r.status, "role": r.role})
    return results


def read_dispatch_log(path: Path = DISPATCH_LOG_DEFAULT) -> list[dict]:
    if not path.exists():
        return []
    return [json.loads(l) for l in path.read_text().splitlines() if l.strip()]
