# Phase 5: cannibalization audit (2026-11-11)

Five clusters were audited by one agent each (every page, the single query it targets, the intent) and every merge decision was tested by a skeptic (reports/05-clusters-analysis.json). Seven pages merged into a stronger page and now 301 to it (plus the summer-storage tool article, handled in Phase 4). Pages that stay distinct got the title, opening and cross-link changes the audit asked for, except where the page was in Phase 2's rework set at the time (listed under Deferred; they are applied after Phase 2). Each merge was carried by an agent and checked by a skeptic (reports/04-05-apply-results.json, reports/05-finish-results.json).

## Merge decisions

| Cluster | Merged page (now a 301) | Into | Skeptic |
|---|---|---|---|
| Winter | ithaca-rental-heat-requirements-winter | ithaca-heat-out-frozen-pipes-landlord-must-do | see results file |
| Parking | ithaca-parking-garages-dryden-road-green-street-cayuga | parking-collegetown-downtown-ithaca-garages-permits | sound |
| Parking | having-a-car-at-cornell-student-guide | cornell-parking-guide-campus-collegetown-ithaca | see results file |
| Subletting | sublet-apartment-study-abroad-semester-cornell | cornell-summer-sublet-how-to-sublet-apartment-ithaca | see results file |
| Subletting | summer-storage-vs-shipping-vs-sublet-cornell-cost | /tools/summer-storage-vs-shipping-vs-sublet-cornell-cost/ | Phase 4 |
| Lease timing | how-early-collegetown-leases-sign-2012-2026 | when-to-sign-collegetown-lease-cornell | sound |
| Co-ops and Greek housing | how-cornell-co-ops-work-chores-meals-governance | cornell-co-ops-all-eight-compared | see results file |
| Co-ops and Greek housing | cornell-fraternity-house-cost-live-in-rules | cornell-fraternity-sorority-housing-2026-27 | sound |

## Query map per cluster

### Winter (16 pages)

Winter cluster: 16 live pages (12 core, 4 at the edge), per-page map in pages. Four more keyword hits are the breaks cluster and are left to that audit: cornell-winter-break-travel-home-2026 (1672w), cornell-winter-break-housing-who-can-stay (1524w), cornell-dining-hours-winter-break-closures (915w), storing-a-car-ithaca-summer-winter-break-cornell (916w). No winter-specific tool or dataset exists.

(a) Same query or intent

One merge. ithaca-rental-heat-requirements-winter (housing, 1260w, 5 sources) and ithaca-heat-out-frozen-pipes-landlord-must-do (1256w, 14 sources, moving to housing in Phase 3) serve the same renter with the same answer: both open with the Sept. 15 to May 31 season and the 68F day, 62F night minimums, and four of seven sections repeat (minimums, landlord will not fix, utility shutoff notice, who pays for heat). Keep heat-out: 14 sources against 5, plus frozen pipes, the Building Division number, the withholding-rent warning and a steps figure. Move in heat-req's two unique pieces (Ithaca's Sept. 15 start against the statewide Oct. 1, and "Do these myths hold up?"). Retitle the kept page "Ithaca heat rules for renters: 68F by day, 62F at night, and what to do when it fails", primary_query "ithaca apartment heat law landlord", and 301 /cornell/housing/ithaca-rental-heat-requirements-winter/ to its new housing URL. Explicit: heat-req has no tool or dataset and both its figures are duplicated in heat-out; per spec section 12, confirm with the owner before removing it.

No other pair shares a query. Section-level duplicates to cut, not merge: the driving page's "Where can you park overnight in winter?" and the storms page's parking table both repeat the winter parking page; activities and blues both carry a dress paragraph and the $10 day pass and $115 membership; what-to-wear and driving both repeat the pillar's monthly snow table.

(b) Distinct but easy to confuse

1. Pillar (surviving an ithaca winter) vs surviving-ithaca-winter-old-apartment-drafty-house: the slugs share "surviving-ithaca-winter". Phase 3 moves the drafty page to housing anyway, so rename it then to how-to-stay-warm-old-ithaca-apartment under the same 301. Title and H1 ("How to stay warm in an old Ithaca apartment") already differ. Links: the pillar's "Off campus: heat, bills and the sidewalk out front" to drafty, heat-out and sidewalk; drafty's "What to do next" to the pillar.

2. Blues vs pillar and drafty: "How to cope with Ithaca winter: Cornell resources" reads as a general survival page. Title and H1: "Winter blues at Cornell: light boxes, Let's Talk and when to call"; primary_query "winter blues Cornell"; opening: "If the dark Ithaca winter is pulling your mood down, start with Cornell Health: $20 light boxes, Let's Talk drop-ins and a 24-hour line at 607-255-5155." Link it from the pillar's "The winter blues" section.

3. Storms vs driving: the storms primary_query is a keyword string ("Cornell Ithaca winter driving I-81 Route 13 snow tips") that collides with "driving in Ithaca in winter". Set it to "winter storm getting back to Cornell after break" and open with "If a storm is forecast for the day you travel back to Cornell, leave a day early: in 2019 OurBus cancelled Sunday trips and added Saturday ones." Driving page: title and H1 "Driving in Ithaca in winter: hills, plows and salt"; opening "Leave early, favor main roads over the steep side streets the city plows last, and park where the plows can reach." Cut its parking section to two lines pointing at the winter parking page. Link both ways.

4. Merged heat page vs drafty: "below the legal minimum" against "legal but cold". Drafty's second section already says so; add to the heat page: "If your thermometer reads above the minimums, the apartment is legal and cold; see how to stay warm in an old Ithaca apartment."

5. Sidewalk vs trash-tags page: the trash page's "Snow" section must link to the sidewalk page; sidewalk already links back. Cut the dress paragraphs in activities, blues and the pillar's November section to one line plus a link to what-to-wear.

6. Hub wiring: the pillar links only five spokes (storms, biking, utilities, parking, trash) and no spoke links to the pillar. Every spoke's "What to do next" should name the pillar, and each pillar section should link its spoke (snow days, tcat, biking, driving, what-to-wear, activities from the matching sections).

(c) Lease timing: not in this cluster; no year ranges to reconcile here.

Skeptic: The merge holds: same renter, same opening answer, and the overlap is larger than stated (five of heat-req's seven sections repeat heat-out; "Is no heat a repair problem or a legal problem?" restates heat-out's first section). No tool, dataset or site-unique data is lost: the NYSEG 800-572-1111 bill-history tip, the "Report a Concern" form and the Sept. 15 vs Oct. 1 comparison all appear on other housing pages, so section 12 needs no owner sign-off. Corrections: (1) Three of the four stated "adds" are false. heat-req already has the Building Division number (line 99), the withholding warning (line 101) and a steps figure ("Getting heat restored"). heat-out is stronger for 14 sources vs 5, frozen pipes, the 2018 Thurston Ave 53-day case, enforcement detail and the Cayuga Heights and international reader blocks. (2) Wrong keep path: the file is content/articles/housing/ithaca-heat-out-frozen-pipes-landlord-must-do.md, already topic: housing with redirect_from for the getting-around URL (live: getting-around 200, housing 404). Add /cornell/housing/ithaca-rental-heat-requirements-winter/ to that redirect_from list. (3) Also carry over the parent reader block and the Jan. 2024 petition date, and keep "frozen pipes" in the title and meta so the kept page's one unique section keeps its hook.

### Parking (14 pages)

Parking cluster, 14 pages. Format: slug (words) PQ; target query if different; intent; opening answer. URL /cornell/getting-around/<slug>/ unless noted.

- cornell-parking-guide-campus-collegetown-ithaca (pillar, 6248) cornell parking; whole system; "Cornell sells campus spaces; the city runs streets and garages".
- cornell-student-parking-permit-cost-rules (1735) cornell student parking permit cost; cornell parking permit cost; price a permit; "Resident $752.98, commuter $359.77".
- having-a-car-at-cornell-student-guide (3319) Cornell student car parking permit winter; having a car at cornell; car owner's year; "Resident permit $752.98".
- parking-collegetown-downtown-ithaca-garages-permits (A, 1624) parking in collegetown ithaca; parking in collegetown; a spot off campus; "Dryden Road Garage, $2.25 an hour".
- ithaca-parking-garages-dryden-road-green-street-cayuga (B, 933) ithaca parking garages rates; ithaca parking garages; price a garage; "Three garages, all $2.25 an hour".
- ithaca-residential-parking-permit-streets-how-to-apply (1015) ithaca residential parking permit; get the permit; "$45, City Clerk, in person".
- ithaca-winter-parking-rules-cornell-odd-even (1365) ithaca winter parking rules odd even; ithaca odd even parking; avoid a tow; "Odd/even runs Nov. 1 to April 1".
- storing-a-car-ithaca-summer-winter-break-cornell (916) where to leave a car over break at cornell; park for weeks; "Permit area, never a city street".
- ithaca-parking-tickets-fines-how-to-appeal-cornell (923) ithaca parking ticket fine appeal; ithaca parking ticket; contest a ticket; "Cornell $50; city $15 to $200".
- cornell-visitor-parking-for-parents (710) cornell visitor parking; park for a visit; "Weekdays paid, weekends free".
- cornell-move-in-day-parking-unloading (1150) cornell move-in day parking; unload on move-in day; "Unload, then move to the 3-hour lot".
- cornell-motorcycle-scooter-bike-parking (781) cornell motorcycle scooter and bike parking; cornell motorcycle parking; two-wheelers; "M permit $120.01".
- housing/ithaca-apartments-parking-included (902) ithaca apartments with parking included; pick an apartment; "Westview Terrace, 400 Triphammer, Kelvin Place".
- money/should-i-bring-a-car-cornell-ithaca-cost (2453 + 1191 tool) should I bring a car to cornell; decide; "For most students, leave the car at home".

(a) Merges
1. B into A. Both open with the same $2.25 garage table and share four paragraphs (Dryden winter floors, 13-day break-even, Seneca, Cayuga bus stop). A wins: 1624 vs 933 words, 18 vs 13 sources, two embedded tools, 23 in-links vs none, a slug naming downtown and garages. B has no tool or dataset; move its unique facts into A: Premier Parking's long-term referral (607-256-7275), Green Street's $5 event rate, the Seneca redevelopment sentence, the Cascadilla and Sheldon Court move-out block. Retitle A "Parking in Collegetown and downtown Ithaca: garages, streets and permits". 301 B to A.
2. having-a-car into the pillar. Its PQ glues three queries together; Steps 2, 4, 5, 6 and 8 repeat the pillar's August, tickets, winter, breaks and spring sections. Pillar is stronger: 6248 words, 38 sources, feature mode, newer. Move "Out-of-state plates and licenses" to new-york-drivers-license-ithaca-dmv-cornell-students and the Aug. 4, 2026, 9 a.m. sale time into the pillar's August section. No tool or dataset. 301 it and repoint its 25 content in-links; the pillar has none.
3. Not a merge: should-i-bring-a-car keeps its calculator tool and dataset link; its /tools/ twin is Phase 4.

(b) Distinct but confusable
- Residential permit vs A: A's H2 "How do I get the city's $45 residential permit?" repeats the page's steps figure and 1640-e paragraph. Cut it to three sentences, end A's opening with "our residential permit guide shows how to apply", and link (the page has no content in-links).
- Winter rules vs storing-a-car: the winter page's "Where can I leave my car over winter break?" table is storing-a-car's whole answer. Cut it to two sentences and link; open storing-a-car with "Over winter or summer break, leave the car in your campus permit area".
- Tickets vs permit page, pillar and winter page: the Cornell fine table sits on all four. Keep full tables and appeal steps only on the tickets page, retitled "Cornell and Ithaca parking tickets: fines and how to appeal"; the others keep the $50 line and link.
- Visitor, motorcycle and apartments-parking-included are distinct but have no content in-links: link them from the pillar's "Parents and visitors", the M permit rows, and A's renter block; cut apartments-parking-included's "What does parking cost if your building has none?" to a pointer.

(c) Years: not applicable. No parking page or dataset spans years; the one dataset in reach, cost-of-getting-around-cornell-2026-27, covers 2026-27 only, as do every page's prices. The 2012 to 2026 vs 2017 to 2025 question belongs to the lease-timing audit.

Skeptic: Both merges hold. Gaps to close: Merge 1: A's Dryden paragraph gives the merchants' survey no date; carry B's 'October 1998' caveat with it. B calls the long-term operator 'Premier Parking' while A, the pillar and storing-a-car say 'Premium Parking'; settle the name against the city page before moving the (607) 256-7275 referral. Keep B's FAQ line that Dryden and Cayuga post no Sunday rule. Merge 2: the plan is silent on Step 7 (ITH $8 a day or $40 a week, SYR $14 and $22 caps) and 'The year in dollars' (It's My Car $310 plus $6 an hour, 59 to 70 permit-hours, 93-hour crossover). Nothing is lost: cornell-to-ithaca-airport-tcat-taxi-parking and ithaca-carshare-cornell-students-cost hold those figures, and both embedded tools live on nine other pages each. Add the 'transfer or arriving in January' reader block to the pillar's August section; the pillar names no transfer-spring reader. The 25 in-links include three tool.md files, the cost-of-getting-around dataset and three start pages, so the repoint reaches tools/, datasets/ and start/. The NY license page already carries the DMV and insurance sentences, so only the IDP note moves.

### Subletting (12 pages)

Subletting cluster. URLs: /cornell/housing/<slug>/ unless noted; H1 equals title; words per reports/00-baseline.md. Fields: slug; primary_query; searcher's query; intent; words; opening.

1. subletting-in-ithaca-guide-cornell-students; "subletting in ithaca"; same; understand both sides; 5409; no answer; narrative lede (Nora Rabah, 2016).
2. cornell-summer-sublet-how-to-sublet-apartment-ithaca; "how to sublet my apartment for the summer Ithaca Cornell"; how to sublet my apartment ithaca; tenant: get consent; 1830; "You need your landlord's written consent to sublet."
3. summer-sublet-ithaca-finding-housing-may-august; "summer sublet Ithaca Cornell internship research"; summer sublet ithaca; subtenant: find a place; 1501; "take a furnished sublet found on Cornell's marketplace".
4. sublet-apartment-study-abroad-semester-cornell; "sublet apartment study abroad semester Cornell"; sublet while abroad; tenant: get consent; 1278; "only with your landlord's written consent".
5. can-landlord-refuse-sublet-new-york-ithaca; "can a landlord refuse a sublet in New York"; same; right and remedy; 1152; "cannot refuse a sublet without a reasonable cause".
6. where-to-list-sublet-ithaca-cornell; "where to post a sublet Ithaca Cornell"; where to post a sublet ithaca; pick channels; 935; "Post your sublet on Cornell's Off-Campus Housing Marketplace".
7. sublet-scams-ithaca-how-to-avoid; "sublet scams Ithaca Cornell"; sublet scams ithaca; avoid both scams; 1034; "Do not send money for a sublet until you have seen the unit".
8. sublet-agreement-what-to-put-in-writing-ithaca; "what to include in a sublet agreement New York"; same; write the sublease; 923; "name both people, give the exact start and end dates".
9. take-over-collegetown-lease-assignment; "how to take over a collegetown lease"; take over a lease collegetown; taker: assignment vs sublease; 1330; "get the landlord's written consent before you pay".
10. /tools/ithaca-sublet-request-timeline/; none; sublet request 30 days; the consent dates; 1434; "works out the dates in a New York sublet request".

Adjacent, no merge: cornell-summer-housing-options-rates-dates, ithaca-12-month-lease-real-cost-9-month-student, leaving-things-in-apartment-over-summer-ithaca-lease, breaking-a-lease-early-ithaca-cornell, roommate-leaves-joint-lease-who-pays-ithaca-cornell. summer-storage-vs-shipping-vs-sublet-cornell-cost duplicates its /tools/ twin: Phase 4's call; its storage-vendor data is unique, so ask the owner first.

(a) Same intent. Merge sublet-apartment-study-abroad-semester-cornell into cornell-summer-sublet-how-to-sublet-apartment-ithaca and 301 it. Both tell the tenant how to sublet out; the abroad page's consent, subtenant-search and sublease sections repeat the how-to, which already has an "If you're going abroad or away for a semester" block. The how-to wins on words (1830 vs 1278), sources (16 vs 10), inbound links (27 vs 0) and the embedded tool. Move the Education Abroad decision dates (Jan. 29, July 13) into that block; no tool, dataset or unique data is lost. No other pair shares a query.

(b) Distinct but confusable.
- how-to vs may-august: both say "summer sublet" in slug and title but face opposite sides; the how-to's glance and opening never say summer. Retitle the how-to "How to sublet your Ithaca apartment: landlord consent, step by step", opening "To sublet out your Ithaca room for a summer, a semester abroad or a co-op, you need your landlord's written consent." Retitle may-august "Finding a summer sublet in Ithaca: May to August housing for Cornell students and interns", opening "If you need a place in Ithaca from May to August, take a furnished sublet". Point each opening at the other.
- The pillar is isolated: it links to two spokes, one page links to it, and five spokes (study-abroad, where-to-list, scams, agreement, take-over) have no inbound links. Add a Related guides block on the pillar naming every spoke and the tool, a "full guide" link in each spoke's opening, and a scam-section link to the scams page.
- may-august omits Cornell's summer rooms (June 1 to Aug. 11, $58.50 a night); add a row linking cornell-summer-housing-options-rates-dates, which already links back.

(c) Lease-timing year ranges. They measure different things. 2017 to 2025 spans the nine dated signings (the CSV rows). 2012 to 2026 spans how-early's context timeline (2012 and 2014 camp-outs, 2013 and 2022 notice laws, the Nov. 8, 2026 sold-out count), which the dataset keeps in a separate table lacking 2012 and 2014. Reconcile: (1) say "nine dated signings, 2017 to 2025" wherever a count appears (how-early's title and meta say 2012 to 2026, its dek 2017 to 2025); (2) keep the slug, retitle "How early do Collegetown leases sign? Nine signings, 2017 to 2025, and the rush since 2012"; (3) add 2012 and 2014 rows to the dataset's context table and the 2012 Sun story to how-early's sources list, which omits it; (4) when-to-sign's table shows six of the nine cases it cites; show all nine.

Skeptic: No merge rejected. Merge 1 holds: the abroad page's Education Abroad dates, the 2016 Sun story, the Ithaca Renting rules and the $15/$20 fee all survive in subletting-in-ithaca-guide-cornell-students, and 27 vs 0 inbound links is confirmed. Two fixes: "the sublet-request tool embedded" is not a differentiator, since the abroad page embeds ithaca-sublet-request-timeline too; and the how-to's sentence "No Ithaca landlord publishes a standard sublet fee or a typical summer sublet rent" contradicts the abroad page's Ithaca Renting $15/$20 fee, so carry that fee and Ithaca Renting's sublet rules into the how-to during the merge. Merge 2 holds under Phase 4, but the vendor data is not unique: cornell-move-out-storage-shipping-options already compares BRSS, Storage Squad, Storage Scholars, Uncle Marty's and Bolt at the same prices, including the six-boxes-plus-fridge $369 vs $315 case. Unique to the article: the Bolt $252 and Uncle Marty's $365 totals, the rent-plus-sublet-plus-storage table ($1,058.75 to $3,738.75), the $184.50 shipping break-even and the only link to the pillar. Do not send that content to ithaca-12-month-lease-real-cost-9-month-student: it embeds no storage tool, so the spec's rule points to the tool page itself, which today has zero inbound links.

### Lease timing (6 pages)

PAGES (Phase 0 counts)
1. how-early-collegetown-leases-sign-2012-2026, /cornell/housing/how-early-collegetown-leases-sign-2012-2026/. primary_query "how early do collegetown leases sign"; searcher: "how early do Collegetown leases get signed"; intent: learn the lead time. 1,202 words, 12 sources, 2026-11-10, 3 in-links. Opens: "Collegetown leases sign 10 to 11 months before an August move-in in five of the nine dated cases below, which puts the rush in September and October of the year before."
2. when-to-sign-collegetown-lease-cornell, /cornell/housing/when-to-sign-collegetown-lease-cornell/. primary_query "when to sign a collegetown lease for 2027-28"; searcher: "when should I sign a Collegetown lease"; intent: decide when to sign, or wait. 1,717 words, 19 sources, 2026-11-10, 38 in-links. Opens: "If you want a popular Collegetown unit for 2027-28, sign in the fall of 2026, about 10 to 11 months before an August move-in."
3. when-to-sign-lease-timeline-cornell, /tools/when-to-sign-lease-timeline-cornell/. No primary_query; searcher: "when can I sign a lease at Cornell"; intent: get your dated steps. 1,959 words, 24 sources, 2026-11-08. Opens: "This tool tells you which August your first off-campus lease can start, and when to look and sign for it."
4. collegetown-lease-signing-lead-times-2017-2025, /datasets/collegetown-lease-signing-lead-times-2017-2025/ (+ 9-row CSV). No primary_query; searcher: same as page 1; intent: the record itself. 1,929 words, 12 sources, 2026-11-08. Opens: "Collegetown leases in the Cornell Daily Sun's record are signed 8 to 16 months before an August move-in, mostly 10 to 11 months ahead."
Distinct neighbors: off-campus-housing-cornell-sophomores (2,824 words) and collegetown-lease-dates-august-to-august (1,099).

(a) SAME QUERY
Pages 1 and 4: page 1's primary_query is page 4's H1, and both print the same nine-row table and context; page 2 prints a six-row cut (text says nine; cases 3, 7, 8 missing). Decision: 301 page 1 to page 2, the stronger page (19 sources, seven reader blocks, 38 in-links against 3, the better URL and title). Page 4 stays: it holds the data (CSV, method, qualifiers, change log). Page 1 holds unique facts: eight landlords owning 4,013 of 6,110 bedrooms (2013), the 2012 and 2014 camp-outs, 2016's nearly 200 new bedrooms, the 2012-to-2026 timeline figure. So the owner must approve; those facts move first into page 2's "Is the rush really that early" section and page 4's context table. Then cut page 2's table to three lines plus a link to page 4, which it lacks today.

(b) DISTINCT BUT CONFUSABLE
Tool vs page 2: "When to sign a lease at Cornell: timeline by start term" and "When to sign a Collegetown lease for 2027-28" read as one page. Tool title and H1: "Cornell lease timeline tool: your dates to look, sign and drop a backup room". Opening: "Enter your year, term, transfer, exemption and market to get the August your first lease can start and the dated steps up to it." Link page 4 from its lead-time row (it links only /datasets/).
Dataset vs page 2: H1 "Dataset: Collegetown lease signing lead times, 2017 to 2025 (9 cases)"; add "This is the record behind the when-to-sign guide, which turns it into a decision." The live dataset page links to no cluster page (the build drops its Related guides); link page 2 and the tool in the body.
Sophomore guide: its opening restates page 2. Keep the H1, open with the year plan (group, neighborhood, fall or spring signing, Jan. 31 cutoff), link page 2 (live, only the tool is linked), delete its duplicate title key.
Pillar lines 433 and 721 name page 2 without a link; link both. The lease-dates page already links page 2.

(c) YEAR RANGES
Every page dates the signings 2017 to 2025 except page 1's slug, title and H1 (2012 to 2026), the context span from the 2012 camp-out to the Nov. 8, 2026 count; page 1's own dek says 2017 to 2025. Reconcile: 2017 to 2025 is the record and the only range for a title; the 2012 to 2026 events stay as dated context rows, which page 4 already holds. The merge removes the conflicting slug; if page 1 survives, drop its years. Also: page 1's glance and dek say nine signings fall 8 to 16 months, but its table has one at most 6; and a 2027-28 row, which page 4's change log promises, would outdate its slug, so date the record in the citation line.

Skeptic: Merge 1 (how-early into when-to-sign) holds: same lead-time query (page 2's first H2 answers it with the same table), readers a subset, no tool lost (both embed the timeline tool), the dataset keeps the nine rows and context table, and the crawl confirms 38 in-links vs 3, page 1's three being the housing hub, the author page and the tool's auto-generated 'Guides that use this tool' list. Refinements: (1) review/ideas-plan.json records idea 141 as 'history page, not a duplicate of the 2027-28 decision page'; the page as written refutes that (primary_query, glance and opening lead with the lead time; the first section reprints the dataset), so the owner's approval should name that reversal. (2) The move list misses one unique fact: the timeline row 'Student Agencies among first to open for 2023-24, early September 2022' (facts.csv 4.1-0441, Sun 2022-09-12), on no other page; and the 2012 camp-out's source (Sun 2012-10-01) is cited in page 1's body but absent from its frontmatter, so add it to when-to-sign's sources. (3) The 2013 landlord concentration and 2016 nearly-200-bedrooms figure already live on collegetown-landlords-who-owns-the-buildings and new-construction-collegetown-buildings-since-2015; a link can replace a copy.

### Co-ops and Greek housing (15 pages)

# Phase 5: Co-ops and Greek housing

URLs: /cornell/housing/<slug>/. Words/sources: reports/00-baseline.md. Title = H1.

| Slug | primary_query | Searcher says | Intent | Words/sources | Opens with |
|---|---|---|---|---|---|
| cornell-co-ops-all-eight-compared | cornell co-ops | same | compare the eight | 5435/33 | "To win a room at Triphammer Cooperative, you first cook dinner for strangers" |
| how-cornell-co-ops-work-chores-meals-governance | how do cornell co-ops work | same | chores, meals, governance | 1037/14 | "small houses where residents run the household themselves" |
| cornell-co-op-vs-dorm-cost-lifestyle | cornell co-op vs dorm | same | choose one | 1104/10 | "A co-op double costs $3,782 to $6,770 a year less than a hall double" |
| cornell-co-ops-greek-houses-cost-how-to-join | how to get into a cornell co-op or greek house | "co-op or frat house instead of a dorm" | dorm alternative for sophomores | 1717/20 | "Co-ops pick members through a house-by-house selection called the mosey" |
| cornell-fraternity-sorority-housing-2026-27 | cornell fraternity and sorority housing | "cornell fraternity housing" | eligibility, chapter rents | 5303/31 | "Cornell President Michael I. Kotlikoff canceled every party and social event" |
| cornell-fraternity-house-cost-live-in-rules | cornell fraternity house cost live in requirement | "how much does a frat house cost at cornell" | cost, live-in rule | 1350/11 | "charges what its members vote and its owner sets" |
| cornell-fraternity-suspension-2026-housing-2027-28 | cornell fraternity suspension 2026 housing | "does the frat suspension affect housing" | will a 2027-28 plan hold | 1272/13 | "stops parties and social events but not housing" |
| 302-wait-avenue-cooperative-cornell 629/5, 660-stewart-avenue-cooperative-cornell 701/6, prospect-of-whitby-cooperative-cornell 634/5, redbud-cooperative-von-cramm-hall-cornell 717/7, triphammer-cooperative-cornell 751/7, wari-cooperative-cornell 674/8, watermargin-cooperative-cornell 728/6 (Wait Terrace has no page) | "<House> co-op Cornell" | house name | one house | listed | "<House> is a Cornell-owned co-op at <address> with N residents", cost_table each |

## (a) Merge

1. how-cornell-co-ops-work-chores-meals-governance into cornell-co-ops-all-eight-compared, 301. The pillar wins on depth (its "How a co-op works", "Getting in: the mosey" and "What a co-op really costs" sections already hold the explainer's facts, down to Julie Paige, co-ops@cornell.edu and the rate standardization), sources (33 to 14) and title. Its cost_table duplicates the pillar's and its calculator embed lives at /tools/; nothing unique is lost.

2. cornell-fraternity-house-cost-live-in-rules into cornell-fraternity-sorority-housing-2026-27, 301. Same scorecard, same question; the pillar has the 41-row chapter table, the $7,400 median, the $1,152 and $602 parlor fees and 31 sources to 11. Move its "Who owns the houses?" paragraph first; its one figure is a four-row summary; no tool or dataset.

Not merged: cornell-co-ops-greek-houses-cost-how-to-join. Seven pages link to it, it links to none, and its three figures restate the pillars' mosey steps, cost table and timelines.

## (b) Distinct, easily confused

Greek pillar vs suspension page: both open on the Oct. 13 party ban; neither links to the other. Pillar: keep the title; open with "A recognized chapter house counts as sophomore housing if you affirm it by March 15, 2027; chapters set the rent, $2,000 to $14,673 a semester on Cornell's scorecard", and move the Oct. 13 lede into "The Chi Phi case and the 2026-27 review", linking the suspension page. Suspension page: title and H1 "Does Cornell's 2026 fraternity suspension change 2027-28 housing?"; link the pillar and ithaca-2026-moratorium-student-event-permits.

Join page: title and H1 "Cornell co-op or Greek house instead of a dorm: how a sophomore gets in"; opening "Sophomores can meet the residential requirement in a co-op or a recognized chapter house: win a mosey room in November or February, or belong to the chapter, then confirm it on the housing application by March 15." Replace "What does each option cost?" and its cost figure with links to cornell-co-op-vs-dorm-cost-lifestyle and the Greek pillar; link both pillars and the house pages. co-op-vs-dorm and the pillar's "The trade-offs" should link each other.

The co-op pillar links to none of the seven house pages: link each row of "The eight houses side by side" to its page, and write "Redbud (Von Cramm Hall)" everywhere (the join page says "Von Cramm").

(c) Not applicable: no lease-timing page here.

The dataset (4352/8) holds co-op rows 2 and 3 only; its note that Greek prices "are not published" contradicts the scorecard pages (owner's call to add rows).

Skeptic: Both merges hold. Merge 1: nothing to reject. The only explainer fact the pillar lacks is that Triphammer cook groups have three or four members; no content page links to the explainer. Merge 2 needs three fixes to its instructions. (1) Do not move 'Who owns the houses?': the pillar already has the 15 privately owned and Chi Phi university-owned labels in 'How Cornell's chapter houses got here', the 12 MGFC chapters at 136 Ho Plaza in the table's source note and the $500 Certificate of Compliance in 'Who inspects the house'; moving it repeats the facts. (2) Reconcile the SFL Supplemental price before the 301: the cost page says $2,088.77 a semester (Cornell's bear-supplemental page), the pillar $2,167.51 (undergraduate-meal-plans page); both corpus copies are dated 2026-11-06 and intel/money/raw/market-part12.md could not tell which is current. (3) Carry over what the pillar lacks: the annualized $14,800 vs $20,800 comparison, the Sept. 30, 2026 fall switch deadline and the renters-insurance link. The chapter table has 39 rows, not 41. The Zeta Psi photo is the same file and credit the pillar already runs, and no content page links to the cost page, so the 301 drops nothing else.

## Distinctions applied

- Edited: ithaca-winter-survival-guide-cornell.md. Pillar, November section (report b5): cut the dress paragraph to one line plus a link. The line keeps Cornell Health's advice (warm, loose layers, a water-resistant jacket and boots, covered hands and ears) with its existing citation. The link goes to /cornell/daily-life/what-to-wear-ithaca-winter-c
- Edited: ithaca-parking-tickets-fines-how-to-appeal-cornell.md, storing-a-car-ithaca-summer-winter-break-cornell.md, parking-collegetown-downtown-ithaca-garages-permits.md, cornell-parking-guide-campus-collegetown-ithaca.md, ithaca-apartments-parking-included.md. Tickets page (ithaca-parking-tickets-fines-how-to-appeal-cornell.md): retitled to the report's 'Cornell and Ithaca parking tickets: fines and how to appeal' (59 characters). The body has no H1. primary_query changed from 'ithaca parking ticket fine appeal' to the report's target 'ithaca parking tick
- Edited: subletting-in-ithaca-guide-cornell-students.md, cornell-summer-sublet-how-to-sublet-apartment-ithaca.md, summer-sublet-ithaca-finding-housing-may-august.md, can-landlord-refuse-sublet-new-york-ithaca.md, where-to-list-sublet-ithaca-cornell.md, sublet-scams-ithaca-how-to-avoid.md, sublet-agreement-what-to-put-in-writing-ithaca.md, take-over-collegetown-lease-assignment.md. subletting-in-ithaca-guide-cornell-students.md (pillar), report (b) 'Related guides block': I added a section at line 424, before '## Sources', headed '## Related sublet guides'. It lists every remaining spoke: the how-to, may-august, can-landlord-refuse, where-to-list, scams, agreement and take-ove
- Edited: tool.md, collegetown-lease-signing-lead-times-2017-2025.md. tool.md, frontmatter title (line 2): changed from 'When to sign a lease at Cornell: timeline by start term' to the report's exact title, 'Cornell lease timeline tool: your dates to look, sign and drop a backup room'. ToolLayout renders this as the H1. The body has no H1 of its own. The same title be
- Edited: cornell-co-ops-greek-houses-cost-how-to-join.md, cornell-fraternity-suspension-2026-housing-2027-28.md, cornell-co-ops-all-eight-compared.md, cornell-co-op-vs-dorm-cost-lifestyle.md. Join page, title: now 'Cornell co-op or Greek house instead of a dorm: how to join' (59 characters). The report's title ends 'how a sophomore gets in' and runs 71 characters, past the 60-character cap in page_check.py and docs/v2/style.md. Its first clause is kept word for word.

## Deferred to after Phase 2 (pages that were being reworked at the time)

- 1) Some Winter-cluster changes from the report fall on files listed in reports/02-pages.json, so they still need to be made once the other process releases those files:
- blues: new title, H1, primary_query and opening.
- storms: new primary_query and opening.
- driving: new title, H1 and opening; parking section cut to two lines.
- storms and driving: link to each other.
- heat-out: add the 'above the minimums' line with a link to drafty.
- trash: link the sidewalk page from its Snow section.
- activities and blues: trim the dress paragraphs to one line plus a what-to-wear link.
- duplicate sections to cut: the driving and storms parking material, the fitness pass prices on activities and blues, and the monthly snow table on what-to-wear and driving.
- 'What to do next' should name the pillar (/cornell/daily-life/ithaca-winter-survival-guide-cornell/) on what-to-wear, activities, blues, driving, storms, tcat, biking, drafty, heat-out, parking and trash.
- tcat links to snow days through the old-style URL /daily-life/cornell-snow-days-class-cancellation-how-it-works/. That URL maps through the link map; the link rewrite should handle it.

2) The editable spokes contain gap or narra
- 1) Report changes I could not make because the files are in reports/02-pages.json:
- Winter page (ithaca-winter-parking-rules-cornell-odd-even.md): cut 'Where can I leave my car over winter break?' to two sentences and link storing-a-car. Cut its Cornell fine table to the $50 line and link /cornell/getting-around/ithaca-parking-tickets-fines-how-to-appeal-cornell/. Change primary_query to 'ithaca odd even parking'.
- Permit page (cornell-student-parking-permit-cost-rules.md): cut its Cornell fine table to the $50 line and link the tickets guide. Link the motorcycle page from its M permit row if it has one. Change primary_query to 'cornell parking permit cost'.
- Motorcycle page: change primary_query to 'cornell motorcycle parking'.
- Until the winter page links it, storing-a-car still has no content in-links.

2) Another process edited parking-collegetown-downtown-ithaca-garages-permits.md while I worked (about 17:53 to 17:59; it also ran scripts/v2/lint.py with network on that file). None of these changes are mine:
- swapped the scl.cornell.edu move-out source URL;
- added the 2026 Final Budget Proposal source and link;
- linked 'Dryden Road Garage';
- added that Green Street cars
- 1) Site-level, for the owner: the Astro build (site/src/lib/markdown.ts renderArticle) pulls any body section titled exactly 'Related guides' out of the page, and no layout renders body.related. About 80 articles end with a '## Related guides' list that never appears on the live site. In its place, the auto RelatedGrid shows the longest same-topic pages. That is why the pillar's new block is headed 'Related sublet guides'. Rename it to 'Related guides' only after the build renders that section.
2) The changed primary queries should go into the Phase 5 query map (reports/05-clusters.md): the how-to is now 'how to sublet my apartment ithaca' and may-august is 'summer sublet ithaca'.
3) Edits beyond the report's list, each made to meet the hard rule against research-gap sentences or to keep a page consistent, so the orchestrator can revert any of them:
- the pillar's line 311 clause
- may-august's glance bullet 3 and line 145
- can-landlord-refuse's 'The page does not answer that'
- may-august's dek, from three routes to four
- the how-to's meta, trimmed from 156 to 154 characters
- two anchor texts, changed from 'summer housing guide' to sublet wording.
4) can-landlord-refuse-sublet-
- 1) Title length: both new titles are the report's exact text, but they exceed the 60-character house limit that .claude/skills/page-checks/scripts/page_check.py flags (tool 76, dataset 69). No required lint checks tool or dataset titles, and the repo already has 61 to 67 character tool titles. If the owner wants 60 or fewer: 'Cornell lease timeline tool: look, sign, drop a backup room' (59) and 'Dataset: Collegetown lease signing lead times, 2017 to 2025' (59; the byline already shows 'Sample: 9'). 2) Still to apply by whoever owns those files after Phase 2: the sophomore guide items (year-plan opening, link to /cornell/housing/when-to-sign-collegetown-lease-cornell/, the duplicate title key; its frontmatter now shows one title key) and the pillar's two links (cornell-off-campus-housing-guide.md lines 433 and 721). 3) Page 2 now has a figure titled 'The Collegetown rush, 2012 to 2026' (carried from page 1). Reconciliation (c) says 2017 to 2025 is the only range for a title. This is a timeline of dated context events, so it is probably fine, but the merge verifier should confirm. 4) The dataset's context table runs from 2013 to 2026-11-08. The 2012 and 2014 camp-outs and the Student
- 1) Greek pillar, once the other process finishes with it: the sentence 'Our [comparison of co-ops, Greek houses and dorms](/cornell/housing/cornell-co-ops-greek-houses-cost-how-to-join/) prices them side by side.' (originally line 241, in 'Year two') is now wrong, because the join page no longer prices anything. It needs a one-line rewrite, for example 'Our guide to [a co-op or Greek house instead of a dorm](...) shows how a sophomore gets into each.' The pillar also keeps the sentence 'Cornell's pages do not say what happens to a sophomore living in a chapter house if the chapter loses recognition mid-year.', which the linter does not catch but which breaks the no-gap rule.
2) About 20 inbound links elsewhere still describe the join page as covering costs. They need new link text in the link-rewrite step. Examples: content/start/affiliated-housing.md ('what each co-op charges'), start/first-year.md, start/low-budget.md, the tool.md pages for the cancellation-fee calculator, the can-i-live-off-campus quiz and the lease timeline, the dataset .md, and several housing articles whose link text says 'cost and how to join' (for example cornell-housing-costs-by-room-type, when-to-apply-fo

## Checks

- scripts/prelaunch/merge_pages.py: 7 pages removed with their check, review and edit sidecars; redirect_from on each keeper (both old URL forms, and the Phase 3 URLs where the merged page had moved); 25 files re-pointed; 7 queue rows read rejected with a note.
- The build's check (scripts/check-build.mjs) passes for every link and redirect; its only failures at the time of writing were the transfer hub not yet listing the transfer tools and datasets the Phase 7 run was still writing.
