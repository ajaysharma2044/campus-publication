"""Shard a planned page list across N headless workers (specs/bulk-mode.md section 3, the no-API-key fallback; acceptance B5).
Called by scripts/parallel_headless.sh; usable on its own:

  worker/.venv/bin/python scripts/shard_headless_pages.py --pages <file> --workers N --run-dir <dir> [--limit M] [--dry-run]

Input: a JSON list (or {"pages": [...]}) of planned pages with the keys question_id, path, page_type, question, cluster_id (null allowed),
as `campus_worker.bulk plan --json` and `campus_worker.lean queue --json` print them. Pages go round-robin to the workers; pages that share a
cluster id land on the same worker (the pipeline writes one report file per cluster, so one writer per cluster). Duplicate paths are dropped
(first wins) and reported. Writes:
  <run-dir>/pages.json                 every page with its worker index and draft slug
  <run-dir>/shards.json                [{"worker": i, "pages": k}]
  <run-dir>/worker-<i>/pages.json      the worker's shard
  <run-dir>/worker-<i>/page_count      the shard size (read by the shell script)
  <run-dir>/worker-<i>/prompt.md       scripts/headless_worker_prompt.md rendered for this worker
  --dry-run adds worker-<i>/out.json ({"worker": i, "done": [], "skipped": [every page as "dry-run"]}) and exit_code 0, so the merge can run
  without `claude -p`.
Prints one summary line. Exit 2 on an empty or malformed page list.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = REPO_ROOT / "scripts" / "headless_worker_prompt.md"
PAGE_KEYS = ("question_id", "path", "page_type", "question", "cluster_id")
UUID_RE = re.compile(r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$")


def slug_for(path: str) -> str:
    """Draft file name for a page path: /schools/cornell-university/housing/costs/ -> schools-cornell-university-housing-costs."""
    s = re.sub(r"[^a-z0-9]+", "-", path.lower()).strip("-")
    return s[:120].rstrip("-") or "page"


def load_pages(path: Path) -> list[dict]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, dict):
        data = data.get("pages")
    if not isinstance(data, list):
        raise SystemExit(f"shard: {path} must hold a JSON list of planned pages (or {{\"pages\": [...]}})")
    out, problems = [], []
    for n, item in enumerate(data):
        if not isinstance(item, dict) or not isinstance(item.get("path"), str) or not item["path"].startswith("/"):
            problems.append(f"item {n}: no page path (expected keys {', '.join(PAGE_KEYS)})")
            continue
        cid = item.get("cluster_id")
        cid = str(cid) if cid not in (None, "") else None
        if cid and not UUID_RE.match(cid):
            problems.append(f"item {n} ({item['path']}): cluster_id {cid!r} is not a UUID")
            continue
        question = " ".join(str(item.get("question") or "").split())
        out.append({"question_id": item.get("question_id"), "path": item["path"].strip(), "page_type": item.get("page_type") or "guide",
                    "question": question, "cluster_id": cid})
    if problems:
        raise SystemExit("shard: malformed planned pages:\n  " + "\n  ".join(problems))
    return out


def assign(pages: list[dict], workers: int) -> tuple[list[list[dict]], list[str]]:
    """Round-robin by position; a repeated cluster id follows its first page's worker; a repeated path is dropped."""
    shards: list[list[dict]] = [[] for _ in range(workers)]
    seen_paths: set[str] = set()
    cluster_worker: dict[str, int] = {}
    dropped: list[str] = []
    nxt = 0
    for pg in pages:
        if pg["path"] in seen_paths:
            dropped.append(pg["path"])
            continue
        seen_paths.add(pg["path"])
        cid = pg["cluster_id"]
        if cid and cid in cluster_worker:
            w = cluster_worker[cid]
        else:
            w = nxt
            nxt = (nxt + 1) % workers
            if cid:
                cluster_worker[cid] = w
        shards[w].append(pg)
    for w, shard in enumerate(shards):  # unique draft file names inside one folder
        used: dict[str, int] = {}
        for pg in shard:
            base = slug_for(pg["path"])
            used[base] = used.get(base, 0) + 1
            pg["slug"] = base if used[base] == 1 else f"{base}-{used[base]}"
            pg["worker"] = w
    return shards, dropped


def folder_label(run_dir: Path, worker: int) -> str:
    """How the worker names its folder in commands run from the repository root: relative inside the repo, absolute elsewhere (tests)."""
    d = run_dir / f"worker-{worker}"
    try:
        return d.relative_to(REPO_ROOT).as_posix() + "/"
    except ValueError:
        return d.as_posix() + "/"


def render_prompt(template: str, *, worker: int, workers: int, run: str, folder: str, shard: list[dict]) -> str:
    lines = []
    for n, pg in enumerate(shard, 1):
        cid = pg["cluster_id"]
        lines.append(f"{n}. path: `{pg['path']}` · slug: `{pg['slug']}` · page_type: {pg['page_type']} · question_id: {pg['question_id'] or 'null'}"
                     f" · cluster_id: {('`' + cid + '`') if cid else 'null (skip)'}")
        lines.append(f"   question: {pg['question'] or '(none recorded)'}")
        if cid:
            lines.append(f"   run:    worker/.venv/bin/python -m campus_worker.pipeline run {cid} --until verify --path {pg['path']}")
            lines.append(f"   report: build/runs/pipeline/{cid[:8]}.json")
            lines.append(f"   draft:  worker/.venv/bin/python scripts/headless_draft.py <version_id> --out {folder}{pg['slug']}.json")
    text = template
    for key, val in (("{{WORKER}}", str(worker)), ("{{WORKERS}}", str(workers)), ("{{RUN}}", run), ("{{FOLDER}}", folder),
                     ("{{PAGE_COUNT}}", str(len(shard))), ("{{PAGES}}", "\n".join(lines) or "(no pages: end your reply with the final JSON line, done and skipped empty)")):
        text = text.replace(key, val)
    return text


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--pages", required=True, help="planned pages JSON (bulk plan --json or lean queue --json output)")
    ap.add_argument("--workers", type=int, required=True)
    ap.add_argument("--run-dir", required=True, help="build/bulk/headless/<run>")
    ap.add_argument("--limit", type=int, default=0, help="take at most M pages (0 = all)")
    ap.add_argument("--dry-run", action="store_true", help="also write the fake out.json per worker (every page skipped as dry-run)")
    a = ap.parse_args(argv)
    if a.workers < 1:
        raise SystemExit("shard: --workers must be at least 1")
    run_dir = Path(a.run_dir).resolve()
    pages = load_pages(Path(a.pages))
    if a.limit and a.limit > 0:
        pages = pages[: a.limit]
    shards, dropped = assign(pages, a.workers)
    total = sum(len(s) for s in shards)
    if total == 0:
        raise SystemExit("shard: the page list is empty; nothing to shard")
    template = TEMPLATE.read_text(encoding="utf-8")
    run_dir.mkdir(parents=True, exist_ok=True)
    flat = [pg for shard in shards for pg in shard]
    (run_dir / "pages.json").write_text(json.dumps(flat, indent=1))
    (run_dir / "shards.json").write_text(json.dumps([{"worker": w, "pages": len(s)} for w, s in enumerate(shards)], indent=1))
    for w, shard in enumerate(shards):
        d = run_dir / f"worker-{w}"
        d.mkdir(parents=True, exist_ok=True)
        (d / "pages.json").write_text(json.dumps(shard, indent=1))
        (d / "page_count").write_text(f"{len(shard)}\n")
        (d / "prompt.md").write_text(render_prompt(template, worker=w, workers=a.workers, run=run_dir.name, folder=folder_label(run_dir, w), shard=shard))
        if a.dry_run:
            (d / "out.json").write_text(json.dumps({"worker": w, "done": [], "skipped": [{"path": pg["path"], "reason": "dry-run"} for pg in shard]}) + "\n")
            (d / "exit_code").write_text("0\n")
    print(json.dumps({"run": run_dir.name, "workers": a.workers, "pages": total, "per_worker": [len(s) for s in shards], "dropped_duplicates": dropped, "dry_run": bool(a.dry_run)}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
