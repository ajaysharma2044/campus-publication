#!/usr/bin/env python
"""v3 research sprint driver (docs/v3/spec.md, step 1). One session per lane, in parallel, each writing intel/<topic>/raw/<lane>.md."""
from __future__ import annotations

import argparse
import csv
import sys
from datetime import date
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "scripts" / "v2"))
from lib import sessions  # noqa: E402

LANES = {"A": "official", "B": "market", "C": "voice", "D": "competition", "E": "analysis"}
TOOLS = "WebSearch,WebFetch,Read,Grep,Glob,Write(intel/**)"


def topics() -> dict[str, dict]:
    return {t["slug"]: t for t in yaml.safe_load((REPO / "scripts/v3/topics.yml").read_text())}


def demand_notes(topic: dict, out: Path) -> int:
    """The demand rows we already have for this topic (queue/queue.csv), for lanes C and D."""
    rows = [r for r in csv.DictReader((REPO / "queue/queue.csv").open()) if r["topic"] == topic["dir"]]
    lines = [f"# Demand rows for {topic['title']} (from queue/queue.csv, {date.today().isoformat()})", "", "| id | question | primary query | verdict | top results |", "|---|---|---|---|---|"]
    for r in rows:
        lines.append(f"| {r['id']} | {r['question']} | {r['primary_query']} | {r['verdict']} | {r['top_results'][:300]} |")
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return len(rows)


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(prog="research.sh", description=__doc__)
    ap.add_argument("topic")
    ap.add_argument("--lanes", default="A,B,C,D,E")
    ap.add_argument("--workers", type=int, default=5)
    ap.add_argument("--model", default="sonnet")
    ap.add_argument("--max-turns", type=int, default=120)
    ap.add_argument("--timeout", type=int, default=7200)
    a = ap.parse_args(argv)
    t = topics().get(a.topic)
    if not t:
        print(f"unknown topic {a.topic!r}; see scripts/v3/topics.yml", file=sys.stderr)
        return 2
    raw = REPO / "intel" / a.topic / "raw"
    raw.mkdir(parents=True, exist_ok=True)
    log, log_path = sessions.open_log("research")
    sessions.clear_stop(log)
    n_demand = demand_notes(t, raw / "demand-questions.md")
    log(f"research sprint for {t['title']} ({a.topic}): lanes {a.lanes}, {a.workers} workers, model {a.model}, {a.max_turns} turns; {n_demand} demand rows exported; log {log_path}")
    jobs = []
    for lane in [x.strip().upper() for x in a.lanes.split(",") if x.strip()]:
        name = LANES[lane]
        out = raw / f"{name}.md"
        template = (REPO / "scripts/v3/prompts" / f"research-{name}.md").read_text(encoding="utf-8")
        prompt = sessions.fill(template, topic_title=t["title"], topic_scope=t["scope"], topic_slug=a.topic, topic_dir=t["dir"], out_path=str(out.relative_to(REPO)),
                               demand_path=str((raw / "demand-questions.md").relative_to(REPO)), today=date.today().isoformat())
        jobs.append({"id": f"{a.topic}:{lane}", "prompt": prompt, "expect": [str(out)]})
    st = sessions.run_jobs(jobs, workers=a.workers, label="research", model=a.model, max_turns=a.max_turns, allowed_tools=TOOLS, timeout_s=a.timeout, log=log)
    for j in jobs:
        f = Path(j["expect"][0])
        words = len(f.read_text(encoding="utf-8").split()) if f.exists() else 0
        log(f"  {j['id']}: {words} words in {f.relative_to(REPO)}")
    log(f"research done: {st['ok']} ok, {st['failed']} failed; {st['sessions']} sessions; {st['hours']:.2f} h; {st['pauses']} pause(s)")
    return 0 if st["failed"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
