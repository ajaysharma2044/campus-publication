# Footnote Daily (campus-publication), v3

Research-first guides for students, parents and alumni of Cornell University and Ithaca. Owner specs: `docs/v3/spec.md` (2026-11-08, wins where it conflicts) over `docs/v2/spec.md` (files, lint, render, images, monetization, deploy). Style: `docs/v2/style.md`. Quality bar: `docs/v2/exemplar.md`. Status: `STATE.md`, overwritten, under 60 lines. This file and STATE.md describe only what exists and runs.

## What exists today
- Research sprint (v3 step 1): `scripts/v3/research.sh <topic> [--lanes A,B,C,D,E] [--workers N] [--model sonnet|opus] [--deepen]` writes dated, sourced raw notes to `intel/<topic>/raw/<lane>.md` (official, market, voice, competition, analysis). Topics and scopes: `scripts/v3/topics.yml`. Done so far: getting-around (all lanes), money (all lanes), dining (A to C), off-campus housing (in progress).
- v2 steps still in use: `scripts/v2/find_demand.sh` (queue rows), `write.sh`, `review.sh`, `publish.sh` (lint, render, Netlify deploy), `lint.py`, `render_site.py`, `find_images.py` (licensed photos and the credits ledger), `run_continuous.sh` (stopped; superseded by v3 once its steps exist), `export_corpus.py`.
- Content and data: `content/articles/<topic>/<slug>.md`, `content/reviews/`, `content/images/` (`credits.yml`, `inbox/`), `queue/queue.csv`, `corpus/<host>/<path>.txt` (2,522 crawled pages), `intel/`, `reports/`, `config/monetization.yml`.
- Kept worker code: `worker/campus_worker/render/` (templates, static assets, figures) and the modules the scripts import; everything else from v1 is under `archive/v1/`.

## Not built yet (v3 steps 2 to 7)
`brief.sh`, `readers.sh`, `plan.sh`, `write.sh`, `check.sh` under `scripts/v3/`, the v3 publish requirements in `lint.py`, and the v3 render blocks. Until they land, no v3 article is written.

## Rules
- Every hard fact links inline to its source; student experience is paraphrased and attributed; never invent facts, numbers, quotes or people.
- Respect robots and site terms; no logins; no bulk scraping; images only with a reuse license or written permission, credited.
- Quality fixes go in prompts, the style guide, the exemplar and the briefs, never in code rules. No new gates, scores or databases. No scheduled jobs.
- Secrets live only in `worker/.env`, which Claude never reads (the one remaining hook rule). Commit per step; never force-push.

## Running
- Python: `worker/.venv` (pyyaml, markdown, jinja2, httpx, Pillow, psycopg). Tests: `cd worker && .venv/bin/python -m pytest -q`.
- Stop any step cleanly: `scripts/v2/stop.sh`. Deploy: `bash scripts/deploy_netlify.sh`. Logs: `build/runs/v2/`.
