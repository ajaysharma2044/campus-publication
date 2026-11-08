#!/usr/bin/env bash
# Step 1 of docs/v2/spec.md: find demand. One claude -p session per topic seed (tools: WebSearch, WebFetch, Read, Write(queue/**))
# writes queue/proposed/<topic>-<timestamp>.csv; this script merges those files into queue/queue.csv (gap|weak -> proposed,
# owned -> owned) and prints the counts. Log: build/runs/v2/find_demand-<timestamp>.log. Stop cleanly: scripts/v2/stop.sh.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
PY="$ROOT/worker/.venv/bin/python"

usage() {
  cat <<'EOF'
usage: scripts/v2/find_demand.sh <topic|all> [--auto-approve] [--workers N] [--model sonnet|opus] [--max-turns N] [--timeout SECONDS]

Topics: housing getting-around academics money daily-life careers parents alumni ("all" runs every seed).
Each topic session collects real questions (web results and People-also-ask style questions, r/Cornell and r/ithaca thread
titles, College Confidential threads, data/questions/*.yaml), searches each candidate once, records the top 5 results, gives a
verdict (gap | weak | owned) with a one-sentence angle, dedupes by meaning against queue/queue.csv and content/articles/, and
writes queue/proposed/<topic>-<timestamp>.csv. The script merges the files into queue/queue.csv: gap and weak rows become
status proposed, owned rows owned. --auto-approve flips the rows merged by this run from proposed to approved.
Defaults: --workers 4, --model sonnet, --max-turns 120, --timeout 3600.
EOF
}
for a in "$@"; do case "$a" in -h|--help) usage; exit 0;; esac; done
[ $# -ge 1 ] || { usage; exit 2; }
cd "$ROOT"
exec "$PY" - "$@" <<'PY'
import argparse
import sys
from datetime import date, datetime

sys.path.insert(0, "scripts/v2")
from lib import queue as q, sessions

SEEDS = {  # the Scope section of docs/v2/spec.md, one seed per topic slug
    "housing": "Housing: dorms, program houses, co-ops, Greek housing, off-campus apartments, Collegetown vs Fall Creek vs downtown, specific buildings and landlords, leases, subletting, roommates, move-in and move-out, storage, renters insurance, tenant rights in Ithaca.",
    "getting-around": "Getting there and around: flights into ITH, SYR and ELM, buses and shuttles to NYC, Boston and Philly, airport rides, driving and parking, TCAT routes, biking in winter, rideshare, break travel.",
    "academics": "Classes and academics: specific courses and professors (from public course review sites and student discussion), easy and hard requirements, registration strategy, add/drop, switching colleges, internal transfer, study spots, tutoring.",
    "money": "Money: real cost of living, cheap groceries, meal plan math, jobs on and off campus, financial aid appeals, budgeting by scenario.",
    "daily-life": "Daily life: dining, food in Collegetown and downtown, gyms, healthcare and pharmacies, phones and banking, winter gear, safety, nightlife, clubs and joining them.",
    "careers": "Careers: internships, recruiting timelines, career fairs, specific employers that hire from the school.",
    "parents": "Parents and families: visiting, hotels, move-in weekend, graduation, what to send.",
    "alumni": "Alumni: benefits, events, staying in Ithaca after graduation.",
}
ap = argparse.ArgumentParser(prog="find_demand.sh", add_help=False)
ap.add_argument("topic")
ap.add_argument("--auto-approve", action="store_true")
ap.add_argument("--workers", type=int, default=4)
ap.add_argument("--model", default="sonnet")
ap.add_argument("--max-turns", type=int, default=120)
ap.add_argument("--timeout", type=int, default=3600)
a = ap.parse_args()
topics = list(SEEDS) if a.topic == "all" else [a.topic]
if any(t not in SEEDS for t in topics):
    sys.exit(f"unknown topic {a.topic!r}; one of: all {' '.join(SEEDS)}")

REPO = sessions.REPO
log, _ = sessions.open_log("find_demand")
sessions.clear_stop(log)
template = (REPO / "scripts/v2/prompts/demand.md").read_text(encoding="utf-8")
rows = q.read()
queue_text = "\n".join(f"{r['id']} | {r['topic']} | {r['status']} | {r['question']}" for r in rows) or "(empty)"
articles_text = "\n".join(f"/{p.parent.name}/{p.stem}/ | {q.frontmatter(p).get('title') or p.stem}" for p in q.articles()) or "(none yet)"
owner = [f"### {f.relative_to(REPO)}\n{f.read_text(encoding='utf-8')}" for f in sorted((REPO / "data/questions").glob("*.y*ml"))]
owner_text = "\n".join(owner)[:40000] or "(no files in data/questions/ yet)"
ts = datetime.now().strftime("%Y%m%dT%H%M%S")
(REPO / "queue/proposed").mkdir(parents=True, exist_ok=True)

jobs = []
for t in topics:
    out = f"queue/proposed/{t}-{ts}.csv"
    prompt = sessions.fill(template, date=date.today().isoformat(), topic=t, seed=SEEDS[t], out_file=out,
                           queue=queue_text, articles=articles_text, owner_questions=owner_text)
    sessions.save_prompt("demand", t, prompt)
    jobs.append({"id": t, "prompt": prompt, "expect": [out]})
log(f"{len(jobs)} topic session(s): {', '.join(topics)}; the queue has {len(rows)} rows")

tally = {"gap": 0, "weak": 0, "owned": 0, "skipped": 0, "ids": []}


def on_done(job, ok, r, problems):
    if not ok:
        return
    added, skipped = q.merge_proposed(REPO / job["expect"][0], topic=job["id"])
    for row in added:
        tally[row["verdict"]] += 1
        tally["ids"].append(row["id"])
    tally["skipped"] += len(skipped)
    log(f"[{job['id']}] merged {len(added)} rows ({sum(1 for x in added if x['verdict'] == 'gap')} gap, "
        f"{sum(1 for x in added if x['verdict'] == 'weak')} weak, {sum(1 for x in added if x['verdict'] == 'owned')} owned), skipped {len(skipped)}")
    for question, why in skipped:
        log(f"[{job['id']}]   skipped ({why}): {question[:90]}")


sessions.run_jobs(jobs, workers=a.workers, label="demand", model=a.model, max_turns=a.max_turns,
                  allowed_tools="WebSearch,WebFetch,Read,Write(queue/**)", timeout_s=a.timeout, log=log, on_done=on_done)
if a.auto_approve:
    done = q.approve(tally["ids"])
    log(f"auto-approved {len(done)} rows")
counts = {}
for r in q.read():
    counts[r["status"]] = counts.get(r["status"], 0) + 1
log(f"merged this run: {tally['gap']} gap, {tally['weak']} weak, {tally['owned']} owned ({tally['skipped']} skipped); "
    f"queue/queue.csv now {sum(counts.values())} rows: {counts}")
PY
