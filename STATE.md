# STATE

Last updated: 2026-11-06 (session 3, local Mac run; specs/continuous-local-run.md v2.5). Update after every completed task.

## Session 3: continuous local run (2026-11-06, branch `continuous-local-run`)
Spec: `specs/continuous-local-run.md` v2.5 (owner-approved). Plan and AT mapping: `docs/ops/continuous-local-run-plan.md`.

### M1 Mac parity — done (AT29, AT31, AT32 against the local DB; AT32 hosted re-run pending DATABASE_URL)
- Toolchain on the Mac (Apple Silicon, macOS 26.6): Homebrew 7.0.12; Python 3.13.18 in `worker/.venv` (`pip install -e "worker[dev]"`); PostgreSQL 16.15 (`brew services start postgresql@16`, role `campus`, DBs `campus_research_test` for pytest and `campus_research_local` for dev smoke checks); PHP 8.3.36 (`/opt/homebrew/opt/php@8.3`, pdo_sqlite/mbstring/curl/gd/zip present); Node 22.23.4; Playwright chromium-1248; git 2.50.1; gh 2.103.3; Claude Code CLI 2.1.319 at `~/.local/bin/claude` (native installer, user-space).
- `pyproject.toml` gained runtime deps the cloud container had installed ad hoc but never declared: markdown, nh3, starlette, uvicorn; dev: pypdf.
- Tests: **130 passed** on the Mac against `TEST_DATABASE_URL` (local). Never the hosted DB.
- Local WordPress staging: `wp-local/` cloned, `scripts/wp_local.sh setup` + new `install` subcommand (stores the application password in `worker/.env` without printing it), served on 127.0.0.1:8089; `cli status` reports the CMS adapter **connected**; `scripts/wp_roundtrip.py` proves the hash no-op (second upsert created=False changed=False, same post id).
- Backups: `scripts/backup.sh` + `scripts/restore_test.sh` pass on macOS (checksums no longer include SHA256SUMS itself; `shasum -a 256` fallback; no `su postgres`).
- Scripts ported from Linux-only tools: BSD-safe `sed -i`, `mkdir` lock instead of `flock` (absent on macOS).
- Current blockers: `DATABASE_URL` not yet in `worker/.env` (hosted Postgres 16); `claude auth login` not done (CLI is separate from the desktop app login).

### M2 doctor + rebuild — done locally (AT1 partial, AT28 local proof; hosted AT2/AT28/AT32 pending DATABASE_URL)
- `scripts/doctor.sh`: PASS/FAIL with versions for every R32 item, DB reachability, migrations, git push, Cornell/NCES hosts, claude CLI + login + workspace trust, agent files, skill symlink, settings.json.
- `scripts/rebuild_from_repo.sh` → `campus_worker.rebuild`: migrate → seed → SHA256-verified IPEDS import → guarded session-2 replay (8 questions, 17 estimate claims, 1 held version). Run twice on a fresh local DB: identical counts (6,072 pending_verification + 1 labeled synthetic fixture; Cornell disambiguation = 3). Replayed ids: `docs/research/rebuild-id-map.json`; the session-2 report is untouched.

### M3 project skill + settings + hooks — done (AT17 by 12 tests; AT30 live listing pending CLI login)
- `.claude/skills/national-college-publishing` → symlink to `skills/national-college-publishing/`; `.claude/settings.json` (deny `.env` reads, force-push, sudo/brew/pip; allowlist for the loop's commands; PreToolUse hook); `.claude/hooks/guard.sh` + `guard.py` (blocks SPEC/specs, gate constants, live-ramp default, settings.json, unlisted skills; Bash write-ish commands too); `docs/ops/skill-evaluations.md` seeded with the in-repo baseline; CLAUDE.md "Local run mode" (47 lines).
- Workspace trust flag set for this repo in `~/.claude.json` (the CLI ignores project settings otherwise).

### M4 execution mode + unthrottled production + live ramp — done (AT8, AT9 by tests)
- `CAMPUS_EXECUTION_MODE=session|api` (default session): `budget.status(..., execution_mode)` never pauses in session mode; `budget.record_session_usage` writes one unpriced ledger row per iteration / dispatch. API-mode cap tests unchanged.
- Migration 0003: `pages.ready_at/niche_score/tier/local_published_at`, `ramp_state`, `live_releases`. `ramp.py` parses `CAMPUS_LIVE_RAMP` ("5x14,15"), computes the day's allowance, orders the ready queue by niche_score, holds the rate on >20% unindexed. `publisher.publish_local` (build/site + staging draft, no quota) and `publisher.release_live` (ramp). The §26 daily quota no longer applies to publishing (owner decision); `render/site.py` renders passed versions to `build/site/`.

### M5 run loop — built; fixture-proven (AT4–AT7 by 10 tests); AT3 live run pending CLI login
- `scripts/run.sh` (caffeinate, mkdir lock → exit 11, STOP file / Ctrl-C → finish iteration then stop, 3 consecutive failures → exit 1, usage limit → exit 20 with no retry, auth error → exit 30, `--max N` → exit 12, `--mode sweep` auto-switches to normal on `sweep_complete`), `scripts/stop.sh`, `scripts/iteration_prompt.md` (R4 contract; ends with a parsed `iteration_summary` JSON), `scripts/iteration_tools.txt` (fixed allowlist), `scripts/runlog.py` (R10 lines in `build/runs/<run-start>.jsonl` + session ledger entry), `scripts/fixtures/iteration_stub.sh` (ok/nowork/slow/fail/usage/auth).
- Observed `claude -p --output-format json` shape on 2.1.319: `type, subtype, is_error, num_turns, result, session_id, total_cost_usd, usage, stop_reason, api_error_status, permission_denials, ...`; "Not logged in · Please run /login" arrives as `is_error: true` with exit 1. `--max-turns` is accepted by the parser; run.sh retries once without it if the CLI ever rejects it.

### M6–M11 build status (2026-11-06, later in session 3)
- **M6 agent team**: 15 subagents in `.claude/agents/`, 3 new contracts, `agents/dispatch.py` (packet by id with the exact contract embedded, one bounded same-tier repair, ≤4 read-only in parallel, dispatch log + per-dispatch output files under `build/runs/agent-output/`). AT10 fixture test passes; AT30 live: `claude -p` lists `national-college-publishing` and loads project settings.
- **M7 skill scout**: two live opus dispatches (6 min + 1.5 min). 11 candidates, 5 source reviews (3 accept, 2 reject), 3 rejections, coverage gaps recorded in `docs/ops/skill-evaluations.md` (generated by `campus_worker.skills_scout merge`). **Benchmarks still empty**: the first reply was truncated and the second pass could not clone sources because `git clone` was not in the headless allowlist. Build-time settings change (owner-level file): added `Bash(git clone --depth 1 *)`, `Bash(git -C * log *)`, `Bash(git -C * rev-parse *)`, `Bash(npx playwright *)` to `.claude/settings.json`. A third scout pass (benchmarks only) is queued.
- **M8 demand engine**: migration 0004; 22-topic taxonomy + 15 audience topics (`docs/strategy/topic-taxonomy.md`); access modes (R35) with robots honouring Claude-agent disallows; live harvest on the hosted DB: 42 Cornell residence halls, 29 dining locations, 24 libraries, 20 city services, 5 city parks, 33 county departments, 25 TCAT routes (GTFS feed; tcatbus.com, flyithaca.com and parks.ny.gov disallow agents → search observation only). 1,350 entity hypotheses + topic seed queries for every R33 topic; batch search-intel (25 clusters / 170 s / 24 searches); AGI + sweet-spot scoring; bounded sweep (`CAMPUS_SWEEP_INTEL_CAP`, default 300) with deferral; auto-topics (R46), Class Roster / Stack Exchange / first-party collectors (fixture-tested), Reddit API collector built and OFF.
- **M9**: live search intel for the Cornell transfer-housing cluster (AT12: 2 variants × 10 results, labeled, demand evidence stored) → sweet spot (D=2 AGI=4 G=4 E=4, niche 64); 25-cluster housing batch → 1 more sweet spot ("Cornell housing application deadline", niche 72), 12 watch (dedicated official hall pages rank), 11 reject, 1 navigational; strategist (opus, 87 s) → `docs/strategy/cornell-university/housing.md` with every R14 section (AT13), 2 win plans, 4 query targets, no cannibalization.
- **M10**: tier-2 profiles, observed-pair comparisons, process graphs + navigator (renders, passes the R45 gate items and 5-width screenshot QA), sequential expansion, volume projection (AT41–AT43, AT47 fixture parts pass).
- **M11**: `docs/editorial/style.md`, extended filler check, information gain, competitor-beat review, deterministic SEO gate (every R45 item), `/towns/` URL policy (AT37–AT39, AT44 pass).
- **S6 done (AT15)**: Cornell `identity_status = verified` against the official NCES HD2024 release (sha256 recorded in `data/ipeds/NCES_HD2024_SHA256SUMS` and on the external id).
- **Hosted DB**: rebuilt three times (`scripts/rebuild_from_repo.sh`): run 1 imported 6,072 institutions (the session-2 replay was lost to a transient error), run 2 replayed it (8 questions, 17 estimate claims, 1 held version), run 3 changed nothing rebuild-owned (import skipped by release count, replay skipped). Backups: `scripts/backup.sh` + `restore_test.sh` pass on the Mac (local dump); the hosted-dump run is part of the final regression.
- Observed agent economics: search-intel 3 clusters = 26 s / 8 turns / 7 searches; 25 clusters = 170 s / 26 turns / 24 searches; strategist 87 s / 2 turns; skill scout 356 s / 54 turns.

### Assumptions (session 3)
- `living.cornell.edu` resolves (to a static-web load balancer) but never answers on 80 or 443; treated as a retired alias of `scl.cornell.edu` and reported as WARN, not a required failure. The housing source of record is `scl.cornell.edu`.
- Python runs from `worker/.venv` (Homebrew python is externally managed); every script resolves that interpreter first.
- `claude --help` 2.1.319 does not list `--max-turns`; subagents declare `maxTurns` in frontmatter, and `run.sh` probes the flag on its first iteration.
- `worker/.env` is the canonical env file (spec says `.env`); all scripts source it; values with `&` must be single-quoted. Claude never reads it (deny rule in M3); the owner pasted the URL into chat once (02:xx) and should rotate that password.
- AGI calibration (deterministic, not a spec threshold): non-dedicated results capped at 0.6 strength, stale results at 0.4, half-up rounding — so stale Student Assembly PDFs and partial official pages read as the gap they are.
- Synthetic fixture institutions are never swept or searched live (`sweep.scopes(include_fixtures=False)`); 98 Riverbend hypotheses created before that rule were deleted from the hosted DB.
- Bounded sweep: clusters beyond `CAMPUS_SWEEP_INTEL_CAP` (300) are decided `watch` with a deferral reason so `run.sh --mode sweep --max 5` can finish with every cluster decided; the discovery lane observes them later.

### Proposed spec changes (SPEC.md v3, not edited)
- §26 daily publish quota is superseded by the live ramp (continuous-local-run R8, owner decision 2026-11-06); local/staging publishing is unthrottled.
- §09 "Reddit disabled": collection stays disabled; search-result observation of Reddit titles/URLs is permitted (R35/R36).


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
