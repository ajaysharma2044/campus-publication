# BACKLOG

Prioritized implementation tasks. IDs are stable. Status: `todo`, `doing`, `done`, `blocked`. Acceptance checks are executable commands or explicit observations. The database (jobs table) is authoritative for content-production jobs; this file tracks implementation milestones only.

Legend for evidence state in STATE.md: **implemented** (code exists) → **tested locally** (checks pass here) → **connected** (talks to a real external service with real credentials) → **deployed** (reachable outside this container) → **scheduled** (runs on an external scheduler).

## Stage A — registry, schema, queue, budget

| ID | Task | Depends | Acceptance check | Status |
|----|------|---------|------------------|--------|
| A1 | Control files: SPEC.md, BACKLOG.md, STATE.md, CLAUDE.md | — | files exist; CLAUDE.md < 120 lines | done |
| A2 | Local PostgreSQL 16 cluster + `campus_research` / `campus_research_test` DBs | — | `psql -c 'select 1'` succeeds | done |
| A3 | Migration runner (plain SQL, versioned, checksummed, forward-only with documented down scripts) | A2 | `pytest worker/tests/test_migrations.py` | done |
| A4 | Core schema migration 0001: all 33 tables from SPEC §14 with FKs, constraints, indexes, enums | A3 | `pytest worker/tests/test_schema.py` (every table present, FK integrity, money integer, UTC) | done |
| A5 | Typed records (pydantic) for institution, campus, school_config, claim, job, usage entry | A4 | `pytest worker/tests/test_types.py` | done |
| A6 | Institution registry: IPEDS importer (header-driven, release-dated), alias/external-id mapping, system-vs-campus rule | A5 | `pytest worker/tests/test_registry.py` with synthetic IPEDS CSV fixture | done |
| A7 | School configs: Cornell (real identity, verified only via owner-supplied IPEDS row) + synthetic commuter community college fixture | A6 | configs load; housing topic `not_applicable` for the commuter fixture | done |
| A8 | Source permissions registry + connector capability states | A4 | `pytest worker/tests/test_permissions.py` (Reddit disabled, unknown domain denied) | done |
| A9 | Job queue: states, atomic lease, lease expiry reclaim, idempotency keys, 3-retry backoff+jitter, held/dead_letter with reason | A4 | `pytest worker/tests/test_queue.py` (duplicate idempotency, expired lease, retries→dead_letter, hold with retry condition) | done |
| A10 | Budget ledger: atomic reservation, daily/monthly caps, unknown-cost hold, reconciliation, headroom | A4 | `pytest worker/tests/test_budget.py` (reservation failure prevents call; unpriced job held) | done |
| A11 | Model adapter with role aliases, resolved-model recording, preapproved fallbacks, escalation ceiling; `capability()` = unconnected without key | A10 | `pytest worker/tests/test_model_adapter.py` (fixture provider; escalation ceiling; hold not escalate on missing evidence) | done |
| A12 | Config loader + `.env.example` + auth-mode inspection (no secret exposure) | — | `python -m campus_worker.cli status` prints mode | done |

## Stage B — collection, claims, discovery, opportunity

| ID | Task | Depends | Acceptance check | Status |
|----|------|---------|------------------|--------|
| B1 | Safe fetcher: allowlist, private-IP/metadata block, redirect revalidation, size cap, per-domain rate limit, conditional requests, circuit breaker | A8 | `pytest worker/tests/test_fetcher.py` (SSRF cases, oversized, redirect to private) | done |
| B2 | Official-HTML collector → fetch_snapshots with hash, change detection, navigation-noise filter | B1 | `pytest worker/tests/test_collector_html.py` (fixture pages; nav change ≠ material change) | done |
| B3 | PDF/table collector (pdfplumber) with page/footnote/academic-year preservation, low-confidence routing | B1 | `pytest worker/tests/test_collector_pdf.py` | done |
| B4 | Claim extraction (deterministic selectors on fixtures + model-extraction contract), typed values, per-person/per-unit, academic year, conflicts | A5,B2 | `pytest worker/tests/test_claims.py` (mixed years, room vs building price, conflict blocks critical claim) | done |
| B5 | Prompt-injection sanitizer for model inputs | B4 | `pytest worker/tests/test_sanitize.py` | done |
| B6 | Question discovery import (official FAQ, suggestions export, discussion export when authorized) + normalization + clustering by answer | A4 | `pytest worker/tests/test_discovery.py` (dup vs independent, synonyms merge, audience split, hypotheses labeled) | done |
| B7 | Demand + SERP adapters (unconnected; import from supplied exports), null-preserving | A4 | `pytest worker/tests/test_demand.py` (overlap not summed, suppressed preserved) | done |
| B8 | Opportunity scoring (D,G,W,E,M anchors, priority formula, threshold, editorial exception record) + action decision | B6,B7 | `pytest worker/tests/test_scoring.py` | done |
| B9 | Source-change propagation via dependencies (claim → page_versions/tools) | B4 | `pytest worker/tests/test_propagation.py` | done |

## Stage C — briefs, contracts, editorial gates

| ID | Task | Depends | Acceptance check | Status |
|----|------|---------|------------------|--------|
| C1 | JSON schemas for all 12 role outputs + common envelope; validator with bounded repair | A11 | `pytest worker/tests/test_contracts.py` (malformed rejected, next_jobs are proposals, no command execution) | done |
| C2 | Brief builder from claims/clusters (reader, decision, answer, contribution, critical claims, unresolved, overlap) | B8,C1 | `pytest worker/tests/test_brief.py` | done |
| C3 | Deterministic editorial checks: banned openings, unsupported critical claims, fake byline, fabricated consensus, arithmetic, headline/claim consistency, outdated prose vs table, duplicate-audience similarity | C1 | `pytest worker/tests/test_editorial_checks.py` | done |
| C4 | Rubric gate (6 × 0–4, ≥20, none <3) + hard gates + findings persistence; versioned drafts | C3 | `pytest worker/tests/test_gates.py` | done |
| C5 | Writer/editor/verifier role runners (fixture model) end to end on synthetic evidence | C2,C4,A11 | `pytest worker/tests/test_roles_e2e.py` | done |

## Stage D — design system and templates

| ID | Task | Depends | Acceptance check | Status |
|----|------|---------|------------------|--------|
| D1 | Design tokens + CSS (paper/ink/navy, 12-col grid, type scale, spacing, focus, reduced motion, print) | — | `scripts/check_css.py` contrast ≥ 4.5:1 for text pairs | done |
| D2 | Templates: base, homepage, school hub, topic hub, article, entity profile, comparison, calculator, search, 404/empty/stale states, policies | D1 | `python -m campus_worker.render.preview` renders all without error | done |
| D3 | Screenshot QA at 360/390/768/1280/1440 with Playwright; inspect; fix defects | D2 | `scripts/qa_screens.py` produces PNGs; no horizontal overflow; findings logged in docs/design/qa.md | done |
| D4 | Comparison + total-cost calculator (server-rendered + progressive JS, deterministic, keyboard, unknown inputs) | D2 | `pytest worker/tests/test_tools.py`; JS unit checks via node | done |

## Stage E — CMS publication

| ID | Task | Depends | Acceptance check | Status |
|----|------|---------|------------------|--------|
| E1 | Campus Core WP plugin: CPTs (school, topic, entity_profile, guide, comparison, tool), meta by stable IDs, REST upsert by external id + content hash | — | `php -l` all files; plugin unit script | done |
| E2 | Campus Editorial theme (templates mirror D2) | D2,E1 | `php -l`; renders in local WP | done |
| E3 | WP CMS adapter (REST, idempotent upsert, revision, redirects) + local WordPress staging via SQLite drop-in | E1 | `pytest worker/tests/test_cms_adapter.py` (repeat publish = no duplicate); local WP smoke | done |
| E4 | Sitemap/robots/canonical/noindex rules; structured data validator; redirects | E2 | `pytest worker/tests/test_seo.py` | done |

## Stage F — analytics, dashboard, ads, revenue, experiments

| ID | Task | Depends | Acceptance check | Status |
|----|------|---------|------------------|--------|
| F1 | Event dictionary + validator (no PII fields, dedupe, consent category) | — | `pytest worker/tests/test_analytics.py` | done |
| F2 | Ad adapter (AdSense, disabled), one loader, slot components, staging guard, ads.txt generator | D2 | `pytest worker/tests/test_ads.py` (no ad code when disabled; one loader; staging never production) | done |
| F3 | Revenue model (separate denominators, RPM math) + report import interface | — | `pytest worker/tests/test_revenue.py` | done |
| F4 | Experiments registry (hypothesis, allocation, metric, guardrails, stopping rule) | — | `pytest worker/tests/test_experiments.py` | done |
| F5 | Operational dashboard (server-rendered, staff-only): sources, jobs, budget, held/dead-letter, heartbeat, integration status | A9,A10 | `python -m campus_worker.dashboard.app` serves /; `pytest worker/tests/test_dashboard.py` | done |

## Stage G — scheduler, backups, production

| ID | Task | Depends | Acceptance check | Status |
|----|------|---------|------------------|--------|
| G1 | Scheduler tick (`run-once`): hourly/daily/weekly plans, lock, checkpoint, heartbeat, exit codes for executing/waiting/paused/blocked | A9,A10 | `pytest worker/tests/test_scheduler.py`; interrupt+resume test | done |
| G2 | Backup/restore scripts + restore test into test DB | A2 | `scripts/backup.sh`, `scripts/restore_test.sh` pass | done |
| G3 | Continuation runner (bounded iterations, completes ≥2 dependent backlog items without manual continue; logs stop reason) | G1 | `scripts/continuation_demo.sh` log shows two dependent jobs and stop condition | done |
| G4 | Calibration exercises 1–4 on fixtures; report traceability, rubric, holds | C5,D4 | `docs/editorial/calibration.md` with run IDs | done |
| G5 | Deploy docs; real credential wiring (model key, WP, AdSense, Search Console, IPEDS download) | all | blocked on owner credentials/hosting | blocked |
| G6 | Usage-optimization evaluation (baseline, candidate tools reviewed, not installed) | — | `docs/ops/usage-optimization.md` | done |

## Owner dependencies (cannot be completed from this environment)
- OD1 Anthropic API key (API-billed) or approved automation credential for worker model calls.
- OD2 Managed WordPress host + application password for the REST API.
- OD3 Managed PostgreSQL connection string.
- OD4 Domain / brand decision (working masthead only until then).
- OD5 AdSense account approval; ads.txt publisher ID.
- OD6 Search Console property verification + service account.
- OD7 Keyword-metrics provider authorization or exports.
- OD8 Reddit Data API commercial authorization (stays disabled otherwise).
- OD9 Network egress policy allowing cornell.edu / nces.ed.gov (blocked in this container; collectors tested on fixtures only).
- OD10 External scheduler (cron on host, cloud scheduled task, or Claude Code Routine) for continuous operation.
