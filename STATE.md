# STATE (v2, overwritten; keep under 60 lines)

Updated: 2026-11-07 23:0x EST. Spec: docs/v2/spec.md. Preview: https://campus-ledger-preview.netlify.app (noindex until the real domain).

## Running now
- Nothing. The pilot (acceptance 1) finished at 22:56 EST. Continuous operation (acceptance 4) waits for acceptance 2 and 3, which are Ajay's: the blind comparison of 5 articles against the #1 Google result, and a 20-fact spot check.

## Counts
- Queue: 217 rows from the first demand pass (8 topic sessions, 5 minutes): 25 gap, 137 weak, 55 owned; 151 approved rows still unwritten.
- Pilot: 10 questions written in 5 minutes (10 sessions, 1.2 to 3.2 min each, 1,000 to 1,650 words). Every first review said fix (2 to 5 mismatches each). After the one allowed revision: 6 passed and are published, 4 rejected on a second round of attribution and paraphrase errors (academics distribution courses, Collegetown landlords, winter biking, care packages); 3 of the 4 still beat the #1 result on the reviewer's test.
- Published: 6 articles (the exemplar "Cornell transfer housing: how it actually works" plus 6 pilot articles: meal plan vs cooking, Collegetown vs Fall Creek vs downtown, subletting, pharmacies near campus, alumni gym access, part-time jobs in Ithaca). Photos: 3 with Wikimedia Commons credits in content/images/credits.yml.
- Pilot cost: 51 sessions (8 demand, 10 write, 10 fix, 23 review) and 88 session-minutes; 6.7 session-minutes per article on average (4.2 to 11.3); wall time 40 minutes from demand to the last publish. No usage pause.
- v1: 833 pages unpublished; corpus/ holds 2,522 crawled pages (15 MB).

## Last 5 decisions
1. 2026-11-07: Footnote Daily v2 spec adopted; v1 archived to archive/v1; guard reduced to the .env block; every v1 page unpublished.
2. 2026-11-07: queue rows auto-approved for the pilot (the spec allows --auto-approve); 10 pilot questions chosen as one per topic plus two more housing ones.
3. 2026-11-07: the exemplar went through the review loop by hand (three reviews, 16 then 6 then 0 mismatches) and is published as the first article; Ajay still edits it.
4. 2026-11-07: style guide and writer prompt gained a "precision when paraphrasing" block (exact attribution, no added detail, official wording for categories, apply every listed fix), because all four rejections were of that kind.
5. 2026-11-07: the publish lint treats a 401/403/429 from a cited page as a blocked warning, not a dead link (rentcafe.com, nysenate.gov and a Cornell announcements page block automated clients; reviewers open them fine).

## Open questions (owner)
- footnote-style-guide.md was not in the repo or home folder; docs/v2/style.md is a draft stand-in. Replace it verbatim when provided.
- The 4 rejected pilot questions are real gaps; say the word and they re-enter the queue as fresh rows after the style and exemplar edits (the spec's one-revision rule stands as written).
- reddit.com blocks Anthropic's fetcher, so sessions use College Confidential, the Cornell Daily Sun, YouTube and search snippets for student experience; a read-only Reddit API credential would be needed to open threads.
- Launch and money items that need owner accounts or keys: real domain and DNS, Search Console and GA4 ids, a Google-certified consent platform, AdSense (after 25 to 40 articles), affiliate programs, Grow, Unsplash and Pexels keys. Everything is wired through config/monetization.yml; policy pages carry [OWNER: fill in] markers for the legal entity, address and contact email.
- Ithaca College (v1 B7) is outside the v2 scope as written; its crawl was stopped.
