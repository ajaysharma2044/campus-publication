#!/usr/bin/env python
"""v3 research sprint driver (docs/v3/spec.md, step 1). One session per lane, in parallel, each writing intel/<topic>/raw/<lane>.md."""
from __future__ import annotations

import argparse
import csv
import re
import sys
from datetime import date
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "scripts" / "v2"))
from lib import sessions  # noqa: E402

LANES = {"A": "official", "B": "market", "C": "voice", "D": "competition", "E": "analysis"}
TOOLS = "WebSearch,WebFetch,Read,Grep,Glob,Write(intel/**),Edit(intel/**)"


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


COMPLETE = re.compile(r"^## Lane complete:.*$", re.M)


def lane_complete(path: Path) -> bool:
    """A lane is done only when its file ends with the '## Lane complete: ...' line (docs/v3 catch-up, step 5)."""
    if not path.exists():
        return False
    tail = path.read_text(encoding="utf-8").rstrip().splitlines()[-3:]
    return any(COMPLETE.match(l) for l in tail)


def merge_fragments(raw: Path, lane: str, log=print) -> None:
    """One file per lane: fold any stray part files a session created (<lane>-b.md, <lane>-part2.md, <lane>.md.part2, <lane>-sections-*.md) into <lane>.md."""
    target = raw / f"{lane}.md"
    frags = sorted(p for p in raw.iterdir() if p.is_file() and p != target and (p.name.startswith(lane + "-") or p.name.startswith(lane + ".md.")) and p.suffix in (".md", ".part2", ".txt"))
    for f in frags:
        text = f.read_text(encoding="utf-8").strip()
        if text:
            cur = target.read_text(encoding="utf-8") if target.exists() else ""
            cur = COMPLETE.sub("", cur).rstrip()   # the merged file is not complete until a session says so again
            target.write_text(cur + f"\n\n<!-- merged from {f.name} -->\n" + text + "\n", encoding="utf-8")
        f.unlink()
        log(f"  merged {f.name} into {target.name}")


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(prog="research.sh", description=__doc__)
    ap.add_argument("topic")
    ap.add_argument("--lanes", default="A,B,C,D,E")
    ap.add_argument("--workers", type=int, default=5)
    ap.add_argument("--model", default="sonnet")
    ap.add_argument("--max-turns", type=int, default=120)
    ap.add_argument("--timeout", type=int, default=7200)
    ap.add_argument("--deepen", action="store_true", help="extend each lane's existing notes (gaps against the scope) instead of starting fresh")
    ap.add_argument("--force", action="store_true", help="rerun a lane even if its file ends with a Lane complete line")
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
        merge_fragments(raw, name, log)
        if lane_complete(out) and not a.force:
            log(f"  {a.topic}:{lane}: already complete ({out.relative_to(REPO)} ends with a Lane complete line); use --force to redo or --deepen to extend")
            continue
        if out.exists() and not a.deepen and out.read_text(encoding="utf-8").strip():
            a.deepen = True   # an unfinished lane is continued in the same file, never restarted
        template = (REPO / "scripts/v3/prompts" / f"research-{name}.md").read_text(encoding="utf-8")
        deepen = ""
        if a.deepen and out.exists():
            deepen = (f"DEEPEN MODE: {out.relative_to(REPO)} already holds your earlier notes ({len(out.read_text(encoding='utf-8').split())} words). Read it first. "
                      "Do not rewrite or shorten it. Find the gaps against SCOPE and the coverage list, read new pages, and APPEND new sourced rows and sections "
                      "(use Edit to add at the end or under the right heading). Target: at least 2,000 new words and 20 new source URLs this session.")
        prompt = sessions.fill(template, topic_title=t["title"], topic_scope=t["scope"], topic_slug=a.topic, topic_dir=t["dir"], out_path=str(out.relative_to(REPO)),
                               demand_path=str((raw / "demand-questions.md").relative_to(REPO)), today=date.today().isoformat(), deepen=deepen)
        jobs.append({"id": f"{a.topic}:{lane}", "prompt": prompt, "expect": [str(out)]})
    if not jobs:
        log("every requested lane is complete; nothing to run")
        return 0
    st = sessions.run_jobs(jobs, workers=a.workers, label="research", model=a.model, max_turns=a.max_turns, allowed_tools=TOOLS, timeout_s=a.timeout, log=log)
    for j in jobs:
        f = Path(j["expect"][0])
        words = len(f.read_text(encoding="utf-8").split()) if f.exists() else 0
        log(f"  {j['id']}: {words} words in {f.relative_to(REPO)}; {'complete' if lane_complete(f) else 'NOT complete (rerun research.sh to continue it)'}")
    log(f"research done: {st['ok']} ok, {st['failed']} failed; {st['sessions']} sessions; {st['hours']:.2f} h; {st['pauses']} pause(s)")
    return 0 if st["failed"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
