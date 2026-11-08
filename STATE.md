# STATE (v2, overwritten; keep under 60 lines)

Updated: 2026-11-08 00:0x EST. Spec: docs/v2/spec.md. Preview: https://campus-ledger-preview.netlify.app (noindex until the real domain).

## Running now
- v3 (docs/v3/spec.md, 2026-11-08) is the operating spec. Research sprints started 2026-11-07 23:5x EST: off-campus housing (lanes A to E) and getting-around (lanes A to C), sonnet, 8 sessions; raw notes land in intel/<topic>/raw/. The v2 continuous run was stopped at 23:55 EST (16 published, 11 rejected, 15 drafts waiting; those go through v3's write and check later).
- (ended) v2 continuous run, started 23:09 EST on Ajay's go-ahead: scripts/v2/run_continuous.sh with 4 workers, batches of 12 (write, review, one fix round, review, publish with a deploy every 10, demand refill when approved rows drop below 20). Log: build/runs/v2/continuous-<ts>.log. Stop: scripts/v2/stop.sh.

## Counts
- Queue: 217 rows from the first demand pass (8 topic sessions, 5 minutes): 25 gap, 137 weak, 55 owned; 151 approved rows still unwritten.
- Pilot: 10 questions written in 5 minutes (10 sessions, 1.2 to 3.2 min each, 1,000 to 1,650 words). Every first review said fix (2 to 5 mismatches each). After the one allowed revision: 6 passed and are published, 4 rejected on a second round of attribution and paraphrase errors (academics distribution courses, Collegetown landlords, winter biking, care packages); 3 of the 4 still beat the #1 result on the reviewer's test.
- Published: 16 articles (exemplar, 6 pilot, the rest from the continuous run); queue now: 119 approved and unwritten, 12 written awaiting review or publish, 0 in a fix round, 11 rejected, 55 owned. Photos: Wikimedia Commons credits in content/images/credits.yml.
- Pilot cost: 51 sessions (8 demand, 10 write, 10 fix, 23 review) and 88 session-minutes; 6.7 session-minutes per article on average (4.2 to 11.3); wall time 40 minutes from demand to the last publish. No usage pause.
- v1: 833 pages unpublished; corpus/ holds 2,522 crawled pages (15 MB).

## Last 5 decisions
1. 2026-11-08: two pipeline fixes after the run tripped: a written row may go to fix or rejected from the publish lint (the run crashed on q-money-0019), and a link to a sibling article still in the pipeline is not a lint failure; the renderer turns links to unpublished articles into plain text so the site never carries a dead internal link.
2. 2026-11-07: queue rows auto-approved for the pilot (the spec allows --auto-approve); 10 pilot questions chosen as one per topic plus two more housing ones.
3. 2026-11-07: the exemplar went through the review loop by hand (three reviews, 16 then 6 then 0 mismatches) and is published as the first article; Ajay still edits it.
4. 2026-11-07: style guide and writer prompt gained a "precision when paraphrasing" block (exact attribution, no added detail, official wording for categories, apply every listed fix), because all four rejections were of that kind.

## Open questions (owner)
- The v3 paste named footnote-v2-fixes-1.md and footnote-style-guide.md; neither is in the repo or home folder. docs/v2/style.md stays the stand-in (now with Part 6 editing passes and Part 7 swap test written from the v3 spec). A Reddit API key (PRAW, read-only) would let lane C and E read threads; without it they use search results.
- Rejections run about 30% of attempted articles (11 of 36), nearly all on a second review round for paraphrase precision (a word the source does not use, a poster's point stated more strongly than they did, a rent figure that turned out to be for Trumansburg). Every rejected piece still beat the #1 result on the reviewer's test. The writer prompt already carries the self-fact-check; the spec's one-revision rule stands. If you want these back, say so and they re-enter as fresh rows.
- footnote-style-guide.md was not in the repo or home folder; docs/v2/style.md is a draft stand-in. Replace it verbatim when provided.
- The 4 rejected pilot questions are real gaps; say the word and they re-enter the queue as fresh rows after the style and exemplar edits (the spec's one-revision rule stands as written).
- reddit.com blocks Anthropic's fetcher, so sessions use College Confidential, the Cornell Daily Sun, YouTube and search snippets for student experience; a read-only Reddit API credential would be needed to open threads.
- Launch and money items that need owner accounts or keys: real domain and DNS, Search Console and GA4 ids, a Google-certified consent platform, AdSense (after 25 to 40 articles), affiliate programs, Grow, Unsplash and Pexels keys. Everything is wired through config/monetization.yml; policy pages carry [OWNER: fill in] markers for the legal entity, address and contact email.
- Ithaca College (v1 B7) is outside the v2 scope as written; its crawl was stopped.
