EduExplained Pre-Launch Fix Spec

For: Claude Code, working in the campus-publication repo Owner: Ajay Sharma Goal: Fix every issue found in the November 2026 site review, build the missing sections, and set up a safe, gated launch system. Execute this spec faithfully. Do not redesign things this spec does not ask you to change.

0. Context

EduExplained is a research-first education publisher. The current site (Astro, hosted on Netlify at https://eduexplained.netlify.app/) has about 380 pages, all about Cornell and Ithaca: roughly 305 articles, 19 tools, 8 datasets and 22 "start here" pages. The custom domain is registered on GoDaddy and connected to Netlify. Wherever this spec says {{DOMAIN}}, use that domain (ask Ajay if it is not in the repo config).

The content quality is strong: answer-first structure, heavy sourcing, original tools and datasets, consistent figures. This spec fixes the gaps, not the foundation.

Right now every page is noindex, nofollow, robots.txt disallows all crawlers, and sitemap.xml is empty. Keep it that way until Phase 9, and do not run Phase 9 without Ajay's explicit approval.

1. Non-negotiable rules (apply to every phase)
No em dashes anywhere in content, UI copy, metadata or reports. Use commas, colons, periods or parentheses.
Never publish a research gap. No sentence may tell the reader that the sources, the guide or the page lack information. If research cannot answer a question the page promises to answer, follow the gap workflow in Phase 1. Never ship the admission.
Never invent facts. Every number, date, price, rule and name must trace to a cited source. AI fills templates from verified data; it does not write facts from memory.
No forum users as sources. Do not cite Reddit, College Confidential or similar posters. Official sources, government data, primary documents and established news outlets only.
Sensitive topics stay strictly factual. Fraternity matters, crime, evictions, landlords and legal rights: sourced facts only, no characterizations of named people or companies beyond what a cited source states. Legal-rights pages carry a short line that the page is general information, not legal advice.
Do not change indexing state (robots, noindex, sitemap) outside Phase 9.
Every change must be verifiable. Each phase ends with a report and passing checks (Section 11).
All AI work runs on Ajay's Claude subscription inside Claude Code. Do not add an Anthropic API key.
Phase 0: Baseline audit (do first, change nothing)
Crawl the built site locally and produce reports/00-baseline.md with:
every URL, its section, word count, external source count, Updated date
a list of pages matching the banned-phrase patterns in Phase 1
every tool that exists at more than one URL
every page whose section does not match its topic (see Phase 3 mapping)
pages per section
Commit the report. Do not modify content in this phase.

Acceptance: report exists and its counts match a fresh crawl.

Phase 1: Fix the pipeline so gaps are never published
1a. Banned-phrase linter

Create scripts/lint-content.(ts|js|py) that fails the build if any page body matches these patterns (case-insensitive). Extend the list if you find variants.

sources? (for|behind|in) this (guide|page|article)
the sources? .{0,40}(do not|does not|don't|contain no|include no)
no source (gives|lists|says|reports|provides)
(page|site|document) (lists|gives|shows|provides) no 
we (could not|couldn't) find
not (included|available) in (our|the) sources
as of (our|this) research

Wire it into the build and into the article pipeline so a draft that fails cannot be saved as publishable.

1b. Gap workflow (replace current behavior)

When a draft cannot answer a question the page's title or headings promise:

Search harder, using a source checklist for the topic type. Add these to the research agent's skill/md files:
Crime or safety: Cornell's Annual Security and Fire Safety Report (Clery Act statistics), Cornell Police reports, Ithaca Police Department data
Voting: New York State Board of Elections, Tompkins County Board of Elections (deadlines, registration, polling place lookup)
Local rules: City of Ithaca code and department pages, Town of Ithaca, Tompkins County
Tenant law: New York statutes (General Obligations Law, Real Property Law), NYS Attorney General tenant guides
Cornell policy: the specific Cornell office page, current-year PDFs, Cornell Chronicle
If the answer is found: add it with a citation.
If it is still not found: remove the unanswered section and adjust the title and headings so the page no longer promises it. If the remaining page no longer has a distinct purpose, merge it into the closest related page and add a 301 redirect.
Log every gap decision to reports/gaps.md (page, missing item, sources tried, outcome).

Acceptance: linter passes on the whole site; reports/gaps.md lists every resolved gap.

Phase 2: Rework the affected pages
Fix every page flagged in Phase 0 (expect roughly 50: about 10 with "sources for this guide" phrasing and about 40 with "page lists no" phrasing). Apply the Phase 1b workflow to each.
Mandatory specific fixes:
/cornell/getting-around/voting-in-ithaca-cornell-student-register-polling-place/: add New York registration deadlines, how to register, and how to find a polling place, sourced to the NYS and Tompkins County Boards of Elections. Link the official polling place lookup instead of listing locations from memory.
/cornell/getting-around/is-collegetown-safe-cornell-dorm-security-crime/: add campus crime statistics from Cornell's most recent Annual Security and Fire Safety Report, with the report year stated, plus any official Ithaca Police data available. Keep the existing building-safety and late-night-transit content.
/cornell/housing/ithaca-landlords-to-avoid-collegetown-reviews/: keep the approach (no naming without evidence). Rename the slug and title to match what the page actually does (for example "how to check an Ithaca landlord's record") and 301 the old URL. Replace the 1985 Dryden Road lead photo (see Phase 6).
Re-run the linter and fact checks after every batch of 10 pages.

Acceptance: zero linter failures; each mandatory page answers its title's question with citations.

Phase 3: Fix the category structure

Many non-transport topics sit under /cornell/getting-around/. Restructure before launch, because URLs are expensive to change after indexing.

3a. Target sections

Keep: housing, dining, money, academics, careers, transfer, parents, alumni. Use or create: getting-around (transport only), daily-life, health-safety, winter (optional, only if it improves navigation; otherwise fold winter pages into the sections below).

3b. Move these pages out of getting-around (adjust if Phase 0 finds more)
Page topic	New section
Dorm fire safety rules	health-safety
Student health insurance and finding a doctor	health-safety
Winter blues and campus resources	health-safety
Is Collegetown safe	health-safety
Snow days and class cancellations	daily-life
Voting in Ithaca	daily-life
Cornell ID card	daily-life
Dorm mail and packages; off-campus mail	daily-life
Laundry in dorms; laundromats	daily-life
Internet in dorms and apartments; internet providers	daily-life
Which dorms have air conditioning	housing
Heat out and frozen pipes; drafty apartments; setting up utilities	housing
Sidewalk snow removal rules	housing
New York driver's license and DMV	daily-life
What to wear in winter; winter activities; winter survival guide	daily-life (or winter)
First-month logistics checklist	daily-life

Driving, parking, buses, airports, biking, rideshare, carshare and break travel stay in getting-around.

3c. Mechanics
Generate 301 redirects for every moved URL in Netlify _redirects (or netlify.toml).
Update every internal link to point at the new URL directly. No internal link may hit a redirect.
Update breadcrumbs, section hubs, structured data and the search index.
Add a test that crawls the build and fails on any internal 301, 404 or orphan page (a page no hub links to).

Acceptance: zero internal redirects or 404s; every page reachable from its section hub; _redirects covers every old URL.

Phase 4: Consolidate duplicate tool URLs

These tools exist at two URLs, each self-canonical. Make /tools/<slug>/ the single canonical home:

rent split calculator (unequal rooms)
meal plan calculator by meals a week
should I bring a car (cost)
summer storage vs shipping vs sublet
Ithaca rent commute calculator

For each: keep the /tools/ page, 301 the duplicate to it, and where the duplicate had article content worth keeping, move that content onto the tool page or into a related article that embeds the tool component. Re-check Phase 0's list for any others.

Acceptance: each tool resolves at exactly one URL; no two pages render the same tool as their primary content.

Phase 5: Cannibalization audit
For each cluster below, list every page, the single search query it targets, and the intent.
Winter (about 12 pages)
Parking (about 10 pages)
Subletting (about 9 pages)
Lease timing (how-early-collegetown-leases-sign-2012-2026, when-to-sign-collegetown-lease-cornell, and the lead-times dataset, which uses 2017 to 2025; reconcile the year ranges)
Co-ops and Greek housing (cornell-co-ops-all-eight-compared, cornell-co-ops-greek-houses-cost-how-to-join, the fraternity pages)
Where two pages target the same query or intent, merge them into the stronger page and 301 the other. The two parking garage pages (parking-collegetown-downtown-ithaca-garages-permits and ithaca-parking-garages-dryden-road-green-street-cayuga) are the first candidate.
Where pages are distinct, make the distinction explicit in titles, H1s and opening answers, and cross-link them.
Write reports/05-clusters.md with the query map and every merge decision.

Acceptance: no two indexable pages target the same primary query.

Phase 6: Images
Flag every lead image that is more than 20 years old, does not show the page's subject, or is generic. Replace with a current, relevant, properly licensed image (Wikimedia Commons, Openverse, official press images where reuse is allowed) or remove the lead image.
Keep full attribution on every image: author, source, license name and license link.
Captions must describe what the photo actually shows. Never caption a photo as something it is not.

Acceptance: reports/06-images.md lists every replacement; no lead image fails the rules above.

Phase 7: Fill the empty sections

transfer, health, parents have zero articles; academics has 2; careers and alumni have 1 each. Empty hubs look thin.

7a. Transfer section (priority; build first)

Build data-first pages, each with a computed finding or official data table:

Cornell transfer admissions overview: requirements, deadlines, fall vs spring, who is eligible
One page per undergraduate college with transfer requirements and recommended coursework (CALS, Arts and Sciences, Engineering, Human Ecology, ILR, Hotel / Nolan within SC Johnson, Dyson within SC Johnson, Brooks, AAP). Confirm current college structure from Cornell's site before creating pages.
Cornell transfer acceptance data from the Common Data Set (section D), multiple years, as a dataset page with CSV, plus a trend chart
Guaranteed Transfer option: which colleges offer it, how it works, requirements (verify current policy)
Transferring from community college to Cornell: course planning and credit transfer
Transfer credit at Cornell: how credits are evaluated by college
Transfer student housing (link the existing page), transfer orientation, transfer student first-semester checklist
Transfer deadlines tool or timeline

TransferringUp rule: these pages stay neutral and informational. Do not insert TransferringUp promotion into article bodies. A single clearly labeled line in the author bio or a site-level disclosure is the only allowed mention.

7b. Other empty hubs

Until a hub has at least 5 quality articles, either fill it to 5 or hide it from navigation and keep it unindexed. Suggested starts:

Parents: visiting Cornell (hotels for move-in, family weekend, graduation), what parents should know about housing and leases as guarantors, aid and billing basics, how to send packages
Health and safety: Cornell Health basics, insurance, safety statistics (from Phase 2), emergency resources
Academics: pre-enrollment, waitlists (exists), majors overview by college, academic calendar
Careers: part-time jobs (exists), on-campus jobs, summer jobs, career services

Acceptance: transfer section has at least 10 published pages including the CDS dataset; every visible hub has at least 5 articles.

Phase 8: Authorship and trust
Replace "EduExplained editors" with real bylines. Create an author page for Ajay Sharma (editor-in-chief) with a bio placeholder for Ajay to fill: Cornell transfer student, public policy at the Brooks School, founder of a transfer admissions firm (with disclosure). Leave {{BIO}} placeholders rather than writing claims he has not approved.
Add "Edited by" / "Reviewed by" lines and Person structured data linked from each article.
Confirm editorial standards, corrections, sources and about pages are linked from the footer and from each article.
Data labeling: where figures can differ by definition (for example beds vs residents), state which one the page uses. Example: the site uses Cornell Housing resident counts (Toni Morrison Hall 306, Ganędagǫ: Hall 564), while the construction manager lists bed counts (314 and 577). Any page using either must say which.

Acceptance: no article shows a generic byline; author pages render with structured data.

Phase 9: Quality gate and wave release system (build now, launch only with approval)
9a. Per-page index control
Add an index field to every page's frontmatter: false by default.
Build a quality scorer (scripts/score-pages) that marks a page eligible only if all pass:
linter passes
at least 3 cited official or primary sources
has a distinct primary query (from Phase 5 map) not used by another indexable page
has at least one data element: table, computed figure, tool or dataset link
has a named author and an Updated date within the last 12 months
images pass Phase 6
Output reports/09-eligibility.csv with every page's score and failing checks.
9b. Robots, noindex and sitemap generation
Pages with index: true render index, follow; all others render noindex, follow (change from nofollow so links are still followed once crawlable).
sitemap.xml is generated only from index: true pages.
robots.txt is controlled by a single config flag LAUNCHED. When false (current state): Disallow: /. When true: allow all, block nothing needed, and list the sitemap URL. Block AI training crawlers (for example GPTBot, Google-Extended, CCBot) and allow search and retrieval crawlers (Googlebot, Bingbot, OAI-SearchBot, PerplexityBot). Check each company's current crawler documentation for exact user-agent names before writing the file.
9c. Waves
config/waves.json defines waves. Wave 1 is the top 300 to 500 eligible pages by score and expected demand, spread across sections, always including the transfer section and the best housing, dining and tools pages.
A script promotes the next wave by flipping index: true on its pages and regenerating the sitemap.
Stop rule (Ajay enters Search Console numbers into config/wave-metrics.json): the next wave is allowed only if the previous wave is at least 50 percent indexed after 3 to 4 weeks, impressions are flat or rising, the weekly audit error rate is under 3 percent, and there are no manual actions.
Kill switch: one command sets index: false for an entire section and rebuilds.
Weekly audit script: samples 20 random indexable pages per section, re-fetches each cited source where possible, and flags numbers or dates that no longer match. Output reports/audit-YYYY-MM-DD.md.
9d. Domain cutover (prepare, do not execute)

Write LAUNCH_CHECKLIST.md with these steps for Ajay to approve and trigger:

Set the site base URL and all canonicals to https://{{DOMAIN}}.
Set {{DOMAIN}} as the Netlify primary domain; 301 every eduexplained.netlify.app URL to the matching {{DOMAIN}} URL.
Set LAUNCHED=true, promote wave 1 only, rebuild.
Verify with curl: robots.txt allows crawling, wave 1 pages return index, follow, other pages return noindex, follow, sitemap lists only wave 1, netlify.app redirects work.
Submit the sitemap in Google Search Console and Bing Webmaster Tools; enable IndexNow for Bing.

Do not perform these steps. Stop and report when the checklist is ready.

Acceptance: with LAUNCHED=false, the built site is byte-for-byte equivalent in indexing behavior to today (everything blocked). A dry run with LAUNCHED=true in a local build produces the correct robots, meta tags and sitemap for wave 1.

10. Order of work
Phase 0 (audit)
Phase 1 (pipeline fix)
Phase 3 (categories) and Phase 4 (tools), since they change URLs
Phase 5 (clusters)
Phase 2 (rework flagged pages, on their final URLs)
Phase 6 (images)
Phase 7 (transfer first, then other hubs)
Phase 8 (authorship)
Phase 9 (gate and waves, build only)

Commit after each phase with a clear message. Do not start a phase until the previous phase's acceptance checks pass.

11. Verification and reporting

After every phase:

Run the build, the content linter, the internal link test and the em dash check (grep for the em dash character across content and output must return nothing).
Write reports/NN-<phase>.md summarizing what changed, counts before and after, and anything left unresolved.
If a check fails and you cannot fix it within the rules above, stop and report instead of working around it.
12. Stop and ask Ajay when
a fix would require naming or characterizing a specific person, landlord or organization beyond what a source states
an official source contradicts another official source and the page's answer depends on which is right
a merge would remove a page that has a tool, dataset or unique data
the domain value is missing
anything in Phase 9d would be executed
