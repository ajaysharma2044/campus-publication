# Bulk mode runbook (specs/bulk-mode.md)

Research once, write many: a plain Python pipeline that calls the Anthropic Message Batches API directly. Claude Code builds and
maintains it; it does not write pages one by one. Package: `worker/campus_worker/bulk/`. Every command runs from the repo root with the
worker's env sourced (`set -a; . worker/.env; set +a`); Claude never reads that file.

## Owner actions (once)
- Create an API key at console.anthropic.com, add billing, and put `ANTHROPIC_API_KEY=...` in `worker/.env`.
- Optionally `CAMPUS_API_DAILY_CAP_USD=25` (the default) in the same file. The pipeline estimates each batch before submitting, refuses
  to exceed the cap, and records actual cost from the API's usage fields.
- A second school needs its registry record verified and a `source_permissions` row for its official domain (see `data/schools/<slug>.yaml`).

## Commands
```bash
worker/.venv/bin/python -m campus_worker.bulk crawl --school cornell-university --dry-run     # sitemap discovery only, prints selected counts
```
```bash
worker/.venv/bin/python -m campus_worker.bulk crawl --school cornell-university               # D1: fetch through the safe fetcher (robots, permissions, per-host rate)
```
```bash
worker/.venv/bin/python -m campus_worker.bulk extract --school cornell-university --dry-run   # D2 estimate; without --dry-run: one Batches request per page
```
```bash
worker/.venv/bin/python -m campus_worker.bulk dossier --school cornell-university             # D3-D6: docs/dossiers/<school>/ + question map + ranking
```
```bash
worker/.venv/bin/python -m campus_worker.bulk run --school cornell-university --limit 20 --dry-run   # B1: plan, gather, cost estimate, no API call
```
```bash
worker/.venv/bin/python -m campus_worker.bulk run --school cornell-university --limit 20 --deploy    # B2: write → check → verify → publish → Netlify
```
```bash
worker/.venv/bin/python -m campus_worker.bulk run --school cornell-university --limit 500 --chunk 250 --deploy --run-id bulk-500   # B3
```
```bash
worker/.venv/bin/python -m campus_worker.bulk run --school cornell-university --run-id bulk-500 --resume --deploy   # resume after an interruption
```
```bash
worker/.venv/bin/python -m campus_worker.bulk status --school cornell-university
```
Fallback without a key: `scripts/parallel_headless.sh 4 --pages <bulk plan --json output>` shards the page list across `claude -p` workers
(each writes only to its own folder under `build/bulk/headless/<run>/`), then one serial merge; `--dry-run` exercises it without the CLI.

## What each stage guarantees
- Crawl: sitemaps (robots `Sitemap:` lines or `/sitemap.xml`, index recursion, gzip) and a shallow link walk for hosts without one; one
  worker per host so the permitted rate is exact; text stored by content hash in `fetch_snapshots` with URL and date.
- Extract: the model proposes typed claims with a quote; code keeps a claim only when the quote is verbatim on the page (whitespace- and
  quote-insensitive), the field is in the taxonomy and the value parses; `claims.store_claim` dedupes across pages.
- Dossier: `docs/dossiers/<school>/` (identity, entities, claims, processes, deadlines, costs, policies, contacts, town, conflicts, gaps,
  crawl, stats, `summary.md`); the database stays the source of truth.
- Questions: generated from the facts that exist (so each has an answer) plus `data/questions/*.yaml` and the observed intent clusters,
  deduped by answer key and audience into `bulk_questions`.
- Rank: incumbent class from cached search observations only (14 days, the cluster's variants; no new search in bulk mode). Observed
  rows with an empty result list stay `unscanned` and rank after the questions with evidence. Order: forum-only / outdated / none, then
  weak, then unscanned, then strong incumbents; underserved audiences first within a tier; a one-line win note per question.
- Plan / gather: paths `/schools/<school>/<topic>/<slug>/` (towns under `/towns/`), existing paths skipped unless their sources changed;
  facts with quotes from the dossier only, never the web; internal link targets from published and planned pages.
- Write: one request per page, the shared prefix cached; structured JSON validated against a schema.
- Check (code): every number, date and dollar amount in the prose must appear in a cited quote that is verbatim on the source page;
  title ≤ 60 with the primary query's words, meta 120-155, one H1, answer ≤ 50 words, 2+ internal links (added when missing), no filler
  or internal terms, overlap < 60% with any existing page. Failing claims and their sentences are removed; a page whose answer does not
  survive is skipped with the reason.
- Verify: one cheaper request per page; unsupported claims and their sentences are removed; the page is rendered to `build/site/` with
  a `bulk` gate record (checks + verdict counts in `gate_findings`) and Netlify is deployed once per run.
- Resume: every stage transition is committed per page; `--resume` continues from `bulk_pages.stage`.
- Report: `build/runs/bulk/<run_id>.json` with pages published, skipped (with reasons), failed, minutes, cost and cost per published page.

## Figures and photos
Pages get deterministic figures built only from their fact table (`render/figures.py`: cost chart, deadline timeline, steps diagram) and
a photo slot filled only from `content/images/credits.yml` with rights recorded (`render/photos.py`); never a placeholder on a real page.
