# STATE (v3, overwritten; keep under 60 lines)

Updated: 2026-11-08 16:58 EST. Spec: docs/v3/spec.md (owner's file, byte for byte). Live preview: https://footnote-daily.netlify.app (the Astro site, noindex until the real domain; article URLs are /cornell/<topic>/<slug>/ and the old /<topic>/<slug>/ paths redirect there). campus-ledger-preview.netlify.app is no longer deployed to (since 2026-11-08). Repo map: docs/v3/repo-map.md.

## Running now
- Housing (the spec's first topic): `scripts/v3/run.sh off-campus-housing` started 16:49 EST (8 workers, opus synthesis, sonnet checks). It is in brief.sh: the synthesis session had written 10.3k words of intel/off-campus-housing/brief.md by 16:56; then an expand pass if under 15k words, one sonnet fact check per lane (brief-check.md), readers.sh (at least 10 reader types), plan.sh. It stops with reports/plan-off-campus-housing.md for Ajay's approval; nothing is written until then. Logs: build/runs/v2/run-20261108T164955.log, brief-20261108T164956.log. Stop: scripts/v2/stop.sh.

## Getting-around: done (16:51 EST)
- 59 of 59 plan rows published: pillar, 22 spokes, 9 reader guides, 1 rewrite (the v2 biking page), 7 tools, 4 datasets, 15 start-here pages. All live at footnote-daily.netlify.app/cornell/getting-around/<slug>/. reports/to-read.md lists every page for Ajay's spot check; reports/blind-compare.md is still open.
- Speed (REPORT lines in build/runs/v2/run-2026110*.log): first run 11 pages in 0.34 h (32.7 pages/hour, 6.6 session-minutes a page), then 13 more before the laptop slept (about 05:00 to 16:25 EST, lid or manual sleep; the scripts hold off idle sleep only); restart 9 pages in 0.27 h (33.1/hour, 10.2 min a page: the slow cycle held the pillar's two drafts and cold pick), then 29 in 0.35 h (83.5/hour, 3.9 min a page: the start pages are short), then 4, then 4. 0 minutes paused on usage limits all day.
- The last 4 pages (TCAT free rides, Collegetown parking, winter storms, off-campus renters) were held only by cited sources that never answered (yahoo.com, fingerlakes1.com). publish.sh now sends a page whose source fails on two passes to a writer round that replaces the source (commit d24c4a1); the four rounds took 0.4 to 0.7 minutes each and the pages published at 16:51. check.py now records a hash of the page with each passing check, so a page a writer round changes is checked again instead of skipping to publish.
- Fixed during the run: the publish step had rejected the pillar after one revision, against the spec (lint failures now go to the image step or the writer, up to three rounds, and only duplicates reject); slow check sessions (17 to 26 minutes, throttling) now trigger the pause and probe; a figures-only page no longer crashes lint; local place names (TCAT, Campus-to-Campus, Ho Plaza, Ithaca Commons, ...) added to the photo relevance config.

## Catch-up and cleanup (owner instructions 2026-11-08), step by step
1. Owner files: docs/v3/spec.md replaced with footnote-v3-spec.md from ~/Downloads, unchanged. footnote-style-guide.md and footnote-v2-fixes-1.md never arrived (not in the repo, Downloads, Desktop or home); docs/v2/style.md stays the marked stand-in (Part 6 editing passes and Part 7 swap test written from the v3 spec). No scheduled job, timer or "weekly" step exists anywhere; the learn run is `scripts/v3/learn.sh`, on demand.
2. Fixes file (the listed items, since the file itself is missing): production robots.txt from config/crawlers.yml (search and AI-search bots allowed, training bots blocked) and IndexNow (config/indexnow.key served at /<key>.txt, scripts/v2/indexnow.py after each deploy; a preview build submits nothing) are wired; every published article carries a licensed lead photo (Wikimedia Commons scenes of Cornell and Ithaca; find_images.py requires a school or town term plus a subject term, per config/schools.yml); queue duplicates merge (`queue.py dedupe`, cross-topic); the exemplar and the transfer-housing article open with the answer; reports/blind-compare.md exists. The 13 lead photos that fail the subject-match audit (reports/photo-audit.md) stay, on Ajay's word; each page gets a subject-matched photo at its v3 rewrite.
3. CLAUDE.md rewritten (23 lines): only what exists and runs.
4. Repo cleanup by import graph: 109 worker modules, every worker test, eight docs folders, 6 unused scripts, skills/, fixtures/, data/schools, data/ipeds, backups moved to archive/v1/. Before: 118 Python files, 15,839 lines, 39.1 MB tracked outside archive/ and corpus/. After: 17 files, 6,028 lines, 9.1 MB. Every kept script compiles and the renderer runs.
5. Research output: one file per lane ending in a `## Lane complete` line; research.sh folds stray part files and continues an unfinished lane in place. Housing 57.0k raw words and getting-around 55.8k, 5 of 5 lanes complete each.
6. v3 built and tested on getting-around: brief 28,132 words (11 sections, 518 sourced fact rows; checks 154 ok / 27 fixed / 18 unverifiable), 15 reader types, a 59-row plan approved by Ajay at 01:56 EST, then the run above.

## Counts
- Research: housing 57.0k and getting-around 55.8k raw words (complete); money 42.7k and dining 38.3k (lanes without completion lines; research.sh continues them when run). Briefs: getting-around; housing in progress.
- Queue: 82 published (59 getting-around plan rows, 23 v2 pages due for v3 rewrites via requeue_v2.py), 115 approved v2 rows (not used by v3), 11 v2 drafts, 13 rejected, 55 owned.

## Still missing
- The two owner files (style guide, fixes). Housing brief, reader map and plan (running). Money and dining lane completion. The 23 v2 pages' rewrites. Ajay's blind compare and the 20-fact spot check from reports/to-read.md. Launch items that need Ajay's accounts: domain, Search Console, GA4, consent platform, AdSense, affiliates.

## Ajay's next command
When reports/plan-off-campus-housing.md exists, read it, then from the repo root: `cd /Users/ajaysharma/Ads/campus-publication && scripts/v3/plan.sh off-campus-housing --approve && scripts/v3/run.sh off-campus-housing`.

## Other sessions in this checkout
"Website preview launch" (robots, IndexNow, photo rule; done), "Campus webpages and ads repo (fork)" (read-only), an Astro templates session writing only under site/, reports/templates/, reports/lighthouse/ and DECISIONS.md (it owns scripts/deploy_netlify.sh's Astro build and the footnote-daily project).
