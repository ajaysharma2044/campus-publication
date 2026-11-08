# Footnote Daily v2: research-first article pipeline

Owner spec, 2026-11-07. Paste this into Claude Code in the campus-publication repo. It replaces bulk-mode, subscription-only, lean mode and continuous-local-run wherever they conflict.

## Why v2 exists (read this first)

v1 optimized for "never say anything unverifiable" and ended up only able to restate cornell.edu. Specific causes found in the repo:

1. Topics come from supply, not demand. `bulk/questions.py` turns facts found on official pages into questions. Result: live pages like "Profile Picture Kiosk 2.0", "PE 1643 Intro to Routesetting", "Student Employee of the Year Award". Only 114 of 964 clusters had any observed demand, and there is no SERP access, so the system never knows who ranks.
2. The writer is blindfolded. Workers get `Read,Write` only, a list of up to 40 extracted quotes, no web, no full pages, no competitor view. Every sentence must map to a quote, then the verify pass deletes sentences. A page built this way can never contain more than the official page already says, so it cannot outrank it.
3. The content rules ban what wins. `UNSERVABLE` drops reddit, reviews, experiences, "what is it like", "worth it", "best", "pros and cons". Those are the searches students make where official pages are weak.
4. Fact-family hubs produce grab-bags. "Cornell Campus Services Rules" mixes library chat, I-9 forms and club constitutions on one page because they share a fact family.
5. Bureaucracy compounds. ~117k words of spec/state/docs, 22.8k lines of Python, 15 agents, a 26-item SEO gate, a 24-point rubric, WordPress, a live ramp, budget caps, guard hooks. Each fix (lean, bulk, reader-first, subscription-only) added a layer and removed nothing. The first live page took 28 dispatches, 876 turns and 227 minutes; three verifier rounds contradicted each other.
6. Sources were locked to official sites. `data/schools/cornell-university.yaml` crawls only Cornell, city and county hosts, and the crawl, extract, dossier, plan and verify stages all filter on `source_kind LIKE 'official%'`. Apartments, landlords, transit, airlines, buses, course reviews, local businesses and student discussion were never read.

v2 principle: one page that beats the current #1 result is worth more than 50 pages that restate the official site.

## Scope: everything a student, parent or alum deals with

Anything about life at the school or in its town is in scope. Starting topic seeds (the demand step adds more on its own):

* Housing: dorms, program houses, co-ops, Greek housing, off-campus apartments, Collegetown vs Fall Creek vs downtown, specific buildings and landlords, leases, subletting, roommates, move-in and move-out, storage, renters insurance, tenant rights in Ithaca.
* Getting there and around: flights into ITH, SYR and ELM, buses and shuttles to NYC, Boston and Philly, airport rides, driving and parking, TCAT routes, biking in winter, rideshare, break travel.
* Classes and academics: specific courses and professors (from public course review sites and student discussion), easy and hard requirements, registration strategy, add/drop, switching colleges, internal transfer, study spots, tutoring.
* Money: real cost of living, cheap groceries, meal plan math, jobs on and off campus, financial aid appeals, budgeting by scenario.
* Daily life: dining, food in Collegetown and downtown, gyms, healthcare and pharmacies, phones and banking, winter gear, safety, nightlife, clubs and joining them.
* Careers: internships, recruiting timelines, career fairs, specific employers that hire from the school.
* Parents and families: visiting, hotels, move-in weekend, graduation, what to send.
* Alumni: benefits, events, staying in Ithaca after graduation.

## Sources the writer may use (any public page, ranked by trust)

1. Official: the school, city, county, transit agencies, airlines, bus companies, landlords' own sites. These are required for hard facts (prices, dates, rules, schedules, addresses).
2. Listings and data: apartment listing sites, booking and schedule pages, public course review sites, public salary or employer data, map data.
3. Student and local voices: Reddit (r/Cornell, r/ithaca), College Confidential, student newspapers (Cornell Daily Sun), YouTube dorm tours, local news. Used for experience, tips, gotchas and opinions, always attributed and linked, never treated as the source of a hard fact.

Read pages live with WebSearch and WebFetch. Respect robots and terms, never log in, never scrape listing sites in bulk; read a page the way a person would.

## Article types (pick the one that fits the question)

* How-to / process guide: "How to sublet your Collegetown apartment for summer."
* Decision guide: "Collegetown vs downtown Ithaca: where should you live junior year?" with a clear recommendation by situation.
* Use-case / scenario guide: "Getting from JFK to Cornell as an international student with two suitcases", "Budget for a sophomore living off campus on $1,200/month", "Parents' guide to move-in weekend."
* Comparison: buildings, landlords, meal plans, buses to NYC, side by side with prices.
* Place / thing guide: a specific dorm, apartment building, course or route, written as what it is actually like plus the facts.
* Checklist / timeline: "Everything to do before your first Cornell winter", "Transfer student first-month checklist."
* Roundup: "Cheapest ways to get to NYC from Ithaca", "Quiet study spots that are open late." Rankings are allowed when the criteria are stated.

Each article should include whatever makes it most useful: cost tables, step lists, timelines, maps or directions, "if you are X, do Y" sections, common mistakes, and a short FAQ answering the related questions found in step 1.

## Pipeline (4 steps, files not database)

1. FIND DEMAND: real questions + who ranks now. Ajay approves. queue (5 min)
2. RESEARCH + WRITE: one claude -p session per article; web + local corpus
3. REVIEW: fresh session fact-checks + beats-#1 test, one fix round
4. LINT + PUBLISH: code checks, render, Netlify

### Step 1: Find demand (`scripts/v2/find_demand.sh <topic>`)

One `claude -p` session per topic seed from the Scope section. Tools: WebSearch, WebFetch, Read, Write(`queue/**`).
For each seed it collects real questions from: web search results and "People also ask" style questions, r/Cornell and r/ithaca thread titles found through web search, College Confidential threads, and `data/questions/` (the owner's 90-question list). It then searches each candidate question once and records the top 5 results.
Output: append rows to `queue/queue.csv`:
`id, question, primary_query, topic, demand_evidence (urls), top_results (urls), verdict, angle, status`

* `verdict`: `gap` (no good answer ranks), `weak` (ranking answer is thin, old, forum-only or off-topic), `owned` (a strong dedicated page already answers it). Only `gap` and `weak` get `status=proposed`.
* `angle`: one sentence on what our page will do that the top result does not (combine 4 official pages, add costs in one table, add student experience, add a decision, cover the Ithaca side).
* Dedupe against existing `queue.csv` and `content/articles/` by meaning, not stemmer rules (the session judges it).

Ajay marks rows `approved` (or runs with `--auto-approve`). No scoring formulas.

### Step 2: Research and write (`scripts/v2/write.sh --workers 4`)

One `claude -p` session per approved row. Tools: Read, Grep, Glob (repo + `corpus/`), WebSearch, WebFetch, Write(`content/articles/**`). Model: opus for writing if the plan allows, else sonnet. Max ~40 turns.
Inside the session, in this order:

1. Read the top 3 current results for the primary query. Note what they get right and what they miss.
2. Research hard facts from official sources of any kind (school, city, transit, landlords, airlines, bus companies): grep `corpus/` (the 2,508 crawled Cornell pages exported as text) when it helps, and fetch live pages for everything else and for anything time-sensitive.
3. Research the real experience from listings, review sites, student newspapers and student discussion (Reddit, College Confidential): pain points, tips, gotchas, what people wish they had known.
4. Pick the article type from the Scope section that best fits the question.
5. Write the article to `content/articles/<topic>/<slug>.md` following `docs/v2/style.md` and matching the quality of `docs/v2/exemplar.md`.

Frontmatter: `title (<=60 chars), meta (120-155), primary_query, topic, school, updated, sources: [{url, title, accessed}], queue_id`.
Content rules (the whole list; keep it this short):

* First paragraph answers the question directly. Then the details a student actually needs, in the order they need them.
* Every hard fact (number, date, fee, deadline, rule, phone, address) links inline to the official source it came from. No fact without a source.
* Student experience is allowed and wanted: paraphrased, attributed to where it came from ("Several 2025 r/Cornell threads say the Route 30 is the one that runs late"), linked. Never invent quotes, people, ratings or numbers. Never copy more than a short phrase.
* Our own advice is allowed when it is clearly advice and follows from the facts ("If you need a single, apply in the first window").
* Tables for comparisons and costs, numbered steps for processes, at least two internal links to related articles when they exist.
* No em dashes. No filler ("navigating", "it's important to note", "delve", "vibrant"). Length fits the question; most pages 700 to 1,500 words.

### Step 3: Review (`scripts/v2/review.sh`)

A fresh `claude -p` session per article (it did not write it). Tools: Read, WebFetch, WebSearch, Write(`content/reviews/**`).
It does two things and writes `content/reviews/<slug>.json`:

1. Fact check: opens every cited source and checks every hard fact against it. Lists mismatches.
2. Beats-#1 test: searches the primary query, opens the #1 result, and answers: "Would a student with this question be better served by our page? yes/no, why, and the 1 to 3 changes that would make it yes."

Verdict: `pass`, `fix` (with an exact list), or `reject`. A `fix` goes back to the writer session for ONE revision, then publishes if facts are clean, or is rejected. No rubric scores, no multiple rounds.

### Step 4: Lint and publish (`scripts/v2/publish.sh`)

Code only: frontmatter complete, title and meta length, no em dashes, banned-phrase list, internal links resolve, every source URL returns 200, no near-duplicate of an existing article (title + primary query similarity), no copy of more than 25 consecutive words from any source. Then render with the existing `render/` templates to `build/site/` and deploy to Netlify every 10 articles.

## Images and visuals

Every article gets at least one useful visual. Never use an image we don't have the rights to.
Primary source: photos from the internet that are licensed for reuse, credited on the page. Automated, no owner work needed.

1. Photo finder (`scripts/v2/find_images.py`): for each article, search by subject ("Mews Hall Cornell", "Collegetown Ithaca", "TCAT bus") in this order: Wikimedia Commons API, Openverse API (aggregates Flickr and other openly licensed collections), then Unsplash and Pexels APIs for generic shots. Accept only these licenses: CC0, Public Domain, CC BY, CC BY-SA, Unsplash License, Pexels License. Reject NC (non-commercial, since the site runs ads), ND if we crop or edit, and anything with no clear license.
2. Store the proof: download the file, resize to WebP under about 150 KB, and record in `content/images/credits.yml`: source page URL, author, license name, license URL, date found. Keep the license data from the API response; do not guess it.
3. Credit on the page: caption under each photo in the license's required form, e.g. "Photo: Jane Doe / Wikimedia Commons, CC BY-SA 4.0" with links to the source and license. CC BY-SA images that we edit are shared under the same license.
4. The writer session picks the best 1 to 4 images per article from what the finder returns, writes alt text and captions, and places them where they help (the building in a dorm guide, the bus in a transit guide).

Also used:

* Generated visuals built from the article's facts (code, not AI images): cost charts, deadline timelines, step diagrams, route tables. Extend `render/figures.py`.
* Maps: OpenStreetMap-based static maps with the required attribution.
* Embeds: YouTube dorm tours and Instagram posts through their official embed players (the platform handles permission).
* Owner photos whenever Ajay or the team drop them into `content/images/inbox/`; they replace internet photos for the same subject.
* Permission photos: a template email asking landlords and local businesses to let us use their photos with credit and a link; approved ones are logged in `credits.yml` with the email saved.

Never: photos copied from cornell.edu, landlords, news sites or Google Images without a reuse license or written permission, even with a credit (a credit is not permission); AI-generated images that look like photos of real places. Every image gets descriptive alt text and a caption. Pages stay fast: lazy-load images, keep each under about 150 KB.

## Ads and money

Start earning on day one, with a staged plan:

1. Now (before launch): move off the Netlify preview to the real domain, remove `noindex` from production, add Google Search Console and GA4, and add privacy, about, contact, editorial policy and corrections pages. Add a cookie consent banner that uses a Google-certified consent platform, which ads need for EU/UK visitors. Leave ad slots in the templates (in-content after paragraph 3, sidebar on desktop, sticky footer on mobile) that collapse when empty.
2. Apply to Google AdSense once 25 to 40 v2 articles are live. It has no traffic minimum, but it rejects thin or unfinished sites, which is another reason to unpublish the v1 pages first. Add `ads.txt`.
3. Affiliate links from launch (often worth more than ads on a new site): renters insurance, dorm and apartment essentials, bus and train tickets to NYC/Boston, storage, moving, textbooks. Disclose them on every page that has them. Links only where they actually help the reader.
4. Switch networks as traffic grows (check each network's own page before applying, since these change often):
   * Mediavine Journey: about 1,000 sessions a month from US/UK/CA/AU/NZ visitors, plus its Grow script running for 30 days first. Install Grow at launch so the clock starts.
   * Raptive: about 25,000 pageviews a month, mostly from US and similar countries.
   * Mediavine full network: about $5,000 a year in ad revenue.
5. Direct local sponsors later: Ithaca landlords, storage companies, tutoring services and restaurants on matching pages, clearly labeled "Sponsored". Never let a sponsor change what an article says.

Build: `render/` reads ad and affiliate settings from one `config/monetization.yml`, so switching AdSense to Mediavine is a config change, not a rebuild.

## Repo cleanup (do this first, in one commit)

* Move to `archive/v1/` (do not delete): `scripts/run.sh` loop, `.claude/agents/*`, `worker/campus_worker/bulk/`, `agents/`, `pipeline.py`, ramp, budget, dispatch, `seo_gate.py`, rubric/editorial gates, `wp/`, `specs/*.md`, old `STATE.md`, `BACKLOG.md`, `SPEC.md`. Keep: crawler/fetcher, `render/` templates and static assets, Netlify deploy, robots/permission handling.
* Remove every `source_kind LIKE 'official%'` restriction and the `UNSERVABLE` filter from anything v2 keeps.
* Export crawled page text from Postgres to `corpus/<host>/<path>.txt` (one-time script). After that, v2 does not need the database for content; articles and queue are files in git.
* New `CLAUDE.md` under 40 lines (points to this spec, style guide, how to run). New `STATE.md` under 60 lines and overwritten, not appended: what is running, counts, last 5 decisions, open questions.
* Remove the hook rules that block editing specs/settings; keep only the `.env` read block.
* Unpublish all 262 current pages from the preview. Any that are worth keeping get re-queued as rows and go through v2.

## Files to create

* `docs/v2/style.md`: copy `footnote-style-guide.md` exactly as the owner provides it.
* `docs/v2/exemplar.md`: one hand-polished article (start with "Cornell transfer housing: how it actually works") that every writer session reads as the quality bar. Ajay edits it before the batch run.
* `scripts/v2/*.sh` and short prompt files `scripts/v2/prompts/{demand,write,review}.md`. Plain bash + python, parallel workers, pause and resume on usage limit (reuse the existing `Pause` logic), STOP file.

## Acceptance

1. Pilot: 10 approved questions, written and reviewed. Report time per article and sessions used.
2. Ajay blind-compares 5 of them against the current #1 Google result for their query. Target: ours preferred on at least 4. If not, fix the style guide and exemplar, not the pipeline.
3. Zero fact mismatches on a manual spot check of 20 hard facts across the 10 pages.
4. Only after 1 to 3 pass: run continuously at 4 workers, report articles/hour after every 10.

## Guardrails for Claude Code

* Build only what this spec lists. If something seems missing, write it under "Open questions" in STATE.md and keep going on the rest; do not add new gates, agents, scores or databases.
* Do not patch around quality problems with code rules (stemmers, regexes on titles). Quality problems are fixed in the prompts, the style guide and the exemplar.
* Respect robots and site terms; paraphrase forum content and link it; never scrape behind logins.
