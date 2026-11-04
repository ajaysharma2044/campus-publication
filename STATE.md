# STATE

Last updated: 2026-11-04 (session 2, in-session execution mode). Update after every completed task.

## Session 2 summary (2026-11-04)
- Execution approach changed: the language-judgment roles run inside the Claude Code session (no worker model credential needed); deterministic code unchanged.
- **Cornell transfer-housing guide**: discovered 8 questions, scored the cluster (priority 54, decision hold because E=2), stored 17 snippet-attributed claims as `estimate`, drafted, edited and checked the article (0 deterministic findings, rubric 22/24 with attribution 2), gate **failed** on `unsupported_critical_claim`, page **held**, rendered to `build/preview/schools/cornell-university/housing/transfer-housing/`. Report: `docs/research/cornell-transfer-housing-run.md`; evidence: `docs/research/cornell-transfer-housing-evidence.md`.
- **Registry**: 6,072 real institutions imported from an IPEDS HD2024 mirror on GitHub (`data/ipeds/README.md`), all `pending_verification`; Cornell row matched (Ithaca, NY, private nonprofit); disambiguation separates Cornell University / Cornell College / Weill.
- **Hub pages from DB**: `python -m campus_worker.render.from_db` renders /schools/, the Cornell hub and topic hubs with honest counts (0 verified, 1 held).
- **Exact blocker for publishing anything about Cornell**: `scl.cornell.edu`, `faq.enrollment.cornell.edu`, `admissions.cornell.edu` (and `nces.ed.gov` for identity verification) must be added under Allowed domains in the environment's Network access settings; every path (curl and the session fetch tool) fails DNS for them. Web search works and was used for discovery only.
- Tests: 130 passing after the gate change (critical claims with category `estimate` now block).

## Environment inventory (observed 2026-11-02)
- Container: Linux, Python 3.13, Node 22, PHP 8.3 (pdo_sqlite, mysqli, curl, gd, mbstring, zip), PostgreSQL 16 server (local, started), git, gh, Playwright 1.63 + Chromium. No docker daemon. No wp-cli.
- Network: PyPI, npm and github.com (git) reachable. **Blocked (403 by proxy policy):** cornell.edu, nces.ed.gov, ed.gov, wordpress.org, developers.google.com, cdnjs, api.data.gov, GitHub API. Live source collection and IPEDS download are impossible from this container; collectors run on labeled fixtures.
- Credentials: no `ANTHROPIC_API_KEY` (worker model calls would be API-billed; adapter reports **unconnected**). No WordPress host, AdSense, Search Console, keyword-provider or Reddit credentials. `GH_TOKEN` unused; no remote repository was requested.
- Repository: `/home/user/campus-publication`, local git on `main`, 8 commits, no remote.

## Evidence states
| Component | implemented | tested locally | connected to real service | deployed | scheduled |
|-----------|-------------|----------------|---------------------------|----------|-----------|
| Control files (SPEC/BACKLOG/STATE/CLAUDE) | yes | n/a | n/a | n/a | n/a |
| PostgreSQL schema (2 migrations, 34 tables), migration runner, down scripts | yes | yes | local cluster only | no | no |
| Institution registry (IPEDS-layout import, aliases, systems vs campuses, disambiguation) | yes | yes (synthetic CSV) | no — real IPEDS file not downloadable here | no | no |
| School configs (Cornell pending_verification; Riverbend CC synthetic) | yes | yes | no | no | no |
| Source permissions (Reddit disabled), safe fetcher (SSRF/redirect/size/rate/circuit) | yes | yes (mock transport) | no live fetch possible | no | no |
| HTML + PDF collectors, change detection, retention | yes | yes (fixtures) | no | no | no |
| Claims, conflicts, supersession, stale/source-gone, propagation, regression guard | yes | yes | n/a | no | no |
| Discovery (normalize/dedupe/cluster/hypotheses), demand/SERP import, scoring + decision | yes | yes | keyword/SERP providers **unconnected** | no | no |
| JSON contracts (12 roles) + validator; briefs; deterministic editorial checks; rubric gates; versioned drafts | yes | yes | n/a | no | no |
| Model router (role aliases, budget reservation, repair/escalation ceiling, fallback, run recording) | yes | yes with **FixtureProvider only** | **unconnected** (no key) — real Sonnet/Opus routing **untested** | no | no |
| Budget ledger ($3/day, $60/month, headroom, unpriced hold) | yes | yes | n/a | no | no |
| Job queue (lease/reclaim/retry/hold/dead-letter/idempotency/delegation depth) | yes | yes | n/a | no | no |
| Design system, 18 templates/states, OFL fonts self-hosted, preview, screenshot QA at 5 widths, contrast checks | yes | yes (90 renders, 0 problems) | n/a | no | no |
| Comparison + total-cost calculator (Python + mirrored JS) | yes | yes | n/a | no | no |
| Campus Core WP plugin + Campus Editorial theme | yes | yes — **real local WordPress on SQLite**: idempotent REST upsert, hash no-op, sanitised HTML, canonical path routing, 301 redirects, sitemap, staging noindex, ads.txt | local only | no | no |
| CMS publisher (gated versions only, quota, redirects) | yes | yes (in-memory CMS; adapter verified against local WP) | managed WP **unconnected** | no | no |
| SEO (URL policy, sitemap, robots, structured-data validator, link check, titles) | yes | yes | Search Console **unconnected** | no | no |
| Analytics contracts (dictionary, PII rejection, dedupe, bots, aggregates, retention) | yes | yes | no analytics endpoint deployed | no | no |
| Ads adapter (AdSense, disabled; one loader; consent; approved placements; staging guard) | yes | yes (no ad code emitted anywhere) | **disabled / no account** | no | no |
| Revenue model (separate denominators) + report import; experiments registry | yes | yes | no reports exist | no | no |
| Operational dashboard (+ /health, /status.json) | yes | yes (served locally) | local only | no | no |
| Scheduler tick (lock, reclaim, budget pause, exit codes, heartbeat), daily plan with exploration share | yes | yes | n/a | no | **no external scheduler** |
| Continuation runner (bounded, flock, stop reason) | yes | yes (3 dependent jobs, 1 retry, stopped on no work) | n/a | no | no |
| Backup + restore proof | yes | yes (pg_dump → scratch DB restore verified) | local only | no | no |
| Calibration exercises 1–4 | yes | yes (docs/editorial/calibration.md, scripted model) | **not run with a real model** | no | no |
| Skill pack (coordinator + 12 references) | yes (files in repo) | n/a | **not installed** in any skill registry | n/a | n/a |
| Usage-optimization evaluation | baseline doc only | — | no optimizer installed | — | — |

Test suite: **130 passed** (`cd worker && pytest -q`), plus `scripts/check_css.py`, `scripts/check_tools_js.js`, `scripts/qa_screens.js` (90/90 clean), `scripts/restore_test.sh`.

## What is live / automatic
Nothing is live. Nothing runs automatically outside this container. The local PostgreSQL, local WordPress (SQLite) and dashboard are development instances that stop with the container.

## Blockers (owner action; each blocks only its integration)
OD1 Anthropic API key for the worker (API-billed) · OD2 managed WordPress + application password · OD3 managed PostgreSQL · OD4 domain/brand (masthead is a placeholder) · OD5 AdSense approval + publisher id · OD6 Search Console property + service account · OD7 keyword/SERP provider or exports · OD8 Reddit Data API commercial authorization (stays disabled) · OD9 egress to cornell.edu / nces.ed.gov (or owner-supplied IPEDS file and page snapshots) · OD10 external scheduler for continuous operation.

## Assumptions recorded
- Masthead "The Campus Ledger" is a working title, editable in `CAMPUS_PUBLICATION_NAME` / WP site name; not a brand decision.
- Local PostgreSQL role `campus` / `campus_local_dev` is development-only.
- Cornell identity (UNITID 190415) entered by hand; `identity_status = pending_verification` until matched to a downloaded IPEDS HD release. No Cornell facts exist in the database; nothing about Cornell is published.
- Model price table in `budget.MODEL_PRICE_PER_MTOK_MINOR` is an upper-bound placeholder for reservations; replace from the provider's current price list before connecting a key.
- Thresholds (priority 65, E/G ≥ 3, rubric 20/24, similarity 0.82) are unvalidated starting policy.

## Next actions (in order)
1. Owner supplies OD1 → run `python -m campus_worker.calibration` path with `AnthropicProvider` (one real Sonnet worker, one real Opus review), compare against the scripted report, record resolved model ids.
2. Owner supplies OD9 or files → register Cornell housing sources (`scl.cornell.edu`, `living.cornell.edu`), run `collect_source` → `extract_claims`, verify Cornell identity against the IPEDS release, then exercises 1–3 on real records (still staging, draft status).
3. Owner supplies OD2/OD3 → deploy plugin/theme, point the worker at managed PostgreSQL and WordPress, publish as drafts.
4. OD10 → hourly `run-once`, daily `plan_daily`, weekly diagnosis; enable bounded auto-publish (1 page/day, 5 updates/day) for entity_profile and comparison templates only after the three calibration outputs pass with a real model.
5. OD5/OD6/OD7 as they arrive; each flips one adapter from unconnected to connected without template changes.
