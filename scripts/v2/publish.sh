#!/usr/bin/env bash
# Step 4 of docs/v2/spec.md: lint and publish. Code checks (scripts/v2/lint.py) over every article whose review verdict is pass
# and whose row is not yet published; a clean article's row becomes published, a failing one is printed and stays unpublished.
# Then scripts/v2/render_site.py renders build/site/ and scripts/deploy_netlify.sh deploys, every N newly published articles and
# once more at the end. Log: build/runs/v2/publish-<timestamp>.log. No claude sessions in this step.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
PY="$ROOT/worker/.venv/bin/python"

usage() {
  cat <<'EOF'
usage: scripts/v2/publish.sh [--deploy-every 10] [--no-deploy] [--render]

Lint (per article, all must pass): frontmatter complete, title <= 60 and meta 120..155 characters, no em dash, no banned phrase
(navigating, it's important to note, delve, vibrant, journey, seamless, robust, leverage, unlock, dive into, in today's),
internal links resolve, every source URL returns 200 (HEAD then GET, 10 s, cached), no near-duplicate of a published article
(title + primary query token Jaccard >= 0.8), no run of more than 25 words copied from a cited page.
  --deploy-every N   render and deploy after every N newly published articles (default 10; the rest at the end)
  --no-deploy        render only, skip scripts/deploy_netlify.sh
  --render           render (and deploy) even when nothing new was published
Lint one file by hand: worker/.venv/bin/python scripts/v2/lint.py content/articles/<topic>/<slug>.md
EOF
}
for a in "$@"; do case "$a" in -h|--help) usage; exit 0;; esac; done
cd "$ROOT"
exec "$PY" - "$@" <<'PY'
import argparse
import json
import shutil
import subprocess
import sys

sys.path.insert(0, "scripts/v2")
import lint
from lib import queue as q, sessions

ap = argparse.ArgumentParser(prog="publish.sh", add_help=False)
ap.add_argument("--deploy-every", type=int, default=10)
ap.add_argument("--no-deploy", action="store_true")
ap.add_argument("--render", action="store_true")
a = ap.parse_args()

REPO, PY = sessions.REPO, sys.executable
REVIEWS = REPO / "content/reviews"
log, _ = sessions.open_log("publish")
sessions.clear_stop(log)
rel = lambda p: str(p.relative_to(REPO))


def run(cmd, timeout):
    p = subprocess.run(cmd, cwd=REPO, capture_output=True, text=True, timeout=timeout)
    for line in (p.stdout + p.stderr).strip().splitlines()[-4:]:
        log(f"    {line[:200]}")
    return p.returncode


def published_articles():
    return [a for a in (q.article_for(r["id"]) for r in q.by_status("published")) if a]


def render_and_deploy():
    rs = REPO / "scripts/v2/render_site.py"
    if not rs.exists():
        log("render skipped: scripts/v2/render_site.py does not exist yet (another agent builds it); the rows are published in the queue "
            "and will render on the next publish.sh (use --render)")
        return
    # the renderer takes every file under its articles dir, so it gets a copy of the published rows' articles only
    stage = REPO / "build/publish/articles"
    if stage.exists():
        shutil.rmtree(stage)
    arts = published_articles()
    for p in arts:
        (stage / p.parent.name).mkdir(parents=True, exist_ok=True)
        shutil.copy2(p, stage / p.parent.name / p.name)
    log(f"rendering build/site/ with scripts/v2/render_site.py ({len(arts)} published articles)")
    if run([PY, str(rs), "--articles-dir", str(stage)], 1800):
        log("render failed; deploy skipped")
        return
    if a.no_deploy:
        log("deploy skipped (--no-deploy)")
        return
    log("deploying with scripts/deploy_netlify.sh")
    log("deployed" if run(["bash", "scripts/deploy_netlify.sh"], 1200) == 0 else "deploy failed")


cands = []
for r in q.by_status("written"):
    art = q.article_for(r["id"])
    if not art or not (REVIEWS / f"{art.stem}.json").exists():
        continue
    try:
        verdict = json.loads((REVIEWS / f"{art.stem}.json").read_text(encoding="utf-8")).get("verdict")
    except ValueError:
        verdict = None
    if verdict == "pass":
        cands.append((r, art))
log(f"{len(cands)} article(s) with a passing review to lint")
web = lint.Web(REPO)
published = lint.published_pairs(REPO)
# an internal link must land on a page that will be live: a published article or one being published in this run
live = {f"/{a.parent.name}/{a.stem}/" for a in published_articles()} | {f"/{a.parent.name}/{a.stem}/" for _, a in cands}
new = since = 0
for r, art in cands:
    if sessions.stopped():
        log("STOP file found; stopping before the next article")
        break
    errs = lint.lint_article(art, root=REPO, web=web, published=published, live=live)
    if errs:
        log(f"FAIL {rel(art)} ({r['id']}) stays unpublished:")
        for e in errs:
            log(f"  - {e}")
        continue
    q.set_status(r["id"], "published")
    fm = q.frontmatter(art)
    published.append((r["id"], str(fm.get("title") or ""), str(fm.get("primary_query") or "")))
    new += 1
    since += 1
    log(f"PUBLISHED {r['id']} -> /{art.parent.name}/{art.stem}/")
    if a.deploy_every > 0 and since >= a.deploy_every:
        render_and_deploy()
        since = 0
if since or (a.render and not new):
    render_and_deploy()
counts = {}
for r in q.read():
    counts[r["status"]] = counts.get(r["status"], 0) + 1
log(f"newly published: {new}; failed lint: {len(cands) - new}; queue: {counts}")
PY
