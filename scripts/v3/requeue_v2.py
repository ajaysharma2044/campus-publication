#!/usr/bin/env python
"""Queue the topic's published v2 articles for a v3 rewrite (docs/v3/spec.md, "Publish requirements": re-run every published v2 article
through steps 5 to 7). Every content/articles/<dir>/<slug>.md whose frontmatter has no `kind` (a v2 page) and whose queue row is published
gets a plan row (contract 2) with kind=rewrite, so scripts/v3/write.sh rewrites it in place from the topic brief.

    scripts/v3/requeue_v2.py <topic> [--approve] [--dry-run] [--again] [--queue FILE] [--articles-dir DIR] [--intel-dir DIR]

The new row: id from queue.py next_id; question = the article's title; primary_query = the article's; topic = the dir;
demand_evidence = intel/<topic>/brief.md; verdict plan; angle "kind=rewrite; slug=<slug>; readers=; type=<type>; replaces=<old id>";
status proposed (--approve: approved at once, as plan.sh --approve would). An article that already has a rewrite row is skipped unless
--again (then a rejected rewrite may be queued once more). Prints what it queued.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "scripts" / "v2"))
sys.path.insert(0, str(REPO / "scripts" / "v3"))
from lib import queue as q  # noqa: E402
import write as w  # noqa: E402


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(prog="requeue_v2.py", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("topic", help="topic slug from scripts/v3/topics.yml (or its content dir)")
    ap.add_argument("--approve", action="store_true", help="approve the new rows at once")
    ap.add_argument("--dry-run", action="store_true", help="print the rows without writing the queue")
    ap.add_argument("--again", action="store_true", help="queue an article again when its earlier rewrite row was rejected")
    ap.add_argument("--queue")
    ap.add_argument("--articles-dir")
    ap.add_argument("--intel-dir")
    ap.add_argument("--content-dir")
    ap.add_argument("--state-file")
    a = ap.parse_args(argv)
    topic = w.resolve_topic(a.topic)
    tdir = topic["dir"]
    P = w.Paths(a, topic)
    rows = q.read(P.queue)
    status = {r["id"]: r for r in rows}
    rewrites = {}   # slug -> status of the existing rewrite row(s)
    for r in rows:
        ang = w.parse_angle(r["angle"])
        if r["topic"] == tdir and ang.get("kind") == "rewrite" and ang.get("slug"):
            rewrites.setdefault(ang["slug"], []).append(r["status"])
    brief_rel = w.rel(P.brief)
    new, skipped = [], []
    for p in sorted((P.articles / tdir).glob("*.md")):
        fm = q.frontmatter(p)
        if not fm:
            skipped.append((p.stem, "no frontmatter"))
            continue
        if fm.get("kind"):
            skipped.append((p.stem, f"already a v3 page (kind {fm['kind']})"))
            continue
        old = status.get(str(fm.get("queue_id") or ""))
        if not old or old["status"] != "published":
            skipped.append((p.stem, f"queue row {fm.get('queue_id')!r} is {old['status'] if old else 'missing'}, not published"))
            continue
        had = rewrites.get(p.stem, [])
        if had and (not a.again or any(s != "rejected" for s in had)):
            skipped.append((p.stem, f"rewrite row exists ({', '.join(had)})"))
            continue
        new.append({"id": "", "question": str(fm.get("title") or old["question"]), "primary_query": str(fm.get("primary_query") or old["primary_query"]),
                    "topic": tdir, "demand_evidence": brief_rel, "top_results": "", "verdict": "plan",
                    "angle": f"kind=rewrite; slug={p.stem}; readers=; type={fm.get('type') or 'how-to'}; replaces={old['id']}",
                    "status": "proposed"})
    for slug, why in skipped:
        print(f"- skipped {slug}: {why}")
    if not new:
        print(f"nothing to queue: no published v2 article of {tdir} without a rewrite row")
        return 0
    if a.dry_run:
        for r in new:
            print(f"+ (dry run) {r['angle']} | {r['question'][:70]}")
        print(f"{len(new)} rewrite row(s) would be added to {w.rel(P.queue)}")
        return 0
    added = q.append(new, P.queue)
    if a.approve:
        q.approve([r["id"] for r in added], P.queue)
    for r in added:
        print(f"+ {r['id']} {'approved' if a.approve else 'proposed'} {r['angle']} | {r['question'][:70]}")
    print(f"queued {len(added)} rewrite row(s) in {w.rel(P.queue)}" + ("" if a.approve else f"; approve them with plan.sh --approve {topic['slug']} or queue.py approve --ids ..."))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
