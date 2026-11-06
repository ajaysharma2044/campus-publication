# Bulk mode: page template notes

Source: the vendored programmatic-seo playbook in `skills/vendor/marketingskills-programmatic-seo/` (pinned to commit `96798cf38736ecdba015a1d2b0521b0c8f8f41dd`; details in its `VENDOR.md`). Context: `specs/bulk-mode.md` sections 2 and 4. Written 2026-11-06.

Status: proposals only. No template, gate or constant was changed. The playbook gives no numbers, so every threshold below is a starting value to tune on the B2 (20 pages) and B3 (500 pages) runs.

Page types follow the bulk spec: question guide, entity guide, process guide, and comparison (observed pairs only).

Prerequisite for items 5, 8 and 9: in the site build, `render/site.py` (`TEMPLATE_BY_FORMAT`) sends every format except `policy` to `article.html`. `entity_profile.html` and `comparison.html` are used only by the fixture preview (`render/preview.py`). The site build has to pick a dedicated template per page type and pass the extra fields.

## Question guide

**1. A floor on what survives, checked after claims are removed.**
- Change: once the Check and Verify stages have removed failing claims, count what is left. A question guide needs the answer plus at least 3 quote-backed supporting facts (a figure, date, rule or step). Below that, do not render it: hold it and add its answer as a section on the topic hub (the same fold-into-a-hub move D5 uses for strong-incumbent questions).
- Why: the spec lets a page continue whenever "the answer survives", so a page can end up as one sentence. The playbook says to drop or noindex very thin variants instead of shipping them (`SKILL.md`, Indexation Strategy and Common Mistakes). Entity profiles already have a floor (`tier2.MIN_VERIFIED_CLAIMS` is 6, and 4 in lean mode). Question guides have none.
- Check: the B2 report lists pages held as thin, with the surviving claim count.

**2. Definition questions get a fixed shape.**
- Change: for "what is" and "what does ... mean" questions, use a one-sentence definition as the first paragraph, one worked example with a real figure or date from the dossier, then two or three related questions linked by code from the question map.
- Why: the playbook's glossary pattern asks for a definition, an example and related terms, with more depth than a dictionary (`references/playbooks.md` section 9). The strategy contract already has a `definition_sentence` snippet format; the template gives it a place.
- Check: the first paragraph stays inside the existing answer-first limit (50 words), and the example's figure maps to a claim.

**3. Audience pages must differ in substance, or become a section.**
- Change: make a separate guide for an audience (transfer, international, first-gen, parent, alum) only when the dossier has facts tagged to that audience that differ from the general answer: a different deadline, form, office or eligibility rule. Otherwise add an "If you are a transfer student" section to the general guide and make no new page.
- Why: persona pages need audience-specific content, and the usual failure is the same page under a different label (`references/playbooks.md` section 7; `SKILL.md`, Common Mistakes). `processes.decide_pages` already makes this standalone, section or none call for process nodes; reuse the idea in the Plan stage.
- Check: every pair of audience pages for one question differs in at least one critical claim.

**4. Related links filled by code after the batch's survivors are known.**
- Change: add a second render pass. Once the batch's published set is final, code fills the related block and the next-step links from dossier relationships (same entity, same office, adjacent step, same deadline), only to pages that exist, with descriptive anchors.
- Why: hub-and-spoke linking with no orphans (`SKILL.md`, Internal Linking Architecture). Today `version_context` in `render/site.py` sets `related=[]`, so the "Related tasks" list in `article.html` never renders, while the gate wants contextual links (`internal_links_three_contextual`, `not_orphan`). In a 500-page batch some pages get skipped, so links chosen earlier would point at pages that never publish.
- Check: `seo.check_internal_links` over the batch output reports no link to an unpublished page. It flags only redirected paths and paths missing from the registry today, so extend it to flag registry pages that are not published.

## Entity guide

**5. An "At a glance" block whose rows exist only when the data does.**
- Change: `entity_profile.html` is currently just an extension of `article.html`. Give it an "At a glance" block built from the dossier: cost (with period and basis), location, capacity or hours, deadline, owning office. A row renders only if a verified claim exists for it, carries its checked date, and is never a placeholder.
- Why: data-driven, conditional sections and per-page unique value (`SKILL.md`, Template Design and Core Principles 1). Profiles should aggregate sourced facts instead of restating one page (`references/playbooks.md` section 12).
- Check: a fixture entity with missing claims renders no empty rows.

**6. Show where official pages disagree.**
- Change: render a dossier conflict as a `conflicted` row in the fact table (`partials/fact_table.html`) with both values, each linked to its page, plus one plain line saying which office to ask. Keep gaps in the single Not confirmed note (3 bullets at most). Use plain wording, none of the audit-trail words the reader-first rules ban.
- Why: the dossier's conflicts and gaps are data that forum threads and PDFs do not have (`SKILL.md`, Core Principles 2, proprietary data). The `conflicted` status already exists in the comparison tool and has a style in `campus.css`.
- Check: every open conflict for the entity in the dossier appears as a row.

**7. Overlap measured on the prose, with names and numbers masked, across schools.**
- Change: add a second overlap measure in the Check stage. Split the written text into 5-word shingles after replacing school, entity and place names, numbers and dates with placeholders. Compare against every other page, including other schools, and hold a page that goes above the existing 60% limit.
- Why: the name-swap failure (`SKILL.md`, Common Mistakes; `references/playbooks.md` section 6, which asks for real local data rather than a swapped city name). The current overlap code (`tier2.overlap_with_published`) compares fact-table rows only, and each row key includes its value, so two profiles with the same scaffolding but different values pass. B7 (a second school by config only) is where this will show.
- Check: two synthetic pages that differ only by hall name fail; two genuinely different halls pass.

## Process guide

**8. A dedicated template fed by the step graph.**
- Change: add `process_guide.html` (extends `article.html`) with fixed blocks: who this is for; before you start (prerequisites, forms); numbered steps, each naming the office that owns it; a dated Deadlines table; exceptions; then the Not confirmed note. Fill it from `processes.effective_rules` (steps, prerequisites, GPA and course requirements, deadlines, forms, offices, exceptions). The Plan stage emits a standalone page only where `processes.decide_pages` says standalone; other nodes become sections or nothing.
- Why: real, specific steps and use cases beat a vague overview (`references/playbooks.md` section 8, Integrations), and doorway pages are out (`SKILL.md`, Core Principles 6). Today the graph is rendered by the navigator tool; a standalone process page would go through the generic `article.html`.
- Check: every numbered step has a claim id, and a node identical to its parent produces no page.

## Comparison

**9. "Pick by situation" lines generated from the rows that differ.**
- Change: below the table, add a short block built by code: one line for each row where both sides are known and the values differ, in the form `Need [row label]? [A]: [value]. [B]: [value].` No ranking and no model-written verdict. The existing "Tradeoffs the records support" list stays.
- Why: the playbook wants balanced analysis plus a clear recommendation by use case (`references/playbooks.md` section 4). Generating the lines from the table keeps the values exact.
- Where: `comparison.html` already flags differing cells, and the data comes from `tools/comparison.py` (`compare`).
- Check: every value in the block equals a cell in the table.

**10. A comparison floor, and a refresh tied to both sides.**
- Change: publish a comparison only when at least 5 rows have known values on both sides and at least 2 of those rows differ; otherwise skip it. Re-render whenever either entity's claims change, and show the older of the two sides' check dates as "Facts verified" instead of the render date.
- Why: actual comparison data that is updated when the compared things change (`references/playbooks.md` section 4); stale rows make pages wrong and thin (`references/implementation-platforms.md`, data refresh). Comparisons are already limited to observed pairs (`tier2.py`); this adds a content floor.
- Check: the batch reports list comparisons skipped for too few comparable rows.

## Already covered, no change needed

- R45 gate items for unique title and meta, one H1, breadcrumb and page-type schema, contextual links, orphans and cannibalization (`seo_gate.py`).
- Subfolder URLs (`seo.classify_url`), observed-pair comparisons and the entity claim floor (`tier2.py`), process page decisions (`processes.py`).

## Not taken from the playbook

- Best-of curation, persona testimonials, downloadable templates, example galleries, converters and translations: no matching page type, or banned (superlative headlines, fake reviews).
- The platform comparison and vendor disclosure text in `references/implementation-platforms.md`: we render statically and deploy to Netlify.
- Rollout, not template work: split sitemaps by page type and school (`SKILL.md`, Indexation Strategy), and prove the first 20 to 50 pages before scaling (`references/implementation-platforms.md`, Choosing step 4). B2 and B3 already do the second.
