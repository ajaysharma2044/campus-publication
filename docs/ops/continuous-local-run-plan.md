# Plan: continuous local run + agent team

Source of truth: `specs/continuous-local-run.md` (v2.1). Written 2026-11-06 before any code, per the kickoff prompt step 1. Status: **awaiting owner approval**.

## Objective (one sentence)

One command on Ajay's Mac runs campus-publication unattended: a coordinator session dispatches 15 subagents to find niche, weakly-answered student searches, produce verified pages for them within daily publish quotas, and commit every result to GitHub and a hosted Postgres database until stopped or out of work.

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
- JSON output documents `result`, `session_id`, `total_cost_usd`; exit code is 0 on success, non-zero on failure, 143 on SIGTERM. Rate-limit / auth categories (`rate_limit`, `authentication_failed`, `billing_error`) are documented only as stream-json `api_retry` events, so `run.sh` will classify usage pauses from the result text plus exit status, and M5 records the shape actually observed.
- Subagents: `.claude/agents/<name>.md` with frontmatter `name`, `description`, `tools` (comma list), `model` (`sonnet|opus|haiku|inherit|full id`), plus `maxTurns`, `permissionMode`, `disallowedTools`, `skills`, `hooks`, `memory`, `background`. Unrecognized fields are silently ignored, so names must match exactly.
- Hooks: `PreToolUse` with `matcher` (e.g. `Edit|Write`) and `hooks:[{type:"command", command, timeout}]`; stdin carries `tool_name` and `tool_input` (`file_path`, `content`/`old_string`/`new_string`, `command`); exit 2 blocks and stderr is the message.
- Permissions: rules are `Tool` or `Tool(specifier)`; `Bash(prefix *)`, `Read(./.env)`, `Edit(path)`, `WebFetch(domain:host)`; evaluated deny → ask → allow; `.claude/settings.local.json` must be gitignored by hand when created manually.
- Skills: `.claude/skills/<name>/SKILL.md`; a symlinked directory is explicitly supported.

## Milestones and acceptance-test mapping

| # | Milestone | Builds | Satisfies |
|---|---|---|---|
| M1 | Mac parity | `claude` CLI (native installer, `~/.local/bin`); Homebrew packages python@3.13, postgresql@16, php; `pip install -e "worker[dev]"`; Playwright Chromium; local `campus_research_test` DB; `wp-local/` clone + setup; macOS fixes to `wp_local.sh` (BSD sed), `backup.sh`/`restore_test.sh` (`shasum -a 256`, no `su postgres`); run full pytest | AT29, AT31, AT32 |
| M2 | Doctor + hosted DB + rebuild | `scripts/doctor.sh`; migrations on hosted DB; `scripts/rebuild_from_repo.sh` (migrate → seed → IPEDS import with checksum → replay 8 questions, 17 estimate claims, 1 held version from `docs/research/*.json`), idempotent | AT1, AT2, AT28 |
| M3 | Project skill + settings + hooks + CLAUDE.md | `.claude/skills/national-college-publishing` symlink; `.claude/settings.json` (deny rules, allowlist, hooks); `.claude/hooks/guard.sh`; `docs/ops/skill-evaluations.md` seeded with the in-repo baseline; CLAUDE.md "Local run mode" section | AT30, AT17 |
| M4 | Execution mode + publish quota | `CAMPUS_EXECUTION_MODE`, session-mode ledger entries (unpriced, never blocking), `CAMPUS_PUBLISH_*` quota env, publish queue with overflow-to-next-day, `cms/publisher` render-to-`build/site/` path | AT8, AT9 |
| M5 | Run loop | `scripts/run.sh` (caffeinate, mkdir lock, `--max`, `--force-fail`, usage-pause detection, exit codes 11/20), `scripts/stop.sh`, `scripts/iteration_prompt.md`, run log writer, `build/runs/*.jsonl` | AT3, AT4, AT5, AT6, AT7 |
| M6 | Agent team | 15 files in `.claude/agents/`; schemas `skill_eval.json`, `serp_intel.json`, `search_strategy.json`; envelope role enum +3; `campus_worker/agents/dispatch.py` (packet by artifact id, turn budget, partial-result logging, parallel ≤4 read-only); fixture-packet validation test; opt-in live dispatch test | AT10 |
| M7 | Skill scout first pass | `docs/ops/skill-eval-set.md`, `docs/ops/skill-coverage.md`, scout run → `docs/ops/skill-evaluations.md` (≥10 candidates, ≥5 source-reviewed, benchmarks), usage tools (Session Report, token-optimizer, context-mode, rtk) evaluated per `docs/ops/usage-optimization.md` | AT11, AT27 |
| M8 | Demand engine | migration 0003 (entity sources, query hypotheses, serp cache, strategies, publish queue); `harvest.py`, `query_patterns.md` + `expand.py`, `agi.py`, `sweetspot.py`, `lanes.py`, `funnel.py` (dispatch log), serp cache in ledger | AT19–AT24 |
| M9 | Search intel + strategist on Cornell housing | live search-intel on the transfer-housing cluster → `serp_intel.json`; strategist → `docs/strategy/cornell-university/housing.md` + `search_strategy.json`; planner brief carries win plan | AT12, AT13 |
| M10 | Cornell pipeline (R16/R17) | S4 fetch primary pages, extract claims, supersede estimates, verifier gate; S6 NCES HD2024 download + checksum → `identity_status=verified`; first review-intent entity guide; then S5 comparison | AT14, AT15, AT25 |
| M11 | Digest + metrics + regression | `digest.py` (R9 sections + R29 metrics), dashboard tiles, full `pytest -q`, `check_css.py`, `qa_screens.js` | AT16, AT18, AT26 |

Every AT from 1 to 32 appears exactly once above. Each milestone ends with its verification run and a commit tagged with R# and AT#.

## Ambiguities, contradictions, conflicts with existing code

1. **R22 vs SPEC §11 threshold (needs your answer).** R22 says thresholds stand, and §11's advance threshold is priority ≥ 65 with E ≥ 3, G ≥ 3. A sweet-spot cluster at D=2, G=3, E=3, W=3, M=0 scores 49, so almost nothing niche would ever advance. §11 allows "documented editorial exceptions". Proposed: `scoring.decide` keeps 65; a sweet-spot advance is recorded as an editorial exception with rationale `niche_first (R22)` in `opportunity_scores.editorial_exception`. No gate or rubric is touched.
2. **Quota env names.** Spec: `CAMPUS_PUBLISH_NEW_PER_DAY` / `CAMPUS_PUBLISH_UPDATES_PER_DAY`. Code: `CAMPUS_QUOTA_NEW_PAGES_PER_DAY` / `CAMPUS_QUOTA_UPDATES_PER_DAY`. Proposed: spec names win, old names remain as fallback; the guard hook protects the default literals for both.
3. **The settings.json hook blocks me too.** Once M3 lands, this session cannot edit `.claude/settings.json`, `specs/**`, gate constants, or quota defaults either. So M3 writes a complete settings.json (allowlist for every later milestone's commands). If a later milestone proves an entry missing, I stop and ask you to make the edit. The hook also inspects Bash commands that reference protected paths (best effort; Bash can't be fully policed).
4. **M3 before M4.** Hooks are installed before config.py changes. The hook therefore guards only the quota default values, not the whole file, so M4 can add `CAMPUS_EXECUTION_MODE` to config.py.
5. **Linux-only scripts.** `continuation_demo.sh` uses `flock` (absent on macOS); `restore_test.sh` uses `su postgres` and `sha256sum`; `backup.sh` uses `sha256sum`; `wp_local.sh` uses GNU `sed -i`. M1 ports them (mkdir lock, `shasum -a 256`, plain `psql` role, `sed -i ''`), keeping Linux behavior via a small OS switch.
6. **AT10 live dispatch costs subscription usage.** Default test: all 15 files parse, declare a contract, and a fixture response per agent validates against its schema. A separate `pytest -m live` test really dispatches each agent once with `claude -p`; run once for the AT10 evidence.
7. **Envelope role enum** has 12 roles; M6 adds `skill_scout`, `search_intel`, `search_strategist`. Schema version stays `1.x`.
8. **Hosted Postgres major version.** `pg_dump` must be at least the server's major. Neon and Supabase default to Postgres 17; the spec installs 16 locally. Please create the hosted DB as Postgres 16, or tell me to install the 17 client instead.
9. **"settings.json with the R11 agents".** Agents are files under `.claude/agents/`, not settings keys. settings.json will carry deny rules, the allowlist and hooks only.
10. **Application password into `.env`.** The deny rule stops me reading `.env`; `wp_install.php` prints the password. `scripts/wp_local.sh install` will append it to `worker/.env` directly without echoing it.
11. **`.env` location.** Spec says `.env`; existing docs and code use `worker/.env`. Proposed: `worker/.env` stays canonical; every new script sources it.
12. **Replayed ids.** The cloud DB is gone, so replayed rows get new UUIDs. `docs/research/cornell-transfer-housing-run.md` keeps its old ids as history; the rebuild writes `docs/research/rebuild-id-map.json`.
13. **Concurrency.** SPEC §37 and `config.Quotas.max_concurrent_model_tasks=2` govern the API-mode worker and stay. The coordinator's parallel read-only subagents get a separate `CAMPUS_PARALLEL_READONLY_AGENTS=4`.
14. **Exit code for the `--max` ceiling and consecutive failures.** Not specified. Proposed: `--max` reached → 12 (as `continuation_demo.sh`), consecutive failures → 1, locked → 11, usage paused → 20, stop file / no work → 0.
15. **WebSearch inside headless subagents** has not been exercised on this account; M6's live test is where it gets confirmed.

## Owner actions before M1 can pass

1. Install Homebrew (needs your password once; everything after runs without sudo):
   `/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"`
2. Create the hosted Postgres database (Postgres 16 preferred, see item 8) and put `DATABASE_URL=...` in `worker/.env`. I will never read that file; `doctor.sh` reports reachability only.

I can start M1's user-space parts (CLI install, repo script ports, `.env.example` additions) before either action lands.
