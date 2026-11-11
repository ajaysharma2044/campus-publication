# Phase 4: one URL per tool (2026-11-11)

## What changed
- The five tools that lived at two self-canonical URLs now have one home each at /tools/<slug>/: rent-split-calculator-unequal-rooms, cornell-meal-plan-calculator-by-meals-a-week, should-i-bring-a-car-cornell-ithaca-cost, summer-storage-vs-shipping-vs-sublet-cornell-cost, ithaca-rent-commute-calculator. The article copy of each (under /cornell/housing/, /cornell/dining/ or /cornell/money/) is removed and 301s to the tool page, as does its Jinja-era /<section>/<slug>/ path (redirect_from on the tool.md frontmatter, written into dist/_redirects by the build).
- Before removal, one agent per tool applied a skeptic-verified plan (reports/04-tools-analysis.json): the article content worth keeping moved onto the tool page (worked examples, figures, reader blocks, failure modes, FAQ answers, with their sources) or into the related article that embeds the tool (for example the rent-split reasoning and steps figure into cornell-off-campus-roommates-joint-liability, the car-cost sections into the having-a-car guide, the storage advice into the subletting guide); duplicated passages were dropped. The details per tool are in reports/04-05-apply-results.json.
- 12 files that linked to an article URL now link to /tools/<slug>/ directly; the five retired article rows in queue/queue.csv read rejected with a note (superseded by the tool page).
- Tooling: scripts/prelaunch/consolidate_tools.py (removal, redirect_from, link rewrite, queue).

## Counts
| Measure | Before | After |
|---|---|---|
| Tools rendered as the primary content of two pages | 5 | 0 |
| Pages built | 391 | 386 |
| Redirect lines in dist/_redirects | 362 | 369 |
| Broken internal links, links that hit a redirect, pages off a hub | 0 | 0 |

## Checks run
- `LINT_CONTENT_WARN=1 npm run build`: check-build passed (386 pages, 359 content pages on their hubs, 369 redirects). The content linter still reports the pages Phase 2 is reworking (warn mode).
- scripts/prelaunch/baseline.py crawl rules: each tool resolves at exactly one URL; no two pages render the same tool as their primary content (the embeds in 48 housing pages are embeds, not primary content).
