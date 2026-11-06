SPEC: Bulk mode, research once, write many
Version: 2.0 · Owner: Ajay · Date: 2026-11-06 · Overrides: fast-mode and earlier specs where they conflict
1. Objective
Move page production out of Claude Code sessions and into a plain Python pipeline that calls the Anthropic API directly, using the Message Batches API. Claude Code builds and maintains the pipeline; it does not write pages one by one. Target: 500+ verified pages from one batch run, finished in about an hour, then repeated per school.
Why: one interactive session writes a few pages an hour. The Batches API takes up to 100,000 requests per batch, charges 50% of standard prices, and most batches finish within an hour.
2A. School dossiers first (research once)
Before any article, build a full intelligence dossier for each school and its town. Every later page draws from it, so nothing gets researched twice.

* D1. Crawl the official sites through their sitemaps (sitemap.xml and robots-allowed sections only), concurrency 20, using the existing safe fetcher:
   * the school's housing, dining, registrar, admissions, financial aid, bursar, transportation, health, careers, alumni, parents and international offices
   * every college and department page
   * the course catalog and Class Roster API
   * city, county, and transit sites
 Store every page's text by hash, with URL and date.
* D2. Extract structured facts with the Batches API (one request per fetched page, `extraction_model` alias). The output is typed claims (fees, deadlines, rules, eligibility, locations, contacts, steps), each with an exact source quote. Code then checks that each quote appears verbatim in the page text, and dedupes facts across pages.
* D3. Assemble the dossier per school at `docs/dossiers/<school>/` plus the database. It covers:
   * identity
   * every entity (halls, dining, libraries, buildings, routes, offices, programs, majors)
   * every process as a step graph (applying for housing, changing majors, internal transfer, add/drop, leave, transfer credit)
   * costs, every dated deadline, policies, and contacts
   * the town (neighborhoods, transit, services, rentals data from permitted sources)
   * known conflicts between official pages
   * gaps (what the official sites don't say)
 The dossier also gets a readable `summary.md` for Ajay.
* D4. Question map from the dossier. Generate every question a student, transfer, parent, alum, or job seeker would ask about each entity, process, cost, and deadline in the dossier. Merge in `data/questions/*.yaml` and the existing 1,230 clusters, then dedupe by answer.
* D5. Ranking and niche scan (cheap, batched).
   * For each question, use cached search observation (top 10, two variants, at most one search per question cluster, cache 14 days) to classify the incumbent as strong dedicated, weak, outdated, forum-only, or none.
   * Order the queue: underserved questions first (forum-only, outdated, or no dedicated answer), then weak, then the rest. Strong-incumbent questions are written last, or folded into a hub as a section.
   * Underserved audiences (transfers, community-college transfers, international, first-gen, parents, alumni, staff job seekers, town residents) get priority within each tier.
* D6. Per-question win note: one line from the scan ("top results are 2018 Reddit threads and a PDF; we win with the current fee table and step list"), passed to the writer.

The dossier refreshes on each source's refresh date. Changed pages trigger re-extraction and update the affected articles.
2. Architecture for articles (5 stages, only 2 use a model)

1. Plan (code): build the page list from `data/questions/*.yaml` plus every harvested entity (halls, dining, libraries, TCAT routes, town services), with templates per page type: question guide, entity guide, process guide, comparison only for observed pairs. Skip existing pages, unless their sources changed.
2. Gather (code): pull the page's facts and source quotes from the dossier, not from the web. Fetch new pages only for gaps.
3. Write (Batches API): one request per page.
   * The shared system prompt (style guide, page template, citation format) goes in a cached prefix.
   * The page's question, its dossier facts with quotes, and its win note (D6) go in the user turn.
   * The output is structured JSON: title, meta, H1, answer, sections, table, next steps, and claim list with source ids and exact quotes.
   * Model: `writing_model` alias.
4. Check (code):
   * every number, date, and dollar amount in the prose matches a quote that appears verbatim in its source text
   * the SEO basics from the R45 gate (title ≤ 60 with key words, meta, one H1, answer first, 2+ internal links, schema)
   * no banned filler or internal terms
   * the overlap check (< 60% with any page)
 Failing claims are removed. If the answer survives, the page continues; otherwise it's skipped.
5. Verify + publish (Batches API, then code): one cheaper verification request per page (`verification_model` alias) confirms each remaining claim against its quote. Claims marked wrong are removed. The page is rendered to `build/site/` and Netlify is deployed once per batch.

3. Speed and cost controls

* Prompt caching on the shared prefix for every request.
* One write request and one verify request per page. No correction rounds, no agent dispatches, no strategist or planner calls.
* Batches are submitted in chunks of 200 to 1,000 pages. Results are polled and processed as each batch completes, and the run resumes from the database after any interruption.
* Spend cap: `CAMPUS_API_DAILY_CAP_USD` in `.env` (default 25). The pipeline estimates cost before submitting each batch, refuses to exceed the cap, and records actual cost from the API usage fields. The digest reports cost per published page.
* Fallback with no API key: `scripts/parallel_headless.sh N` shards the page list across N parallel `claude -p` workers (default 4), each writing only to its own output folder. One serial publish step merges them. This is slower and limited by plan usage.

4. Skills to adopt (reference only, no hooks)

* Vendor `coreyhaines31/marketingskills` programmatic-seo (instructions only) pinned to a commit. Use its playbooks and thin-content checklist to improve our page templates. Record the source, SHA, and license in `docs/ops/skill-evaluations.md`.
* Do not install `claude-seo` or any skill with scripts or hooks until its code is reviewed and logged. Not needed for bulk mode.

5. Writing rules (unchanged from reader-first)

* Direct, practical answer first. Built from what sources say.
* One short "Not confirmed" note at the end, at most 3 bullets.
* Tables for comparisons, numbered steps for processes.
* Plain dates ("November 6, 2026"), and a clean sources list.
* One brand: Footnote Daily. No internal terms on public pages.

6. Keep exactly

* Facts only from fetched official or permitted sources, each tied to an exact quote.
* No scraping against robots or terms.
* No fake reviews, ratings, or copied text.
* No near-duplicate pages.
* Secrets only in `.env`.
* The live ramp still governs public release once a real domain is connected. Bulk mode fills the ready queue and the preview; it does not mass-publish to a live domain.

7. Owner actions

* Create an API key at console.anthropic.com, add billing, and add `ANTHROPIC_API_KEY` to `worker/.env` (Ajay does this; Claude never reads `.env`).
* Optionally set `CAMPUS_API_DAILY_CAP_USD`.

8. Acceptance

* B0. The Cornell + Ithaca dossier exists:
   * at least 1,000 official pages crawled
   * every claim has a verbatim quote
   * entities, process graphs, deadlines, costs, conflicts, and gaps are filled in
   * `summary.md` is readable
   * the question map has at least 500 deduped questions
   * each question has an incumbent class and an order, with underserved questions first
   * cost and minutes are reported
* B1. A dry run (no API calls) on 20 pages builds the plan, fetches sources, and prints the cost estimate.
* B2. A 20-page batch completes end to end: written, checked, verified, published to the preview. The report shows pages published, pages skipped with reasons, minutes, and cost per page.
* B3. A 500-page batch run completes, resumes correctly after a forced interruption, stays under the spend cap, and redeploys the preview.
* B4. A random 10-page sample passes a manual-style audit by a fresh Claude Code review (facts match sources, reads well, no internal terms). Its findings are logged in the digest.
* B5. The parallel headless fallback runs with 4 workers on 20 pages without file conflicts.
* B6. Existing tests still pass.
* B7. A second school completes dossier, question map, and 100+ pages using only config changes.

9. Milestones

1. Dossier for Cornell + Ithaca: crawl, extract, assemble, question map, niche scan (B0)
2. Plan + gather stages and the dry run (B1)
3. Write, check, and verify through the Batches API on 20 pages (B2)
4. Scale to 500, with resume and the spend cap (B3, B4)
5. Headless fallback, skill vendoring, regression (B5, B6)
6. Next schools: run dossiers for the expansion list one school at a time, then bulk articles for each (B7)
