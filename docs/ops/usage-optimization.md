# Usage optimization: baseline and tool evaluation (SPEC §38, §39)

**Status: baseline recorded; no optimizer hook installed.** Nothing in this document claims a saving.

## Baseline (this build session, 2026-11-02)
- Interface: Claude Code cloud session on subscription/session auth. The worker has **no** model credential (`ANTHROPIC_API_KEY` unset), so every model-backed worker job holds with `provider_auth`; worker spend to date is $0.00 and the usage ledger is empty except for test fixtures in the test database.
- Session-level token totals are not exposed to the agent programmatically in this environment; the Session Report plugin was not available in the session (plugin catalog not installed). Record the owner-visible usage figure for this session from the Claude Code usage panel as the baseline before trialling any optimizer.
- Measured engineering throughput of the session: 130 passing tests, 18 preview pages, one verified WordPress round-trip, in a single session with no "continue" prompts.

## Candidates reviewed (not installed)
| Tool | What it would do | Decision | Why |
|------|------------------|----------|-----|
| Anthropic Session Report | per-session token/tool diagnostics | **adopt first when available** | read-only; needed to produce a before/after at all |
| alexgreensh/token-optimizer | audits, compaction checkpoints, usage hooks | trial after baseline, alone | installs hooks; must be read and pinned first; overlaps with context-mode compaction |
| mksglu/context-mode | focused retrieval from large tool outputs | trial for research-heavy work only | risk: compression hiding footnotes/conflicts — final critical-claim checks must fetch raw source (`roles/runners.run_verifier(source_excerpts=…)` already requires raw excerpts) |
| rtk-ai/rtk | filters verbose dev-command output | trial for pytest/build output | low risk; must keep a `--raw` bypass for failure details |
| addyosmani context-engineering | instruction/context organisation | partially applied by hand | CLAUDE.md is short and routes to modules; no install needed |

Repository source, licenses and hook definitions were **not** fetched in this session (GitHub API blocked by the proxy; git clone would work). Do not install from memory: clone, read `hooks`, pin a commit, and record the rollback (`rm` the hook entry from `.claude/settings.json`).

## Fixed evaluation set (to run before/after any optimizer)
1. Clean structured extraction — `fixtures/synthetic/sources/fixture_hall_rates_v1.html` → `claims.extract_rate_table` (expected 6 claims, 0 warnings).
2. Conflicting policy — rates page vs brochure (`fixture_brochure_conflict.html`) → one open conflict, both claims blocked.
3. Audience-specific guide — `briefs.audience_guide_justified` on transfer eligibility (expected: no page until rules differ).
4. Multi-source comparison — `tools.comparison.compare` on two fixture halls (expected $460 difference, three unknown cells).
5. Long PDF — `fixture_rate_sheet.pdf` (two academic years detected, footnote kept, review flag set).
6. Noisy test failure — run `pytest -q` with a deliberately broken assertion and confirm the failure text survives any output filter.
7. Resumable milestone — `scripts/continuation_demo.sh 8 --seed-demo` interrupted after iteration 1, resumed; expected no duplicate job completions.

Record per run: accepted quality (gates), factual errors, source omissions, input/output/cached tokens, tool calls, retries, elapsed time, priced spend. Separate one-time audit overhead from steady state. Bytes saved ≠ tokens ≠ dollars.

## Prompt caching
The model adapter puts stable role instructions in `system` and per-task material in `user`, which is the layout prompt caching needs; cache hit/write counts are recorded in `runs.usage` (`cached_tokens`) once a real provider is connected. No keep-alive calls are made.

## Billing mode
`python -m campus_worker.cli status` prints `auth_mode`: `none` (current), or `api_key` with the note that API usage is billed per token and is **not** subscription allowance.
