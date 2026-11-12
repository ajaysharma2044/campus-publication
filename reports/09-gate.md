# Phase 9: quality gate and wave release system (2026-11-11), built and run: wave 1 launched 2026-11-11 23:50 EST on Ajay's approval

Launched: LAUNCHED=true is set on the production deploy, wave 1 is promoted (index: true on 331 pages), robots.txt allows the search and retrieval crawlers and lists the sitemap (331 URLs), every other page is noindex, follow.

## 9a. Per-page index control
- Every page carries `index: false` (scripts/prelaunch/index_field.py; 408 pages). The site build reads it (site/src/lib/model.ts); a missing field means false.
- Scorer: scripts/prelaunch/score_pages.py -> reports/09-eligibility.csv. Checks: linter, 3 or more official or primary sources and no forum sources, a distinct primary query (frontmatter, else the queue row), a data element, a named author with an Updated date within 12 months, a lead image that passed Phase 6 or none.
- Result: 408 pages scored, 335 eligible (21 pages whose queue row is not published are not built and fail the new "built" check). Failing checks among the rest: {'sources3': 41, 'distinct_query': 5, 'data_element': 17} (a page can fail more than one).

## 9b. Robots, noindex and sitemap
- `site/site.config.ts`: `launched: process.env.LAUNCHED === 'true'`. Base.astro renders `index, follow` only when launched and the page's index is true; everything else `noindex, follow`.
- `site/src/pages/sitemap.xml.ts`: only `index: true` pages, only when launched. `site/src/pages/robots.txt.ts`: Disallow: / until launched; then the lists from config/crawlers.yml (allow Googlebot, Bingbot, OAI-SearchBot, ChatGPT-User, PerplexityBot, Perplexity-User, Claude-SearchBot, Claude-User, Applebot, Meta-WebIndexer; disallow GPTBot, Google-Extended, CCBot, ClaudeBot, Applebot-Extended, meta-externalagent, Bytespider; tokens checked against each company's crawler documentation on 2026-11-11) and the sitemap URL.

## 9c. Waves
- config/waves.json: wave 1 = 331 eligible pages by score and demand across the visible sections (transfer 31, housing 195, getting-around 55, dining 21, money 18, daily-life 12, health-safety 4); the hidden hubs (academics, careers, parents, alumni) stay out until they reach five articles. No later wave yet.
- `scripts/prelaunch/waves.py promote 1` flips `index: true` on the wave's pages and the next build regenerates the sitemap; `waves.py status` prints the stop-rule inputs; `waves.py kill` reverts a wave. Stop rule: no new wave while the weekly audit's error rate is above the threshold in config/wave-metrics.json.
- Weekly audit: scripts/prelaunch/audit_weekly.py samples 20 indexable pages per section, re-fetches each cited source and flags numbers that no longer appear (reports/audit-YYYY-MM-DD.md).

## 9d. Launch steps (Ajay only)
LAUNCH_CHECKLIST.md: point www.eduexplained.com at Netlify, set LAUNCHED=true in the Netlify environment, promote wave 1, deploy, submit the sitemap, run the first weekly audit. Not executed.

## Checks
- `cd site && npm run build` with the strict linter passes (build/runs/astro-build-strict3.log). External links: reports/09-links.md (1,800 ok, 0 dead).
