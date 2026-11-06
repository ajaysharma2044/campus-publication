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
- **M7 skill scout — done (AT11, AT27)**: three live opus dispatches (6 min, 1.5 min, ~3 min). Pass 3 cloned the three accepted candidates (SHAs pinned in `docs/ops/skill-evaluations.md`), read their sources and benchmarked them on `docs/ops/skill-eval-set.md`: `claude-seo.seo-content-brief` 6 / 9 / 5 against baseline 9 / 9 / 9 (tasks 1, 5, 6; it drops .edu and forum results and breaks the URL model), `humanizer` 9 vs 8 on task 4 and 9 vs 9 on task 5 (single non-blind scorer, one-point margin), `session-report` re-reviewed and rejected (undisclosed Google Fonts load, writes into the current directory). The R12 adoption rule is not met, so nothing is vendored under `.claude/skills/` and the guard still blocks unlisted skills. Coverage matrix carries per-task baseline scores and "—" where no eval task measures a capability (AT27); humanizer's pattern idea is folded into `references/editing.md` as an in-repo improvement (R30). Eval-set defects the scout found are fixed (task 1 deposit ground truth, task 6 names `navigational.json`). Build-time settings change (owner-level file, 2026-11-06 earlier): `Bash(git clone --depth 1 *)`, `Bash(git -C * log *)`, `Bash(git -C * rev-parse *)`, `Bash(npx playwright *)` added to `.claude/settings.json` so the scout could clone.
- **M8 demand engine**: migration 0004; 22-topic taxonomy + 15 audience topics (`docs/strategy/topic-taxonomy.md`); access modes (R35) with robots honouring Claude-agent disallows; live harvest on the hosted DB: 42 Cornell residence halls, 29 dining locations, 24 libraries, 20 city services, 5 city parks, 33 county departments, 25 TCAT routes (GTFS feed; tcatbus.com, flyithaca.com and parks.ny.gov disallow agents → search observation only). 1,350 entity hypotheses + topic seed queries for every R33 topic; batch search-intel (25 clusters / 170 s / 24 searches); AGI + sweet-spot scoring; bounded sweep (`CAMPUS_SWEEP_INTEL_CAP`, default 300) with deferral; auto-topics (R46), Class Roster / Stack Exchange / first-party collectors (fixture-tested), Reddit API collector built and OFF.
- **M9**: live search intel for the Cornell transfer-housing cluster (AT12: 2 variants × 10 results, labeled, demand evidence stored) → sweet spot (D=2 AGI=4 G=4 E=4, niche 64); 25-cluster housing batch → 1 more sweet spot ("Cornell housing application deadline", niche 72), 12 watch (dedicated official hall pages rank), 11 reject, 1 navigational; strategist (opus, 87 s) → `docs/strategy/cornell-university/housing.md` with every R14 section (AT13), 2 win plans, 4 query targets, no cannibalization.
- **M10**: tier-2 profiles, observed-pair comparisons, process graphs + navigator (renders, passes the R45 gate items and 5-width screenshot QA), sequential expansion, volume projection (AT41–AT43, AT47 fixture parts pass).
- **M11**: `docs/editorial/style.md`, extended filler check, information gain, competitor-beat review, deterministic SEO gate (every R45 item), `/towns/` URL policy (AT37–AT39, AT44 pass).
- **S6 done (AT15)**: Cornell `identity_status = verified` against the official NCES HD2024 release (sha256 recorded in `data/ipeds/NCES_HD2024_SHA256SUMS` and on the external id).
- **Hosted DB**: rebuilt three times (`scripts/rebuild_from_repo.sh`): run 1 imported 6,072 institutions (the session-2 replay was lost to a transient error), run 2 replayed it (8 questions, 17 estimate claims, 1 held version), run 3 changed nothing rebuild-owned (import skipped by release count, replay skipped). Backups: `scripts/backup.sh` + `restore_test.sh` pass on the Mac (local dump); the hosted-dump run is part of the final regression.
- Observed agent economics: search-intel 3 clusters = 26 s / 8 turns / 7 searches; 25 clusters = 170 s / 26 turns / 24 searches; strategist 87 s / 2 turns; skill scout 356 s / 54 turns.

- **M12 Cornell pipeline (R16/R17) — S4 run live on the hosted DB**: the five official Cornell pages (residential policy, new-transfer page, new-undergrad application process, rates/cancellation, admissions FAQ) were re-collected after an extractor fix (content root chosen before noise stripping; the SCL pages had kept only their titles). Deterministic rate claims from the official table verified the session-2 estimates (double, single, triple, super single per semester; quad, townhouse double, academic-year totals, rate.includes, damage deposit = $0 created). The researcher agent extracted 27 policy claims from the opened pages (15 created, 8 estimate→verified upgrades, 3 supersedes, 0 conflicts) and 12 more from the current-undergraduate application page (2027-28 selection timeline, juniors and seniors not guaranteed housing). `campus_worker.pipeline` then ran R16 end to end: planner (information gain 5 items, R37), writer (0 deterministic findings), editor (6 substantive findings, among them two unsupported application steps cut and a no-show paragraph trimmed to its claim), competitor-beat review by a fresh editor dispatch — passed, 21 against 13 / 8 / 14 for the Student Assembly PDFs and the 2018 Sun article (AT38 mechanics live) — and the verifier. Verifier round 1 held the page because its snapshot tool call was denied (every claim `source_opened=false`); the coordinator now exports each claim's snapshot text to `build/runs/snapshots/<id>.txt` and lists every source per claim (opened pages before search snippets), so the verifier needs only Read/Grep. Round 2 result: see "S4 outcome" below. The cluster's demand evidence dipped to D=1 while mirror-observed Reddit threads were being purged (see assumptions) and recovered to D=2 on a fresh observation (sweet spot, niche 64).
- **M12 funnel live (AT23)**: "Can a transfer student cancel Cornell housing and live off campus?" → search intel → AGI=0 (the official cancellation page answers it) → `watch`, no researcher/writer/editor/verifier dispatched. "Cornell housing application deadline" was planned, written, edited and beat-reviewed (21 against 8 / 0 / 7) while it was a sweet spot, then re-scored `watch` (AGI=1: a dedicated official page) on a fresh observation; the funnel refused its verifier (logged `refused_by_funnel`), the page is held with that reason and the draft version is kept unpublished. S5 (West vs South comparison), the first review-intent entity guide (AT25), the first non-housing page and the first town page (AT38 on a non-housing page) are not produced yet: no observed-query comparison pair or entity cluster has reached the sweet-spot queue, and the first-page link rule (below) wants sibling pages in the same build.
- **M13 reporting — done**: `campus_worker.digest` writes `docs/digest/YYYY-MM-DD.md` with every R9 section, R29 efficiency metrics from the ledger and dispatch log, and the R44 volume table + projection; `run.sh` calls it at run end and at midnight; the operations dashboard shows the same tiles plus the sweet-spot top 10. First live digest: `docs/digest/2026-11-06.md` (AT16, AT26, AT43; AT22's top-10 table lists the sweet-spot clusters that exist, 2 at the time).
- **Regression (AT18)**: `cd worker && pytest -q` passes in full (fixture pipeline chain, funnel refusal, digest, year-check tests added); `scripts/check_css.py` ok; `scripts/qa_screens.js` over the preview build: 90 page-widths, 0 problems (a visually-hidden table caption widened the document at 360/390 px; fixed in `campus.css`). `scripts/doctor.sh`: 0 required failures, 1 warning (AT1). Hosted backup + restore (AT32): `scripts/backup.sh` dumps the Neon DB (`--no-privileges`, Homebrew pg tools on PATH) and `restore_test.sh` restores it into `campus_restore_test`: institutions=6073, claims=56, migrations=5.

### S4 outcome (AT14 live, 2026-11-06)
- `/schools/cornell-university/housing/transfer-housing/` version 7 (`71a4e9f2`) is published locally: `build/site/...` and WordPress staging draft (cms id 5, hash-tracked). Chain on the hosted DB: planner (information gain 5 claim-linked items) → writer (0 deterministic findings) → editor (6 substantive findings) → competitor-beat review by a fresh editor dispatch, 21 against 13 / 8 / 14 → verifier. Verifier round 1 held (its snapshot tool was denied); round 2, with every source exported as readable text, opened 31 of 31 sources and found one wrong-scope claim (the 2-year rule's audience was empty although the page scopes it to first- and second-year students) plus a 2/4 attribution score; the claim was re-scoped and the editor applied the verifier's six corrections; round 3 asked for the cancellation deadlines and fee to be cited (they were in the opened page but not in claim_refs) and for the ranking documents to be named as observed titles only; round 4 passed (rubric 20/24, no hard failures, 31/31 opened). Two heading-only editor passes then satisfied the R45 `headings_cover_secondary_questions` item (typographic apostrophes and the planned question's words) with the round-4 rubric carried; the SEO gate passed all 26 items with the seo agent's checklist attached (`page_versions.seo_gate.agent_checklist`), and `publish_local` rendered the page plus the site shell (home, schools index, Cornell hub, housing hub, policies) and pushed the draft to the local WordPress.
- Known weak spots the seo agent flagged for the next revision: the answer-first check passed on the "checked on" line rather than a real answer paragraph; two H2s overlap (sources sections); the win plan's outbound link to the application-deadline guide is absent because that page is held.
- Claims added for the page during verification: `placement.first_year_residence_halls` and `process.guaranteed_waitlist` (verbatim sentences from the opened pages), `eligibility.residency_years_required` re-scoped to `first_second_year`.
- Cost of the first live page (R29, from the ledger and dispatch log): 28 dispatches, 876 turns, 227 minutes across the day, which includes the fixes to the pipeline made while running it.

### Owner decision 2026-11-06: LEAN MODE (overrides specs/continuous-local-run.md where they conflict)
Pasted by the owner after the first live day. In force from this commit; the spec file itself is untouched (owner-only).
1. Stop building new features. Finish the current loop run and open the PR, then spend all effort on producing pages.
2. Demand evidence and sweet-spot scores only set the order of work. Any cluster that is not navigational and has no strong dedicated incumbent gets a page if it has verified facts.
3. Competitor-beat review runs on 1 in 10 pages as a spot check, not on every page; one editor pass for the rest.
4. Information-gain minimum is 1 new verified fact. Tier-2 pages need 4 verified claims instead of 6.
5. Kept exactly: verified, sourced, dated facts; no scraping against terms; no fake reviews or copied text; the SEO gate; the 60% overlap rule.
6. `CAMPUS_SWEEP_INTEL_CAP` raised so every deferred cluster gets checked.
Implementation: `CAMPUS_LEAN_MODE` (default on) in `config.py`; `funnel.qualify` lean rule (not navigational, AGI ≥ 2 i.e. no strong dedicated incumbent, ≥ 1 verified claim in scope; D only orders); `quality.check_information_gain` minimum 1; tier-2 minimum 4 claims; `pipeline.run_r16` beat review on every 10th produced page, editor pass otherwise; sweep cap default 5000 and the 1,087 deferred clusters re-opened for observation. Gates, rubric, critical-claim rule, SEO gate, overlap rule and all source rules unchanged.

### Sweep outcome (AT40 live, 2026-11-06)
- The Cornell + Ithaca sweep is complete: 1,230 clusters (906 Cornell, 324 Ithaca) across all 40 R33 topics, every one scored and decided — 2 sweet-spot (both Cornell housing: "Do Cornell transfer students have to live on campus?" niche 80 and the North Campus transfer cluster 72), 1,161 watch (1,087 of them deferred beyond the first-day intel cap of 125, 18 waiting for a second independent occurrence, the rest observed with a dedicated incumbent), 55 reject, 11 navigational. `docs/strategy/opportunity-map.md` and `build/opportunity-map.csv` are the artifacts. `scripts/run.sh --mode sweep --max 5` (run 20261106T201209Z) found it complete in iteration 1, regenerated and committed the map, reported `sweep_complete`, and switched to the normal lane mix (R41).
- What the sweep did not find yet: no non-housing sweet spot (AT33), no auto-created topic (AT46), 17 Reddit occurrences across 5 topics or entities (AT36 wants 10), and only 4–5 observed watch clusters each for alumni, parents and jobs (AT45 counts 8–9 only with deferrals). The deferred 1,087 clusters are the discovery lane's queue for the next days.

### Loop fixes found by the live runs (M5, 2026-11-06)
- `run.sh` passed the allowlist word-split (`-m` became a CLI option: every iteration failed in 0 s); now one comma-joined argument with a `--print-argv` test.
- Headless Claude Code kills a coordinator's background tasks 10 minutes after its last turn; `run.sh` now exports `CLAUDE_CODE_PRINT_BG_WAIT_CEILING_MS=0` and the prompt says to run long commands in the foreground.
- The coordinator could not dispatch a search-intel batch from the allowlist (`sweep intel` only listed); the loop's own iteration 4 added `sweep run-intel` (one batch dispatch, ingest, score), kept and tested.
- An absolute-path `cd … && .venv/bin/python …` was denied in dontAsk mode; every next-step hint and the prompt now use the allowlisted shapes.
- The Mac slept mid-run once (the CLI reported "Your computer went to sleep mid-response"), which broke a verifier dispatch and two iterations; `caffeinate` cannot prevent lid-close sleep. Owner: keep the Mac awake (lid open or a keep-awake setting) for unattended runs.
- Hosted-DB connections drop while an agent runs for minutes; pipeline stages now reconnect after every dispatch and after the render + screenshot QA, and the per-dispatch output files let a lost reply be re-ingested without a new dispatch.
- `dontAsk` mode denies `cd worker && .venv/bin/python …` (verified with three headless probes) while `worker/.venv/bin/python -m campus_worker.<module>` is allowed; the prompt and every next-step hint now use the repo-root shapes, and the checks run as `worker/.venv/bin/pytest worker/tests`.
- The first sweep batches exposed three defects: `run_score` after each batch re-scored all 1,230 clusters against the hosted DB (20+ minutes a batch) and reopened the 1,087 deferred clusters as `needs_intel`; a reply with an 11th result position failed the contract at the root, so the bounded repair could not see what to fix. Now each batch scores only its own clusters, re-scoring keeps the deferral and single-occurrence decisions, and contract errors name the deepest failing path.
- Single-occurrence clusters without hypotheses are decided `watch` ("waiting for a second independent occurrence", R20) so the bounded sweep can reach `complete`.
- The loop's own iterations fixed two test flakes under load (`CAMPUS_RUN_NO_DIGEST` for the run-loop tests; a connection fixture that tolerates a test-closed connection) and committed them with tests.

### Assumptions (session 3)
- `living.cornell.edu` resolves (to a static-web load balancer) but never answers on 80 or 443; treated as a retired alias of `scl.cornell.edu` and reported as WARN, not a required failure. The housing source of record is `scl.cornell.edu`.
- Python runs from `worker/.venv` (Homebrew python is externally managed); every script resolves that interpreter first.
- `claude --help` 2.1.319 does not list `--max-turns`; subagents declare `maxTurns` in frontmatter, and `run.sh` probes the flag on its first iteration.
- `worker/.env` is the canonical env file (spec says `.env`); all scripts source it; values with `&` must be single-quoted. Claude never reads it (deny rule in M3); the owner pasted the URL into chat once (02:xx) and should rotate that password.
- AGI calibration (deterministic, not a spec threshold): non-dedicated results capped at 0.6 strength, stale results at 0.4, half-up rounding — so stale Student Assembly PDFs and partial official pages read as the gap they are.
- Synthetic fixture institutions are never swept or searched live (`sweep.scopes(include_fixtures=False)`); 98 Riverbend hypotheses created before that rule were deleted from the hosted DB.
- Bounded sweep: clusters beyond `CAMPUS_SWEEP_INTEL_CAP` (300) are decided `watch` with a deferral reason so `run.sh --mode sweep --max 5` can finish with every cluster decided; the discovery lane observes them later.
- Reddit occurrences (R36): the search tool surfaces third-party mirrors of r/Cornell and r/ithaca threads (reddit.birdcat.cafe, reddit.sentinel-team.org) rather than reddit.com. A mirror result is kept as an observed occurrence labeled `mirror_observed`, keyed by the Reddit thread id so one thread seen on two mirrors counts once, and is never opened or quoted (title, date, visible snippet only). Owner may overrule: dropping mirrors entirely leaves the transfer cluster at D=1 and no Cornell page qualifies today.
- Verifier source access: agents in `dontAsk` mode could not run the snapshot CLI, so the coordinator exports each cited snapshot's text to `build/runs/snapshots/` (untrusted data, gitignored) and the verifier opens it with Read/Grep. Every claim lists all of its sources, opened pages first, so a claim with only a search-snippet source is visibly snippet-only.
- First page in a scope: the R45 gate wants three contextual links to related pages plus one inbound link. The site shell (`render/site.py render_shell`) renders hubs and policy pages from the database, so the hubs give the inbound link; the three contextual links can only resolve once sibling pages exist in the same build. A page held only on `internal_links_three_contextual` waits for siblings and is re-gated with `pipeline publish --siblings`.
- Placement wording: the residential-requirement page and the transfer-housing page list different areas (the latter adds North Campus); stored as two claims (`placement.areas_upper_level`, `placement.areas`) and reported as two statements, never merged. The residential-requirement page states no academic year and the cancellation fee tiers carry none (deadlines are dated 2026); rows are labeled accordingly.
- Academic-year check: ISO dates (2026-05-15) are not year ranges, and a year range the fact table labels explicitly (the 2027-28 selection cycle on a 2026-27 page) is not a wrong-year finding.

### Proposed spec changes (SPEC.md v3, not edited)
- §26 daily publish quota is superseded by the live ramp (continuous-local-run R8, owner decision 2026-11-06); local/staging publishing is unthrottled.
- §09 "Reddit disabled": collection stays disabled; search-result observation of Reddit titles/URLs is permitted (R35/R36).
- continuous-local-run R36: say how mirror-observed community threads count (this build: kept, labeled, keyed by thread id, never opened).
- continuous-local-run R45 / AT44: state that the first pages under a new hub are held on the three-contextual-links item until two sibling pages pass, and that the maintenance lane re-gates them together; otherwise no scope can ever publish its first page.
- continuous-local-run AT14: the transfer guide's "cite fetched primary snapshots" is met by opened-page claim sources; the first-year guarantee and several rates also keep their search-snippet sources as secondary evidence.


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

## Run 20261106T140001Z iteration 4 (sweep)
- pytest passed; doctor: 0 required failures (1 warning: living.cornell.edu).
- `sweep run-intel --batch 25` exceeded the 600s foreground cap and was killed with no output. Nothing was committed.
- `sweep status` before the run: need_intel 50, watch 1128. After the kill: need_intel 462, watch 709. This change is unexplained. Check whether the killed run left partial scoring writes before the next run-intel.
- Next: use a smaller `--batch` (for example 10), or raise the foreground cap, so one batch finishes inside 600s.

## Run 20261106T201209Z iteration 2 (production, HELD)
- pytest passed; doctor 0 required failures (1 warning: living.cornell.edu).
- `lanes next` → sweet-spot cluster 5d69fed9 "Do transfer students have to live on campus at Cornell?". `pipeline run <id>` alone was refused ("no page path"): the strategy win plans are keyed to "Is housing guaranteed for transfer students at Cornell" and the cluster label does not match. Re-ran with `--path /schools/cornell-university/housing/transfer-housing/` (the strategy's transfer-housing win plan). Suggest the win-plan lookup also match cluster variants/queries listed in the strategy's query targets.
- First planner reply was invalid JSON (extra data); the second run planned (information gain ok, 5 items), wrote, edited and reached the verifier. `competitors` was 0 for this cluster even though search intel exists — check `competitors_for_cluster`.
- Verifier: FAILED (hard failure `unsupported_critical_claim`, rubric 16/24). Held version 638e04a1. Corrections required include: the draft says the guaranteed waitlist does not promise a room, but a source says waitlisted students are guaranteed an assignment; room-type request statement; other exemption categories; penalty-free cancellation deadlines (Fall June 15, Spring Dec 1, 2026; $500 fee after); enrollment deposit in step 1. Needs claims backing each, then `pipeline run` again / `pipeline verify`.
- Not mine: 8 tracked files (funnel, lanes, pipeline, quality, sweep, tier2, conftest, iteration_prompt) plus `lean.py` and `test_lean.py` were modified/untracked in the working tree during this run (tree was clean at start). Left uncommitted for the owner.

## Next actions (in order)
1. Owner supplies OD1 → run `python -m campus_worker.calibration` path with `AnthropicProvider` (one real Sonnet worker, one real Opus review), compare against the scripted report, record resolved model ids.
2. Owner supplies OD9 or files → register Cornell housing sources (`scl.cornell.edu`, `living.cornell.edu`), run `collect_source` → `extract_claims`, verify Cornell identity against the IPEDS release, then exercises 1–3 on real records (still staging, draft status).
3. Owner supplies OD2/OD3 → deploy plugin/theme, point the worker at managed PostgreSQL and WordPress, publish as drafts.
4. OD10 → hourly `run-once`, daily `plan_daily`, weekly diagnosis; enable bounded auto-publish (1 page/day, 5 updates/day) for entity_profile and comparison templates only after the three calibration outputs pass with a real model.
5. OD5/OD6/OD7 as they arrive; each flips one adapter from unconnected to connected without template changes.

### Iteration 2 (run 20261106T093045Z, sweep) — blocked, no work done
- Checks: pytest passed (exit 0, 220 tests); `scripts/doctor.sh` 0 required failures, 1 warning (living.cornell.edu).
- `sweep next` → step `intel`: 99 clusters still need search observation; sweep not complete. No CLI subcommand dispatches the batch: `search_intel.run_batch` (≤25 clusters, then ingest) is only a Python function, and the iteration allowlist permits only `python -m campus_worker.*`, so the coordinator cannot ingest agent output.
- Proposed (owner or next build iteration): add `python -m campus_worker.sweep run-intel [--batch N]` that calls `run_batch` and then `run_score`.

### Iteration 4 (run 20261106T093045Z, sweep) — unblocked the intel lane
- Checks: full pytest passed at start (exit 0); `scripts/doctor.sh` 0 required failures, 1 warning (living.cornell.edu).
- Implemented `python -m campus_worker.sweep run-intel [--batch N]` (`sweep.run_intel`): picks up to 25 clusters, one `search_intel.run_batch` dispatch (validates + ingests), then `run_score`. `sweep next` now points at it. Test `test_sweep_run_intel_dispatches_one_batch_ingests_and_scores` added; `tests/test_demand_engine.py` passes. Full suite not re-run after the change (it exceeds the 120 s foreground limit); the next iteration's checks-first run covers it.
- Not yet run live: 99 clusters still need search observation (sweep not complete). Next sweep iteration: `python -m campus_worker.sweep run-intel --batch 25`.

### Iteration 1 (run 20261106T140001Z, sweep) — checks fix
- Checks: first pytest run stopped at `tests/test_ensure_conn.py::test_closed_connection_is_replaced` (teardown error: the `conn` fixture called `rollback()` on a connection the test closed on purpose; `ensure_conn` itself was fine). Fixed `worker/tests/conftest.py` so teardown skips rollback/close when the connection is already closed. Re-run: full suite passed (exit 0). `test_ensure_conn.py` is now tracked.
- `scripts/doctor.sh`: 1 required FAIL — `https://nces.ed.gov` HTTP 000 (external host unreachable from this machine; not fixable in the repo; blocks only IPEDS identity verification, see Next actions 2). Warning: living.cornell.edu (retired alias).
- No discovery work done this iteration (checks were the unit of work).

### Iteration 2 (run 20261106T140001Z, sweep) — checks fix
- First full pytest stopped at `test_run_loop.py::test_usage_limit_exits_20_with_no_retry_inside_60s` (116s inside the full suite; 2.9s alone). The run-end digest was the only non-stub step, so `run.sh` now skips it when `CAMPUS_RUN_NO_DIGEST` is set and the run-loop tests set it (they no longer touch the DB or write digests). Root cause of the 116s was not independently proven. Re-run: 225 passed.
- `scripts/doctor.sh`: 0 required failures, 1 warning (took over 5 minutes this run; worth a look). No discovery work this iteration.

### Iteration 5 (run 20261106T140001Z, sweep) — run-intel batch 10 did not finish in the foreground cap
- Checks: pytest passed (exit 0). `scripts/doctor.sh`: 2 required FAIL (`admissions.cornell.edu` and `nces.ed.gov`, HTTP 000; external, not fixable in the repo), 1 warning (living.cornell.edu). One `sweep next` call hit a transient DNS failure for the Neon host and succeeded on retry.
- `sweep next` -> step `intel`, 40 need intel (remaining 40 after a 25-cluster batch). `sweep run-intel --batch 10` hit the 600s Bash cap (the tool maximum; the 20-minute timeout in the prompt cannot be set) and was moved to the background. Its output file stayed empty; I could not confirm whether it finished, ingested or scored (`ps` is denied). No commit of results.
- `sweep status` after: need_intel 141, sweet_spot 2, watch 1030, reject 47, undecided 149, deferred 986. Before: need_intel 40, sweet_spot 1, watch 1131, undecided 50. need_intel rising from 40 to 141 while watch fell by 101 is unexplained and matches the shift seen in iteration 4 after a killed batch. Likely `run_score` re-decides clusters as it runs (possible re-opening of deferred `watch` clusters); not proven.
- Next: read `sweep run_score` / deferral logic to see why scoring flips `watch` to `need_intel`; make `run_intel` score only its batch; give run-intel a time budget under 600s (batch of 3-5) or a progress log so a kill is diagnosable.

### Iteration 3 (run 20261106T140001Z, sweep) — first live `run-intel`, scoring fix
- Checks: pytest passed, doctor 0 required failures (warning: living.cornell.edu).
- `sweep run-intel --batch 25` (first live run): the dispatch and ingest worked (`need_intel` 99 -> 74), then `run_score` died with `psycopg.OperationalError: server closed the connection unexpectedly`. A separate `sweep score` hit the same error. Cause of the drops not established (Postgres log not readable from the headless allowlist).
- Fix: `sweetspot.score_all` now reconnects (`ensure_conn`) and retries the failing cluster once; each cluster already commits on its own. Test `test_score_all_reconnects_once_when_the_connection_drops` added; full suite passed after the change.
- Open: full scoring of 1,230 clusters takes over 20 minutes on the hosted DB (a `sweep score` run was stopped at the background time limit; per-cluster work is persisted). Likely per-cluster query cost (`demand_points`, `e_estimate`, `latest_intel`); worth batching or scoring only changed clusters. Status after the partial runs: need_intel 74, sweet_spot 1, reject 15, undecided 93; sweep not complete.
- Next sweep iteration: `sweep next`, then `sweep run-intel --batch 25` (74 clusters left, 3 batches). Consider making `run_intel` score only the clusters in its batch.
