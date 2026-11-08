# Skill evaluations (specs/continuous-local-run.md R12, R30; AT11, AT27)

This file is the authority for what may live under `.claude/skills/`. The guard hook (`.claude/hooks/guard.sh`) blocks any write into `.claude/skills/<name>/` unless `<name>` appears below with status `adopted` and a 40-hex commit SHA, or as the in-repo baseline. Rollback for any adopted skill: delete its folder and revert the adopting commit.

last scout run: 2026-11-06 · runs: skill-scout-live-1.json, skill-scout-live-2.json, skill-scout-live-3.json

## Installed

| name | status | source | sha | license | eval (baseline → candidate) | installed |
|---|---|---|---|---|---|---|
| `national-college-publishing` | baseline (in-repo) | `skills/national-college-publishing/` (symlink) | in-repo | repo | baseline | 2026-11-06 |

## Candidates (R12: top 10 with url, author, license, last commit, stars, what it does, hooks/scripts)

| name | kind | url | author | license | last commit | stars | what it does | hooks | scripts | capabilities |
|---|---|---|---|---|---|---|---|---|---|---|
| `claude-seo` | plugin | https://github.com/AgriciDaniel/claude-seo | AgriciDaniel | MIT | 2026-11-01T06:07:26Z | 26975 | Large SEO skill pack: 26 sub-skills and 19 sub-agents for technical audits, schema, briefs, clusters, drift, GEO, local and international SE | True | True | technical SEO audit, structured data / schema, content briefs, SERP and competitor gap analysis, topical authority and cluster mapping, content refresh and decay detection, on-page SEO (titles, meta, headings), long-tail keyword and query research |
| `claude-seo.seo-content-brief` | skill | https://github.com/AgriciDaniel/claude-seo/tree/main/skills/seo-content-brief | AgriciDaniel (repo); SKILL.md metadata and LICENSE.txt name puneetindersingh as author | MIT | 2026-10-22T16:47:38Z | 26975 | Markdown SEO content brief: SERP top-5 competitor scoring, gap types, intent, outline with word counts, meta rules (title 50-60, meta 130-15 | False | False | content briefs, SERP and competitor gap analysis, snippet and answer formatting |
| `marketingskills` | skill | https://github.com/coreyhaines31/marketingskills | coreyhaines31 | MIT | 2026-11-04T19:01:33Z | 58790 | Marketing skill collection covering CRO, copywriting, copy-editing, content-strategy, ai-seo and analytics. Reads a product-marketing contex | False | True | editorial writing, substantive editing, topical authority and cluster mapping |
| `humanizer` | skill | https://github.com/blader/humanizer | blader | MIT | 2026-10-28T07:17:33Z | 65379 | Single SKILL.md (v3.1.0) covering 26 AI-writing patterns. It keeps every supported claim and adds no fact, number, date, quote or citation.  | False | True | editorial writing, substantive editing |
| `seo-skill` | skill | https://github.com/aevans-eng/seo-skill | aevans-eng | MIT | 2026-03-14T21:09:48Z | 15 | Single-file SEO audit and fix skill for static portfolio sites: meta, Open Graph, JSON-LD, sitemap, robots, alt text, H1s, canonicals. Edits | False | True | technical SEO audit, on-page SEO (titles, meta, headings), structured data / schema |
| `seo-geo-claude-skills` | skill | https://github.com/aaron-he-zhu/seo-geo-claude-skills | aaron-he-zhu | Apache-2.0 | 2026-09-04T04:50:54Z | 240 | Signpost repo: the 16 SEO/GEO skills moved to aaron-marketing-skills, and the older 20-skill version is kept at tag v9.9.12. Source not insp | False | False | long-tail keyword and query research, on-page SEO (titles, meta, headings) |
| `mcp-server-typescript` | mcp_server | https://github.com/dataforseo/mcp-server-typescript | dataforseo | Apache-2.0 | 2026-11-02T11:44:17Z | 260 | MCP server for the DataForSEO API: SERP, keyword volume, difficulty, intent and on-page parsing. Needs a DataForSEO API account. | False | True | long-tail keyword and query research, SERP and competitor gap analysis |
| `session-report` | plugin | https://github.com/anthropics/claude-plugins-official/tree/main/plugins/session-report | anthropics | Apache-2.0 | 2026-11-06T07:07:19Z | 46251 | Node analyzer reads ~/.claude/projects transcripts and prints JSON to stdout. SKILL.md then writes /tmp/session-report.json and copies templ | False | True |  |
| `token-optimizer` | plugin | https://github.com/alexgreensh/token-optimizer | alexgreensh | PolyForm-Noncommercial-1.0.0 | 2026-11-06T08:07:33Z | 2906 | Token and context auditor with compaction checkpoints and waste detectors. Registers hooks on PreToolUse, PostToolUse, SessionStart, Stop, U | True | True |  |
| `context-mode` | plugin | https://github.com/mksglu/context-mode | mksglu | unknown | None | None | Focused retrieval from large tool outputs (per docs/ops/usage-optimization.md). Risk: compression can hide footnotes or conflicts. Metadata  | True | True |  |
| `rtk` | plugin | https://github.com/rtk-ai/rtk | rtk-ai | unknown | None | None | Filters verbose dev-command output such as pytest and build logs (per docs/ops/usage-optimization.md). A --raw bypass must be kept for failu | True | True |  |

## Source reviews (top 5: full source read; reject on undisclosed network calls, out-of-scope writes, unclear license, paid account)

| name | decision | network calls disclosed | writes in scope | license clear | paid required | reasons | files read |
|---|---|---|---|---|---|---|---|
| `claude-seo` | **reject** | True | False | True | False | install.sh writes into the global ~/.claude, which is outside the allowed scope; ships hooks; includes an IndexNow submitter and GSC/GA4 scripts that make network calls; paid extensions are optional |  |
| `claude-seo.seo-content-brief` | **accept** | True | True | True | False | No scripts and no hooks: the skill is instruction text only. MIT license (LICENSE.txt points to the repo root).; Its network use is disclosed: WebFetch of the target page and sitemap, plus optional DataForSEO and Ahrefs MCPs that it does not require. It treats fetched content as untrusted.; Fit conc | skills/seo-content-brief/SKILL.md, skills/seo-content-brief/LICENSE.txt, skills/seo-content-brief/references/excluded-domains.md, skills/seo-content-brief/refer |
| `humanizer` | **accept** | True | True | True | False | No hooks. No network calls in the skill itself. MIT license, also stated in plugin.json.; scripts/validate-package.py only reads package files and checks versions and pattern numbering. It makes no writes and no network calls.; The CI workflow runs npx skills and a global claude-code install on GitH | SKILL.md, scripts/validate-package.py, LICENSE (listed, not opened), .claude-plugin/plugin.json, .github/workflows/validate.yml |
| `session-report` | **reject** | False | True | True | False | Revised from accept. template.html loads fonts.googleapis.com and fonts.gstatic.com, yet the docs call the report self-contained and the first pass said 'no network calls'. That is an undisclosed network call when the report is viewed.; The first pass said 'no file writes', which is wrong. SKILL.md  | plugins/session-report/skills/session-report/SKILL.md, plugins/session-report/skills/session-report/analyze-sessions.mjs, plugins/session-report/.claude-plugin/ |
| `token-optimizer` | **reject** | True | False | False | False | registers six lifecycle hooks; hooks are forbidden; PolyForm-Noncommercial license may not fit a publication with ad revenue; opt-in Keep-Warm makes model API calls |  |

## Benchmarks (docs/ops/skill-eval-set.md; baseline = in-repo references)

| name | task | baseline | candidate | errors | turns | seconds | hard-rule regression | notes |
|---|---|---|---|---|---|---|---|---|
| `claude-seo.seo-content-brief` | 1-cluster-brief-housing | 9 | 6 | 0 | 2 | 25 | False | Both arms: double $12,042 (+$462, +3.99% vs 2025-26; $6,021 per semester); deposit and kitchen unknown because the fixture has no deposit claim. Candidate: Markdown, not planner.json; slug breaks URL  |
| `claude-seo.seo-content-brief` | 5-title-and-snippet | 9 | 9 | 0 | 1 | 15 | False | Hand-counted (python was denied). Baseline: titles 56/55/54 chars, meta 146, intro 44 words. Candidate: titles 55/56/54, meta 144, intro 37 words. Every title contains the query. Candidate's 50-60/130 |
| `claude-seo.seo-content-brief` | 6-serp-gap-analysis | 9 | 5 | 1 | 1 | 20 | False | Baseline: forum_only = 5 forum results, not dedicated, stale (2022-05-01), unsourced, so AGI 5; dedicated_official = position 1 official, dedicated, current, sourced, complete, so AGI 0. Candidate rem |
| `humanizer` | 4-draft-edit | 8 | 9 | 0 | 1 | 20 | False | Both arms flagged $9,999 per month as unsupported (fixture: $12,042 per person per academic year; no monthly basis) and 'Students agree' as unsupported. The candidate's pattern list also caught the st |
| `humanizer` | 5-title-and-snippet | 9 | 9 | 0 | 1 | 10 | False | The candidate intro is plainer (36 words). The dash rule turns '2026–27' into '2026-27', which changes no fact. Humanizer has no SEO or title rules. Tie, no win. |
| `session-report` | usage-optimization-set (not run) | 0 | 0 | 0 | 0 | 0 | False | Read-only reporting plugin; benchmark = runs without error on a transcript. Not installed and not run. The 0/0 is a placeholder (candidate = baseline), not a measured score. The source review now reje |

## Rejected

| name | reason |
|---|---|
| `claude-seo` | Global install into ~/.claude, ships hooks, and runs network-calling scripts (IndexNow, GSC/GA4). |
| `token-optimizer` | Ships six lifecycle hooks; noncommercial license is unclear for an ad-supported site; Keep-Warm pings the API. |
| `mcp-server-typescript` | Needs a paid DataForSEO account; paid calls would have to go through budget.py reservation before any use. |
| `session-report` | Revised after reading the source. The template loads Google Fonts, which the docs do not disclose, and the skill writes /tmp/session-report.json plus an HTML file into the current directory, contradicting the first pass. The analyzer script alone is clean and could be re-evaluated on its own. |
| `claude-seo.seo-content-brief` | Not adopted: worse than baseline on task 1 (6 vs 9) and task 6 (5 vs 9), tied on task 5. Its competitor filter drops .edu official pages and forums, which misjudges the answer gap for campus queries. Its brief format conflicts with planner.json and the URL model. |

## Coverage gaps reported by the scout (become scout jobs, R30)

- content briefs, SERP gap analysis, on-page SEO and snippet formatting: baseline score still '—'; benchmark against claude-seo.seo-content-brief is pending
- content briefs, SERP gap analysis, snippet formatting: in-repo baseline kept (task 1 = 9, task 5 = 9, task 6 = 9); no external candidate beats it
- editorial filler detection: humanizer won task 4 (9 vs 8) but tied task 5, so the adoption rule fails. Suggest adding a short AI-tell pattern list to references/editing.md and re-running task 4
- editorial writing and substantive editing: benchmark against humanizer is pending; it should use eval task 4, not tasks 1/5/6
- eval-set defect: task 1 ground truth 'deposit $250 refundable' is not in fixture_hall_rates_v1.html
- eval-set defect: task 6 ground truth 'cornell housing portal → navigational' is in neither SERP fixture
- internal linking
- internal linking, local and campus navigation content, technical SEO audit: still no candidate
- local and campus navigation content
- local and campus navigation content: no candidate covers it and it has no benchmark
- task 2 fixture fixtures/synthetic/town/route_fixture.json not supplied; tasks 2-3 not run
- technical SEO audit: no candidate covers it and it has no benchmark
- usage tooling: session-report is pending on the docs/ops/usage-optimization.md eval set
- usage tooling: session-report is rejected as packaged; a run of analyze-sessions.mjs alone on a synthetic transcript dir is still pending

## Scout uncertainties (verbatim)

- The previous reply was truncated. The context-mode and rtk metadata (license, last_commit, stars) and the earlier benchmark rows were lost, so they are left as unknown or null rather than guessed. ships_hooks=true for both is a cautious placeholder, not a verified fact.
- benchmarks is empty: no candidate was run on eval tasks 1, 5 or 6, and the recorded baseline scores were lost in the truncation. The in-repo baseline still has no recorded score ('—' in skill-coverage.md).
- The source reviews are based on what the earlier pass observed. Full source was not cloned and read verbatim, so the accept decisions are provisional until clone and benchmark.
- Bash ran read-only commands in this repair turn, so the bash_permission_denied hold reason may be stale. The coordinator should check before re-dispatching.
- No adoption is proposed because no candidate has been shown to beat baseline.
- Bash was denied ('don't ask' permission mode), so no candidate was cloned. With no clone there are no pinned SHAs, and not every file could be read. Nothing is adopted.
- No benchmark rows are reported. Running the candidate arm without the candidate's real SKILL.md would mean making up scores, turns and seconds. WebFetch was not used to read SKILL.md: it returns a model summary, not the file text, so it cannot stand in for loading the skill.
- Unverified HEAD SHAs from WebFetch's summarizer; do not pin them. claude-seo 6be93f45064ffbadced572b5d5c95f55fd263af0 at 2026-10-22T16:47:38Z, which does not match the first pass's 2026-11-01. humanizer 0ef9fe5bc3572734fd3ae6c448fe00a30cd5dcf0 at 2026-10-28T07:17:33Z, which matches. claude-plugins-official a1ecfbc7f138a0ef455088f7f28cda2d22a0f853 at 2026-11-06T07:07:19Z, versus 07:27:34Z in the first pass.
- Task 1 fixture conflict: fixture_hall_rates_v1.html has 6 per-person academic-year rate cells (double, single and triple for 2025-26 and 2026-27) and air-conditioning claims, but no deposit claim. The ground truth 'deposit $250 refundable' is not in that file. Either fix the eval set or supply the deposit's source.
- Task fit: tasks 1/5/6 match only claude-seo.seo-content-brief. humanizer is a writing and editing skill, so it belongs on task 4 (draft_filler.md). session-report is a usage tool, so it belongs on the usage-optimization eval set.
- The packet's scratch path (.../-Users-ajaysharma-Ads/e4f68972-.../scratchpad/scout) is not this session's scratchpad. The sandbox may reject writes to it even when Bash is allowed.
- The packet scratch path (.../-Users-ajaysharma-Ads/e4f68972-.../scratchpad/scout) was denied, so the clones went to this session's scratchpad at /private/tmp/claude-501/-Users-ajaysharma-Ads-campus-publication/913cd9c9-6c10-4d91-ada3-2bf6805392b7/scratchpad/scout/<name>.
- The SHAs are from git log on shallow clones: claude-seo 6be93f45064ffbadced572b5d5c95f55fd263af0, humanizer 0ef9fe5bc3572734fd3ae6c448fe00a30cd5dcf0, claude-plugins-official a1ecfbc7f138a0ef455088f7f28cda2d22a0f853. These are repo HEADs, not the last commit for each subpath.
- Star counts come from the first pass and were not re-verified.
- python3 was denied, so title, meta and intro lengths were counted by hand and seo.seo_gate was not executed. A deterministic re-check is recommended.
- Scoring is a single non-blind scorer. The humanizer SKILL.md was read before its baseline run, which may have raised the baseline. A 1-point margin is within noise.
- Seconds and turns are approximate: both arms combined, shared reads apportioned. Total session time to the scoring step was about 165 s by epoch timestamps.
- Claim ids in task 1 are local labels for the 6 rate cells in the fixture; the fixture has no claim ids. The rate table is for all undergraduate halls; the source does not say it applies to Fixture Hall specifically.
- Some files were not opened: humanizer README.md, AGENTS.md, CHANGELOG.md, agents/openai.yaml, marketplace.json and .cursor-plugin/plugin.json (docs and manifests, not scripts or hooks), claude-seo references/keyword-density.md, and template.html beyond a grep for URLs.

## Vendored references (instructions only, not installed)

Added 2026-11-06 for `specs/bulk-mode.md` section 4. This is reference text, not adoption under the R12 rule above: nothing is placed under `.claude/skills/`, no row in this section has the status `adopted`, and the guard hook allows nothing new. Rollback: delete `skills/vendor/marketingskills-programmatic-seo/` and revert the vendoring commit.

| name | status | source | pinned sha | license | location | skill version | vendored |
|---|---|---|---|---|---|---|---|
| `marketingskills.programmatic-seo` | vendored (reference only) | https://github.com/coreyhaines31/marketingskills (path `skills/programmatic-seo/`, branch `main`) | 96798cf38736ecdba015a1d2b0521b0c8f8f41dd | MIT, Copyright (c) 2025 Corey Haines (full text in `VENDOR.md`) | `skills/vendor/marketingskills-programmatic-seo/` | 2.1.1 | 2026-11-06 |

Copied (Markdown only, byte-identical to upstream at the pinned SHA; sizes and sha256 are in `VENDOR.md`):

- `skills/vendor/marketingskills-programmatic-seo/SKILL.md`
- `skills/vendor/marketingskills-programmatic-seo/references/playbooks.md`
- `skills/vendor/marketingskills-programmatic-seo/references/implementation-platforms.md`
- `skills/vendor/marketingskills-programmatic-seo/VENDOR.md` (written locally: source, SHA, date, license text, file list)

Not copied:

- `skills/programmatic-seo/evals/evals.json`: a JSON eval fixture, data rather than instruction text. It is the only other file in the upstream skill folder.
- The skill folder has no scripts, no hooks and no binaries, so nothing of that kind was left out of it. The upstream repository does ship code outside the skill folder (CLI tools in `tools/`, `scripts/`, `tests/`, GitHub workflows, and other skills with scripts such as `conversion-tracking`). None of it was copied. Its plugin manifests have no hook entries.

Review (same columns as Source reviews above):

| name | decision | network calls disclosed | writes in scope | license clear | paid required | reasons | files read |
|---|---|---|---|---|---|---|---|
| `marketingskills.programmatic-seo` | **vendor as reference** | n/a (no code) | n/a (nothing installed) | True | False | Instruction text only: no scripts, hooks or binaries in the skill folder. MIT license, LICENSE read at the pinned SHA.; No hidden characters or HTML comments in the three Markdown files.; The text speaks to an agent (look for a product-marketing context file, ask intake questions). It is treated as data and not followed.; references/implementation-platforms.md compares site platforms as of 2026-10 and carries partner-disclosure wording for one vendor. Unused: we render statically and deploy to Netlify. | skills/programmatic-seo/SKILL.md, skills/programmatic-seo/references/playbooks.md, skills/programmatic-seo/references/implementation-platforms.md, skills/programmatic-seo/evals/evals.json (shape only), LICENSE, .claude-plugin/plugin.json, skills/seo-audit/SKILL.md lines 265-310 (read for the thin-content question, not vendored); .claude-plugin/marketplace.json, .codex-plugin/plugin.json and .agents/plugins/marketplace.json searched for hook entries only |

### Thin-content checklist and playbook points worth adopting

Upstream has no file or section titled as a thin-content checklist. The guidance is spread across `SKILL.md` (Core Principles, Template Design, Indexation Strategy, Quality Checks, Common Mistakes) and the "Value requirements" lists in `references/playbooks.md`. The points below pull it together in our terms. A short literal "Thin Content Issues" list exists in a different upstream skill (`skills/seo-audit/SKILL.md`, about line 283 at the pinned SHA). It was not vendored because the spec names programmatic-seo only.

- Name-swap test (`SKILL.md` Core Principles 1 and Common Mistakes; `references/playbooks.md` section 6, Locations): a page is thin when its only difference from its siblings is a name or place. Every page needs content that exists only because of its own data. Highest risk for us: hall and dining pages, and the second-school run (B7).
- Data-gated sections (`SKILL.md` Template Design, uniqueness): render a block only when the data has something for it. No empty, placeholder or boilerplate blocks.
- Own data first (`SKILL.md` Core Principles 2): public data is the weakest advantage. Lead with what only the dossier has: quote-backed figures, conflicts between official pages, stated gaps.
- Demand and fold rules (`SKILL.md` Common Mistakes and Indexation Strategy): no page without a real query, one page per query, and noindex or fold very thin variants instead of publishing them.
- Pre-launch pass/fail list (`SKILL.md` Quality Checks): unique value, intent answered, readable; unique title and meta; heading structure; schema; connected to the site; related pages linked; no orphans; in the sitemap; no conflicting noindex. The R45 gate (`worker/campus_worker/seo_gate.py`) already covers the technical half. The content-quality half has no gate yet.
- Hub-and-spoke links and sitemaps split by page type (`SKILL.md` Internal Linking Architecture and Indexation Strategy; `references/implementation-platforms.md`, per-page indexation control, limit of 50,000 URLs or 50 MB per sitemap file).
- Per-playbook value requirements (`references/playbooks.md` sections 4 Comparisons, 7 Personas, 9 Glossary, 12 Profiles): comparisons need same-basis data, balance, a pick by situation and a refresh when either side changes; profiles need sources, refreshes and aggregation rather than a restatement of one page; glossary answers need a definition, an example and related terms; audience pages need audience-specific facts (not testimonials, which we ban).
- Freshness is a thin-content risk (`references/implementation-platforms.md`, data refresh): stale rows make a page wrong and thin, and updates should reach pages without a full rebuild.
- Small-batch proof (`references/implementation-platforms.md`, Choosing step 4; `SKILL.md` Post-Launch Monitoring): publish the 20 to 50 strongest pages, confirm they index, then scale. This matches B2 before B3 in the bulk spec.

Not adopted from the playbooks: Curation (best-of lists; our headline rules fail superlatives), persona testimonials (fake reviews are banned), Templates, Examples, Conversions, Integrations and Translations as page types (no match with our four types; the Integrations idea of real setup steps is reused for process guides), and the platform comparison table plus vendor disclosure text in `references/implementation-platforms.md` (we render statically and deploy to Netlify).

Applied to our templates in `docs/ops/bulk-mode-template-notes.md` (proposals only; no template, gate or constant has been changed).

`claude-seo` is not installed. `specs/bulk-mode.md` section 4 says not to install it, or any skill with scripts or hooks, until its code is reviewed and logged, and it is not needed for bulk mode. Its decision stays **reject** (see Source reviews and Rejected above); nothing in this section changes that.

Notes and uncertainties:

- The pinned SHA is the upstream repository HEAD at clone time, a merge of upstream pull request #926 on 2026-11-06T12:52:45-05:00. The last upstream commit that touched the skill folder is 15b38b5388dfdd17f4ab424e986ccd32c24d5b22 (2026-10-27).
- The `marketingskills` row under Candidates is scout output and was left as written. Its `scripts True` refers to repo-level code that was not copied.
- No benchmark was run: this is reference text, not a skill adoption. The adoption rule (beat the baseline on the eval set, no hard-rule regression) applies only if someone proposes installing it.
- Upstream gives no numeric thresholds for thin content. Any number in the template notes is a proposal to tune on the B2 and B3 runs.
- The checklist points are one reader's synthesis of three files and were not tested against our pages.
- The clone used for reading lived in a scratch directory outside the repository. Nothing from it other than the three files above entered the repo.
