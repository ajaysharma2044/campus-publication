# STATE (v2, overwritten; keep under 60 lines)

Updated: 2026-11-07 19:4x EST. Spec: docs/v2/spec.md.

## Running now
- Pilot (acceptance 1): write.sh is writing 10 approved questions (one per topic plus two) with 4 workers; review.sh is re-checking the exemplar. The v1 run and the Ithaca College crawl were stopped at 19:20 EST when the v2 spec arrived.

## Counts
- v1 pages unpublished: 833 (the preview at https://campus-ledger-preview.netlify.app shows a holding page).
- Corpus: 2,522 crawled pages from 26 hosts in corpus/ (15 MB), exported by scripts/v2/export_corpus.py.
- v2 queue: 217 rows from the first demand pass (8 topic sessions, 5 minutes): 25 gap, 137 weak (161 auto-approved), 55 owned. v2 articles: 1 written (the exemplar, "Cornell transfer housing: how it actually works", in review after one fix round); 10 pilot articles being written. Reviews: 1.

## Last 5 decisions
1. 2026-11-07: Footnote Daily v2 spec adopted; it replaces bulk-mode, subscription-only, lean mode and continuous-local-run wherever they conflict.
2. 2026-11-07: v1 pipeline moved to archive/v1 (specs, agents, bulk mode, pipeline, ramp, budget, dispatch, SEO gate, editorial gates, WordPress, old STATE and BACKLOG, their tests). Kept: fetcher, permissions, sitemap crawler, collectors, render templates and static assets, Netlify deploy.
3. 2026-11-07: guard hook reduced to the .env block; settings.json no longer protects specs or gate constants.
4. 2026-11-07: every v1 page unpublished; topics worth keeping go through v2 as queue rows.
5. 2026-11-07: official-only source filters removed from kept code (collectors, crawler); v1's UNSERVABLE filter left in the archive.

## Open questions (owner)
- reddit.com blocks Anthropic's fetcher (WebSearch and WebFetch return a 400 for the domain), so writer and demand sessions cannot open r/Cornell or r/ithaca threads directly; they can use thread titles and snippets surfaced by general web search, College Confidential, the Cornell Daily Sun and YouTube. If Reddit matters, an owner-supplied Reddit API credential (read-only, within Reddit's terms) would be needed; the v1 "Reddit collection stays off" rule still stands until you say otherwise.
- `footnote-style-guide.md` was not in the repo or home folder; docs/v2/style.md is a draft stand-in written from the spec's content rules. Replace it verbatim when provided.
- Monetization and launch items that need owner accounts or keys: real domain and DNS, Google Search Console and GA4 property ids, a Google-certified consent platform, AdSense (after 25 to 40 articles), affiliate programs, Grow by Mediavine, Unsplash and Pexels API keys (Wikimedia Commons and Openverse need none). Config lives in config/monetization.yml.
- Ithaca College (v1 acceptance B7) is outside the v2 scope as written (one school and its town); its crawl was stopped. Say the word if a second school should enter the queue.
- v1 worker modules not in the spec's archive list but importable (lanes, sweep, scoring, discovery, tools, ...) stay in worker/campus_worker/ unused; archive them later if they get in the way.
