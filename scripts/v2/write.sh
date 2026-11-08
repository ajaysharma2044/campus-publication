#!/usr/bin/env bash
# Step 2 of docs/v2/spec.md: research and write. One claude -p session per approved queue row (tools: Read, Grep, Glob, WebSearch,
# WebFetch, Write(content/articles/**)) writes content/articles/<topic>/<slug>.md. Before each session the image finder runs
# (scripts/v2/find_images.py, when it exists). Log: build/runs/v2/write-<timestamp>.log. Stop cleanly: scripts/v2/stop.sh.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
PY="$ROOT/worker/.venv/bin/python"

usage() {
  cat <<'EOF'
usage: scripts/v2/write.sh [--workers 4] [--limit N] [--model sonnet|opus] [--ids a,b] [--fix] [--max-turns 40] [--timeout SECONDS]

Takes every row in status approved (status -> writing while the session runs), runs the image finder for it when
scripts/v2/find_images.py exists (content/images/candidates/<id>.json), then one writer session with scripts/v2/prompts/write.md.
Afterwards the row is written when content/articles/<topic>/<slug>.md exists with complete frontmatter, else it goes back to
approved with the reason in the log. The slug comes from the primary query. The photos the writer picked in the frontmatter are
then stored by find_images.py --fetch as content/images/<slug>/<n>.webp and logged in content/images/credits.yml.
  --fix        instead take rows in status fix: one revision session per article with the review's exact fix list
               (content/reviews/<slug>.json) appended to the prompt; the row returns to written for a second review.
  --ids a,b    only these queue ids.   --limit N   at most N rows.   --model opus   for the writing model (default sonnet).
Defaults: --workers 4, --max-turns 40, --timeout 2700.
EOF
}
for a in "$@"; do case "$a" in -h|--help) usage; exit 0;; esac; done
cd "$ROOT"
exec "$PY" - "$@" <<'PY'
import argparse
import json
import os
import re
import subprocess
import sys
import threading
from datetime import date

import yaml

sys.path.insert(0, "scripts/v2")
import lint
from lib import queue as q, sessions

ap = argparse.ArgumentParser(prog="write.sh", add_help=False)
ap.add_argument("--workers", type=int, default=4)
ap.add_argument("--limit", type=int, default=0)
ap.add_argument("--model", default="sonnet")
ap.add_argument("--ids", default="")
ap.add_argument("--fix", action="store_true")
ap.add_argument("--max-turns", type=int, default=40)
ap.add_argument("--timeout", type=int, default=2700)
a = ap.parse_args()

REPO, PY = sessions.REPO, sys.executable
ARTICLES, REVIEWS = REPO / "content/articles", REPO / "content/reviews"
FIND_IMAGES = REPO / "scripts/v2/find_images.py"
step = "write-fix" if a.fix else "write"
want = "fix" if a.fix else "approved"
fetch_lock = threading.Lock()   # find_images.py --fetch rewrites content/images/credits.yml; one fetch at a time
log, _ = sessions.open_log(step)
sessions.clear_stop(log)
rel = lambda p: str(p.relative_to(REPO)) if str(p).startswith(str(REPO)) else str(p)

rows = q.by_status(want)
if a.ids:
    ids = [i.strip() for i in a.ids.split(",") if i.strip()]
    have = {r["id"] for r in rows}
    for i in ids:
        if i not in have:
            log(f"{i}: not in status {want}; skipped")
    rows = [r for r in rows if r["id"] in ids]
if a.limit:
    rows = rows[: a.limit]
if not rows:
    log(f"nothing to do: no rows in status {want}")
    sys.exit(0)
if not (REPO / "docs/v2/exemplar.md").exists():
    log("note: docs/v2/exemplar.md is missing; writers work from docs/v2/style.md alone")
template = (REPO / "scripts/v2/prompts/write.md").read_text(encoding="utf-8")
status = {row["id"]: row["status"] for row in q.read()}
existing = []   # articles a writer may link to: every article file whose row is not rejected (a rejected article's file stays on disk)
for p in q.articles():
    fm = q.frontmatter(p)
    if status.get(str(fm.get("queue_id") or ""), "") != "rejected":
        existing.append(f"  /{p.parent.name}/{p.stem}/ | {fm.get('title') or p.stem}")
existing = "\n".join(existing) or "  (none yet)"
today = date.today().isoformat()


def unique_slug(r):
    base = slug = q.slugify(r["primary_query"] or r["question"])
    k = 2
    while (p := ARTICLES / r["topic"] / f"{slug}.md").exists() and str(q.frontmatter(p).get("queue_id")) != r["id"]:
        slug, k = f"{base}-{k}", k + 1
    return slug


def revision_text(slug):
    rev = REVIEWS / f"{slug}.json"
    if not rev.exists():
        return "The row is marked fix but no review file exists; re-check every hard fact against its source and tighten the article."
    d = json.loads(rev.read_text(encoding="utf-8"))
    lines = ["This is the one revision round. A reviewer checked the first draft. Read the current article, apply exactly these fixes, "
             "keep everything else as it is, then overwrite the file."]
    if d.get("fixes"):
        lines += ["Fixes:"] + [f"- {f}" for f in d["fixes"]]
    mism = [f for f in d.get("fact_check") or [] if f.get("status") == "mismatch"]
    if mism:
        lines += ["Fact-check mismatches:"] + [f"- {f.get('claim')} (source {f.get('source_url')}): {f.get('note')}" for f in mism]
    bt = d.get("beats_top") or {}
    if bt.get("changes"):
        lines += [f"Changes that would make the page beat the current #1 result ({bt.get('top_url')}):"] + [f"- {c}" for c in bt["changes"]]
    return "\n".join(lines)


def finder_env():
    """UNSPLASH_ACCESS_KEY and PEXELS_API_KEY from worker/.env for the image finder only; the claude sessions never see them."""
    env = dict(os.environ)
    dotenv = REPO / "worker/.env"
    if dotenv.exists():
        for line in dotenv.read_text(encoding="utf-8").splitlines():
            m = re.match(r"\s*(?:export\s+)?(UNSPLASH_ACCESS_KEY|PEXELS_API_KEY)\s*=\s*[\"']?([^\"'\s#]+)", line)
            if m:
                env.setdefault(m.group(1), m.group(2))
    return env


def prepare(r, cand, art):
    def go():
        q.set_status(r["id"], "writing")
        art.parent.mkdir(parents=True, exist_ok=True)
        if cand.exists():
            return
        if not FIND_IMAGES.exists():
            log(f"[{r['id']}] scripts/v2/find_images.py is not there yet; no image candidates")
            return
        cand.parent.mkdir(parents=True, exist_ok=True)
        queries = []   # the finder searches by subject and shortens a query that finds nothing: the short phrase first, then the question
        for text in (r["primary_query"], r["question"]):
            if text and text not in queries:
                queries += ["--query", text]
        try:
            p = subprocess.run([PY, str(FIND_IMAGES), *queries, "--out", str(cand)], cwd=REPO, env=finder_env(), capture_output=True, text=True, timeout=300)
            tail = (p.stdout + p.stderr).strip().splitlines()
            log(f"[{r['id']}] find_images exit {p.returncode}: {tail[-1][:160] if tail else ''}")
        except Exception as e:  # noqa: BLE001 - no photo candidates is not a reason to skip the article
            log(f"[{r['id']}] find_images failed: {type(e).__name__}: {str(e)[:120]}")
    return go


def place_images(art, cand, qid):
    """The writer picks candidates in the frontmatter (credit_url = the candidate's page_url) but has no Bash, so after the session
    find_images.py --fetch downloads them to content/images/<slug>/<n>.webp and logs them in content/images/credits.yml; the entries
    then get the stored file name and the API's license data, and an entry that could not be fetched is dropped. An entry whose file
    is already there (a revision, a photo placed by hand) is kept as it is."""
    fm, body, _, errs = lint.parse(art)
    images = fm.get("images") or []
    if errs or not isinstance(images, list) or not images or not FIND_IMAGES.exists():
        return
    norm = lambda u: str(u or "").strip().lower().replace("http://", "https://").rstrip("/")
    cands = json.loads(cand.read_text(encoding="utf-8")) if cand.exists() else []
    index = {norm(c.get(k)): i for i, c in enumerate(cands) if isinstance(c, dict) for k in ("page_url", "file_url") if c.get(k)}
    folder = REPO / "content/images" / art.stem
    keep = []   # (entry, candidate index, or None when its file is already stored)
    for im in images:
        if not isinstance(im, dict):
            continue
        if im.get("file") and (folder / str(im["file"])).is_file():
            keep.append((im, None))
        elif (i := index.get(norm(im.get("credit_url")))) is not None:
            keep.append((im, i))
        else:
            log(f"[{qid}] image {im.get('file')!r}: credit_url is not a candidate's page_url; dropped")
    picks = [i for _, i in keep if i is not None]
    placed = {}
    if picks:
        with fetch_lock:
            p = subprocess.run([PY, str(FIND_IMAGES), "--out", str(cand), "--fetch", art.stem, "--pick", ",".join(map(str, picks))],
                               cwd=REPO, env=finder_env(), capture_output=True, text=True, timeout=900)
        try:
            placed = {norm(x["credit_url"]): x for x in json.loads(p.stdout or "[]")}
        except (ValueError, KeyError, TypeError):
            placed = {}
        if p.returncode or len(placed) < len(picks):
            log(f"[{qid}] find_images fetch exit {p.returncode}: {len(placed)} of {len(picks)} stored: {(p.stderr.strip().splitlines() or [''])[-1][:160]}")
    new = []
    for im, i in keep:
        x = placed.get(norm(cands[i].get("page_url"))) if i is not None else None
        if i is not None and not x:
            log(f"[{qid}] image {im.get('file')!r}: not fetched; dropped")
            continue
        if x and im.get("file") and str(im["file"]) != x["file"]:   # a body reference like ![alt](2.webp) follows the stored name
            body = re.sub(r"\]\(\s*" + re.escape(str(im["file"])) + r"\s*\)", f"]({x['file']})", body)
        new.append({**im, "file": x["file"], "credit": x["credit"], "credit_url": x["credit_url"], "license": x["license"], "license_url": x["license_url"]} if x else im)
    if new != images:
        fm["images"] = new
        art.write_text("---\n" + yaml.safe_dump(fm, sort_keys=False, allow_unicode=True, width=10000) + "---\n" + body, encoding="utf-8")
    log(f"[{qid}] images: {len(new)} under content/images/{art.stem}/")


def check(art, qid, cand):
    def go():
        fm = q.frontmatter(art)
        miss = lint.missing_keys(fm)
        if fm and str(fm.get("queue_id", "")) != qid:
            miss.append(f"queue_id is {fm.get('queue_id')!r}, expected {qid}")
        if miss:
            return [f"frontmatter incomplete: {'; '.join(miss)}"]
        try:
            place_images(art, cand, qid)
        except Exception as e:  # noqa: BLE001 - photos are optional; the article stands without them
            log(f"[{qid}] images not placed: {type(e).__name__}: {str(e)[:160]}")
        return []
    return go


def on_done(job, ok, r, problems):
    if ok:
        q.set_status(job["id"], "written")
        log(f"[{job['id']}] written: {rel(job['article'])}")
    else:
        q.set_status(job["id"], want)
        log(f"[{job['id']}] back to {want}: {'; '.join(problems)[:300]}")


jobs = []
for r in rows:
    if a.fix:
        art = q.article_for(r["id"])
        if not art:
            log(f"{r['id']}: status fix but no article carries this queue_id; skipped")
            continue
    else:
        art = ARTICLES / r["topic"] / f"{unique_slug(r)}.md"
    cand = REPO / "content/images/candidates" / f"{r['id']}.json"
    prompt = sessions.fill(template, date=today, id=r["id"], question=r["question"], primary_query=r["primary_query"], topic=r["topic"],
                           verdict=r["verdict"] or "unknown", angle=r["angle"] or "(none given)", top_results=r["top_results"] or "(none recorded)",
                           demand_evidence=r["demand_evidence"] or "(none recorded)", article_path=rel(art), candidates_path=rel(cand),
                           revision=revision_text(art.stem) if a.fix else "None: this is the first draft.", existing_articles=existing)
    sessions.save_prompt(step, r["id"], prompt)
    jobs.append({"id": r["id"], "prompt": prompt, "expect": [str(art)], "article": art, "prepare": prepare(r, cand, art), "check": check(art, r["id"], cand)})

log(f"{len(jobs)} article session(s) with {a.model}, {a.workers} workers")
stats = sessions.run_jobs(jobs, workers=a.workers, label=step, model=a.model, max_turns=a.max_turns,
                          allowed_tools="Read,Grep,Glob,WebSearch,WebFetch,Write(content/articles/**)", timeout_s=a.timeout, log=log, on_done=on_done)
log(f"written this run: {stats['ok']}; back to {want}: {stats['failed']}; next: scripts/v2/review.sh")
PY
