# SPEC: Continuous local run + agent team (SEO, search, strategy)

Version: 2.1 · Owner: Ajay · Date: 2026-11-06 · Builds on: SPEC.md v3 (§11, §15, §21, §25, §26, §29, §35, §37, §38), BACKLOG S1 to S6, STATE.md (2026-11-04)

## 1. Objective

When Ajay types one command on his MacBook, Claude Code runs campus-publication by itself. A coordinator directs a team of specialist agents that:

- find and vet the best SEO and writing skills
- research what students search and who currently ranks
- plan how to win those searches
- research, write, edit, verify, optimize, and publish pages
- keep building backlog features

Every result is saved to GitHub and a hosted Postgres database, and the run continues until Ajay stops it or nothing unblocked remains.

Core loop, which never stops while a run is active: find data, then turn it into search terms, then find the searches with decent demand and no clear authority (niche, not too hard to rank, e.g. "Boldt Tower review"), then capture that demand with the best verified page or tool, then re-check, then repeat. Do this with the least wasted work possible.

Why: Ajay wants the publication to grow and win search traffic without prompting each step. Running locally also removes the network blocker that held the Cornell article (the laptop can reach cornell.edu and nces.ed.gov).

## 2. Users & context

- Only user: Ajay, starting and stopping runs on his Mac (Apple Silicon, macOS).
- Runs happen only when Ajay starts them. No cron, no cloud scheduler.
- All language judgment runs in-session inside Claude Code on Ajay's subscription ("in-session execution mode", added 2026-11-04). No Anthropic API key.
- Between runs, Ajay reviews progress in Cowork, which reads the repo and the daily digest (R9). Commits and digests must be readable by someone who wasn't watching.
- Reuse what already exists rather than rebuilding it:
  - 12 role contracts in `worker/campus_worker/contracts/schemas/`: onboarding, discovery, opportunity, researcher, planner, writer, editor, verifier, seo, tool_engineer, ad_ops, analyst
  - the job queue, gates, scoring, scheduler tick, and continuation runner
  - the coordinator skill at `skills/national-college-publishing/` with 12 references

## 3. Scope

In scope:

- Local setup against hosted Postgres; the start/stop run loop; the iteration contract
- The agent team: Claude Code subagents in `.claude/agents/`, mapped onto the existing role contracts, plus 3 new agents (skill scout, search intelligence, search strategist)
- Skill discovery and evaluation for SEO, writing, and research. Approved skills get installed, pinned.
- Search intelligence and a win-the-search strategy per topic cluster, feeding the existing scoring and briefs
- The Cornell content pipeline (BACKLOG S4, S6, S5), auto-publish within daily limits, the daily digest, and the run log

Out of scope (do not build, even if it seems helpful):

- Cloud schedulers, cron, launchd, scheduled GitHub Actions
- Anthropic API key wiring or API-billed calls
- AdSense, Search Console, and paid keyword providers. Their adapters stay unconnected, but the strategist must work without them.
- Reddit (stays disabled)
- Outreach of any kind: emailing sites, link requests, guest posts, social posting (SPEC §01: no messages to third parties)
- Buying tools, domains, or hosting
- Schools beyond Cornell and the synthetic community college, until the Cornell guide publishes and Ajay says to expand

## 4. Requirements

### Run loop

- **R1.** `scripts/doctor.sh` prints PASS/FAIL for each of these, and exits non-zero on any required failure:
  - Python version and installed dependencies
  - `DATABASE_URL` reachable, migrations current
  - `git push` to origin works
  - HTTPS reachability of scl.cornell.edu, living.cornell.edu, admissions.cornell.edu, nces.ed.gov
  - `claude --version`
  - every agent file in `.claude/agents/` parses
- **R2.** `scripts/run.sh` keeps the Mac awake (`caffeinate -dimsu`), takes a single-instance lock, and runs iterations back to back. Each iteration is one `claude -p` call using `scripts/iteration_prompt.md`, with a fixed tool allowlist.
- **R3.** `scripts/stop.sh` creates `.run/STOP`. The current iteration finishes and commits, and no new iteration starts. Ctrl-C behaves the same.
- **R4.** Iteration contract. The coordinator picks one unit of work:
  - failing tests or checks always come first
  - otherwise it picks by lane mix (R24): production (sweet-spot queue), discovery (R18 to R21, skill-scout and search-intel refreshes), or maintenance (re-checks, due DB jobs, the first unblocked BACKLOG item)
  - It dispatches the required agents (R11), runs the acceptance checks, commits with the task ID, pushes, updates STATE.md, appends to the run log, and exits.
- **R5.** The loop stops and logs the reason on any of:
  - the STOP file
  - no unblocked work
  - 3 consecutive failed iterations
  - a usage-limit or auth error from the CLI
  - an optional `--max N` ceiling
  - With no `--max`, it runs until one of the others.
- **R6.** On a usage or rate limit: log it, exit 20 (usage-paused). Never retry in a tight loop, switch accounts, or disguise requests.
- **R7.** Add `CAMPUS_EXECUTION_MODE=session|api` (default session):
  - In session mode, dollar caps never block work. The ledger records one usage entry per iteration and per agent dispatch (task ID, agent, duration, turns).
  - API-mode caps stay as today, configurable via env.
- **R8.** Auto-publish. Pages that pass every gate publish automatically, up to `CAMPUS_PUBLISH_NEW_PER_DAY` (default 1) new pages and `CAMPUS_PUBLISH_UPDATES_PER_DAY` (default 5) updates. The overflow queues for the next day.
  - Until a WordPress host exists (STATE OD2), "publish" means: render to `build/site/`, upsert to local WordPress staging when it's running, and record the published version in the database.
- **R9.** Daily digest at `docs/digest/YYYY-MM-DD.md`, written on the first iteration after midnight and the last iteration of each run. Sections:
  - tasks done (IDs, commits)
  - pages published, held and why
  - claims verified or superseded
  - skills evaluated, adopted or rejected
  - search intel and strategy changes
  - failures and blockers
  - next 3 tasks
- **R10.** Run log: one JSON line per iteration in `build/runs/<run-start>.jsonl`. Fields: iteration, start/end, task ID, agents dispatched, result (succeeded / failed / held / no_work), checks with pass/fail, commit SHA, stop reason.
- **R31.** Cloud-to-local migration. The cloud session's local Postgres and WordPress were inside a temporary container and are gone. Only the repo survived. Rebuild state on the hosted database from committed files:
  - run migrations
  - seed school configs
  - import the registry from `data/ipeds/HD2024_mirror_cshirky_a812f69.csv` after checking SHA256SUMS
  - replay the session 2 Cornell discovery questions, the 17 snippet claims (as estimate), and the held transfer-housing page version from `docs/research/cornell-transfer-housing-run.json` and the evidence file
  - Write a replay script (`scripts/rebuild_from_repo.sh`) that is safe to run twice. Nothing from session 2 may be lost or silently upgraded.
- **R32.** Full parity with the cloud session. Everything the cloud session had must exist on the Mac, and `scripts/doctor.sh` checks each item with its version.
  - Toolchain (cloud inventory in STATE.md, installed via Homebrew where missing):
    - Python 3.13 with `pip install -e "worker[dev]"`
    - PostgreSQL 16 locally, used only for `TEST_DATABASE_URL` and the pg_dump/pg_restore that backups need. Tests must never run against the hosted database.
    - PHP 8.3 with pdo_sqlite, mbstring, curl, gd, zip
    - Node 22
    - Playwright Chromium (`python -m playwright install chromium`)
    - git and gh
  - Local WordPress staging: clone WordPress and the SQLite integration into `wp-local/` (gitignored) exactly as in `docs/ops/run.md`. Run `scripts/wp_local.sh setup` and `wp_install.php`, and store the printed application password in `.env`. The round-trip must work on the Mac.
  - Project skill: the coordinator skill exists in `skills/national-college-publishing/`, but it was never installed into Claude Code (no `.claude/` folder exists in the repo). Install it as a project skill at `.claude/skills/national-college-publishing/` by symlinking the existing folder, so SKILL.md and all 12 references load automatically. Keep one source of truth. Every agent in R11 names the reference it uses.
  - Settings and hooks: create `.claude/settings.json` with the R11 agents, the R7 deny rules and hooks, and a permission allowlist for the commands the loop needs: pytest, `python -m campus_worker.*`, `scripts/*`, git add/commit/push, gh pr. Commit it. Machine-specific settings go in `.claude/settings.local.json` (gitignored).
  - Usage tools: carry the decisions in `docs/ops/usage-optimization.md` into the skill scout's first evaluation: Session Report first, then token-optimizer, context-mode and rtk, each read, pinned, and tested alone against the fixed eval set already defined there.
  - CLAUDE.md: add a short "Local run mode" section pointing to this spec, `scripts/run.sh`, `scripts/stop.sh`, the agents, and the digest. It must stay under 120 lines.
  - Not carried over, on purpose:
    - the cloud environment's network allowlist (the Mac has normal internet)
    - the cloud container's databases (rebuilt by R31)
    - claude.ai connectors from the cloud session (Drive, Canva, etc.). The pipeline does not depend on them. List in STATE.md which ones are present locally, without failing on any of them.

### Agent team

- **R11.** Create one Claude Code subagent per role in `.claude/agents/<name>.md`, each with:
  - frontmatter: name, description, tools, model
  - a body that points to the matching `skills/national-college-publishing/references/*.md` and names the JSON contract it must return
  - The coordinator is the iteration session itself and the only agent that commits, schedules jobs, or publishes. Subagents return contract JSON and findings. They never overwrite another agent's artifact (SPEC §37).

| Agent | Role / contract | Job | Tools | Model |
|---|---|---|---|---|
| skill-scout | new: skill_eval.json | Find, vet, and benchmark SEO, writing, and research skills/plugins/MCP servers (R12) | Read, Grep, Glob, WebSearch, WebFetch, Bash (sandboxed clone + tests only) | opus |
| search-intel | new: serp_intel.json, feeds opportunity.json | For a topic cluster, gather what people search and what currently ranks (R13) | Read, WebSearch, WebFetch | sonnet |
| search-strategist | new: search_strategy.json | Turn intel into a plan to win each query cluster (R14) | Read, Grep, WebSearch | opus |
| onboarding | A: onboarding.json | Institution identity, campuses, source map | Read, Grep, WebFetch, Bash | sonnet |
| discovery | B: discovery.json | Questions, normalization, clustering | Read, Grep, WebSearch, WebFetch | sonnet |
| opportunity | C: opportunity.json | D/G/W/E/M scores + page/section/tool/nothing decision, using search-intel output | Read, Grep | sonnet |
| researcher | D: researcher.json | Primary-source collection and claim extraction | Read, Grep, WebFetch, Bash | sonnet |
| planner | E: planner.json | Writer's brief incl. strategist targets | Read, Grep | sonnet |
| writer | F: writer.json | Draft from brief and verified claims only | Read, Grep, Write (drafts dir only) | sonnet |
| editor | G: editor.json | Substantive edit; findings, not overwrites | Read, Grep | opus |
| verifier | H: verifier.json | Claim-by-claim check against raw sources; gates | Read, Grep, Bash (checks only) | opus |
| seo | I: seo.json | Titles, URL, structured data, internal links, snippet formatting | Read, Grep | sonnet |
| tool-engineer | J: tool_engineer.json | Calculators/comparisons | Read, Grep, Edit, Bash | sonnet |
| ad-ops | K: ad_ops.json | Stays disabled; placement/consent review only | Read, Grep | haiku |
| analyst | L: analyst.json | Maintenance, stale sources, weekly diagnosis, rank re-checks | Read, Grep, WebSearch, Bash | sonnet |

- **R12.** Skill scout. A weekly job, plus once at the start of the first run, does the following:
  - Searches skill marketplaces, GitHub, and official Anthropic skill and plugin sources for SEO, editorial writing, SERP research, and content-strategy skills, plugins, and MCP servers. Records the top 10 candidates with URL, author, license, last commit, stars, what it does, and whether it ships hooks or scripts.
  - For the top 5, reads the full source (SKILL.md, scripts, hooks) and rejects any candidate that:
    - makes network calls not disclosed in its docs
    - writes outside its own scope
    - has an unclear license
    - requires paid accounts
  - Benchmarks survivors on a fixed eval set (`docs/ops/skill-eval-set.md`, created by this spec: 3 cluster briefs, 1 draft edit, 1 title/snippet task, 1 SERP gap analysis). It compares against the current baseline (the repo's own references) and records quality score, errors, turns, and time.
  - Adopts a candidate only if it beats baseline on quality without a regression on any hard rule. Adopted skills are vendored into `.claude/skills/<name>/` pinned to a commit SHA, with the source URL, SHA, license, and eval results in `docs/ops/skill-evaluations.md`. Rejected ones are logged with the reason.
  - Never installs anything globally, never adds hooks without a review note, and keeps a one-command rollback (delete the folder, revert the commit).
- **R13.** Search intelligence. Per cluster, using only permitted sources (the WebSearch tool, official pages, supplied keyword exports):
  - the query variants students actually use
  - observed top results for 2 variants: up to 10 each, with date, result types, who ranks, answer quality, freshness, evidence quality, and the exact missing contribution
  - "people also ask" style follow-up questions when visible
  - seasonality notes
  - Output goes to `serp_intel.json` and the DB, labeled "observed via search tool on <date>", not as Google rank or measured volume. No scraping of Google result pages, autocomplete, or paid tools.
- **R14.** Search strategist. Per school and topic, produces `search_strategy.json` and a readable `docs/strategy/<school>/<topic>.md`:
  - Cluster map: which single page or tool answers each query group, so two of our pages never compete for the same query
  - Win plan per page: the specific contribution that beats current results (a verified fact table, calculator, comparison, or step the others miss), target title/H1, answer-first intro, snippet-ready formatting (tables, numbered steps, definition sentence), FAQ block only where questions are real
  - Hub and internal-link plan: school hub, then topic hub, then guides and tools, with exact anchor text
  - Trust signals: sources section, methods page link, updated date, corrections link
  - Refresh cadence: per page, based on source volatility and season
  - Win criteria: what we will re-check in search to judge whether the page won, and when
  - The planner must include the win plan in the brief. The seo agent must check the draft against it.
- **R15.** Rank re-check. The analyst re-runs R13 for published pages on their refresh date and records whether our page appears for its target variants, labeled as observed via the search tool. Results go into the digest and feed the strategist. With no Search Console data, no causal claims (SPEC §21).
- **R16.** Pipeline per page, as a coordinator-run chain with a commit after each stage: search-intel → discovery → opportunity (decide) → search-strategist → researcher → planner → writer → editor → verifier (gates) → seo → publish (R8) → analyst schedules a re-check. Read-only agents may run in parallel, up to 4 at once (search-intel, discovery, researcher for different clusters). Stages that change files run one at a time.
- **R17.** Cornell first. Run R16 on the Cornell transfer-housing cluster:
  - complete BACKLOG S4 (primary pages fetched, claims verified, snippet estimates superseded) and S6 (NCES verification with checksum)
  - then S5, the West vs South Campus comparison

### Demand capture engine (niche-first)

- **R18.** Entity harvesting, the "always finding data" lane. From official directories and pages for each onboarded school, deterministically harvest named entities into the registry with source and date. Entities include every residence hall, dining location, library, bus route, parking lot, gym, major/program, transfer pathway, and student service. Each new entity triggers query hypotheses (R19). The harvest re-runs on each source's refresh date so new entities appear automatically.
- **R19.** Query expansion. For each entity, generate candidate queries from a versioned pattern library in `docs/strategy/query-patterns.md`. Patterns include:
  - `<entity> review`, `<entity> vs <entity>`, `<entity> room size`, `<entity> cost`
  - `is <entity> good for transfers`, `<entity> parking`, `how to get to <entity>`, `<entity> hours`
  - audience and situation variants
  - Generation is deterministic code, not a model. Every generated query is stored as a hypothesis (SPEC §10), never as observed demand, until R20 finds evidence.
- **R20.** Demand evidence, without paid tools. Search-intel promotes a hypothesis to observed only with recorded evidence. Each item counts as one point, and independent threads count separately:
  - it appears as a related or follow-up question in search results
  - independent forum or discussion threads asking it are visible in search results (titles and URLs only, no Reddit collection)
  - it appears in official FAQ wording
  - it appears in supplied keyword exports or, later, Search Console
  - D is scored from these anchors (SPEC §11). "Decent demand" means D ≥ 2.
- **R21.** Authority-gap scoring, computed deterministically from `serp_intel.json`. For the top 5 observed results on each variant, record:
  - whether a page dedicated to exactly this question exists
  - result type: official, aggregator, forum, news, or other
  - whether it is stale (more than 18 months old, or wrong academic year)
  - whether the answer is complete
  - whether it has evidence or sources
  - From these, compute an Authority Gap Index (AGI, 0 to 5):
    - high when the results are mostly forums, outdated pages, thin aggregators, or official pages that only partly answer
    - low when a dedicated, current, complete page already ranks
  - AGI feeds W and G. Pure navigational queries (e.g. "Cornell housing portal") are tagged navigational and rejected.
- **R22.** Niche-first selection (owner override of SPEC §11 ordering only; the thresholds stand). A cluster enters the sweet-spot queue when:
  - D ≥ 2, AGI ≥ 3, G ≥ 3, and E ≥ 3
  - at least one result is weak or missing (a forum, outdated page, thin aggregator, or partial official answer)
  - The queue is sorted by `niche_score = (AGI + G) × E × min(D, 3)`, with ties broken by seasonality urgency, then freshness risk. Production always takes the top of this queue. Head terms with a strong dedicated incumbent are logged as watch, not worked.
- **R23.** Capture format. For each sweet-spot cluster, the strategist picks the format that best wins that query:
  - an entity guide (the page type for "<hall> review" intent)
  - a comparison
  - a calculator
  - a section on an existing page
  - For review-intent queries, the page covers verified facts (room types, rates, location, distance, amenities, policies) plus a "what residents report" section that may only use permitted, attributed sources, stated with sample and limits (SPEC §9). No invented ratings or experiences. Without permitted experience sources, the page omits that section and says so. Title example: "Boldt Tower: Rooms, Cost, Location and What to Know (2026-27)".
- **R24.** Lane mix. Each iteration chooses its lane by a configurable ratio, after failing tests:
  - Production, the sweet-spot queue to publish: 50%
  - Discovery: R18 to R21: 30%
  - Maintenance, re-checks and backlog features: 20%
  - If a lane has no work, its share goes to the next lane. The ratio is set in `.env` (`CAMPUS_LANE_MIX=50,30,20`).

### Efficiency

- **R25.** Cheapest-first funnel. Run work from cheap to expensive and stop early:
  - deterministic harvest and expansion (no model)
  - search-intel on a sample of 2 variants
  - AGI and threshold check
  - only then primary-source research, writing, editing, and verification
  - A cluster that fails a threshold stops immediately and is logged with the reason. Expensive stages never run on unqualified clusters.
- **R26.** Caching and reuse.
  - Search results are cached per query for `CAMPUS_SERP_CACHE_DAYS` (default 14) and never re-searched inside that window.
  - Fetched sources reuse conditional requests and hashes.
  - Verified claims are shared across every page that needs them and never re-researched per page.
  - Agents receive artifact IDs and small packets, not whole files.
- **R27.** Batching. Discovery and search-intel process clusters in batches of up to 10 per iteration. Any new pattern or prompt runs on 3 items first. If it works, it scales to the batch. If it doesn't, it gets fixed first (Anthropic's batch guidance).
- **R28.** Right-sized agents. Each agent declares model and a `--max-turns` budget in its file:
  - classification and dedup run on haiku or in code
  - opus is reserved for editor, verifier, skill-scout, and strategist
  - A dispatch that exceeds its turn budget stops, returns partial findings, and is logged. It is never silently retried at a bigger model (SPEC §36 escalation rules apply).
- **R29.** Efficiency metrics in the digest and the dashboard:
  - turns and minutes per published page
  - per verified update
  - per qualified cluster
  - discovery yield (qualified clusters / hypotheses tested)
  - wasted-work rate (stages run on clusters later rejected)
  - The weekly analyst pass proposes the single highest-impact efficiency fix in STATE.md.
- **R30.** Skill coverage matrix. `docs/ops/skill-coverage.md` lists the required capabilities, and for each one the skill that covers it (an adopted external skill or an in-repo reference), its pinned version, and its eval score:
  - long-tail keyword and query research
  - SERP and competitor gap analysis
  - topical authority and cluster mapping
  - content briefs
  - editorial writing
  - substantive editing
  - on-page SEO (titles, meta, headings)
  - structured data / schema
  - internal linking
  - content refresh and decay detection
  - technical SEO audit
  - snippet and answer formatting
  - local and campus navigation content
  - Any capability with no covering skill becomes a skill-scout job. If nothing external beats baseline, the scout writes or improves the in-repo reference and benchmarks it.

Non-functional:

- Resumable: a crash loses at most the current stage. The next run continues from the DB queue and STATE.md with no duplicate jobs.
- Secrets only in `.env`. Logs, digests, and agent packets never contain secret values.
- Each agent gets a scoped evidence packet by artifact ID (SPEC §37), not the whole repo.

## 5. Inputs, data & interfaces

- `.env` (gitignored): `DATABASE_URL`, `CAMPUS_EXECUTION_MODE=session`, publish quotas, optional local WP credentials. `.env.example` lists names only.
- Hosted Postgres 15+ created by Ajay (e.g. Neon or Supabase free tier).
- Headless CLI: `claude -p "<prompt>" --allowedTools <list> --permission-mode dontAsk --max-turns <n> --output-format json`. Before relying on each flag, check it against `claude --help` for the installed version, and adapt if one differs.
- Subagent file format: check it against the installed Claude Code's docs (`/agents` or `claude --help`) before writing the files.
- New JSON schemas, with the common envelope from SPEC §15: `skill_eval.json`, `serp_intel.json`, `search_strategy.json`.
- Existing entry points: `cli run-once` (exit codes 0/10/11/20/30/1), `session_run`, `render.from_db`, `cd worker && pytest -q`.

## 6. Decisions already made

| Decision | Choice | Reason |
|---|---|---|
| Where it runs | Ajay's MacBook, local Claude Code | His call. Fixes the network blocker. |
| When it runs | When Ajay starts it, until stopped or out of work | His call. No schedulers. |
| Compute | In-session on subscription, no API key | No API billing. Dollar caps don't apply in session mode. |
| Data store | Hosted Postgres | Survives restarts; readable from any session. |
| Publishing | Auto-publish after gates, 1 new / 5 updates per day | Mass-publishing similar pages risks search penalties. |
| Loop driver | Bash loop of separate `claude -p` iterations | Fresh context per task; clean restarts. |
| Agent model | Claude Code subagents mapped to the existing 12 role contracts + 3 new | Reuses tested contracts; one coordinator. |
| Concurrency (owner override of SPEC §37) | Up to 4 parallel read-only agents; file-changing stages run one at a time; one delegation layer, no agent spawns agents | More throughput locally without edit conflicts. |
| Search data | WebSearch tool + official pages + supplied exports, labeled as observed | No paid providers, no Google scraping. |
| Targeting (owner override of SPEC §11 ordering) | Niche-first: decent demand + weak authority, sorted by niche_score; thresholds unchanged | Fastest path to ranking and traffic for a new domain. |
| Query generation | Deterministic pattern library, not a model | Cheap, repeatable, auditable. |
| Lane mix | 50 production / 30 discovery / 20 maintenance, configurable | Always finding data without starving publishing. |
| Architecture | Keep SPEC.md v3 | Built and tested; this adds an operating mode and agents. |

Do not revisit these. If one blocks progress, stop and record it in STATE.md.

## 7. Constraints & hard rules

Must:

- Use observed command output as evidence for every check.
- Commit and push after every stage that changes files, e.g. `S4: verify Cornell housing claims (specs/continuous-local-run.md R17)`.
- Keep all existing tests passing. New code gets tests.
- Follow Google Search Essentials and its spam policies. The strategy is to be the most useful, best-sourced answer, nothing else.

Must not:

- Weaken, bypass, or retune gates, rubric thresholds, or the critical-claim rule to publish. Held stays held until evidence supports it. Reason: verified facts are the product.
- Fabricate facts, sources, bylines, reviews, search volumes, rankings, or "live" status.
- Use spam tactics, including:
  - scaled near-duplicate or doorway pages
  - keyword stuffing, cloaking, or hidden text
  - link schemes or buying links
  - copying or spinning competitor content
  - fake FAQ questions or fake freshness (changing dates without substantive updates)
- Publish above quota.
- Write fake reviews, star ratings, or first-person resident experiences. "Review" intent is served by verified facts plus attributed, permitted experience evidence only.
- Treat generated query hypotheses as observed demand.
- Contact third parties or post anywhere.
- Install unreviewed or unpinned skills, plugins, or MCP servers; install anything globally; or add paid tools.
- Force-push, rewrite history, or commit secrets.
- Fetch past robots rules, logins, CAPTCHAs, or rate limits. Reddit stays disabled.
- Edit SPEC.md or this spec. Propose changes in STATE.md under "Proposed spec changes".

Enforced by hook / deny rule (in `.claude/settings.json`):

- Deny `Read(./.env)`, `Edit(./.env)`, `Bash(git push --force*)`, `Bash(git push -f*)`
- PreToolUse hook (exit 2) blocking edits to:
  - `SPEC.md` and `specs/**`
  - gate threshold constants in `worker/campus_worker/editorial/gates.py`
  - publish-quota defaults in `config.py`
  - `.claude/settings.json` itself
- PreToolUse hook blocking writes into `.claude/skills/` unless `docs/ops/skill-evaluations.md` already lists that skill as adopted with its SHA

## 8. Acceptance tests (Definition of Done)

- [ ] **AT1.** `scripts/doctor.sh` prints PASS for every required item on the Mac and exits 0. With `DATABASE_URL` unset, it fails the DB item and exits non-zero.
- [ ] **AT2.** Migrations apply to the hosted database. Rerunning is a no-op.
- [ ] **AT3.** `scripts/run.sh --max 3` runs 3 iterations, writes 3 R10 log lines with every field, pushes at least one commit, and updates STATE.md.
- [ ] **AT4.** `scripts/stop.sh` mid-iteration: the iteration commits, the stop reason is `stop_file`, and no new iteration starts.
- [ ] **AT5.** A second `run.sh` while one is active exits 11 ("locked").
- [ ] **AT6.** A forced-failure test flag stops the loop after 3 consecutive failures (`consecutive_failures`).
- [ ] **AT7.** A simulated usage-limit fixture exits 20 (`usage_paused`), with no retry inside 60 seconds.
- [ ] **AT8.** In session mode, in-session work is never blocked by dollar caps and still writes ledger usage entries. API-mode cap tests still pass.
- [ ] **AT9.** Quota 1 with 3 gated pages: 1 publishes, 2 queue.
- [ ] **AT10.** All 15 agent files exist, parse, and declare a contract. A test dispatches each against a fixture packet, and every one returns JSON that validates against its schema.
- [ ] **AT11.** Skill scout run: `docs/ops/skill-evaluations.md` lists at least 10 candidates with the R12 fields, at least 5 source-reviewed with accept/reject reasons, and benchmark results for every survivor against baseline. Any adopted skill is vendored with a SHA. Writing an unlisted skill into `.claude/skills/` is blocked by the hook.
- [ ] **AT12.** Search intel for the Cornell transfer-housing cluster: `serp_intel.json` validates and has 2 variants with up to 10 observed results each, dated and labeled "observed via search tool".
- [ ] **AT13.** Strategy: `docs/strategy/cornell-university/housing.md` exists with every R14 section. The cluster map shows no two pages targeting the same query group, and the planner's brief contains the win plan.
- [ ] **AT14.** S4: the transfer-housing guide's critical claims cite fetched primary snapshots, and the gate result is recorded. If it passes, it publishes under R8 and the seo agent's checklist against the win plan is attached. If it fails, the reason is in the digest.
- [ ] **AT15.** S6: Cornell `identity_status = verified`, with the NCES checksum stored.
- [ ] **AT16.** The digest for the run day exists with every R9 section.
- [ ] **AT17.** Hooks: test edits to SPEC.md, gate thresholds, and `.claude/settings.json` are blocked with the hook message.
- [ ] **AT18.** `cd worker && pytest -q` passes in full, `scripts/check_css.py` passes, and `scripts/qa_screens.js` reports 0 problems.
- [ ] **AT19.** Harvest: running R18 on Cornell housing official pages stores every residence hall listed there as an entity with source URL and date (count matches the official list). A test with a fixture page adds a new hall on re-run.
- [ ] **AT20.** Expansion: R19 produces queries for each entity from the pattern library, all with status hypothesis. A test confirms no hypothesis is counted as demand.
- [ ] **AT21.** AGI: unit tests with fixture `serp_intel.json`:
  - forum-only results score AGI ≥ 4
  - a dedicated current official page scores ≤ 1
  - a navigational query is tagged and rejected
- [ ] **AT22.** Sweet-spot queue: from a fixture set of 10 clusters, exactly the ones meeting R22 are queued, in niche_score order, and head terms are marked watch. A live run on Cornell housing lists the top 10 sweet-spot clusters with D, AGI, G, E, and niche_score in the digest.
- [ ] **AT23.** Funnel: a test cluster failing AGI never dispatches researcher, writer, editor, or verifier (asserted from the dispatch log).
- [ ] **AT24.** Cache: repeating a search-intel job inside 14 days makes zero new search calls (asserted from the ledger).
- [ ] **AT25.** One review-intent entity guide (e.g. a residence hall) completes R16. It contains no ratings or unattributed experiences, and its experience section is either attributed with sample and limits or omitted with a stated reason.
- [ ] **AT26.** The digest shows every R29 efficiency metric with real values from the run.
- [ ] **AT28.** After `scripts/rebuild_from_repo.sh` on an empty hosted database:
  - 6,072 institutions, all pending_verification
  - Cornell disambiguation returns 3 entities
  - 8 discovery questions, 17 Cornell claims (all estimate), and 1 held transfer-housing page version
  - Running the script a second time changes no counts.
- [ ] **AT29.** `scripts/doctor.sh` prints the installed version of every R32 toolchain item. A test DB separate from the hosted one is configured, and `pytest -q` passes against it on the Mac.
- [ ] **AT30.** A fresh Claude Code session in the repo lists national-college-publishing among available skills. It can open all 12 references through the symlink. `.claude/settings.json` is committed and loads without errors.
- [ ] **AT31.** On the Mac, local WordPress staging starts, `cli status` shows the CMS adapter connected, and publishing the same fixture page twice creates no duplicate (hash no-op).
- [ ] **AT32.** `scripts/backup.sh` against the hosted database and `scripts/restore_test.sh` into the local test DB both pass.
- [ ] **AT27.** `docs/ops/skill-coverage.md` lists every R30 capability with a covering skill and eval score, or an open skill-scout job.

Verification method: command output in the final report, plus commit SHAs and file paths.

## 9. Milestones (build order)

1. Mac parity: toolchain, local test DB, WordPress staging, backups (AT29, AT31, AT32)
2. Doctor + hosted DB + rebuild from repo (AT1, AT2, AT28)
3. Project skill + `.claude/settings.json` + guardrail hooks + CLAUDE.md section (AT30, AT17)
4. Execution mode + publish quota (AT8, AT9)
5. Run loop + stop conditions + run log (AT3 to AT7)
6. Agent team: 15 subagent files + 3 new schemas + dispatch tests (AT10)
7. Skill scout first pass + eval set + coverage matrix (AT11, AT27)
8. Demand engine: harvest, expansion, AGI, sweet-spot queue, lane mix, funnel, cache (AT19 to AT24)
9. Search intel + strategist on Cornell housing (AT12, AT13)
10. Cornell pipeline through R16: S4, S6, the first review-intent entity guide, then S5 (AT14, AT15, AT25)
11. Digest with efficiency metrics + full regression (AT16, AT18, AT26)

Commit after each milestone.

## 10. Open questions

None blocking. Owner actions before milestone 1 can pass:

- create the hosted Postgres database and put `DATABASE_URL` in `.env`
- confirm the repo is cloned on the Mac with push access

## 11. Ambiguity rule

If the spec is silent, choose the simplest option consistent with sections 1, 6 and 7, log it under "Assumptions" in STATE.md and the final report, and keep going. If the spec contradicts itself or the codebase, stop and ask.

## Kickoff prompt

(paste into a fresh Claude Code session, in plan mode, from the repo on your Mac)

```
Read specs/continuous-local-run.md in full. It is the source of truth for
this task. Also read CLAUDE.md, STATE.md, BACKLOG.md and SPEC.md §15, §35,
§37, §38 for context. Work on a branch named continuous-local-run. Reference
the spec requirement (R#) and acceptance test (AT#) in every commit message.
Open a PR whose description is your final report.

1. Before writing any code, give me a plan: restate the objective in one
   sentence, list the milestones in order, and map every acceptance test
   (AT1 to AT32) to the step that satisfies it. List anything in the spec
   that is ambiguous, contradicts itself, or conflicts with the existing
   code, and confirm the installed claude CLI flags and subagent format.
2. Do not change anything in "Decisions already made" or build anything in
   "Out of scope." Never weaken a gate to get something published. If a
   hard rule blocks you, stop and tell me.
3. After I approve, execute milestone by milestone. After each one, run its
   verification and commit. If a check fails, fix it before moving on.
4. When finished, report:
   - Acceptance-test checklist: each AT# PASS/FAIL with evidence
     (command + actual output, or file path)
   - Assumptions you made where the spec was silent
   - Anything you'd flag before I start the first real run
Do not report done unless every AT# has evidence.
```
