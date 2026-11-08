# Skill coverage matrix (specs/continuous-local-run.md R30; AT27)

For each required capability: the skill that covers it (adopted external skill, or an in-repo reference under
`skills/national-college-publishing/references/`), its pinned version, and its eval score on
`docs/ops/skill-eval-set.md`. A capability with no cover is an open skill-scout job (R12). Baseline scores are
filled by the first scout pass; "—" means not yet benchmarked.

| capability | covering skill | version | eval score | status |
|---|---|---|---|---|
| long-tail keyword and query research | in-repo `references/discovery.md` + `references/search-intel.md` + `docs/strategy/query-patterns.md` | repo | — (no eval task measures it yet) | baseline; no benchmark |
| SERP and competitor gap analysis | in-repo `references/search-intel.md` + `agi.py` (deterministic) | repo | 9 (task 6) | baseline kept; `claude-seo.seo-content-brief` 5 vs 9 on task 6 |
| topical authority and cluster mapping | in-repo `references/search-strategy.md` | repo | — (no eval task measures it yet) | baseline; no benchmark |
| content briefs | in-repo `references/planning.md` | repo | 9 (task 1) | **gap**: scout job open; baseline kept; `claude-seo.seo-content-brief` 6 vs 9 on task 1 |
| editorial writing | in-repo `references/writing.md` + `docs/editorial/style.md` | repo | 9 (task 5) | **gap**: scout job open; baseline kept; `claude-seo.seo-content-brief` 9 vs 9 on task 5, `humanizer` 9 vs 9 on task 5 |
| substantive editing | in-repo `references/editing.md` | repo | 8 (task 4) | **gap**: scout job open; baseline kept; `humanizer` 9 vs 8 on task 4 |
| on-page SEO (titles, meta, headings) | in-repo `references/seo.md` + `seo.seo_gate` | repo | 9 (task 5) | baseline kept; `claude-seo.seo-content-brief` 9 vs 9 on task 5, `humanizer` 9 vs 9 on task 5 |
| structured data / schema | in-repo `references/seo.md` + `seo.validate_structured_data` | repo | — (no eval task measures it yet) | baseline; no benchmark |
| internal linking | in-repo `references/search-strategy.md` + `seo.check_internal_links` | repo | — (no eval task measures it yet) | **gap**: scout job open |
| content refresh and decay detection | in-repo `references/maintenance.md` + propagation | repo | — (no eval task measures it yet) | baseline; no benchmark |
| technical SEO audit | in-repo `references/seo.md` (sitemap, robots, canonical) | repo | — (no eval task measures it yet) | **gap**: scout job open |
| snippet and answer formatting | in-repo `references/search-strategy.md` + `references/writing.md` | repo | 9 (task 5) | baseline kept; `claude-seo.seo-content-brief` 9 vs 9 on task 5, `humanizer` 9 vs 9 on task 5 |
| local and campus navigation content | in-repo `references/onboarding.md` (source map) + town harvest (R34) | repo | — (no eval task measures it yet) | **gap**: scout job open |

Open skill-scout jobs are dispatched by the coordinator in the discovery lane (weekly, and once at the first run start). Results land in `docs/ops/skill-evaluations.md`; this table is updated from the `skill_eval.json` output.
