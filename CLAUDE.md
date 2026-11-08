# Footnote Daily (campus-publication), v2

Research-first guides for students, parents and alumni of a school and its town. Cornell and Ithaca first.
Owner spec: `docs/v2/spec.md` (authoritative; it replaces the v1 specs now under `archive/v1/`). Style: `docs/v2/style.md`. Quality bar: `docs/v2/exemplar.md`. Status: `STATE.md` (overwritten, under 60 lines).

## Pipeline (files, not a database)
1. Find demand: `scripts/v2/find_demand.sh <topic>` appends rows to `queue/queue.csv` (verdict gap, weak or owned; gap and weak become `proposed`). Ajay marks rows `approved`, or run with `--auto-approve`.
2. Research and write: `scripts/v2/write.sh --workers 4` writes `content/articles/<topic>/<slug>.md` (one `claude -p` session per approved row; web, corpus, style guide, exemplar).
3. Review: `scripts/v2/review.sh` writes `content/reviews/<slug>.json` (fact check plus beats-#1 test; pass, fix or reject; one fix round).
4. Lint and publish: `scripts/v2/publish.sh` runs the code checks, renders `build/site/` with `render/`, deploys to Netlify every 10 articles.
Stop any step cleanly with `touch .run/STOP`. Usage-limit pauses resume on their own.

## Layout
- `content/articles/`, `content/reviews/`, `content/images/` (`credits.yml`, `inbox/`), `queue/queue.csv`, `corpus/<host>/<path>.txt` (2,522 crawled pages; `scripts/v2/export_corpus.py`).
- `scripts/v2/` (bash and python; prompts in `scripts/v2/prompts/`), `config/monetization.yml`, `docs/v2/`.
- `worker/campus_worker/`: kept infrastructure only: `fetcher.py`, `permissions.py`, `crawl.py` (sitemap crawler), `collectors/`, `db.py`, `config.py`, `render/` (templates, static assets, figures).
- `archive/v1/`: the v1 pipeline (specs, agents, bulk mode, gates, WordPress, old STATE and BACKLOG). Reference only; nothing runs from it.

## Rules
- Every hard fact links inline to the official source it came from. Student experience is paraphrased, attributed and linked. Never invent quotes, people, ratings or numbers; never copy more than a short phrase.
- Respect robots and site terms; never log in; read a page the way a person would. Images only with a reuse license or written permission, credited.
- Quality problems are fixed in the prompts, the style guide and the exemplar, never with code rules. No new gates, agents, scores or databases.
- Secrets live only in `worker/.env`, which Claude never reads (the one remaining hook rule). Commit per milestone; never force-push.

## Running
- Python: `worker/.venv` (`psycopg`, `httpx`, `jinja2`, `markdown`, `pyyaml`). Tests: `cd worker && .venv/bin/python -m pytest -q`.
- Deploy: `bash scripts/deploy_netlify.sh` (site `campus-ledger-preview`). Crawl more official pages: `worker/.venv/bin/python -m campus_worker.crawl --school <slug>`.
