# Phase 1: the pipeline never publishes a research gap (2026-11-11)

## What changed
- `scripts/lint-content.py` (new): the banned-phrase linter. The spec's seven patterns plus eleven variants the Phase 0 crawl showed ("Not confirmed:", "honest limit", "we could not confirm", "not in the sources", "the sources lack", and so on), case-insensitive, on every page body under content/articles, content/tools, content/datasets, content/start and content/pages. Exit 1 on any match; `--warn` or `LINT_CONTENT_WARN=1` reports without failing; `--emdash` also fails on an em dash anywhere under content/ or site/dist; `--json` for scripts.
- The site build runs it first: `site/package.json` prebuild is `node scripts/sync-images.mjs && python3 ../scripts/lint-content.py`, so `npm run build` and `scripts/deploy_netlify.sh` stop before Astro when a page matches.
- The article pipeline applies the same patterns: `scripts/v2/lint.py` imports them and reports "research gap: ..." as a text-level failure, which publish.sh routes to a writer fix round (v3 pages) or a revision (v2 pages); a draft that matches is never published.
- Gap workflow (Phase 1b) in the prompts, replacing the old rule that an unfillable hole became a "Not confirmed:" line: `scripts/v3/prompts/write.md` and `write-pillar.md` (search the source checklist; if found, cite it and add it to the brief; if not, cut the sentence and the promise it answers, change the heading, glance line or title, and log the decision under "## Gaps" in content/edits/<slug>.md), `check.md` (an admission line is a fix item, never a pass), `_common.md` and the five `research-*.md` lane prompts (the source checklist: Clery report and police data for crime and safety; the NYS and Tompkins County Boards of Elections for voting; City of Ithaca, Town of Ithaca and Tompkins County for local rules; General Obligations Law, Real Property Law and the NYS Attorney General's tenant guides for tenant law; the office page, current-year PDFs and the Cornell Chronicle for Cornell policy; never a forum poster as a source). `scripts/v3/write.py` lets the writer write content/edits/<slug>.md. `docs/v2/style.md` Part 7 carries the rule for anyone writing by hand.
- `scripts/prelaunch/gaps.py` (new) compiles reports/gaps.md from the writers' "## Gaps" lines and reports/gaps-phase2.md (Phase 2's log).

## Counts
| Measure | Before | After |
|---|---|---|
| Pages matching the spec's seven patterns (Phase 0 crawl of the build) | 66 pages, 86 matches | unchanged until Phase 2 |
| Pages matching the full list (content files, including "Not confirmed:" lines) | 106 pages, 263 matches | unchanged until Phase 2 |
| Builds that can ship such a page | yes | no (prebuild fails) |
| Drafts the publish lint lets through with such a sentence | yes | no |

## Acceptance, as read
The spec's Phase 1 acceptance ("linter passes on the whole site; reports/gaps.md lists every resolved gap") can only be met once Phase 2 reworks the flagged pages, and the spec orders Phase 2 after Phases 3, 4 and 5. So: the linter exists, is wired strictly into the build and the publish lint, and today fails on exactly the pages Phase 2 will rework (the list is `python3 scripts/lint-content.py`). Until Phase 2 passes, local verification builds for Phases 3 to 5 run with `LINT_CONTENT_WARN=1`, and nothing is deployed. reports/gaps.md is empty until Phase 2 logs its decisions.

## Checks run
- `python3 scripts/lint-content.py`: 263 matches on 106 pages (exit 1, as intended); `LINT_CONTENT_WARN=1` exits 0.
- `scripts/v2/lint.py` on a v3 page with "Not confirmed:" lines reports "research gap: not confirmed" (the fetch of its sources makes that run slow; the pattern check itself is instant).
- Em dash check: 0 files under content/ and site/dist.
- The build was not run in strict mode (it fails on the 106 pages by design); the Phase 0 build and check-build passed before this change, and the prebuild step is a one-line addition.
