# STATE (v3, overwritten; keep under 60 lines)

Updated: 2026-11-08 18:15 EST. Spec: docs/v3/spec.md (owner's file, byte for byte). Live preview: https://footnote-daily.netlify.app (the Astro site, noindex until the real domain; article URLs are /cornell/<topic>/<slug>/, the old /<topic>/<slug>/ paths redirect). campus-ledger-preview.netlify.app is retired (no deploys since 2026-11-08). Repo map: docs/v3/repo-map.md.

## Waiting on Ajay: the housing plan
- `scripts/v3/run.sh off-campus-housing` ran 16:49 to 17:59 EST and stopped, as the spec says, at the plan. Brief: 36,032 words, 11 sections, 557 sourced fact rows (18 min synthesis; lane checks 160 ok, 32 fixed in place, 13 unverifiable, 31 min). Reader map: 18 reader types (12 min). Plan: 64 rows, all queued as proposed (9 min): 1 pillar, 21 spokes, 8 reader guides, 8 tools (the rent and commute calculator, the when-to-sign timeline and the move-in checklist the spec names, plus an eligibility quiz, a Good Cause checker, a lease fee checker, a sublet timeline, a cancellation fee calculator), 4 datasets, 18 start-here paths (7 of them extend start pages getting-around already built), 4 rewrites of the published v2 housing pages. 0 minutes paused all day.
- Spec acceptance for housing: brief over 15k words yes; 10 or more readers yes (18); pillar plus 12 or more spokes yes (21); 3 or more reader guides yes (8); rent plus commute calculator yes; a dataset yes (4). Read reports/plan-off-campus-housing.md: the plan table, 18 open research questions (City Code 258-10 text, the DHCR Good Cause thresholds, post-2020 student voice, accessibility) and the planner's own acceptance check.
- Two things to decide while reading: q-housing-0083 rewrites content/articles/housing/cornell-transfer-housing.md, the published copy of the exemplar (docs/v2/exemplar.md stays the quality bar either way); and the four dataset titles carry sample sizes (38, 58, 28 listings, 9 cases) that the writer must find in the brief or narrow. To strike or reword a row: edit intel/off-campus-housing/plan.md, then `scripts/v3/plan.sh off-campus-housing --sync` (no session), then approve.
- An independent three-lens review of the plan (coverage, overlap, feasibility from the brief) is in reports/plan-off-campus-housing-review.md when it exists.

## Ajay's next command
From the repo root: `cd /Users/ajaysharma/Ads/campus-publication && scripts/v3/plan.sh off-campus-housing --approve && scripts/v3/run.sh off-campus-housing`. The run writes the 64 rows (8 workers, opus writes and edits, sonnet checks), publishes as pages pass, and prints a REPORT every 10 pages.

## Live site gap (not the pipeline's files)
- The Astro site that now serves footnote-daily.netlify.app (site/, the "Build Footnote Daily Astro site templates" session) reads only content/articles. Not on the live site: the 7 tools, 4 datasets and 15 start-here pages getting-around published (the Jinja render at build/site has them; it is no longer deployed), and an article's ```tool block renders as a placeholder paragraph. Housing adds 8 tools, 4 datasets and 18 start paths. I sent that session the details at 18:08 EST and asked it to add the three kinds; I am not editing site/. If it declines, the decision is Ajay's: add them to site/, or deploy the Jinja build (CAMPUS_DEPLOY_LEGACY=1 scripts/deploy_netlify.sh) until the Astro site carries them.

## Getting-around: done (16:51 EST)
- 59 of 59 plan rows published: pillar, 22 spokes, 9 reader guides, 1 rewrite, 7 tools, 4 datasets, 15 start pages; the articles are live at footnote-daily.netlify.app/cornell/getting-around/<slug>/. Speed: 32.7 pages/hour (6.6 session-minutes a page) in the first cycle, 33.1/hour (10.2 min, the pillar's two drafts and cold pick) and 83.5/hour (3.9 min, the short start pages) after the restart; the laptop slept about 05:00 to 16:25 EST (lid or manual sleep; the scripts hold off idle sleep only). The last 4 pages were held by sources that did not answer (yahoo.com, fingerlakes1.com) and went through the new writer round in under a minute each. reports/to-read.md lists every page for the spot check; reports/blind-compare.md is still open.

## Pipeline changes today (all committed)
- publish.sh: lint failures go to the image step or the writer (up to three rounds), never to a reject; transient link errors wait; a source that fails on two passes goes to a writer round that replaces it; only duplicates reject. sessions.py: a timed-out session counts as throttling. lint.py: a figures-only page no longer crashes. check.py: a passing check stores a hash of the page, so a page a writer round changes is checked again. Start pages are one per reader and shared by the topics (spec §4, "additions to /start/<reader>/"): plan.py queues a second topic's path, write.py extends the page in place with "Read in this order: <Topic>" sections, check.md scopes the check to that topic's sections; `plan.sh <topic> --sync` queues plan edits without a session.

## Catch-up and cleanup (owner instructions 2026-11-08), done in order
1. docs/v3/spec.md is the owner's file, unchanged. footnote-style-guide.md and footnote-v2-fixes-1.md never arrived; docs/v2/style.md stays the marked stand-in. Nothing runs on a schedule; learn.sh is on demand.
2. Fixes-file items done from the list: production robots.txt and IndexNow wired; every published article has a licensed lead photo (school or town term plus a subject term, config/schools.yml); queue duplicates merge; the exemplar and the transfer-housing page open with the answer; reports/blind-compare.md exists. The 13 photos that fail the stricter audit stay, on Ajay's word.
3. CLAUDE.md: 23 lines, only what exists and runs. 4. Repo cleanup by import graph: 118 Python files, 15,839 lines, 39.1 MB to 17 files, 6,028 lines, 9.1 MB outside archive/ and corpus/. 5. One file per research lane with a `## Lane complete` line; housing 57.0k and getting-around 55.8k raw words, 5 of 5 lanes each. 6. v3 built and tested on getting-around (brief 28,132 words, 15 readers, 59-row plan, then the run above).

## Counts
- Research: housing 57.0k and getting-around 55.8k raw words (complete); money 42.7k and dining 38.3k (lanes without completion lines). Briefs: getting-around, housing.
- Queue: 82 published (59 getting-around plan rows, 23 v2 pages due for v3 rewrites via requeue_v2.py), 64 housing plan rows proposed, 115 approved v2 rows (not used by v3), 11 v2 drafts, 13 rejected, 55 owned.

## Still missing
- The two owner files (style guide, fixes). Money and dining lane completion. The 23 v2 pages' rewrites (4 housing ones are in this plan). Ajay's blind compare and the 20-fact spot check. The live-site gap above. Launch items that need Ajay's accounts: domain, Search Console, GA4, consent platform, AdSense, affiliates.

## Other sessions in this checkout
"Build Footnote Daily Astro site templates" (site/, reports/templates/, reports/lighthouse/, DECISIONS.md, the Astro deploy; idle), "Website preview launch" (done), "Campus webpages and ads repo (fork)" (read-only).
