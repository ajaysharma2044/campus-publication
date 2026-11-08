#!/usr/bin/env bash
# Step 3 of docs/v2/spec.md: review. One fresh claude -p session per article in status written (tools: Read, WebFetch, WebSearch,
# Write(content/reviews/**)) fact-checks every cited source and runs the beats-#1 test, writing content/reviews/<slug>.json.
# Verdict pass: the row stays written (publish.sh reads the review); fix: status fix (then write.sh --fix and review.sh once more;
# a second fix verdict rejects); reject: rejected. Log: build/runs/v2/review-<timestamp>.log. Stop cleanly: scripts/v2/stop.sh.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
PY="$ROOT/worker/.venv/bin/python"

usage() {
  cat <<'EOF'
usage: scripts/v2/review.sh [--workers 4] [--limit N] [--model sonnet|opus] [--max-turns 40] [--timeout SECONDS]

Reviews every article whose queue row is written and has no review yet, or whose review said fix and the article has been
revised (write.sh --fix). The row is reviewing while the session runs. An earlier review is kept as
content/reviews/<slug>.prev.json. Outcome per verdict: pass -> written (publish.sh publishes rows with a passing review);
fix -> fix (first round) or rejected (second round); reject -> rejected. Defaults: --workers 4, --model sonnet,
--max-turns 40, --timeout 1800.
EOF
}
for a in "$@"; do case "$a" in -h|--help) usage; exit 0;; esac; done
cd "$ROOT"
exec "$PY" - "$@" <<'PY'
import argparse
import json
import sys
from datetime import date

sys.path.insert(0, "scripts/v2")
from lib import queue as q, sessions

ap = argparse.ArgumentParser(prog="review.sh", add_help=False)
ap.add_argument("--workers", type=int, default=4)
ap.add_argument("--limit", type=int, default=0)
ap.add_argument("--model", default="sonnet")
ap.add_argument("--max-turns", type=int, default=40)
ap.add_argument("--timeout", type=int, default=1800)
a = ap.parse_args()

REPO = sessions.REPO
REVIEWS = REPO / "content/reviews"
log, _ = sessions.open_log("review")
sessions.clear_stop(log)
rel = lambda p: str(p.relative_to(REPO))
template = (REPO / "scripts/v2/prompts/review.md").read_text(encoding="utf-8")
today = date.today().isoformat()
REVIEWS.mkdir(parents=True, exist_ok=True)


def load(path):
    try:
        d = json.loads(path.read_text(encoding="utf-8"))
        return d if isinstance(d, dict) else {}
    except (OSError, ValueError):
        return {}


def prepare(r, rev):
    def go():
        q.set_status(r["id"], "reviewing")
        if rev.exists():
            rev.replace(rev.with_name(f"{rev.stem}.prev.json"))
    return go


def check(rev, qid):
    def go():
        d = load(rev)
        problems = []
        if d.get("verdict") not in ("pass", "fix", "reject"):
            problems.append(f"verdict is {d.get('verdict')!r}")
        if not isinstance(d.get("fact_check"), list):
            problems.append("fact_check is not a list")
        if not isinstance(d.get("beats_top"), dict):
            problems.append("beats_top is not an object")
        if d.get("verdict") == "fix" and not d.get("fixes"):
            problems.append("verdict fix without a fixes list")
        return [f"review json: {'; '.join(problems)}"] if problems else []
    return go


def on_done(job, ok, r, problems):
    if not ok:
        q.set_status(job["id"], "written")
        log(f"[{job['id']}] review failed, row stays written for the next run: {'; '.join(problems)[:300]}")
        return
    d = load(job["review"])
    verdict = d["verdict"]
    bt = d.get("beats_top") or {}
    mism = sum(1 for f in d.get("fact_check") or [] if f.get("status") == "mismatch")
    if verdict == "pass":
        q.set_status(job["id"], "written")
        log(f"[{job['id']}] PASS ({len(d.get('fact_check') or [])} facts, {mism} mismatches, better={bt.get('better')}); publish.sh will take it")
    elif verdict == "fix" and job["round"] >= 2:
        q.set_status(job["id"], "rejected")
        log(f"[{job['id']}] second fix verdict -> rejected ({len(d.get('fixes') or [])} fixes still open)")
    elif verdict == "fix":
        q.set_status(job["id"], "fix")
        log(f"[{job['id']}] FIX ({len(d.get('fixes') or [])} fixes, {mism} mismatches); run write.sh --fix, then review.sh")
    else:
        q.set_status(job["id"], "rejected")
        log(f"[{job['id']}] REJECT: {str(bt.get('why') or (d.get('fixes') or [''])[0])[:200]}")


jobs = []
for r in q.by_status("written"):
    art = q.article_for(r["id"])
    if not art:
        log(f"{r['id']}: status written but no article carries this queue_id; skipped")
        continue
    rev = REVIEWS / f"{art.stem}.json"
    cur = load(rev) if rev.exists() else {}
    if cur.get("verdict") == "pass":
        continue
    if cur.get("verdict") == "reject":
        log(f"{r['id']}: the review says reject but the row is written; skipped (repair by hand)")
        continue
    # round 2 after the one revision: the current review says fix, or (a failed round-2 session) only the moved-aside .prev.json does
    prev = cur if cur.get("verdict") == "fix" else load(rev.with_name(f"{rev.stem}.prev.json"))
    rnd = 2 if prev.get("verdict") == "fix" else 1
    previous = ("\n" + "\n".join(f"  - {f}" for f in prev["fixes"])) if prev.get("fixes") else "none (first review)"
    rule = ("This is the first review: a fix verdict sends the article back to the writer for one revision." if rnd == 1 else
            "This is the second review, after the only revision allowed. The pipeline turns a second fix verdict into reject, so decide "
            "pass or reject; check first that the previous fixes were applied.")
    prompt = sessions.fill(template, date=today, article_path=rel(art), slug=art.stem, id=r["id"], question=r["question"],
                           primary_query=r["primary_query"], angle=r["angle"] or "(none given)",
                           round="first review" if rnd == 1 else "second review, after the one revision allowed",
                           previous=previous, round_rule=rule, review_path=rel(rev))
    sessions.save_prompt("review", r["id"], prompt)
    jobs.append({"id": r["id"], "prompt": prompt, "expect": [str(rev)], "review": rev, "round": rnd,
                 "prepare": prepare(r, rev), "check": check(rev, r["id"])})
    if a.limit and len(jobs) >= a.limit:
        break
if not jobs:
    log("nothing to do: no written article without a passing review")
    sys.exit(0)
log(f"{len(jobs)} review session(s) with {a.model}, {a.workers} workers")
stats = sessions.run_jobs(jobs, workers=a.workers, label="review", model=a.model, max_turns=a.max_turns,
                          allowed_tools="Read,WebFetch,WebSearch,Write(content/reviews/**)", timeout_s=a.timeout, log=log, on_done=on_done)
counts = {}
for r in q.read():
    counts[r["status"]] = counts.get(r["status"], 0) + 1
log(f"reviews written: {stats['ok']}; failed: {stats['failed']}; queue: {counts}")
PY
