# Skill coverage matrix (specs/continuous-local-run.md R30; AT27)

For each required capability: the skill that covers it (adopted external skill, or an in-repo reference under
`skills/national-college-publishing/references/`), its pinned version, and its eval score on
`docs/ops/skill-eval-set.md`. A capability with no cover is an open skill-scout job (R12). Baseline scores are
filled by the first scout pass; "—" means not yet benchmarked.

| capability | covering skill | version | eval score | status |
|---|---|---|---|---|
| long-tail keyword and query research | in-repo `references/discovery.md` + `references/search-intel.md` + `docs/strategy/query-patterns.md` | repo | — | baseline; scout job open |
| SERP and competitor gap analysis | in-repo `references/search-intel.md` + `agi.py` (deterministic) | repo | — | baseline; scout job open |
| topical authority and cluster mapping | in-repo `references/search-strategy.md` | repo | — | baseline; scout job open |
| content briefs | in-repo `references/planning.md` | repo | — | baseline |
| editorial writing | in-repo `references/writing.md` + `docs/editorial/style.md` | repo | — | baseline; scout job open |
| substantive editing | in-repo `references/editing.md` | repo | — | baseline |
| on-page SEO (titles, meta, headings) | in-repo `references/seo.md` + `seo.seo_gate` | repo | — | baseline; scout job open |
| structured data / schema | in-repo `references/seo.md` + `seo.validate_structured_data` | repo | — | baseline |
| internal linking | in-repo `references/search-strategy.md` + `seo.check_internal_links` | repo | — | baseline |
| content refresh and decay detection | in-repo `references/maintenance.md` + propagation | repo | — | baseline |
| technical SEO audit | in-repo `references/seo.md` (sitemap, robots, canonical) | repo | — | **gap**: scout job open |
| snippet and answer formatting | in-repo `references/search-strategy.md` + `references/writing.md` | repo | — | baseline; scout job open |
| local and campus navigation content | in-repo `references/onboarding.md` (source map) + town harvest (R34) | repo | — | **gap**: scout job open |

Open skill-scout jobs are dispatched by the coordinator in the discovery lane (weekly, and once at the first run start). Results land in `docs/ops/skill-evaluations.md`; this table is updated from the `skill_eval.json` output.
