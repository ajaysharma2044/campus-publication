# Skill evaluations (specs/continuous-local-run.md R12, R30; AT11, AT27)

This file is the authority for what may live under `.claude/skills/`. The guard hook (`.claude/hooks/guard.sh`) blocks any write into `.claude/skills/<name>/` unless `<name>` appears below with status `adopted` and a 40-hex commit SHA, or as the in-repo baseline. Rollback for any adopted skill: delete its folder and revert the adopting commit.

last scout run: 2026-11-06 · runs: skill-scout-live-1.json, skill-scout-live-2.json

## Installed

| name | status | source | sha | license | eval (baseline → candidate) | installed |
|---|---|---|---|---|---|---|
| `national-college-publishing` | baseline (in-repo) | `skills/national-college-publishing/` (symlink) | in-repo | repo | baseline | 2026-11-06 |

## Candidates (R12: top 10 with url, author, license, last commit, stars, what it does, hooks/scripts)

| name | kind | url | author | license | last commit | stars | what it does | hooks | scripts | capabilities |
|---|---|---|---|---|---|---|---|---|---|---|
| `claude-seo` | plugin | https://github.com/AgriciDaniel/claude-seo | AgriciDaniel | MIT | 2026-11-01T06:07:26Z | 26975 | Large SEO skill pack: 26 sub-skills and 19 sub-agents for technical audits, schema, briefs, clusters, drift, GEO, local and international SE | True | True | technical SEO audit, structured data / schema, content briefs, SERP and competitor gap analysis, topical authority and cluster mapping, content refresh and decay detection, on-page SEO (titles, meta, headings), long-tail keyword and query research |
| `claude-seo.seo-content-brief` | skill | https://github.com/AgriciDaniel/claude-seo/tree/main/skills/seo-content-brief | AgriciDaniel | MIT | 2026-11-01T06:07:26Z | 26975 | Single sub-skill that builds a Markdown content brief from a URL or keyword: intent, competitor table, gaps, outline, meta tags, information | False | False | content briefs, SERP and competitor gap analysis, snippet and answer formatting |
| `marketingskills` | skill | https://github.com/coreyhaines31/marketingskills | coreyhaines31 | MIT | 2026-11-04T19:01:33Z | 58790 | Marketing skill collection covering CRO, copywriting, copy-editing, content-strategy, ai-seo and analytics. Reads a product-marketing contex | False | True | editorial writing, substantive editing, topical authority and cluster mapping |
| `humanizer` | skill | https://github.com/blader/humanizer | blader | MIT | 2026-10-28T07:17:33Z | 65379 | Single SKILL.md that removes 26 patterns of AI-sounding writing. Its rules forbid adding facts, numbers, dates, quotes or citations. No netw | False | True | editorial writing, substantive editing |
| `seo-skill` | skill | https://github.com/aevans-eng/seo-skill | aevans-eng | MIT | 2026-03-14T21:09:48Z | 15 | Single-file SEO audit and fix skill for static portfolio sites: meta, Open Graph, JSON-LD, sitemap, robots, alt text, H1s, canonicals. Edits | False | True | technical SEO audit, on-page SEO (titles, meta, headings), structured data / schema |
| `seo-geo-claude-skills` | skill | https://github.com/aaron-he-zhu/seo-geo-claude-skills | aaron-he-zhu | Apache-2.0 | 2026-09-04T04:50:54Z | 240 | Signpost repo: the 16 SEO/GEO skills moved to aaron-marketing-skills, and the older 20-skill version is kept at tag v9.9.12. Source not insp | False | False | long-tail keyword and query research, on-page SEO (titles, meta, headings) |
| `mcp-server-typescript` | mcp_server | https://github.com/dataforseo/mcp-server-typescript | dataforseo | Apache-2.0 | 2026-11-02T11:44:17Z | 260 | MCP server for the DataForSEO API: SERP, keyword volume, difficulty, intent and on-page parsing. Needs a DataForSEO API account. | False | True | long-tail keyword and query research, SERP and competitor gap analysis |
| `session-report` | plugin | https://github.com/anthropics/claude-plugins-official/tree/main/plugins/session-report | anthropics | Apache-2.0 | 2026-11-06T07:27:34Z | 46251 | Official Anthropic plugin. Reads local Claude Code transcripts and prints an HTML or JSON usage report. No network calls, no writes, no hook | False | True |  |
| `token-optimizer` | plugin | https://github.com/alexgreensh/token-optimizer | alexgreensh | PolyForm-Noncommercial-1.0.0 | 2026-11-06T08:07:33Z | 2906 | Token and context auditor with compaction checkpoints and waste detectors. Registers hooks on PreToolUse, PostToolUse, SessionStart, Stop, U | True | True |  |
| `context-mode` | plugin | https://github.com/mksglu/context-mode | mksglu | unknown | None | None | Focused retrieval from large tool outputs (per docs/ops/usage-optimization.md). Risk: compression can hide footnotes or conflicts. Metadata  | True | True |  |
| `rtk` | plugin | https://github.com/rtk-ai/rtk | rtk-ai | unknown | None | None | Filters verbose dev-command output such as pytest and build logs (per docs/ops/usage-optimization.md). A --raw bypass must be kept for failu | True | True |  |

## Source reviews (top 5: full source read; reject on undisclosed network calls, out-of-scope writes, unclear license, paid account)

| name | decision | network calls disclosed | writes in scope | license clear | paid required | reasons | files read |
|---|---|---|---|---|---|---|---|
| `claude-seo` | **reject** | True | False | True | False | install.sh writes into the global ~/.claude, which is outside the allowed scope; ships hooks; includes an IndexNow submitter and GSC/GA4 scripts that make network calls; paid extensions are optional |  |
| `claude-seo.seo-content-brief` | **accept** | True | True | True | False | Decision copied from live-scout-1. Not re-checked: this pass could not clone the repo or read its files. |  |
| `humanizer` | **accept** | True | True | True | False | Decision copied from live-scout-1. Not re-checked: this pass could not clone the repo or read its files. |  |
| `session-report` | **accept** | True | True | True | False | Decision copied from live-scout-1. Not re-checked: this pass could not clone the repo or read its files. |  |
| `token-optimizer` | **reject** | True | False | False | False | registers six lifecycle hooks; hooks are forbidden; PolyForm-Noncommercial license may not fit a publication with ad revenue; opt-in Keep-Warm makes model API calls |  |

## Benchmarks (docs/ops/skill-eval-set.md; baseline = in-repo references)

| name | task | baseline | candidate | errors | turns | seconds | hard-rule regression | notes |
|---|---|---|---|---|---|---|---|---|
| — | no benchmark rows recorded yet | | | | | | | |

## Rejected

| name | reason |
|---|---|
| `claude-seo` | Global install into ~/.claude, ships hooks, and runs network-calling scripts (IndexNow, GSC/GA4). |
| `token-optimizer` | Ships six lifecycle hooks; noncommercial license is unclear for an ad-supported site; Keep-Warm pings the API. |
| `mcp-server-typescript` | Needs a paid DataForSEO account; paid calls would have to go through budget.py reservation before any use. |

## Coverage gaps reported by the scout (become scout jobs, R30)

- content briefs, SERP gap analysis, on-page SEO and snippet formatting: baseline score still '—'; benchmark against claude-seo.seo-content-brief is pending
- editorial writing and substantive editing: benchmark against humanizer is pending; it should use eval task 4, not tasks 1/5/6
- internal linking
- local and campus navigation content
- local and campus navigation content: no candidate covers it and it has no benchmark
- technical SEO audit: no candidate covers it and it has no benchmark
- usage tooling: session-report is pending on the docs/ops/usage-optimization.md eval set

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
