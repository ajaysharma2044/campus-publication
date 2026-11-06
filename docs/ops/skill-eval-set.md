# Skill evaluation set (specs/continuous-local-run.md R12; AT11)

Fixed tasks for benchmarking any candidate SEO / writing / research skill against the in-repo baseline
(`skills/national-college-publishing/references/`). Every task uses synthetic fixtures or already-observed
public evidence; none asks for new institution facts. Score each task 0–10 on the rubric below; a hard-rule
violation (fabrication, unsourced claim, spam tactic, quota/gate change) is an automatic 0 and a regression.

## Rubric (per task)
- 0–4 correctness against the fixture ground truth (facts, ids, arithmetic)
- 0–3 usefulness to the reader task (answer first, specifics, decision-relevant)
- 0–3 contract discipline (valid JSON contract, unknowns stated as unknown, no filler)
Record errors (count), turns, seconds. Baseline = the same task run with the in-repo reference only.

## Tasks
1. **Cluster brief A — housing.** Packet: `fixtures/synthetic/sources/fixture_hall_rates_v1.html` claims (6 verified rate claims), cluster "is fixture hall good for transfers". Produce a planner brief (planner.json) with ≥ 3 information-gain items tied to claim ids. Ground truth: double $12,042 per person per academic year; deposit: not stated anywhere in the fixture, so it must be marked unknown (any deposit amount in the brief is a fabrication); kitchen access unknown.
2. **Cluster brief B — town transit.** Packet: synthetic TCAT-style route fixture (`fixtures/synthetic/town/route_fixture.json`, created with M8): route 30, headway 15 min peak / 30 off-peak, last bus 11:40 pm. Cluster "how to get from Collegetown to the airport by bus". Brief must separate schedule facts (time-bound, academic year) from fare facts.
3. **Cluster brief C — parents.** Same housing fixture, audience "parents and families", question "what does my student pay and when". The audience-guide test must be applied: a separate parent page is justified only if the facts or steps differ (they do not in the fixture → section on the shared page).
4. **Draft edit.** Input: `fixtures/synthetic/editorial/draft_filler.md` (created with M11: a draft full of AI tells and one unsupported number). Output: editor.json with findings; the unsupported number must be flagged `unsupported`, every filler phrase flagged `filler`, body ≥ 200 chars, no new facts.
5. **Title and snippet.** Input: the fixture hall brief. Output: 3 title candidates ≤ 60 chars containing the primary query, one answer-first intro ≤ 50 words, meta description 120–155 chars. Ground truth checks are deterministic (`seo.seo_gate` title/meta rules).
6. **SERP gap analysis.** Input: `fixtures/synthetic/serp/forum_only.json`, `dedicated_official.json` and `navigational.json` (created with M8). Output: per result — dedicated?, type, stale?, complete?, sourced? — and the exact missing contribution. Ground truth: forum-only set → AGI ≥ 4; dedicated current official page → AGI ≤ 1; the `navigational.json` set ("cornell housing portal") → navigational, rejected.

## Usage-tool tasks (docs/ops/usage-optimization.md §Fixed evaluation set)
Run tasks 1–7 from that document before and after installing any single usage tool (Session Report, token-optimizer, context-mode, rtk), one tool at a time, and record accepted quality, factual errors, source omissions, tokens, tool calls, retries, elapsed time. Task 6 there (noisy test failure) must keep the failure text intact through any output filter.
