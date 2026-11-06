# Plan: continuous local run + agent team

Source of truth: `specs/continuous-local-run.md` (v2.5, 2026-11-06). Written before any code, per the kickoff prompt step 1. Status: **approved by owner 2026-11-06 with all resolutions below; executing milestone by milestone.**

## Objective (one sentence)

One command on Ajay's Mac runs campus-publication unattended: a coordinator session dispatches 15 subagents to map every school and town topic, find niche searches with real demand and weak incumbents, and produce verified, competitor-beating pages without a production cap, publishing locally at once and going live under a ramp, until stopped or out of work.

## Environment observed on 2026-11-06 (this Mac)

| Item | Observed | Spec needs |
|---|---|---|
| macOS / CPU | 26.6, arm64 | ok |
| `claude` CLI | **not installed** (desktop app only, no binary on PATH) | install, user-space, no sudo |
| Homebrew | **not installed**; `sudo` needs a password | owner installs Homebrew once |
| Python | 3.9.6 (system) | 3.13 via Homebrew |
| PostgreSQL client/server | none | 16 via Homebrew (local test DB + pg_dump) |
| PHP | none | 8.3 via Homebrew |
| Node | 22.23.4 (`~/.local`) | ok |
| git / gh | present, `gh` logged in as ajaysharma2044, push works | ok |
| `flock` | **absent on macOS** (`shlock` exists) | lock must not use flock |
| `DATABASE_URL` / `.env` | none | owner supplies hosted Postgres URL |
| Repo | cloned, branch `continuous-local-run` | ok |

## Claude Code facts confirmed against the official docs (CLI not yet installed; re-confirm against `claude --help` in M1)

- Flags exist as spelled in the spec: `-p/--print`, `--allowedTools` (alias `--allowed-tools`), `--disallowedTools`, `--permission-mode` with values `default|acceptEdits|plan|auto|dontAsk|bypassPermissions`, `--max-turns` (print mode only), `--output-format text|json|stream-json`, `--model`, `--append-system-prompt`, `--settings`, `--agents`.
- JSON output documents `result`, `session_id`, `total_cost_usd`; exit code 0 on success, non-zero on failure, 143 on SIGTERM. Rate-limit and auth categories (`rate_limit`, `authentication_failed`, `billing_error`) are documented only as stream-json `api_retry` events, so `run.sh` classifies usage pauses from result text plus exit status, and M5 records the shape actually observed.
- Subagents: `.claude/agents/<name>.md` with frontmatter `name`, `description`, `tools` (comma list), `model` (`sonnet|opus|haiku|inherit|full id`), plus `maxTurns`, `permissionMode`, `disallowedTools`, `skills`, `hooks`, `memory`, `background`. Unrecognized fields are silently ignored, so names must match exactly.
- Hooks: `PreToolUse` with `matcher` (e.g. `Edit|Write`) and `hooks:[{type:"command", command, timeout}]`; stdin carries `tool_name` and `tool_input` (`file_path`, `content`/`old_string`/`new_string`, `command`); exit 2 blocks and stderr is the message.
- Permissions: rules are `Tool` or `Tool(specifier)`; `Bash(prefix *)`, `Read(./.env)`, `Edit(path)`, `WebFetch(domain:host)`; evaluated deny → ask → allow; `.claude/settings.local.json` must be gitignored by hand when created manually.
- Skills: `.claude/skills/<name>/SKILL.md`; a symlinked directory is explicitly supported.

## Milestones and acceptance-test mapping

| # | Milestone | Builds | Satisfies |
|---|---|---|---|
| M1 | Mac parity | `claude` CLI (native installer, `~/.local/bin`); Homebrew python@3.13, postgresql@16, php; `pip install -e "worker[dev]"`; Playwright Chromium; local `campus_research_test` DB; `wp-local/` clone + setup; macOS ports of `wp_local.sh` (BSD sed), `backup.sh`/`restore_test.sh` (`shasum -a 256`, no `su postgres`), `continuation_demo.sh` (no flock); full pytest | AT29, AT31, AT32 |
| M2 | Doctor + hosted DB + rebuild | `scripts/doctor.sh`; migrations on hosted DB; `scripts/rebuild_from_repo.sh` (migrate → seed → IPEDS import with checksum → replay 8 questions, 17 estimate claims, 1 held version), idempotent | AT1, AT2, AT28 |
| M3 | Project skill + settings + hooks + CLAUDE.md | `.claude/skills/national-college-publishing` symlink; `.claude/settings.json` (deny rules, allowlist, hooks); `.claude/hooks/guard.sh`; `docs/ops/skill-evaluations.md` seeded with the in-repo baseline; CLAUDE.md "Local run mode" | AT30, AT17 |
| M4 | Execution mode + unthrottled production + live ramp | `CAMPUS_EXECUTION_MODE`; session-mode ledger entries (unpriced, never blocking); `pages.ready_at`/ready queue; local publish with no quota (`build/site/` + WP staging); `CAMPUS_LIVE_RAMP` parser and live-release scheduler ordered by niche_score; indexing-hold rule; migration 0003 part 1 | AT8, AT9 |
| M5 | Run loop | `scripts/run.sh` (caffeinate, mkdir lock, `--max`, `--mode`, `--force-fail`, usage-pause detection, exit 11/20), `scripts/stop.sh`, `scripts/iteration_prompt.md`, run-log writer → `build/runs/*.jsonl` | AT3–AT7 |
| M6 | Agent team | 15 files in `.claude/agents/`; schemas `skill_eval.json`, `serp_intel.json`, `search_strategy.json`; envelope role enum +3; `campus_worker/agents/dispatch.py` (packet by artifact id, turn budget, partial-result logging, ≤4 parallel read-only); fixture-packet validation test; opt-in live dispatch test | AT10 |
| M7 | Skill scout first pass | `docs/ops/skill-eval-set.md`, `docs/ops/skill-coverage.md`, scout run → `docs/ops/skill-evaluations.md`; usage tools evaluated per `docs/ops/usage-optimization.md` | AT11, AT27 |
| M8 | Demand engine + sweep + open discovery | migration 0003 part 2 (`places`, `place_id` columns, topics seed extension with audiences, entity sources, query hypotheses, serp cache, strategies, access modes, auto-topics); `docs/strategy/topic-taxonomy.md` (22 topics + alumni/parents/jobs audience sets); `harvest.py` (school + town); `query-patterns.md` (incl. audience patterns) + `expand.py`; `permissions.py` access modes; Reddit `search_observation` searches + fixture-tested `api_authorized` collector (off); `agi.py`; `sweetspot.py`; `lanes.py`; `funnel.py` (dispatch log); serp cache in ledger; `sweep.py` → `docs/strategy/opportunity-map.md` + `build/opportunity-map.csv`; `run.sh --mode sweep`; `discovery.auto_topic` (≥3 independent unmatched questions → new topic + digest entry); Class Roster API collector; Stack Exchange API collector (attribution); `data/first_party/` loader; audience-guide merge check | AT19–AT24, AT33–AT36, AT40, AT45, AT46 |
| M9 | Search intel + strategist on Cornell housing | live search-intel on the transfer-housing cluster → `serp_intel.json`; strategist → `docs/strategy/cornell-university/housing.md` + `search_strategy.json`; planner brief carries the win plan | AT12, AT13 |
| M10 | Two-tier pages + process graphs + expansion + volume reporting | `tier2.py` (≥6 verified claims, ≥1 observed query, <60% fact-table overlap, gates; pair comparisons only on observed queries); `processes.py` + migration 0004 (process graphs: states, transitions, nodes L0–L3 with inheritance, per-node page decision standalone/section/none); process navigator tool (server-rendered + progressive JS, from the graph); Cornell changing-majors graph filled from official pages; `expansion.py` (`CAMPUS_EXPANSION_LIST`, sequential, trigger = map complete + 10 beat-review passes); digest/dashboard counts by tier/school/topic + projected days to 1,000 and 5,000 | AT41–AT43, AT47 |
| M11 | Writing quality + SEO gate | `docs/editorial/style.md`; filler-phrase check in `editorial/checks.py`; information-gain check in `briefs.py` (watch when <3 novel claim-linked items); competitor-beat review record + one resend then hold; `seo.seo_gate` covering every R45 item; `/towns/` URL policy | AT37–AT39, AT44 |
| M12 | Cornell pipeline (R16/R17) | S4 fetch primary pages, extract claims, supersede estimates, verifier gate; S6 NCES HD2024 download + checksum → `identity_status=verified`; first review-intent entity guide; S5 comparison; first non-housing page and first town page with beat-review records | AT14, AT15, AT25, AT38 |
| M13 | Digest + metrics + regression | `digest.py` (R9 sections, R29 metrics, R44 counts), dashboard tiles, full `pytest -q`, `check_css.py`, `qa_screens.js` | AT16, AT18, AT26 |

Every AT from 1 to 47 appears exactly once above. Each milestone ends with its verification run and a commit tagged with R# and AT#.

## Ambiguities, contradictions, conflicts with existing code

Items marked **(decide)** need your answer; the rest are resolutions I will apply and log under Assumptions.

1. **(decide) Production vs SPEC §26 quota and existing publisher code.** `cms/publisher.publish_version` enforces `new_pages_per_day` only when a version is pushed with status `publish` in production; staging publishes are already unquota'd, which matches R8. Proposed: keep that code path, drive it from the ramp allowance instead of the fixed quota once a live domain exists, and record the §26 override under "Proposed spec changes" in STATE.md. Existing quota tests are rewritten to test the ramp, which is a behavior change to tested code.
2. **"Reddit stays disabled" (§7) vs R36 search observation now.** Resolved by reading: Reddit *collection* stays disabled (`api_authorized` collector built, tested on fixtures, never enabled without credentials); Reddit `search_observation` through WebSearch is allowed. `permissions.py` gains an `access_mode` enforcement so the two cannot be confused.
3. **Batch size.** R27 says 10 per iteration, R41 says 25 in sweep mode. Resolved: 10 in normal mode, 25 in sweep mode.
4. **`CAMPUS_LIVE_RAMP` format** is unspecified. Proposed `5x14,15` meaning 5/day for 14 days then 15/day; parser tested.
5. **Hook now guards live-ramp defaults** in config.py, not the old quota defaults. `Quotas.new_pages_per_day`/`verified_updates_per_day` stay for API mode and are no longer used for local publishing. The hook guards the default literal values only, so M4's other config.py edits proceed (M3 lands first).
6. **The settings.json hook blocks me too.** After M3 this session cannot edit `.claude/settings.json`, `specs/**`, gate constants, or ramp defaults. M3 writes settings.json complete for every later milestone's commands. If an entry proves missing later, I stop and ask you to edit it. Bash commands that reference protected paths are also checked (best effort).
7. **Linux-only scripts.** `continuation_demo.sh` uses `flock`; `restore_test.sh` uses `su postgres` and `sha256sum`; `backup.sh` uses `sha256sum`; `wp_local.sh` uses GNU `sed -i`. M1 ports them with an OS switch.
8. **AT10 live dispatch costs subscription usage.** Default test: files parse, declare a contract, fixture response validates. `pytest -m live` really dispatches each agent once; run once for AT10 evidence.
9. **Envelope role enum** has 12 roles; M6 adds `skill_scout`, `search_intel`, `search_strategist`; schema version stays `1.x`.
10. **(decide) Hosted Postgres major version.** `pg_dump` must be at least the server's major. Neon and Supabase default to 17; the spec installs 16 locally. Create the hosted DB as Postgres 16, or tell me to install the 17 client.
11. **"settings.json with the R11 agents".** Agents are files under `.claude/agents/`; settings.json carries deny rules, allowlist and hooks only.
12. **Application password into `.env`.** I am denied `Read(./.env)`; `scripts/wp_local.sh install` appends the password to `worker/.env` without echoing it.
13. **`.env` location.** Spec says `.env`; code and docs use `worker/.env`. `worker/.env` stays canonical; every new script sources it.
14. **Replayed ids.** Replayed rows get new UUIDs; the old research report keeps its ids as history and the rebuild writes `docs/research/rebuild-id-map.json`.
15. **Concurrency.** SPEC §37's `max_concurrent_model_tasks=2` stays for the API-mode worker; the coordinator's parallel subagents get `CAMPUS_PARALLEL_READONLY_AGENTS=4`.
16. **Exit codes not specified.** `--max` reached → 12 (as `continuation_demo.sh`), consecutive failures → 1, locked → 11, usage paused → 20, stop file or no work → 0.
17. **Topics seed.** Migration 0001 is checksummed and seeds 12 topics; R33's taxonomy (12 school + 10 town topics) is added by migration 0003 with a `scope` column (`school|town`), not by editing 0001.
18. **`places` do not exist in the schema.** Migration 0003 adds `places` (Ithaca, Tompkins County) and nullable `place_id` on entities, source_registry, questions, intent_clusters, pages; `institution_id` becomes nullable where town rows need it, with a CHECK that exactly one scope is set.
19. **URL policy** in `seo.py` only knows `/schools/`; M11 adds `/towns/<town>/<topic>/<slug>/` and the `title_and_description` limit drops from 65 to 60 per R45.
20. **R45 "at least 1 existing page updated to link back"** cannot hold for the very first page under a hub. Resolved: hub pages count as existing pages and are updated by the renderer; the gate requires at least one non-hub backlink only once a sibling page exists.
21. **R43 list has 24 schools**, not 25. Used as given; no school added.
22. **WebSearch `site:` operator and Reddit visibility** in headless subagents are unverified on this account; AT36 is where that gets confirmed. If WebSearch does not honor `site:`, Reddit occurrences come from plain topic searches filtered by domain, and I report the difference.
23. **R8 indexing hold (20% unindexed after 14 days)** cannot be exercised without a live domain; fixture-tested only, like the ramp.
24. **R38 "fresh editor dispatch"**: every subagent dispatch starts with empty context, so the beat review is a second `editor` dispatch with a packet containing only the draft, the claim table and the three competitor summaries, never the drafting transcript.
26. **Class Roster API (R46)** is Cornell's public JSON API at `classes.cornell.edu/api/2.0`; it is registered as `api_authorized` with no credential, rate-limited by the fetcher, and its terms are recorded in the permissions registry before the first call. **Stack Exchange API** runs unauthenticated at the public quota with CC BY-SA attribution stored on every question row. **`data/first_party/`** accepts CSV or JSONL with `question`, `audience`, `topic_hint`, `asked_on` only; a loader rejects any row containing an email, phone, or name-like field.
27. **R47 "every college pair that Cornell's official pages document"**: L1 nodes are created only for pairs an official page describes; pairs with no documented path get no node, and the navigator says so for that path.
25. **AT38 and M12 ordering.** AT38 needs the first published non-housing page, which M12 produces; M11 builds the review and proves it on fixtures. Both are mapped to the milestone that produces their evidence.

## Owner actions before M1 can pass

1. Install Homebrew (needs your password once; everything after runs without sudo):
   `/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"`
2. Create the hosted Postgres database (Postgres 16 preferred, see item 10) and put `DATABASE_URL=...` in `worker/.env`. I will never read that file; `doctor.sh` reports reachability only.

I can start M1's user-space parts (CLI install, script ports, `.env.example` additions) before either action lands.
