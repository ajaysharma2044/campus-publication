#!/usr/bin/env python
"""v3 fact check (docs/v3/spec.md §7, speed mode item 1): one sonnet session per written page checks only the facts that are NOT in the
topic brief (brief facts were checked once when the brief was built), plus our own math and the attributions; it fixes wrong numbers,
dates and attributions in place and logs content/checks/<slug>.json (contract 5).

    scripts/v3/check.sh <topic> [--workers 8] [--model sonnet] [--limit N] [--ids a,b] [--recheck] [--max-turns 50] [--timeout 1800]
                        [--intel-dir DIR] [--queue FILE] [--articles-dir DIR] [--content-dir DIR] [--runs-dir DIR]

Takes the topic's plan rows (angle kind=...) in status written whose page exists and has no passing check yet (--recheck: every written
page; --ids: these rows). A v2 row (no plan angle) is not this step's: scripts/v2/review.sh reviews it, and the log names it once.
The row is reviewing while the session runs. Verdict pass unless the core answer is wrong or a fact cannot be sourced after one search
(reject); fix only when the session could not apply its own fix. Afterwards:
  pass   -> written, and content/reviews/<slug>.json gets the v2 review shape (verdict, fact_check, beats_top, fixes) with verdict pass, so
            scripts/v2/publish.sh lints and publishes it unchanged. A tool, dataset or start-here row (no article for publish.sh to lint)
            goes to published here; the renderer takes it from content/tools/, content/datasets/ and content/start/.
  fix    -> fix (write.sh --fix runs the one revision, then this step checks again; a second fix verdict rejects)
  reject -> rejected (a rejected rewrite gets its old page and queue row back)
A session that leaves no valid check file puts the row back to written for the next run. Logs: build/runs/v2/check-<ts>.log.
Stop cleanly: scripts/v2/stop.sh. The sessions never inherit worker/.env (scripts/v3/write.py scrub_env). CLAUDE_BIN points the sessions
at a stub for tests; --runs-dir moves logs, prompts and the rewrite backups for a test run.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "scripts" / "v2"))
sys.path.insert(0, str(REPO / "scripts" / "v3"))
from lib import queue as q, sessions  # noqa: E402
import write as w  # noqa: E402  (the shared helpers: topics, angles, paths, rewrite restore; it also turns Edit on for the sessions)

STATUSES = ("ok", "fixed", "unverifiable")
PUBLISH_HERE = ("tool", "dataset", "start_here")   # no article for publish.sh to lint; the renderer filters them by their published row
TODAY = date.today().isoformat()


def load(path: Path) -> dict:
    try:
        d = json.loads(path.read_text(encoding="utf-8"))
        return d if isinstance(d, dict) else {}
    except (OSError, ValueError):
        return {}


def check_problems(d: dict, qid: str) -> list[str]:
    problems = []
    if d.get("verdict") not in ("pass", "fix", "reject"):
        problems.append(f"verdict is {d.get('verdict')!r}")
    if not isinstance(d.get("checked"), list):
        problems.append("checked is not a list")
    else:
        bad = [c for c in d["checked"] if not isinstance(c, dict) or not c.get("claim") or c.get("status") not in STATUSES + ("wrong", "mismatch")]
        if bad:
            problems.append(f"{len(bad)} checked item(s) without claim or with a status outside ok|fixed|unverifiable")
    if not isinstance(d.get("brief_updates", []), list):
        problems.append("brief_updates is not a list")
    if d.get("verdict") == "fix" and not d.get("fixes"):
        problems.append("verdict fix without a fixes list")
    if str(d.get("queue_id") or qid) != qid:
        problems.append(f"queue_id is {d.get('queue_id')!r}, expected {qid}")
    return problems


def review_from_check(d: dict, slug: str, qid: str, primary_query: str) -> dict:
    """content/reviews/<slug>.json in the v2 shape publish.sh reads (verdict) and review.sh validates (fact_check, beats_top, fixes)."""
    fact_check = []
    for c in d.get("checked") or []:
        status = c.get("status")
        note = str(c.get("note") or "")
        if status == "fixed":
            status, note = "ok", f"fixed in place: {note}"
        elif status in ("wrong", "mismatch"):
            status = "mismatch"
        fact_check.append({"claim": c.get("claim"), "source_url": c.get("source_url") or "", "status": status, "note": note})
    return {"slug": slug, "queue_id": qid, "verdict": d["verdict"], "fact_check": fact_check,
            "beats_top": {"query": primary_query, "top_url": "", "better": "n/a", "why": "v3: coverage is decided by the topic brief and plan, not a beats-#1 test", "changes": []},
            "fixes": list(d.get("fixes") or []), "brief_updates": list(d.get("brief_updates") or []), "core_answer": d.get("core_answer", ""),
            "reviewed_at": TODAY, "checked_by": "scripts/v3/check.sh"}


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(prog="check.sh", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("topic")
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--model", default="sonnet")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--ids", default="")
    ap.add_argument("--recheck", action="store_true", help="check written pages that already have a passing check")
    ap.add_argument("--max-turns", type=int, default=50)
    ap.add_argument("--timeout", type=int, default=1800)
    ap.add_argument("--intel-dir")
    ap.add_argument("--queue")
    ap.add_argument("--articles-dir")
    ap.add_argument("--content-dir")
    ap.add_argument("--state-file")
    ap.add_argument("--runs-dir", help="logs, prompts and rewrite backups go here instead of build/runs/v2 (tests)")
    a = ap.parse_args(argv)
    topic = w.resolve_topic(a.topic)
    tdir = topic["dir"]
    P = w.Paths(a, topic)
    log, log_path = sessions.open_log("check")
    sessions.clear_stop(log)
    scrubbed = w.scrub_env()
    if scrubbed:
        log(f"{scrubbed} worker/.env variable(s) removed from the sessions' environment")
    P.checks.mkdir(parents=True, exist_ok=True)
    P.reviews.mkdir(parents=True, exist_ok=True)
    template = (w.PROMPTS / "check.md").read_text(encoding="utf-8")
    check_tools = ",".join(["Read", "Grep", "Glob", "WebFetch", "WebSearch", w.rule("Write", P.checks), w.rule("Edit", P.articles), w.rule("Edit", P.tools),
                            w.rule("Edit", P.datasets), w.rule("Edit", P.start), w.rule("Edit", P.topic_intel)])
    ids = {i.strip() for i in a.ids.split(",") if i.strip()}

    jobs, v2_rows = [], []
    for r in q.by_status("written", path=P.queue):
        if r["topic"] != tdir or (ids and r["id"] not in ids):
            continue
        ang = w.parse_angle(r["angle"])
        kind = ang.get("kind") or ""
        if kind not in w.HANDLED:
            v2_rows.append(r["id"])
            continue
        if kind == "tool":
            page = P.tools / ang["slug"] / "tool.md"
            files = [page, P.tools / ang["slug"] / "tool.html"]
        elif kind == "dataset":
            page = P.datasets / f"{ang['slug']}.md"
            files = [page, P.datasets / f"{ang['slug']}.csv"]
        elif kind == "start_here":
            page = P.start / f"{ang['slug']}.md"
            files = [page]
        else:
            page = w.find_article(r["id"], P.articles)
            if not page and ang.get("slug"):
                page = P.articles / tdir / f"{ang['slug']}.md"
            files = [page] if page else []
        if not page or not page.exists():
            log(f"{r['id']}: status written but its page is missing; skipped")
            continue
        slug = page.parent.name if kind == "tool" else page.stem
        chk = P.checks / f"{slug}.json"
        cur = load(chk)
        if cur.get("verdict") == "pass" and not a.recheck and not ids:
            continue
        prev = cur if cur.get("verdict") == "fix" else load(chk.with_name(f"{slug}.prev.json"))
        rnd = 2 if prev.get("verdict") == "fix" else 1
        previous = ("\n" + "\n".join(f"  - {f}" for f in prev["fixes"])) if prev.get("fixes") else "none (first check)"
        rule = ("This is the first check: a fix verdict sends the page back to the writer for one revision." if rnd == 1 else
                "This is the second check, after the only revision allowed. The pipeline turns a second fix verdict into reject, so decide pass or "
                "reject; check first that the previous fixes were applied.")
        page_files = " and ".join(w.rel(f) for f in files)
        prompt = sessions.fill(template, today=TODAY, page_files=page_files, slug=slug, id=r["id"], kind=kind, topic_dir=tdir, brief_path=w.rel(P.brief),
                               check_path=w.rel(chk), round="first check" if rnd == 1 else "second check, after the one revision allowed",
                               previous=previous, round_rule=rule, question=r["question"], primary_query=r["primary_query"])
        sessions.save_prompt("check", r["id"], prompt)

        def prepare(rid=r["id"], chk=chk):
            q.set_status(rid, "reviewing", P.queue)
            if chk.exists():
                chk.replace(chk.with_name(f"{chk.stem}.prev.json"))

        jobs.append({"id": r["id"], "prompt": prompt, "expect": [str(chk)], "prepare": prepare, "check": (lambda c=chk, rid=r["id"]: (lambda: check_problems(load(c), rid)))(),
                     "row": r, "chk": chk, "slug": slug, "kind": kind, "round": rnd, "page": page})
        if a.limit and len(jobs) >= a.limit:
            break
    if v2_rows:
        log(f"{len(v2_rows)} written row(s) of {tdir} without a plan angle are v2 drafts, not this step's (scripts/v2/review.sh reviews them, "
            f"or requeue them as v3 rewrites once published): {', '.join(v2_rows[:12])}{' ...' if len(v2_rows) > 12 else ''}")
    if not jobs:
        log(f"nothing to do: no written plan page of {tdir} without a passing check")
        return 0

    def undo_rewrite(job, rid):
        side_path = w.rewrite_sidecar(P.backups, tdir, job["slug"])
        if job["kind"] in w.ARTICLE_KINDS and side_path.exists():
            side = json.loads(side_path.read_text(encoding="utf-8"))
            if side.get("new_id") == rid and not side.get("restored"):
                w.restore_rewrite(side, P.queue, log)

    def on_done(job, ok, r, problems):
        rid, slug = job["id"], job["slug"]
        if not ok:
            q.set_status(rid, "written", P.queue)
            log(f"[{rid}] check did not finish ({'; '.join(problems)[:300]}); the row stays written for the next run")
            return
        d = load(job["chk"])
        verdict = d["verdict"]
        n = len(d.get("checked") or [])
        fixed = sum(1 for c in d.get("checked") or [] if c.get("status") == "fixed")
        unv = sum(1 for c in d.get("checked") or [] if c.get("status") == "unverifiable")
        briefs = len(d.get("brief_updates") or [])
        (P.reviews / f"{slug}.json").write_text(json.dumps(review_from_check(d, slug, rid, job["row"]["primary_query"]), indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
        if verdict == "pass":
            q.set_status(rid, "written", P.queue)
            if job["kind"] in PUBLISH_HERE:
                q.set_status(rid, "published", P.queue)
                log(f"[{rid}] PASS {job['kind']} {slug} ({n} facts, {fixed} fixed, {unv} unverifiable, {briefs} brief updates) -> published (no article lint applies; the renderer takes it from {w.rel(job['page'].parent)}/)")
            else:
                log(f"[{rid}] PASS ({n} facts, {fixed} fixed in place, {unv} unverifiable, {briefs} brief updates); publish.sh will take it")
        elif verdict == "fix" and job["round"] >= 2:
            q.set_status(rid, "rejected", P.queue)
            log(f"[{rid}] second fix verdict -> rejected ({len(d.get('fixes') or [])} fixes still open)")
            undo_rewrite(job, rid)
        elif verdict == "fix":
            q.set_status(rid, "fix", P.queue)
            log(f"[{rid}] FIX ({len(d.get('fixes') or [])} fixes the checker could not apply, {fixed} fixed in place); write.sh --fix runs the one revision")
        else:
            q.set_status(rid, "rejected", P.queue)
            why = d.get("core_answer") or (d.get("fixes") or [""])[0]
            log(f"[{rid}] REJECT: core answer {why!r}; {n} facts, {unv} unverifiable")
            undo_rewrite(job, rid)

    log(f"{topic['title']} ({tdir}): {len(jobs)} check session(s) with {a.model}, {a.workers} workers; brief {w.rel(P.brief)}; log {w.rel(log_path)}")
    st = sessions.run_jobs(jobs, workers=a.workers, label="check", model=a.model, max_turns=a.max_turns, allowed_tools=check_tools, timeout_s=a.timeout, log=log, on_done=on_done)
    counts: dict[str, int] = {}
    for r in q.read(P.queue):
        if r["topic"] == tdir:
            counts[r["status"]] = counts.get(r["status"], 0) + 1
    log(f"check done for {tdir}: {st['ok']} checked, {st['failed']} failed; {st['sessions']} sessions; {st['pauses']} pause(s); topic queue: {counts}; next: bash scripts/v2/publish.sh")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
