# Repo map (what is here and why), 2026-11-08

Everything a v3 run touches lives at the top level. v1 is under `archive/v1/` for reference only; nothing runs from it.

| Path | What it is |
|---|---|
| `CLAUDE.md` | Routing file for Claude Code: specs, what exists, rules, how to run. |
| `STATE.md` | Current status, overwritten, under 60 lines: running, counts, decisions, open questions. |
| `docs/v3/spec.md` | The owner's v3 spec (current). `docs/v3/best/`, `docs/v3/worst/`: the best-pages library. `docs/v3/repo-map.md`: this file. |
| `docs/v2/spec.md`, `docs/v2/style.md`, `docs/v2/exemplar.md`, `docs/v2/photo-permission-email.md` | The v2 spec (files, lint, render, images, monetization, deploy still apply), the style guide, the quality-bar article, the photo permission template. |
| `scripts/v3/research.sh`, `research.py`, `topics.yml`, `prompts/` | v3 step 1: five research lanes per topic into `intel/<topic>/raw/<lane>.md`; topic list and scopes; lane prompts. |
| `scripts/v2/find_demand.sh` | Demand step: real questions and what ranks, into `queue/queue.csv`. |
| `scripts/v2/write.sh`, `review.sh`, `publish.sh`, `run_continuous.sh`, `stop.sh` | v2 write, review, lint-and-publish steps and the (stopped) v2 loop; `stop.sh` creates `.run/STOP` for any step. |
| `scripts/v2/lint.py` | Code checks before publish (frontmatter, lengths, banned words, links, sources, copying, duplicates). |
| `scripts/v2/render_site.py` | Markdown articles and pages to `build/site/` with the templates under `worker/campus_worker/render/`. |
| `scripts/v2/find_images.py` | Licensed photos (Wikimedia Commons, Openverse, keyed stock sites), WebP conversion, `content/images/credits.yml`. |
| `scripts/v2/export_corpus.py` | One-time export of crawled page text from the old database into `corpus/`. |
| `scripts/v2/lib/sessions.py`, `lib/queue.py` | Parallel `claude -p` sessions with usage-limit pause and STOP; the queue CSV library (statuses, ids, merge, dedupe). |
| `scripts/v2/prompts/` | Demand, write and review prompts. |
| `scripts/deploy_netlify.sh`, `netlify.toml`, `package.json` | Deploy `build/site/` to the Netlify preview; `scripts/qa_screens.js` screenshots pages at phone and desktop widths. |
| `content/articles/<topic>/<slug>.md` | Articles (Markdown with frontmatter). `content/reviews/`: review verdicts. `content/pages/`: about, privacy, contact, editorial policy, corrections. `content/images/`: credits ledger, candidates, stored photos, owner inbox. |
| `queue/queue.csv` | Every question: id, question, primary query, topic, evidence, verdict, angle, status. |
| `intel/<topic>/` | v3 intelligence: `raw/<lane>.md` now; `brief.md`, `readers.md`, `plan.md` when built. |
| `corpus/<host>/<path>.txt` | 2,522 crawled official pages as text, with URL, title and fetch date. |
| `reports/` | `blind-compare.md` (Ajay's comparisons), `to-read.md`, weekly and lessons notes, plan summaries for approval. |
| `config/monetization.yml` | Ads, consent, analytics, affiliates and Grow switches read by the renderer. |
| `data/questions/` | The owner's question list, read by the demand step. |
| `worker/campus_worker/render/` | Jinja templates (`templates/`, `templates/v2/`), static CSS and fonts, `figures.py` (SVG cost tables, timelines, step diagrams). `worker/.venv` holds the Python dependencies; `worker/.env` the secrets. |
| `build/` | Generated: the rendered site, run logs (`build/runs/v2/`), lint caches. Not committed. |
| `archive/v1/` | The v1 pipeline, its specs, agents, tests, docs, scripts, skills, fixtures and crawl configs. Reference only. |
