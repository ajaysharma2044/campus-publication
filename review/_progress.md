2026-11-10 15:52: Run started from docs/v4/RUN-NOW.md with the agent kit installed (commit 38240e6). Calls made so far: (1) new calculators are built under review/tools/<slug>/, never content/tools/, because the site deploy publishes every directory under content/tools/; nothing in this run reaches the live site. (2) The gold-set file .claude/skills/gold-set/examples/feature-pillar.md holds no full text of 'Where Cornell Sleeps' (not in the repo or Downloads), so writers work from its annotated excerpts; paste the article in when it is available. (3) The idea list has no money ideas, so no money fact file was built. (4) The kit's README, SPEC, PILOT and RUN-NOW went to docs/v4/ so the kit's README does not read as the repo's; CLAUDE.md is unchanged, as the kit's SPEC stage 0 says. (5) Checker results go to review/checks/, not content/checks/ (the v3 pipeline's directory). (6) Fact files: housing 635 rows, getting-around 667, dining 651, all validating with zero errors; fixes logged in intel/<topic>/facts-fixes.md.

**10 pages done** (2026-11-10 17:53): 272 left to write; problems: none (four pages were briefly marked for review while their checks were still being recorded; all 14 wave 1 pages passed).

**20 pages done** (2026-11-10 18:15, now 20): 244 left to write; problems: ideas 20 need review.

2026-11-10 18:22: Checker fix: page_check.py treated a one-line tool fence (the way live pages embed a calculator) as opening a block, so everything after the first embedded tool went unchecked, and both page_check.py and match_facts.py ended the frontmatter at the first '---' anywhere, which a URL containing three hyphens triggers. Both fixed minimally in the kit scripts (noted in their headers). Re-checked every review page: three wave 1 pages showed one or two repetition flags that had been hidden; they get one more editor pass. The Collegetown guide now carries a 180-row table of every Collegetown building in the inventory (each row linked to its landlord page). Two conflicts for Ajay's review in that guide's original table: 327 Eddy St. (page: Steve Fontana; county records: Goldenrod Real Estate) and 407 College Ave. (page: listed on Cornell's portal; inventory: Travis Hyde). Collegetown Dwellings (idea 118) has no landlord or official page anywhere, so it has no row.

**30 pages done** (2026-11-10 18:33, now 30): 233 left to write; problems: ideas 20, 24 need review.

**40 pages done** (2026-11-10 18:40, now 40): 222 left to write; problems: ideas 20, 24 need review.

**50 pages done** (2026-11-10 18:48, now 50): 212 left to write; problems: ideas 20, 24 need review.

2026-11-11 09:43: 2026-11-11: on Ajay's instruction (publish, then verify) every idea-run page and calculator was copied into content/ and deployed to https://eduexplained.netlify.app (noindex preview, 391 pages built, all build checks passed). New pages carry no queue row and no photo; rewrites kept their slug, queue row and photos; pages with fewer than five sources render as quick answers. The batched source verification is running on the live copies in content/ and will be followed by one more deploy; review/ keeps the drafts.

**60 pages done** (2026-11-11 11:51, now 253): 9 left to write; problems: ideas 20, 24 need review.

**70 pages done** (2026-11-11 11:51, now 253): 9 left to write; problems: ideas 20, 24 need review.

**80 pages done** (2026-11-11 11:51, now 253): 9 left to write; problems: ideas 20, 24 need review.

**90 pages done** (2026-11-11 11:51, now 253): 9 left to write; problems: ideas 20, 24 need review.

**100 pages done** (2026-11-11 11:51, now 253): 9 left to write; problems: ideas 20, 24 need review.

**110 pages done** (2026-11-11 11:51, now 253): 9 left to write; problems: ideas 20, 24 need review.

**120 pages done** (2026-11-11 11:51, now 253): 9 left to write; problems: ideas 20, 24 need review.

**130 pages done** (2026-11-11 11:51, now 253): 9 left to write; problems: ideas 20, 24 need review.

**140 pages done** (2026-11-11 11:51, now 253): 9 left to write; problems: ideas 20, 24 need review.

**150 pages done** (2026-11-11 11:51, now 253): 9 left to write; problems: ideas 20, 24 need review.

**160 pages done** (2026-11-11 11:51, now 253): 9 left to write; problems: ideas 20, 24 need review.

**170 pages done** (2026-11-11 11:51, now 253): 9 left to write; problems: ideas 20, 24 need review.

**180 pages done** (2026-11-11 11:51, now 253): 9 left to write; problems: ideas 20, 24 need review.

**190 pages done** (2026-11-11 11:51, now 253): 9 left to write; problems: ideas 20, 24 need review.

**200 pages done** (2026-11-11 11:51, now 253): 9 left to write; problems: ideas 20, 24 need review.

**210 pages done** (2026-11-11 11:51, now 253): 9 left to write; problems: ideas 20, 24 need review.

**220 pages done** (2026-11-11 11:51, now 253): 9 left to write; problems: ideas 20, 24 need review.

**230 pages done** (2026-11-11 11:51, now 253): 9 left to write; problems: ideas 20, 24 need review.

**240 pages done** (2026-11-11 11:51, now 253): 9 left to write; problems: ideas 20, 24 need review.

**250 pages done** (2026-11-11 11:51, now 253): 9 left to write; problems: ideas 20, 24 need review.

2026-11-11 13:48: 2026-11-11: the run is complete and verified. Every page the batched source check flagged has been through the fix round: 63 verification batches opened 602 cited sources once each (144 could not be opened: tcatbus.com, SpareFoot, RentHop, ecode360 and apartments.com sit behind bot challenges or returned 403/404, and claims resting only on them were removed or softened), checked 2,114 sentences, corrected 33 values in place (commit 048847f), and listed 549 claims the cited page did not state; 31 Sonnet fix batches rewrote or removed 460 of them, relinked or relabeled 73 as our own arithmetic with the inputs shown, and kept 14 with a reason (the verifier had opened a page other than the one the sentence cites). Batches c03 and c10 lost their reports to a network error after finishing their edits; their leftovers were settled by hand (scripts/ideas/claims_residue.py). page_check then ran over every page: a checker bug (quoted YAML titles counted their quote marks) explained 12 false failures and is fixed; 5 real failures from the fix round were fixed by hand; the corrected checker also failed 17 wave 1 and 2 pages (unsourced arithmetic paragraphs and repeated values after an embedded calculator, which the fence bug had hidden), fixed by one more Sonnet round with no flags kept. The 3BR per-person row on the Collegetown rent page now rests on The Cornell Daily Sun's whole-unit Ivy rent divided by three. Statuses: content/ copies are canonical (review/ keeps the drafts); 253 ideas are pages (215 done, 38 rewrite-done), 22 hub-row, 5 merged, 9 waiting-data (138, 170, 172, 174, 220, 281, 283, 285, 286), 2 needs-review (20, 24, price basis). Redeployed to https://eduexplained.netlify.app after each round; still a noindex preview, still no photos on new pages.
