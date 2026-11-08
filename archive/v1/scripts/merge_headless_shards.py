"""Serial merge of the parallel headless workers' output (specs/bulk-mode.md section 3, the no-API-key fallback; acceptance B5).

  worker/.venv/bin/python scripts/merge_headless_shards.py build/bulk/headless/<run> [--pipeline-reports <dir>]

Reads every worker-<i>/ folder of the run: out.json (the worker's final reply, either the `claude -p --output-format json` envelope whose
`result` text ends with {"worker": i, "done": [...], "skipped": [...]} or, after --dry-run, that object itself), done.json and skipped.json
written during the run, pages.json (the shard), exit_code and the <slug>.json drafts. Checks that no page path was produced by two workers
and that no path was assigned to two workers; any conflict is listed and the exit code is 1. Writes <run>/merged.json (every done and skipped
page with its worker index, the versions found, the conflicts) and prints a summary.

Publishing stays with the pipeline: for every done path the matching build/runs/pipeline/<cluster>.json report supplies the version id and the
gate outcome, listed under `versions` (and `publishable` for gate_passed), ready for `worker/.venv/bin/python -m campus_worker.pipeline publish <version_id>`.
Exit: 0 merged without conflicts · 1 conflicts · 2 no worker folders.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
PIPELINE_REPORTS = REPO_ROOT / "build" / "runs" / "pipeline"
WRITER_KEYS = ("headline", "deck", "body_markdown", "claim_refs", "next_actions")
RESERVED = {"out.json", "pages.json", "done.json", "skipped.json", "merged.json"}
WORKER_DIR = re.compile(r"^worker-(\d+)$")


# ------------------------------------------------------------------------------------------------ reading one worker
def _last_json_object(raw: str) -> dict | None:
    """The CLI may print warnings before its JSON object: take the last JSON object line, else the whole text."""
    for line in reversed(raw.splitlines()):
        line = line.strip()
        if line.startswith("{"):
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(obj, dict):
                return obj
    try:
        obj = json.loads(raw)
    except json.JSONDecodeError:
        return None
    return obj if isinstance(obj, dict) else None


def extract_report(text: str) -> dict | None:
    """The worker ends its reply with {"worker": i, "done": [...], "skipped": [...]}: find the last such object in the reply text."""
    if not text:
        return None
    idx = text.rfind('"worker"')
    while idx >= 0:
        start = text.rfind("{", 0, idx)
        if start < 0:
            return None
        depth = 0
        for i in range(start, len(text)):
            if text[i] == "{":
                depth += 1
            elif text[i] == "}":
                depth -= 1
                if depth == 0:
                    try:
                        obj = json.loads(text[start:i + 1])
                    except json.JSONDecodeError:
                        obj = None
                    if isinstance(obj, dict) and "worker" in obj and ("done" in obj or "skipped" in obj):
                        return obj
                    break
        idx = text.rfind('"worker"', 0, idx)
    return None


def _entries(items, *, default_reason: str | None = None) -> list[dict]:
    """done/skipped items come as path strings or objects with a path; keep the object's other fields."""
    out = []
    for it in items or []:
        if isinstance(it, str):
            e = {"path": it}
        elif isinstance(it, dict) and isinstance(it.get("path"), str):
            e = dict(it)
        else:
            continue
        if default_reason is not None and not e.get("reason"):
            e["reason"] = default_reason
        out.append(e)
    return out


def load_worker_report(out_path: Path) -> tuple[dict | None, str]:
    """(report, note) from out.json: the report object itself (dry run) or the CLI envelope whose `result` text holds it."""
    try:
        raw = out_path.read_text(encoding="utf-8", errors="replace").strip()
    except FileNotFoundError:
        return None, "out.json missing"
    if not raw:
        return None, "out.json empty"
    data = _last_json_object(raw)
    if data is not None and "worker" in data and ("done" in data or "skipped" in data):
        return data, "direct"
    text = data.get("result") if data is not None and isinstance(data.get("result"), str) else raw
    rep = extract_report(text)
    if rep is None:
        err = " (CLI is_error)" if data is not None and data.get("is_error") else ""
        return None, f"no worker report in the reply{err}"
    return rep, "cli"


def _load_list(path: Path) -> list:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return []
    return data if isinstance(data, list) else []


def read_worker(d: Path, index: int) -> dict:
    report, note = load_worker_report(d / "out.json")
    assigned = [pg for pg in _load_list(d / "pages.json") if isinstance(pg, dict) and isinstance(pg.get("path"), str)]
    done: dict[str, dict] = {}
    for e in _entries(_load_list(d / "done.json")) + _entries((report or {}).get("done")):
        done.setdefault(e["path"], {}).update({k: v for k, v in e.items() if v not in (None, "")})
    skipped: dict[str, dict] = {}
    for e in _entries((report or {}).get("skipped"), default_reason="no reason given") + _entries(_load_list(d / "skipped.json"), default_reason="no reason given"):
        skipped.setdefault(e["path"], e)  # the final reply's reason wins over the running file
    for p in list(skipped):  # a page both produced and skipped counts as produced (a retry that succeeded)
        if p in done:
            skipped.pop(p)
    try:
        exit_code = int((d / "exit_code").read_text().strip())
    except (FileNotFoundError, ValueError):
        exit_code = None
    drafts, malformed = [], []
    for f in sorted(d.glob("*.json")):
        if f.name in RESERVED:
            continue
        try:
            doc = json.loads(f.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            malformed.append(f.name)
            continue
        (drafts if isinstance(doc, dict) and all(k in doc for k in WRITER_KEYS) else malformed).append(f.name)
    mismatch = report is not None and report.get("worker") not in (None, index)
    return {"worker": index, "dir": d, "report": report, "note": note + (f"; reply says worker {report.get('worker')}" if mismatch else ""),
            "assigned": assigned, "done": done, "skipped": skipped, "exit_code": exit_code, "drafts": drafts, "malformed_drafts": malformed}


# ------------------------------------------------------------------------------------------------ pipeline reports
def load_pipeline_reports(reports_dir: Path) -> list[dict]:
    out = []
    for f in sorted(reports_dir.glob("*.json")) if reports_dir.is_dir() else []:
        try:
            doc = json.loads(f.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue
        if isinstance(doc, dict) and doc.get("page_path"):
            out.append(dict(doc, _file=f.name))
    return out


def report_for(path: str, reports: list[dict], *, run_id: str, version_id: str | None) -> dict | None:
    cands = [r for r in reports if r.get("page_path") == path]
    if version_id:
        exact = [r for r in cands if str(r.get("version_id")) == version_id]
        if exact:
            cands = exact
    if not cands:
        return None
    mine = [r for r in cands if r.get("run_id") == run_id]
    cands = mine or cands
    return max(cands, key=lambda r: str(r.get("started") or ""))


# ------------------------------------------------------------------------------------------------ merge
def merge(run_dir: Path, *, reports_dir: Path = PIPELINE_REPORTS) -> tuple[dict, int]:
    dirs = sorted(((int(m.group(1)), d) for d in run_dir.iterdir() if d.is_dir() and (m := WORKER_DIR.match(d.name))), key=lambda t: t[0])
    if not dirs:
        return {"run": run_dir.name, "error": f"no worker-<i> folders under {run_dir}"}, 2
    workers = [read_worker(d, i) for i, d in dirs]
    run_id = f"headless-{run_dir.name}"
    reports = load_pipeline_reports(reports_dir)

    assigned_by, done_by = {}, {}
    for w in workers:
        for pg in w["assigned"]:
            assigned_by.setdefault(pg["path"], []).append(w["worker"])
        for p in w["done"]:
            done_by.setdefault(p, []).append(w["worker"])
    conflicts = [{"path": p, "workers": ws, "kind": "produced by more than one worker"} for p, ws in sorted(done_by.items()) if len(ws) > 1]
    conflicts += [{"path": p, "workers": ws, "kind": "assigned to more than one worker"} for p, ws in sorted(assigned_by.items()) if len(ws) > 1 and p not in {c["path"] for c in conflicts}]

    done, skipped, unaccounted, versions = [], [], [], []
    for w in workers:
        for p, e in w["done"].items():
            rep = report_for(p, reports, run_id=run_id, version_id=e.get("version_id"))
            vid = e.get("version_id") or (str(rep["version_id"]) if rep and rep.get("version_id") else None)
            outcome = e.get("outcome") or (rep.get("outcome") if rep else None)
            entry = {"path": p, "worker": w["worker"], "cluster_id": e.get("cluster_id") or (rep.get("cluster_id") if rep else None), "version_id": vid, "outcome": outcome,
                     "report": (f"build/runs/pipeline/{rep['_file']}" if rep else None)}
            done.append(entry)
            if vid:
                versions.append({"version_id": vid, "path": p, "worker": w["worker"], "outcome": outcome})
        for p, e in w["skipped"].items():
            skipped.append({"path": p, "worker": w["worker"], "reason": e.get("reason") or "no reason given"})
        for pg in w["assigned"]:
            if pg["path"] not in w["done"] and pg["path"] not in w["skipped"]:
                unaccounted.append({"path": pg["path"], "worker": w["worker"], "reason": "no result from the worker" if w["report"] is None else "not in the worker's reply"})

    reasons: dict[str, int] = {}
    for s in skipped:
        reasons[s["reason"]] = reasons.get(s["reason"], 0) + 1
    merged = {"run": run_dir.name, "run_dir": str(run_dir), "merged_at": datetime.now(timezone.utc).isoformat(timespec="seconds"), "ok": not conflicts,
              "workers": len(workers),
              "worker_reports": [{"worker": w["worker"], "reported": w["report"] is not None, "note": w["note"], "exit_code": w["exit_code"], "assigned": len(w["assigned"]),
                                  "done": len(w["done"]), "skipped": len(w["skipped"]), "drafts": len(w["drafts"]), "malformed_drafts": w["malformed_drafts"]} for w in workers],
              "assigned": [{"path": pg["path"], "worker": w["worker"], "cluster_id": pg.get("cluster_id"), "question_id": pg.get("question_id")} for w in workers for pg in w["assigned"]],
              "done": done, "skipped": skipped, "unaccounted": unaccounted, "skipped_reasons": reasons, "conflicts": conflicts,
              "versions": versions, "publishable": [v["version_id"] for v in versions if v["outcome"] == "gate_passed"],
              "publish_command": "worker/.venv/bin/python -m campus_worker.pipeline publish <version_id> [--siblings <ids>]",
              "drafts": {str(w["worker"]): w["drafts"] for w in workers}}
    return merged, (1 if conflicts else 0)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("run_dir", help="build/bulk/headless/<run>")
    ap.add_argument("--pipeline-reports", default=str(PIPELINE_REPORTS), help="where the pipeline wrote its per-cluster reports")
    a = ap.parse_args(argv)
    run_dir = Path(a.run_dir).resolve()
    if not run_dir.is_dir():
        print(f"merge: {run_dir} is not a directory", file=sys.stderr)
        return 2
    merged, rc = merge(run_dir, reports_dir=Path(a.pipeline_reports))
    if rc == 2:
        print("merge: " + merged["error"], file=sys.stderr)
        return 2
    (run_dir / "merged.json").write_text(json.dumps(merged, indent=1, default=str))
    for c in merged["conflicts"]:
        print(f"CONFLICT: {c['path']} {c['kind']}: workers {', '.join(str(w) for w in c['workers'])}", file=sys.stderr)
    wr = merged["worker_reports"]
    failed = [w["worker"] for w in wr if (w["exit_code"] not in (None, 0)) or not w["reported"]]
    print(f"headless merge {merged['run']}: workers={merged['workers']} (reported {sum(1 for w in wr if w['reported'])}, failed {len(failed)}{': ' + ','.join(map(str, failed)) if failed else ''})"
          f" assigned={len(merged['assigned'])} done={len(merged['done'])} skipped={len(merged['skipped'])} unaccounted={len(merged['unaccounted'])}"
          f" drafts={sum(w['drafts'] for w in wr)} (malformed {sum(len(w['malformed_drafts']) for w in wr)})"
          f" versions={len(merged['versions'])} (gate_passed {len(merged['publishable'])}) conflicts={len(merged['conflicts'])}")
    if merged["skipped_reasons"]:
        print("  skipped reasons: " + "; ".join(f"{r} x{n}" for r, n in sorted(merged["skipped_reasons"].items(), key=lambda t: -t[1])))
    for w in wr:
        if not w["reported"] or w["exit_code"] not in (None, 0):
            print(f"  worker {w['worker']}: exit={w['exit_code']} {w['note']}")
    if merged["publishable"]:
        print("  publish (serial, existing pipeline): " + " ".join(f"worker/.venv/bin/python -m campus_worker.pipeline publish {v}" for v in merged["publishable"][:3]) + (" …" if len(merged["publishable"]) > 3 else ""))
    print(f"  merged.json: {run_dir / 'merged.json'}")
    if rc:
        print(f"merge FAILED: {len(merged['conflicts'])} conflict(s); nothing was published", file=sys.stderr)
    return rc


if __name__ == "__main__":
    sys.exit(main())
