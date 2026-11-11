# Phase 3: category structure (2026-11-11)

## What changed
- 23 pages moved out of /cornell/getting-around/ to the section the spec's Phase 3b table names (the Phase 0 crawl found all 16 topic rows, several with two or three pages): 15 to daily-life (mail and packages x2, Cornell ID card, snow days, first-month checklist, internet x2, laundry x2, driver's license and DMV, voting, what to wear, winter activities, winter survival guide), 4 to health-safety (dorm fire safety, student health insurance and finding a doctor, winter blues, is Collegetown safe), 4 to housing (which dorms have air conditioning, heat out and frozen pipes, drafty apartments, setting up utilities, sidewalk snow removal). Driving, parking, buses, airports, biking, rideshare, carshare and break travel stayed.
- Four pages a rule matched were reviewed and kept where they are (two on-campus room-selection pages, an apartments-with-laundry page, a utilities-cost page under money); they are listed in reports/00-baseline.md.
- The health section is now health-safety ("Health and safety") in site/site.config.ts, scripts/v3/topics.yml, the queue's topic list and the Jinja renderer; it had no pages, so no URL changed by the rename.
- Each moved page carries `redirect_from` with its two old URLs (/cornell/getting-around/<slug>/ and the Jinja-era /getting-around/<slug>/); the site build turns every entry into a 301 in dist/_redirects and a link-map entry (site/src/lib/model.ts, scripts/check-build.mjs). The three Markdown files that linked to a moved page now link to the new path directly. The queue rows' topic field follows the page.
- New build test (scripts/check-build.mjs): any internal href that equals a redirect source fails the build, on top of the existing broken-link, hub-listing and orphan checks.
- Tooling: scripts/prelaunch/move_pages.py (the move, from reports/00-baseline.json) and scripts/prelaunch/baseline.py (the crawl).

## Counts
| Measure | Before | After |
|---|---|---|
| Articles in getting-around | 67 | 44 |
| Articles in daily-life | 1 | 15 |
| Articles in health-safety | 0 | 4 |
| Articles in housing | 196 | 200 |
| Pages whose section does not match the mapping | 23 | 0 |
| Redirect lines in dist/_redirects | 315 | 362 |
| Internal links that hit a redirect | 0 | 0 |
| Broken internal links, orphans, pages missing from their hub | 0 | 0 |
| Pages built | 391 | 391 |

## Checks run
- `LINT_CONTENT_WARN=1 npm run build` in site/: check-build passed (391 pages, 364 content pages on their hubs, 362 redirects). The content linter still reports the 106 pages Phase 2 reworks (warn mode).
- `scripts/prelaunch/baseline.py` recrawl: 0 section mismatches, 0 orphans, 0 pages off a hub, everything noindex, sitemap empty (unchanged indexing state).
- Em dash check: see the command output in the commit log (0 files).

## Left for later phases
- Breadcrumbs, hubs, structured data and the search index are generated from the page's section at build time, so they changed with the move; the winter pages are spread between daily-life (what to wear, activities, survival guide), health-safety (winter blues) and housing (drafty apartments, snow removal, heat out) rather than a winter section, which the spec made optional. Phase 5 decides whether the winter cluster needs merging.
- The moved v3 pages still link the getting-around pillar as their pillar; the Phase 2 rework and later rewrites repoint them.
