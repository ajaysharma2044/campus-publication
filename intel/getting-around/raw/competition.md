# Getting to Ithaca and getting around it: the competition (Lane D)

Checked 2026-11-08. Raw notes, appended in parts. Today = 2026-11-08.

## Method and caveats (read first)
- Demand rows come from `intel/getting-around/raw/demand-questions.md` (25 rows, q-getting-around-0001 to 0025). Questions 26-30 are my own additions (marked NEW).
- "Top 5" = the first five distinct results the web-search tool returned for the primary query on 2026-11-08. Order is the tool's, not a rank-tracker's. The demand file's own top-5 list is cited where it differs.
- Where I opened a page, the line says READ. Where I only have the search tool's summary of a page, the line says SNIPPET (page not opened); treat the detail as unverified.
- "Typical AI answer" blocks are NOT from a source. They are my own reconstruction of what a general-knowledge LLM would say today, written to show what it would likely get wrong or omit for Cornell and Ithaca. Marked **[LLM-GUESS]**.
- Official facts used to judge competitors come from `intel/getting-around/raw/official.md` (Lane A, checked 2026-11-07) and are cited by URL there. I do not re-verify them here unless stated.
- Rome2Rio, Busbud, CheckMyBus, Expedia and similar aggregator pages are scored as one family: auto-generated, undated, prices are ranges, no Cornell stops.

## Cross-cutting findings so far (details per question below)
| Finding | Evidence | Source URL | Applies to | Checked |
|---|---|---|---|---|
| The Cornell news page that ranks #2 for "NYC to Cornell by bus" is a Jan 4, 2011 Cornell Chronicle item quoting a $75 each-way fare. Official C2C rates page now says $101 non-Cornell / $93.50 student with NetID (Lane A). A reader who clicks the ranking result gets a fare about 26% low and a 2011 schedule. | READ | https://news.cornell.edu/node/269896 (2011); current fares: https://fcs.cornell.edu/departments/transportation-delivery-services/campus-campus-bus-service/c2c-rates | 2011 vs 2026 | 2026-11-08 |
| Cornell Sun, Sept 2, 2026: OurBus now runs 4-6 buses a day, 7 days a week, Ithaca (Commons, West Campus, North Campus) to Manhattan; before that most Cornell stops were break-only. Article gives no fares or times. Most other pages (aggregators, 2025 Sun guide) predate this. | READ | https://www.cornellsun.com/article/2026/09/8kl4l6fodjwk | Sept 2026 | 2026-11-08 |
| Same Sun article: weekend routes add Fresh Meadows (Queens), Melville (Long Island), Cortland, Binghamton, Middletown, Nanuet from "Thursday" (Sept 3, 2026 by inference); Cornell-Syracuse six days a week incl. SYR airport and Destiny USA. Company cites ~20% ridership rise in spring 2026 and links it to fuel prices and the 2025 end of ITH direct flights to Newark (as the article states it; I did not verify the flight claim independently). | READ | same | Sept 2026 | 2026-11-08 |
| Cornell Sun May 4, 2025 guide by Melanie Delfosse: lists C2C, FlixBus, OurBus, Megabus; no fares; TCAT 32 times contradict within the article (text "7:30 a.m.-6:40 p.m."; table 7:34 a.m.-7:31 p.m. arrivals); says Sat/Sun drop-off only on route 32 (as the article's table shows); mentions a Student Assembly shuttle to SYR. | READ | https://www.cornellsun.com/article/2025/05/busses-trains-and-planes-getting-to-and-from-cornell | May 2025 | 2026-11-08 |
| ITH airport service is contested across pages: flyithaca.com/airlines (Lane A) lists Delta to JFK and United to Dulles; Cornell Sun (via OurBus article) says the direct Newark flight ended in 2025; a search summary says United nonstop was last on the schedule in June 2026. Needs a live check before any article says which nonstops exist. | READ + SNIPPET | https://flyithaca.com/airlines ; https://www.cornellsun.com/article/2026/09/8kl4l6fodjwk | 2025-2026 | 2026-11-08 |

---

# PART 1: QUESTIONS (demand rows 0001 to 0014)

## Q1 (q-getting-around-0001) What is the best way to get from NYC to Cornell by bus?
Primary query: "how to get from NYC to Cornell Ithaca bus". Demand verdict: weak. Official options: C2C (Cornell-run), OurBus, FlixBus, Shortline/Coach USA, Greyhound.

| # | URL | Title | Publisher | Date | What it says (2 lines) | What it gets wrong or leaves out |
|---|---|---|---|---|---|---|
| 1 | https://www.cornellsun.com/article/2026/09/8kl4l6fodjwk | OurBus Increases Rides from Cornell to New York City | Cornell Daily Sun (Coral Platt, Giselle Redmond) | 2026-09-02 | READ. OurBus now 4-6 buses/day, 7 days; stops Ithaca Commons, West Campus, North Campus; weekend stops added in Queens, Long Island, Cortland, Binghamton, Middletown, Nanuet. Ridership up ~20% (company figure). | No fares, no times, no NYC-side stop addresses, no return schedule, no mention of C2C or FlixBus. News story, not a how-to. |
| 2 | https://news.cornell.edu/node/269896 | Campus-to-Campus bus expands New York City service | Cornell Chronicle | 2011-01-04 | READ. Six more weekly round trips from Jan 13 (2011); fares unchanged at $75 each way; sample weekday/weekend pattern; points to c2cbus.com. | 15 years old. $75 vs current $101/$93.50/$86 (Lane A). No stops named. Page does not say it is from 2011 in the search snippet, so a reader may think it is current. Also does not say the bus is open to the public (current official page does). |
| 3 | https://www.rome2rio.com/s/Grand-Central-Terminal/Cornell-University | 8 ways to get from Grand Central Terminal to Cornell University | Rome2Rio | none | SNIPPET. Aggregator list of routes by bus, car, train, plane with ranges. | Auto-generated; no C2C booking rules, no Cornell stop names (West Campus vs North Campus), no fare certainty, no break-week sell-out warning. |
| 4 | https://hr.cornell.edu/perks/campus-campus-bus | Campus-to-Campus Bus | Cornell HR | none | SNIPPET. Employee perk page; C2C discounts for staff. | Written for employees; no student-specific info; no comparison with OurBus/Flix. |
| 5 | https://fcs.cornell.edu/departments/transportation-delivery-services/campus-campus-bus-service (demand file's #5, truncated) / https://fcs.cornell.edu/departments/transportation-delivery-services/campus-campus-bus-service/c2c-departure-schedule (appeared in my search) | C2C service / departure schedule | Cornell Food and Campus Services | none | Official. Stops, times, fares (Lane A has details). | Does not compare against OurBus/FlixBus on price or reliability; does not say which is better for a given student. |

Also seen in my search: OurBus "Quick Guide to Ithaca" https://www.ourbus.com/routes/ny-wc (READ: the URL actually serves a New York to Washington page, no Ithaca info; a stale or wrong landing page). FlixBus stop page for Cornell West Campus, 240 West Ave: https://www.flixbus.com/bus/ithaca-ny/cornell-university-west-campus (SNIPPET). Cornell news "Express service with luxury touches: Campus-to-campus bus hits its stride" https://news.cornell.edu/node/282639 (title only, date not checked).

Contradictions inside the results: OurBus NYC pick-up listed as 625 8th Avenue in one search summary; Ithaca drop-off listed as 131 Green Street in one place and "Downtown Ithaca - E. Seneca Street" in another (SNIPPET, both OurBus-family pages). Not resolved.

**[LLM-GUESS] Typical AI answer (not a source):** "The best bus is FlixBus, OurBus or Shortline/Coach USA from Port Authority to Ithaca, about 4-5 hours, around $30-60. Cornell also runs a Campus-to-Campus bus for the Cornell community. Book ahead for breaks."
What it misses or risks: calls C2C "Cornell community only" (the official page says open to the public, Lane A); gives $30-60, missing that C2C is $86-$101 each way and has a $6 fuel/toll surcharge folded in; may name Port Authority as the C2C stop (C2C stops are Weill Medical, 1300 York Ave, and Cornell Club, 6 E 44th St); misses the Nov 4, 2026 new reservation system and mandatory new accounts; misses that OurBus now runs daily with West Campus/North Campus stops (Sept 2026); misses the Cornell-specific stops (West Campus on West Ave, North Campus on Jessup Rd); may say Shortline has Cornell stops it no longer does (not verified).

## Q2 (q-getting-around-0002) Is it worth flying into Ithaca (ITH) or should I fly into Syracuse?
Primary query: "Ithaca airport ITH flights worth it vs Syracuse". Verdict weak.

| # | URL | Title | Publisher | Date | What it says | What it gets wrong or leaves out |
|---|---|---|---|---|---|---|
| 1 | https://roame.travel/flightmap/flights-from-ith | flights from ITH | Roame | none | SNIPPET. Route map of nonstops from ITH. | Not an answer to "worth it"; no price comparison; no ground-cost add-on; undated. |
| 2 | https://fr.flightaware.com/live/airport/KITH | KITH live airport | FlightAware (French UI) | live | SNIPPET. Live arrivals/departures. | Snapshot only. |
| 3 | https://www.airportoverview.com/routes/ITH/SYR | Ithaca to Syracuse (ITH-SYR) | AirportOverview | none | SNIPPET. Treats ITH-SYR as an airline route. | Misleading for this question: nobody flies ITH to SYR as a student; a search summary notes Skyscanner says no flights ITH-SYR as of April 2026, which conflicts. |
| 4 | https://www.flightconnections.com:443/flights-from-ithaca-ith | Non-stop flights from Ithaca | FlightConnections | none | SNIPPET. Lists nonstop destinations. | Listing quality unknown; current schedules need check. |
| 5 | https://www.airportoverview.com/routes/SYR/ITH | Syracuse to Ithaca | AirportOverview | none | SNIPPET. Same family. | Same. |

Seen but not top 5: FlyerTalk "Getting to Ithaca" post https://www.flyertalk.com/forum/27495864-post13.html; Cornell Sun, "Ithaca airport adds Newark flights, loses Washington Dulles service" https://www.cornellsun.com/article/2022/03/ithaca-airport-adds-newark-flights-loses-washington-dulles-service (Mar 2022; stale: official airline page now says JFK and Dulles, and the Sept 2026 Sun piece says the direct Newark flight ended in 2025).
Student anecdote from a search summary (source not identified in the snippet; treat as anonymous): ITH winter-break flight about $600 vs about $300 from SYR; SYR is "just over an hour" from Cornell with nonstops to 23 cities (SYR's own page says 27 destinations per Lane A, so numbers differ by source).

**[LLM-GUESS] Typical AI answer:** "ITH is tiny and convenient (about 10 minutes from campus) but has few flights and higher fares. Syracuse (about an hour) has more nonstops and usually cheaper fares. If you can find a good ITH fare to a hub, take it; otherwise fly into SYR."
What it misses or risks: no current list of ITH nonstops (airline pages and news disagree, see cross-cutting table); no ground cost for SYR (OurBus SYR-Ithaca roughly $9-49 per search summary; taxi about $200 per one transfer site; cannot be stated without live check); no mention that Cornell's own travel page lists six airports (Ithaca, Syracuse, Elmira-Corning, Binghamton, Rochester, Buffalo); no mention of the break-time shuttles Cornell has run to ITH (2023 Thanksgiving); weather diversion/cancellation risk of small ITH aircraft not quantified anywhere.

## Q3 (q-getting-around-0003) How do I get from Cornell to Boston without a car?
Primary query: "Cornell to Boston bus or train". Verdict weak.

| # | URL | Title | Publisher | Date | What it says | What it gets wrong or leaves out |
|---|---|---|---|---|---|---|
| 1 | https://www.rome2rio.com/s/Cornell/Boston | 8 ways to get from Cornell to Boston | Rome2Rio | none | SNIPPET (via summary). FlixBus about 6h18m, roughly $70-375; OurBus about 8h32m roughly $20-95; Amtrak Lake Shore Limited via Syracuse/Utica about 8h50m once daily roughly $45-300; drive about 330 miles, 6h11m. | Rome2Rio may treat "Cornell" as a place that is not the campus (search also returned Cornell, Wisconsin). No Cornell stop names. Transfers not shown. |
| 2 | https://www.rome2rio.com/s/Boston/Cornell | Boston to Cornell | Rome2Rio | none | SNIPPET. Mirror. | Same. |
| 3 | https://static.r2r.io/s/Boston/Cornell-University | Boston to Cornell University | Rome2Rio static mirror | none | SNIPPET. Mirror with FlixBus. | Duplicate content. |
| 4 | https://www.fodors.com/community/united-states/northeast-college-visit-386837-printthread/ | Northeast college visit (forum thread) | Fodor's Travel Talk | thread date not checked | SNIPPET only. Parent-planning thread. | Forum; old; not specific to a student living in Ithaca. |
| 5 | https://www.cornellsun.com/article/2025/05/busses-trains-and-planes-getting-to-and-from-cornell | Busses, Trains and Planes | Cornell Daily Sun | 2025-05-04 | READ. Lists buses and Amtrak; says the Amtrak red-eye NYC route took the author about 22 hours; no Boston-specific content. | No Boston route, no fares. |

No Cornell page was found that addresses Boston. Student experience of Boston trips (FlixBus connection? Megabus?): not found. Where I looked: the five results above and the Sun guide.

**[LLM-GUESS] Typical AI answer:** "There's no direct train. Take a FlixBus or Greyhound from Ithaca to Boston (about 6-8 hours, $50-100), or bus to Syracuse and take Amtrak's Lake Shore Limited to Boston (about 9 hours). Flying from ITH requires a connection."
What it misses or risks: may say Greyhound runs Ithaca-Boston direct (the Philadelphia page shows Greyhound/Flix use "Downtown Ithaca" stops, but a Boston route's existence is not confirmed in my results beyond Rome2Rio); gives no Cornell stop (FlixBus West Campus 240 West Ave vs downtown); cannot say whether FlixBus's route is direct or via NYC/Albany; misses that Amtrak at Syracuse is a bus ride away (Cornell lists station at 1 Walsh Circle, Syracuse).

## Q4 (q-getting-around-0004) How do I get from Ithaca to Philadelphia by bus?
Primary query: "Ithaca to Philadelphia bus". Verdict weak.

| # | URL | Title | Publisher | Date | What it says | Leaves out / wrong |
|---|---|---|---|---|---|---|
| 1 | https://www.rome2rio.com/s/Ithaca/Philadelphia-PA | 8 ways Ithaca to Philadelphia | Rome2Rio | none | SNIPPET. No direct bus; buses via Newark Penn Station, about 6.5 hours (search summary). | Does not say which is best; no Cornell stop. |
| 2 | https://www.rome2rio.com/s/Ithaca-College/Philadelphia | Ithaca College to Philadelphia | Rome2Rio | none | SNIPPET. Includes Flix and Greyhound. | IC-focused. |
| 3 | https://www.rome2rio.com/s/Ithaca/Philadelphia | Ithaca to Philadelphia | Rome2Rio | none | SNIPPET. Duplicate. | Duplicate. |
| 4 | https://www.flixbus.fr/voyages-car/ithaca-ny-philadelphie-pa | Bus Ithaca-Philadelphie | FlixBus (French site) | none | SNIPPET. Operator page. | French-language site ranks for an English query; no Cornell stop. |
| 5 | https://www.rome2rio.com/s/Philadelphia/Ithaca | Philadelphia to Ithaca | Rome2Rio | none | SNIPPET. Reverse. | Duplicate. |

Other operator pages seen: Greyhound route page https://www.greyhound.com/bus-routes/ithaca-ny-philadelphia-pa (SNIPPET: lists 6 buses/day, as little as 7h10m); OurBus https://www.ourbus.com/routes/ithaca-to-philadelphia (SNIPPET: "from $105.2", 5h to 8h45; a search summary says service "set to resume 26 October", date/year not confirmed); CheckMyBus https://www.checkmybus.com/ithaca-ny/philadelphia-pa (SNIPPET: FlixBus 7/day, from $40). Official Cornell listing: "Cornell-Philadelphia (bus.cbtcorp.net)" on Travel Resources (Lane A). Not read: what bus.cbtcorp.net is now or whether it runs.

Contradictions among operator pages (SNIPPET): Greyhound 6/day vs CheckMyBus Flix 7/day; fares $40 (CheckMyBus) vs $105.2 (OurBus). Different operators, different dates; not a true contradiction but a reader sees $40-$105 with no explanation.

**[LLM-GUESS] Typical AI answer:** "Take FlixBus or Greyhound from Ithaca to Philadelphia, about 5-7 hours, $40-80, often with a transfer in NYC or Binghamton. Check schedules."
What it misses or risks: cannot name the Cornell pickup; may claim a direct route; misses OurBus' Philadelphia route and break-time specials; misses the Cornell-Philadelphia charter listed on Cornell's own travel page; misses sell-out timing for Thanksgiving and winter break.

## Q5 (q-getting-around-0005) How do I get from Syracuse airport to Cornell?
Primary query: "how to get from Syracuse airport to Cornell". Verdict weak.

| # | URL | Title | Publisher | Date | What it says | Leaves out / wrong |
|---|---|---|---|---|---|---|
| 1 | https://www.classe.cornell.edu/rsrc/Home/Research/ERL/XDL11Travel/Syracuse.doc | Syracuse Hancock Intl Airport to Cornell University, Ithaca, NY | Cornell CLASSE (lab) | undated, "XDL11" suggests a conference years ago | SNIPPET (summary). Driving directions: I-81 south, US-11 exit toward Homer/Cortland, about 1.5 hours. | Old directions for a lab conference; no bus info; "1.5 hours" vs "just over an hour" elsewhere. |
| 2 | https://www.classe.cornell.edu/rsrc/Home/Research/ERL/XDL11Travel/Syracuse.pdf | same, PDF | Cornell CLASSE | same | SNIPPET. Same. | Duplicate. |
| 3 | https://transfers.th.edreams.com/blog/usa-syracuse-airport-to-cornell-university | Top 5 ways to go from Syracuse airport to Cornell | eDreams (Thai-language transfers blog) | none | SNIPPET. Taxi/transfer about 1h15m, around $200; warns taxis outside the terminal may be hard to find at peak. | Commercial transfer pitch; price unverified. |
| 4 | https://www.rome2rio.com/s/Grand-Central-Terminal/Cornell-University | (irrelevant: Grand Central) | Rome2Rio | none | Not relevant to SYR. | Search engine mismatch. |
| 5 | https://www.rome2rio.com/s/Port-Authority-Bus-Terminal/Cornell-University | (irrelevant: Port Authority) | Rome2Rio | none | Not relevant. | Mismatch. |

Others in results: OurBus SYR-Ithaca page https://www.ourbus.com/routes/syracuseairport-to-ithaca (SNIPPET: pick-up at Terminal A, follow Ground Transportation to the south taxi queue; about 2 hours; about $9-49; "five times a week" per one source); Cornell Johnson transport page https://www.johnson.cornell.edu/new-students/living-in-ithaca/transportation/ ; Cornell conference services https://conferenceservices.cornell.edu/node/196 (says SYR is about 60 miles; note the Cornell Law-type pages say about 46 miles in other places: another contradiction between Cornell pages and third-party pages on distance). Sept 2026 Sun: Cornell-Syracuse bus six days a week incl. SYR airport (READ). Big D's Limousines 607-273-3030 ext 2 on Cornell's Travel Resources (Lane A).

**[LLM-GUESS] Typical AI answer:** "SYR is about an hour from Ithaca. Options: rental car, a pre-booked shuttle or taxi (around $150-200), or a bus such as OurBus or Trailways with a connection. Book ahead."
What it misses or risks: price sanity for taxi; cannot state OurBus days/times (varies by week); misses the Student Assembly / break shuttles; misses Cornell's own listing for Big D's; may mention Greyhound that no longer serves the airport.

## Q6 (q-getting-around-0006) How do I get from Elmira airport to Ithaca and Cornell?
Primary query: "Elmira airport to Ithaca Cornell". Verdict weak.

| # | URL | Title | Publisher | Date | What it says | Leaves out / wrong |
|---|---|---|---|---|---|---|
| 1 | https://www.busbud.com/en/poi/elmira-corning-regional-elm-airport/dr3rf6c | ELM FAQ | Busbud | none | SNIPPET. Bus info for airport. | Aggregator; undated. |
| 2 | https://www.expedia.sa/en/lp/flights/elm/ith/elmira-to-ithaca | Cheap flights ELM to ITH | Expedia Saudi site | none | SNIPPET. Treats it as flight route. | Wrong intent: no useful nonstop ELM-ITH (search summary states none). |
| 3 | https://www.travelprofy.com/elmira-corning-airport-elm/cornell-university | ELM to Cornell University | TravelProfy | none | SNIPPET. Transfer-site page. | Commercial. |
| 4 | https://www.ithaca.edu/academics/graduate-and-professional-studies/graduate-student-life/travel-and-transportation | Travel To and Around Ithaca | Ithaca College | none | SNIPPET. IC grad guide. | Written for IC, not Cornell. |
| 5 | (demand file gives only 4 URLs) | | | | | |

Other: OurBus ELM-Ithaca page (SNIPPET: about $58, about 58 minutes; URL path contains "quarantine", suggests a 2020 pandemic-era page: https://www.ourbus.com/amp/routes/ithaca-to-elmira-cornell-university-quarantine); Trailways https://trailways.ca/schedules/bus-from-elmira-ny-to-ithaca-ny; Visit Ithaca https://www.visitithaca.com/get-here and /plan-your-visit/transportation/ (SNIPPET); Rome2Rio Elmira to Ithaca (taxi/bus/car). Drive about 34-36 miles, about 46 minutes (SNIPPET). Elmira Corning airport page (county) does not give Ithaca ground info (Lane A). Chemung County Transit named on Cornell bus page (Lane A).

**[LLM-GUESS] Typical AI answer:** "ELM is about 35 miles from Ithaca (45 minutes). Take a taxi or rental car, or look for a shuttle; public transit between the two is limited."
What it misses or risks: gives no concrete current option; misses OurBus ELM route if it still runs (page may be a 2020 artifact); no price; no mention that Allegiant and Delta serve ELM (Lane A), which is the reason students use it.

## Q7 (q-getting-around-0007) Can freshmen have a car at Cornell and how much does parking cost?
Primary query: "Cornell student parking permit cost freshman car". Verdict weak. IMPORTANT: demand top results include Cornell College (Iowa) pages. The search engine confuses the two Cornells.

| # | URL | Title | Publisher | Date | What it says | Leaves out / wrong |
|---|---|---|---|---|---|---|
| 1 | https://cornellsun.com/2023/09/04/on-campus-parking-violation-fines-increase-for-first-time-since-2014/ | On-campus parking violation fines increase | Cornell Daily Sun | 2023-09-04 | SNIPPET. Fines up; mentions resident permit annual rate of $752.86 per a search summary. | 2023 price; official page now reads $752.98 resident / $359.77 commuter (Lane A). |
| 2 | https://www.cornellcollege.edu/campus-safety/vehicles-parking/student-parking-form.shtml | Student Vehicle & Parking Regulations | Cornell College (Iowa) | none | WRONG CORNELL. | Not Cornell University. |
| 3 | https://www.cornellcollege.edu/campus-safety/vehicles-parking/student-parking-regulations.shtml | same | Cornell College (Iowa) | none | WRONG CORNELL. | Same. |
| 4 | https://fcs.cornell.edu/node/1456 | (title not captured) | Cornell FCS | undated | SNIPPET. Official. | Not read. |
| 5 | https://news.cornell.edu/node/281986 | Parking permit changes take effect July 1 | Cornell Chronicle | year not checked (node number suggests 2022) | SNIPPET. Permit changes. | Older year. |

Also: https://scl.cornell.edu/families/cornell-family-resource-hub/parking-transportation (SNIPPET: first-years discouraged from bringing a car, limited permits, North Campus resident permits capped and limited to North Campus residents of university housing); https://fcs.cornell.edu/node/17809 "2026/27 Student Permit Sales Begin August 4th" (SNIPPET: sales begin Tue Aug 4 9:00 a.m., first come first served, myparking.cornell.edu). https://www.parksy.com/permits/ca/on/cornell (Cornell, Ontario; wrong place, search tool quoted $359.85 from it) and https://prked.com/post/navigating-cornell-a-complete-guide-to-getting-around-campus-ithaca (SNIPPET: a third-party "complete guide").
Official gap: Lane A found the parking-students page silent on first-year eligibility; the families page (SNIPPET only) says first-years are discouraged and that ND permits are capped to North Campus residents. Not verified by me.

**[LLM-GUESS] Typical AI answer:** "Cornell allows students to bring cars, including first-years, but parking is limited and permits cost roughly $700-1,000 a year depending on lot. Many students don't need a car because TCAT is free."
What it misses or risks: the number (official resident permit $752.98 and commuter $359.77 are in the range but lack lot-by-lot detail); misses that first-year permits are capped and mostly North Campus-linked; misses Collegetown/off-campus overnight rules; misses the $50 fines, winter overnight rules; says "TCAT is free" without the after-6pm/weekend limit for non-first-years; may confuse with Cornell College (Iowa) numbers.

## Q8 (q-getting-around-0008) Is TCAT free for Cornell students and which routes should I use?
Primary query: "TCAT free for Cornell students routes". Verdict: owned.

| # | URL | Title | Publisher | Date | What it says | Leaves out / wrong |
|---|---|---|---|---|---|---|
| 1 | https://news.cornell.edu/node/327352 | (not captured) | Cornell Chronicle | not checked | SNIPPET. Related to TCAT/Cornell contract. | Not read. |
| 2 | https://sustainable.cornell.edu/focus-areas/transportation/bus-commuting | Bus & Commuting | Cornell Sustainability | none | Official (Lane A): first-years free; others free after 6 p.m. weekdays and weekends; routes 81/82/83/90s campus-only, 10, 15, 30, 32. | Undated; route list has an unclear "Becomes 15/17" note; does not tell a student which route to use from which housing. |
| 3 | https://www.masstransitmag.com/bus/press-release/53075491/tompkins-consolidated-area-transit-inc-tcat-tcat-board-of-directors-approves-four-year-contract-with-cornell-university | TCAT Board approves four-year contract with Cornell | Mass Transit magazine (press release) | not checked | SNIPPET. Contract news. | Contract terms, not student rules. |
| 4 | https://fcs.cornell.edu/departments/transportation-delivery-services/sustainable-transportation-options/bus-services-privileges-passes | Bus Services, Privileges, Passes | Cornell FCS | none | Official (Lane A): OmniRide $200/year, grad assistants free, cash $1.50. | Undated. |
| 5 | https://www.tcatbus.com/learn/college-students/ | Welcome College Students | TCAT | none | Official (403 for Lane A). | Unreadable to automated fetch; Ithaca College subsidy detail only via summary. |

Also: Cornell Sun, Nov 3, 2024, "Non-first-year Cornell students no longer able to access TCAT for free" https://cornellsun.com/2024/11/03/non-first-year-cornell-students-no-longer-able-to-access-tcat-for-free/ (SNIPPET: students who had 24/7 free access during a farebox glitch lose it; some IDs denied); Cornell Sun guest column Nov 2025 https://cornellsun.com/article/2025/11/guest-room-from-bikes-to-buses-how-to-sustainably-navigate-campus-this-fall (SNIPPET: since 2005 free for first-year; doctoral/graduate assistants now free; OmniRide option).

**[LLM-GUESS] Typical AI answer:** "Cornell students ride TCAT for free with their ID. Useful routes: 10 (downtown to campus), 30 (Ithaca Mall), 81/82/83 (campus), 32 (airport)."
What it misses or risks: says "free" for all students (true only first-year unlimited; others after 6 p.m. and weekends); misses the 2024 farebox-glitch backstory, ID-denied risk and $1.50 fallback; route list lacks "from North Campus/Collegetown to X" decisions; no night routes 90/92/93 and the inconsistent list; no OmniRide price.

## Q9 (q-getting-around-0009) Can you bike in Ithaca in winter and what is it like?
Primary query: "biking in Ithaca winter Cornell". Verdict gap.

| # | URL | Title | Publisher | Date | What it says | Leaves out / wrong |
|---|---|---|---|---|---|---|
| 1 | https://cornellsun.com/2007/11/12/cyclists-persevere-through-wintry-weather | Cyclists persevere through wintry weather | Cornell Daily Sun | 2007-11-12 | SNIPPET. Some riders keep going in snow; gear and maintenance matter. | 19 years old; no current bike lanes, no snow-clearing info. |
| 2 | https://sustainable.cornell.edu/news/rules-road-biking-season | Rules of the road for biking season | Cornell Sustainability | undated | SNIPPET. Bikes have same road rights as vehicles; rules. | Not winter-specific. |
| 3 | https://cornellsun.com/2023/01/24/ithaca-bikeshare-a-comprehensive-guide-to-ithacas-newest-transportation-option/ | Ithaca Bikeshare guide | Cornell Daily Sun | 2023-01-24 | SNIPPET. Says cold and hills make biking difficult. | Bikeshare season dates not verified. |
| 4 | https://scl.cornell.edu/winter-activities | Winter Activities | Cornell Student and Campus Life | undated | SNIPPET. Winter recreation. | Not about commuting. |
| 5 | https://ccetompkins.org/events/2023/12/01/winter-wheelers-challenge | Winter Wheelers Challenge | CCE Tompkins | 2023-12-01 | SNIPPET. December riding challenge; tips. | 2023 event. (This was result 5 in my run; the demand file has 4 listed.) |

Gap confirmed: no page gives (a) where campus paths are cleared, (b) when Cornell/City plows bike lanes, (c) what students actually ride in January (studded tires, fat bikes), (d) whether Bikeshare runs in winter. Lane A found no official winter guidance (Lane A section 11).

**[LLM-GUESS] Typical AI answer:** "Biking in Ithaca in winter is possible but challenging: hills, snow and ice. Use studded tires, lights, and layers; many students switch to TCAT in the coldest months."
What it misses or risks: nothing specific to Ithaca (which hills: Buffalo St, Stewart Ave, Eddy Gate to Collegetown; Cascadilla gorge; which routes get plowed); no policy on bike storage in dorms in winter; no mention that bikes are impounded if locked to railings (official, Lane A); no data on days of snow cover.

## Q10 (q-getting-around-0010) Are Uber and Lyft reliable in Ithaca or should I use a taxi?
Primary query: "Uber Lyft Ithaca reliable taxi". Verdict weak.

| # | URL | Title | Publisher | Date | What it says | Leaves out / wrong |
|---|---|---|---|---|---|---|
| 1 | https://cornellsun.com/2017/08/29/uber-lyft-receive-mixed-reviews-during-trial-period | Uber, Lyft receive mixed reviews during trial period | Cornell Daily Sun | 2017-08-29 | SNIPPET. Early wait times (one reporter about half an hour), surge example: 3.5-mile ride over $20. | 9 years old; driver supply today unknown. |
| 2 | https://www.cornellsun.com/article/2017/08/uber-lyft-receive-mixed-reviews-during-trial-period | same | same | same | Duplicate URL form. | Duplicate. |
| 3 | https://cornellsun.com/2017/07/01/uber-lyft-begin-trial-period-in-ithaca/ | Uber, Lyft begin trial period in Ithaca | Cornell Daily Sun | 2017-07-01 | SNIPPET. Launch story. | 2017. |
| 4 | https://ride.guru/airports/ITH | Uber, Lyft, Taxis at ITH | RideGuru | none | SNIPPET. Lists services at ITH. | Directory; no wait time data. |
| 5 | (demand list cut off; in my run) https://theithacan.org/?p=26074 and https://theithacan.org/news/ride-hailing-services-slightly-less-expensive-than-taxis-in-ithaca/ | Ride-hailing slightly less expensive than taxis in Ithaca | The Ithacan (Ithaca College) | about 2017 (year not shown in snippet) | SNIPPET. Uber/Lyft slightly cheaper than taxis on common routes; taxi fares set by City in six zones. | Old; fares not current. |

Also: WSKG Oct 2, 2017 "Ride-hailings in Ithaca now" https://www.wskg.org/news/2017-10-02/ride-hailings-in-ithaca-now-so-we-rode-with-an-uber-driver (SNIPPET); Fly Ithaca Ride Share Apps https://www.flyithaca.com/ride-share and https://flyithaca.com/taxis (Lane A: Uber/Lyft by app; taxis 24/7). No post-2018 reliability data found. Where I looked: the five results, search summary.

**[LLM-GUESS] Typical AI answer:** "Uber and Lyft are available in Ithaca but with fewer drivers than a big city, so waits can be longer, especially late at night, early mornings and during breaks. Taxis like Ithaca Dispatch are reliable and good for pre-booking airport rides."
What it misses or risks: gives no wait data or price; misses that taxi fares are set by the City in zones (so published fares exist; I did not find the schedule); misses break-week shortages; misses the airport taxi numbers (Lane A: Ithaca Airport Cab 607-252-9052; Collegetown Cab 607-588-8888; Ithaca Dispatch 607-277-7777).

## Q11 (q-getting-around-0011) How do Cornell students get home for Thanksgiving and winter break?
Primary query: "how Cornell students get home for break bus flight". Verdict weak.

| # | URL | Title | Publisher | Date | What it says | Leaves out / wrong |
|---|---|---|---|---|---|---|
| 1 | https://cornellsun.com/2019/12/02/before-classes-were-cancelled-cornellians-attempted-to-return-to-ithaca-at-all-costs | Before classes were cancelled, Cornellians attempted to return to Ithaca at all costs | Cornell Daily Sun | 2019-12-02 | SNIPPET. Snowstorm return-to-campus story; missed flights, stranded students. | About a one-time snow event; 2019. |
| 2 | https://cornellalumnimagazine.com/getting-there-from-here/ | Getting there from here | Cornell Alumni Magazine | date not checked | SNIPPET. Magazine piece. | Not read; date unknown. |
| 3 | https://www.cornellsun.com/article/2019/12/before-classes-were-cancelled-cornellians-attempted-to-return-to-ithaca-at-all- | same as #1 | | | Duplicate. | Duplicate. |
| 4 | https://www.cornellsun.com/article/2023/11/inside-ourbus-cornellians-preferred-method-of-travel | Inside OurBus: Cornellians' preferred method of travel | Cornell Daily Sun | 2023-11-09 | SNIPPET. OurBus owns no buses itself; one student got second-to-last seat at fall break. | 2023. |
| 5 | https://www.ourbus.com/blog/college-break-special-bus-service-for-cornell-students/ | College break special bus service for Cornell students | OurBus blog | date not checked | SNIPPET. Operator marketing. | Marketing; sell-out timing not independently confirmed. |

Also: Sun 2003 "How students get home" https://cornellsun.com/2003/10/20/how-students-get-home (SNIPPET; says fall/winter break buses sell out right after sales start; 23 years old); Sun 2023-11-19 "Special Thanksgiving shuttle connects Cornell with ITH" https://cornellsun.com/2023/11/19/special-thanksgiving-shuttle-connects-cornell-with-ithaca-tompkins-international-airport/ (SNIPPET; a 2023 program, current status not confirmed); College Confidential threads https://talk.collegeconfidential.com/t/traveling-to-and-from-cornell/1599797 (SNIPPET; posters: Greyhound to Rochester $25; bus to Syracuse $25; year not shown); Coach USA student discounts page https://www.coachusa.com/node/?page=3.

**[LLM-GUESS] Typical AI answer:** "Most students take a bus (OurBus, FlixBus, Campus-to-Campus) to NYC or fly from Ithaca or Syracuse. Book early for Thanksgiving and winter break."
What it misses or risks: no dates for 2026 breaks or book-by dates; does not say C2C reservations for Nov-Dec 23 and from Jan 6 are separate links (Lane A); misses ride board; misses that break dorm closure and car-storage rules (Lane A: students in university housing may leave cars in permit areas) decide the plan.

## Q12 (q-getting-around-0012) Do I need a car at Cornell?
Primary query: "do you need a car at Cornell Ithaca". Verdict weak.

| # | URL | Title | Publisher | Date | What it says | Leaves out / wrong |
|---|---|---|---|---|---|---|
| 1 | https://forums.studentdoctor.net/threads/cars.962192/ | Cars (forum) | Student Doctor Network | thread date not checked | SNIPPET. Medical-student opinions (Weill?). | Unknown relevance; forum. |
| 2 | https://reddit.sentinel-team.org/subreddits/Cornell/snapshots/2026-05-20T16%3A45%3A27.30298Z | r/Cornell snapshot | third-party Reddit mirror | 2026-05-20 | SNIPPET. Mirror of a subreddit snapshot. | Mirror site; individual posts; not an article. |
| 3 | https://reddit.fabiomanganiello.com/r/HWS/comments/1cal9ah/bike_or_car_for_campus_life | Bike or car (HWS) | Reddit mirror | not checked | About Hobart and William Smith colleges, a different school. | Wrong school. |
| 4 | https://forum.thegradcafe.com/topic/153-ithaca-ny/?page=8 | Ithaca NY | The Grad Cafe forum | not checked | SNIPPET. Grad-student chatter. | Old thread (page 8). |

Others (my search): Cornell Law housing page https://lawschool.cornell.edu/life-at-cornell-law/housing (many law students choose not to bring cars); Cornell Johnson https://www.johnson.cornell.edu/new-students/living-in-ithaca/transportation/ ; Cornell postdocs https://postdocs.cornell.edu/postdoc-life/living-in-ithaca (many apartments have no parking; register car in NY); Sun 2020 "Making their way up the hill: professors on their unique commutes" https://www.cornellsun.com/article/2020/01/making-their-way-up-the-hill-professors-on-their-unique-commutes ; College Confidential https://talk.collegeconfidential.com/t/should-i-bring-a-car/1811430 and /t/is-a-car-necessary-if-im-living-downtown/523280 (SNIPPET).
Opinion attribution: all views above are posters' or school offices' opinions, not facts.

**[LLM-GUESS] Typical AI answer:** "Most undergrads don't need a car: campus is walkable, TCAT is free or cheap and parking is expensive. A car helps for grocery runs, off-campus living or trips; consider Ithaca CarShare."
What it misses or risks: parking costs; Ithaca CarShare student pricing; no breakdown by living area (North vs West vs Collegetown vs off-campus apartments); no mention of freshman permit limits; no mention of winter driving.

## Q13 (q-getting-around-0013) How do I get from Ithaca to JFK, LaGuardia or Newark airport?
Primary query: "Ithaca to Newark airport EWR bus Cornell". Verdict weak.

| # | URL | Title | Publisher | Date | What it says | Leaves out / wrong |
|---|---|---|---|---|---|---|
| 1 | https://www.rome2rio.com/s/Newark/Cornell-University-College-of-Engineering | Newark to Cornell Engineering | Rome2Rio | none | SNIPPET. Direct OurBus ~4 hours, $20-75 per the search summary. | Treats a college as a destination; no stop names. |
| 2 | https://dimaggio-old.heartlight.org/ithaca-to-newark-airport-bus-info-3276100613.html | News & Updates | heartlight.org (unrelated domain) | none | SNIPPET. Looks like a low-quality reprint; the tool flagged it. | Spam-like. |
| 3 | https://www.checkmybus.com/ithaca-ny/newark-nj-airport | Bus from Ithaca to Newark Airport | CheckMyBus | none | SNIPPET. About 10 daily departures; 4.5-5 h; cheapest $82 on a February 2026 date. | Price may be a peak-date; disagrees with Rome2Rio. |
| 4 | https://www.rome2rio.com/s/Port-Authority-Bus-Terminal/Cornell-University | Port Authority to Cornell | Rome2Rio | none | SNIPPET. | Mismatch. |
| 5 | https://www.ourbus.com/routes/ithaca-ny-to-newark-airport-nj | Ithaca to Newark Airport | OurBus | none | SNIPPET. Boards at West Campus across from Baker's Flagpole or North Campus on Jessup Road; Newark drop at AirTrain P4 (another OurBus page says P3). | Internal contradiction P3/P4; JFK and LaGuardia not covered by any top result. |

Not covered by any result: JFK and LaGuardia from Ithaca by bus (Port Authority then subway/AirTrain; or C2C to Midtown then transfer). Sept 2026 Sun says direct ITH-Newark flights ended 2025 (READ); Lane A lists ITH-JFK Delta.

**[LLM-GUESS] Typical AI answer:** "Take OurBus or Coach USA to Port Authority, then the AirTrain or a taxi to JFK/LGA/EWR; about 5-6 hours total. Or fly out of Ithaca via Newark."
What it misses or risks: Newark direct bus exists (OurBus); Newark flights from ITH ended; no fares; no JFK/LGA direct options; no Cornell pickup stop; no advice on buffer times (the 2019 Sun piece shows missed flights).

## Q14 (q-getting-around-0014) Is Ithaca CarShare worth it for Cornell students?
Primary query: "Zipcar Cornell Ithaca car share students". Verdict weak.

| # | URL | Title | Publisher | Date | What it says | Leaves out / wrong |
|---|---|---|---|---|---|---|
| 1 | https://reports-dev.aashe.org/institutions/cornell-university-ny/report/2014-03-07/OP/transportation/OP-T2-37 | STARS report | AASHE (dev mirror) | 2014-03-07 | SNIPPET. Sustainability report. | 12 years old; dev mirror. |
| 2 | https://reports.aashe.org/institutions/cornell-university-ny/report/2014-03-07/OP/transportation/OP-T2-37 | STARS report | AASHE | 2014-03-07 | SNIPPET. | Duplicate. |
| 3 | https://reports.aashe.org/institutions/cornell-university-ny/report/2013-03-08/OP/transportation/OP-T2-37 | STARS | AASHE | 2013-03-08 | SNIPPET. 584 Cornell students and 237 employees using the membership incentive (2012-13). | 13 years old. |
| 4 | https://news.cornell.edu/node/274327 | Cornell-supported Ithaca Carshare provides vehicles for pickup at your nearest "pod" | Cornell Chronicle | 2008 | SNIPPET. 2008 launch; Cornell paid the "Just In Case" fee (normally $50) for students until Sept 15; "It's My Car" $140/year. | 2008 prices. |
| 5 | https://sustainablecampus.cornell.edu/campus-initiatives/transportation/ride-car-sharing | Ridesharing & Carsharing | Cornell Sustainability | undated | SNIPPET. Says students eligible for discounted memberships; four campus locations. | No rates; no age minimum; no hourly rate. |

Also: Cornell Sun 2008-08-11 on carshare https://cornellsun.com/2008/08/11/carshare-program-fosters-sustainable-transportation-ithaca. Official site https://www.ithacacarshare.org (Lane A: about 20 vehicles; rates and student discount not on home page). Zipcar results were other universities (no evidence Zipcar operates at Cornell; this is the search tool's finding from search results, not an official statement).

**[LLM-GUESS] Typical AI answer:** "Ithaca CarShare is a local nonprofit with cars at pods around campus; students get discounted memberships. It's cheaper than owning a car if you drive occasionally; check the hourly rates. Zipcar is also an option."
What it misses or risks: Zipcar probably isn't in Ithaca (hallucination risk); no current rates; no age minimum; no break-even math against a $752.98 permit; no pod list.

<!-- merged from competition-part2.md -->
# Getting to Ithaca and getting around it: the competition, part 2 (Lane D)

Continuation of `competition.md` (questions 1-14 and the method note are there). Same rules: SNIPPET = search-tool summary, page not opened; READ = I opened it. **[LLM-GUESS]** = my reconstruction of a general-knowledge AI answer, not a source. Checked 2026-11-08.

---

# PART 2: QUESTIONS (demand rows 0015 to 0025, then my five additions 26-30)

## Q15 (q-getting-around-0015) Where can I park near Collegetown and overnight in Ithaca?
Primary query: "parking in Collegetown Ithaca where to park overnight". Verdict weak.

| # | URL | Title | Publisher | Date | What it says | Leaves out / wrong |
|---|---|---|---|---|---|---|
| 1 | https://news.cornell.edu/node/278473 | Cornell has parking options to handle the overflow | Cornell Chronicle | year not shown (node suggests early 2020s) | SNIPPET. Mentions a city-owned ramp off Dryden Road with 210 spaces; merchants' informal survey found about a third empty in daytime. | Daytime vacancy, not overnight rules; undated; Dryden Road garage price now $18 daily max (City page, Lane A). |
| 2 | https://www.cornellsun.com/article/2023/09/williams-street-parking-lot-struggles-to-accommodate-students | Williams Street parking lot struggles to accommodate students | Cornell Daily Sun | 2023-09-07 | SNIPPET. Student complaints about the Williams Street lot. | 2023; no overnight/legal rules. |
| 3 | https://cornellsun.com/2023/09/07/williams-street-parking-lot-struggles-to-accommodate-students | same | same | same | Duplicate URL form. | Duplicate. |
| 4 | https://cornellsun.com/2000/09/05/city-tries-to-improve-collegetown-parking | City tries to improve Collegetown parking | Cornell Daily Sun | 2000-09-05 | SNIPPET. Says Collegetown streets filled far beyond calculated capacity. | 26 years old. |
| 5 | (demand file's 5th cut off) https://fcs.cornell.edu/sites/default/files/2026-08/ParkmobileMap26.pdf | ParkMobile map 2026 | Cornell FCS | 2026-08 (path) | SNIPPET (title only). A 2026 ParkMobile zone map. | Not read; a map, not an explanation. |

Also in results: Cornell winter parking announcements https://fcs.cornell.edu/announcements/2023-11-16/winter-parking-transportation-information and /2019-11-13/ (SNIPPET: specially signed areas open 5 p.m.-7:30 a.m. to registered vehicles, Dec 1-Apr 1 when snowing or forecast; Lane A has the full area list); Ithaca College overnight/visitor rules https://www.ithaca.edu/public-safety-and-emergency-management/parking-services/visitor-parking/overnight-and-weekend-visitor-vehicle-registration (wrong campus for this question). A jamiemcatee.com page said garages "$1/hour" for downtown and Collegetown (SNIPPET, undated, stale: City page effective Jan 5, 2026 says $2.25/hour in garages, Lane A).
Contradiction: Visit Ithaca (READ, 2026-05-12) says downtown garages on Cayuga and Green Street cost about $2/hour and are free on weekends after Friday night; the City page (Lane A, posted 2025-12-18) says $2.25/hour with daily maximums of $12 and $18. Visit Ithaca's weekend-free claim not seen on the City page I read. URLs: https://www.visitithaca.com/blog/post/your-guide-to-a-great-college-family-weekend-in-ithaca/ ; https://www.cityofithacany.gov/CivicAlerts.aspx?AID=1328
Not found anywhere: City of Ithaca overnight on-street rules for Collegetown, overnight garage pricing, monthly permit availability for students, whether a Cornell permit works in Collegetown.

**[LLM-GUESS] Typical AI answer:** "Collegetown parking is tight. Use the Dryden Road garage (hourly or daily), metered street spots, or a private lot. Overnight street parking may be restricted in winter. Check the City of Ithaca's rules."
What it misses or risks: gives a made-up or stale hourly rate; omits the Nov 1-Apr 1 odd/even rule (Cornell page via Lane A); omits that cars left on city streets over winter break may be towed; omits the Cornell winter-overnight lot list; may confuse "Collegetown garage" with the Dryden Road garage (the same facility? I did not confirm).

## Q16 (q-getting-around-0016) What is it like driving to Ithaca in winter?
Primary query: "Cornell Ithaca winter driving I-81 Route 13 snow tips". Verdict gap.

| # | URL | Title | Publisher | Date | What it says | Leaves out / wrong |
|---|---|---|---|---|---|---|
| 1 | https://www.thetruckersreport.com/truckingindustryforum/posts/6709858/ | (trucker forum post) | The Truckers Report forum | not checked | SNIPPET. Ithaca sits in a valley; approach is steep; a poster called the Route 13 hill north of town aggressive and suggested Route 34 north toward Auburn to reach I-81. | Anecdote; truck-focused; undated; not official. |
| 2 | https://cornellsun.com/2022/11/21/dont-let-it-snow-students-express-concerns-over-driving-conditions-as-temperatures-fall/ | Don't let it snow: students express concerns over driving conditions | Cornell Daily Sun | 2022-11-21 | SNIPPET. Students said roads generally well kept but hills and parking cause trouble. | 2022; opinion. |
| 3 | https://www.fodors.com/community/united-states/driving-conditions-for-late-jan-early-feb-from-indiana- | Driving conditions late Jan/early Feb (forum) | Fodor's forum | not checked | SNIPPET (URL only in demand file). Visitor planning thread. | Forum; not specific. |
| 4 | https://www.tompkinscountyny.gov/All-Departments/Highway-Department/Snow-and-Ice-Maintenance | Snow and Ice Maintenance | Tompkins County Highway Dept | undated | SNIPPET. Official county page. | Not read; county roads only; does not cover I-81 or NY-13 (state). |
| 5 | https://literock973.com/news/025520-new-day-brings-new-problems-for-ithaca-commuters/ | New day brings new problems for Ithaca commuters | local radio news site | about 2020 (slug "025520") | SNIPPET. Commuter snow story. | Dated; one event. |

Also: Sun 2019 "TCAT prepares to swerve away winter storm conditions" https://www.cornellsun.com/article/2019/01/tcat-prepares-to-swerve-away-winter-storm-conditions (snow routes). A search result named generic winter-driving tip pages from other states (Idaho, Rhode Island etc.), not Ithaca.
Not found: any page that gives drive times with a snow allowance from NYC, Boston, Philly or Syracuse; state routes' plow priority; travel-advisory history; NY511 usage. The official NY511 page was not read.

**[LLM-GUESS] Typical AI answer:** "Ithaca gets lake-effect snow and has steep hills. Drive slowly, use snow tires, carry an emergency kit, check NY511, and allow extra time on I-81 and Route 13/17."
What it misses or risks: calls generic tips "local"; may name the wrong highways (the Sept 2026 Sun and forums point to I-81 plus NY-13/NY-79/NY-34); doesn't say which hills (Route 13 north, Route 79 east, Route 96B); no data on typical snowfall days or Cornell snow-parking declarations; no mention of odd/even and winter-overnight lots.

## Q17 (q-getting-around-0017) Who can ride the Cornell Campus-to-Campus (C2C) bus and how do I book it?
Primary query: "Cornell Campus to Campus bus who can ride students tickets". Verdict: owned.

| # | URL | Title | Publisher | Date | What it says | Leaves out / wrong |
|---|---|---|---|---|---|---|
| 1 | https://fcs.cornell.edu/content/campus-campus-bus-service | C2C service | Cornell FCS | undated | Official (Lane A holds details). | Older URL form; check redirect. |
| 2 | https://fcs.cornell.edu/departments/transportation-and-delivery-services/campus-campus-bus-service | C2C service | Cornell FCS | undated | Official; Lane A: open to the public; booking via the new system launched 2026-11-04; Cornell SSO discount. | Does not compare with commercial buses. |
| 3 | https://sustainable.cornell.edu/focus-areas/transportation/bus-commuting | Bus & Commuting | Cornell Sustainability | undated | Official; mentions C2C among options (Lane A read the page for TCAT). | Not the booking page. |
| 4 | https://c2cbus.ipp.cornell.edu/Start.aspx | Campus-to-Campus Bus Service New Reservation | Cornell | old system | SNIPPET. Old reservation host. | The new system launched 2026-11-04 (Lane A: fcs announcement 2026-10-22); this URL may be dead or redirected. Not opened. |
| 5 | https://fcs.cornell.edu/node/4706 / /node/1741 / /node/12445 (several FCS nodes) | (titles not captured) | Cornell FCS | not checked | SNIPPET. Related official pages. | Not read. |

Contradiction to flag: a search summary of an older Cornell news article (https://news.cornell.edu/node/282639, "Express service with luxury touches: Campus-to-campus bus hits its stride", date not checked) says the bus "requires a Cornell connection." The official announcement (Lane A, 2026-10-22) says open to the public, family and visitors included. Likely a policy change over time; I did not fetch node 282639 so I cannot date the claim.
Also: C2C winter-break schedule announcement https://fcs.cornell.edu/announcements/2025-12-02/c2c-winter-break-schedule (SNIPPET only; my fetch got HTTP 403). Terms page https://fcs.cornell.edu/departments/transportation-delivery-services/campus-campus-bus-service/c2c-terms-conditions (SNIPPET).
Old stop info: a summary says stops included "the F train stop outside Roosevelt Island campus"; Lane A says an Aug 1, 2026 change dropped the "F Train" stop but found no page confirming it. Still unconfirmed.

**[LLM-GUESS] Typical AI answer:** "The Campus-to-Campus bus is for Cornell students, faculty and staff between Ithaca and NYC. Reserve online through Cornell's transportation website; fares are around $70-90 each way."
What it misses or risks: says Cornell-only (official: open to public); fare range may miss $101 non-Cornell; omits new account requirement since Nov 4, 2026; omits cancellation rules ($10/$30 per seat per Lane A, one contradiction unresolved); omits luggage/bike/pet rules; does not tell whether Cornell Club or Weill is the right NYC stop.

## Q18 (q-getting-around-0018) How do I get from Ithaca to Toronto?
Primary query: "Ithaca to Toronto bus". Verdict weak.

| # | URL | Title | Publisher | Date | What it says | Leaves out / wrong |
|---|---|---|---|---|---|---|
| 1 | https://www.rome2rio.com/s/Ithaca/Toronto-Pearson-Terminal-1-Station | Ithaca to Toronto Pearson T1 | Rome2Rio | none | SNIPPET. 5 ways; bus (Flix), train, car, plane. Range $43-170, 7h20-8h07 per summary. | Pearson destination, not city centre; no stops. |
| 2 | https://www.rome2rio.com/s/Humber-College-Bus-Terminal/Ithaca | Humber College to Ithaca | Rome2Rio | none | SNIPPET. Reverse route. | Wrong direction; Humber terminal. |
| 3 | https://www.rome2rio.com/s/Kitchener/Ithaca | Kitchener to Ithaca | Rome2Rio | none | SNIPPET. Irrelevant city. | Mismatch. |
| 4 | https://www.flixbus.co.uk/bus-routes/toronto-on-ithaca-ny | Toronto to Ithaca bus | FlixBus UK site | none | SNIPPET. Toronto stop Union Station Bus Terminal, 81 Bay St 2nd floor; first Flix at 8:30 a.m., last 2:05 p.m. per summary. | UK domain; reverse direction. |
| 5 | https://www.greyhound.com/bus-routes/toronto-on-ithaca-ny | Toronto to Ithaca | Greyhound | none | SNIPPET. 2 buses per day; from about $43; earliest 05:05, last 02:15 per summary. | Reverse. |

Others (my search): OurBus https://www.ourbus.com/routes/ithaca-ny-to-toronto-on (SNIPPET: from $55, 6h40, stop 130 E. Seneca St); Megabus https://ca.megabus.com/route-guides/ithaca-to-toronto-bus (SNIPPET: fastest 7h15, earliest 10:50 a.m., up to 1 trip/day, stop 131 East Green St). Frequency per source: 1 to 3 per day (conflicts). I did not find: crossing documents advice for international students (passport, visa, CBP), the Cornell International Student page or any Cornell-specific note. Where I looked: the five results, search summary.

**[LLM-GUESS] Typical AI answer:** "Take FlixBus or Greyhound (about 7-8 hours, $50-100) with a border crossing, or drive about 4.5 hours via Buffalo, or fly through Newark/JFK."
What it misses or risks: says "Buffalo" airport/drive without detail; gives no Cornell stop; misses the border-document angle for international students and the 2-3 departures per day; may say Greyhound has more departures than the sources show.

## Q19 (q-getting-around-0019) How much does Ithaca Bikeshare cost and is it free for Cornell students?
Primary query: "Ithaca Bikeshare cost Cornell students". Verdict weak.

| # | URL | Title | Publisher | Date | What it says | Leaves out / wrong |
|---|---|---|---|---|---|---|
| 1 | https://theithacan.org/?p=45638 | (title not captured) | The Ithacan | about 2023 (id near the 46872 piece) | SNIPPET. Bikeshare coverage. | Not read. |
| 2 | https://news.cornell.edu/index%2ephp/node/270417 | Bike-share program gives Cornellians a free ride | Cornell Chronicle | 2011-05-03 (Lane A) | Lane A READ: Big Red Bikes, 25 free hours/week. | 2011; a different program, not Ithaca Bikeshare. A search summary quotes $3/hour after the first hour from a Cornell item (year unknown) which conflicts with the 2011 page's $5/hour; they may be different years. |
| 3 | https://news.cornell.edu/node/270417 | same | same | same | Duplicate. | Duplicate. |
| 4 | https://cornellsun.com/2018/04/26/new-dockless-bikesharing-service-enters-downtown-ithaca/ | New dockless bikesharing service enters downtown Ithaca | Cornell Daily Sun | 2018-04-26 | SNIPPET. LimeBike entry; 50 cents per 30 minutes for students with college emails (per summary). | LimeBike, not Ithaca Bikeshare; 8 years old. |
| 5 | https://betterbikeshare.org/2023/07/10/ithaca-stands-by-bike-share/ | Ithaca stands by bike share | BetterBikeShare | 2023-07-10 | SNIPPET. Rate raised from $0.15 to $0.20 per minute and $0.50 unlock fee (per summary). | 2023 rate; 2026 rate not confirmed. |

Also: Sun 2023-01-24 guide https://cornellsun.com/2023/01/24/ithaca-bikeshare-a-comprehensive-guide-to-ithacas-newest-transportation-option/ (SNIPPET: no hubs on campus at that time; operator hoped for a free-student-ride deal); Cornell Sustainability https://sustainable.cornell.edu/news/center-community-transportation-launches-new-ithaca-bikeshare and https://sustainable.cornell.edu/news/sustainability-recipe-biking (SNIPPET: pay-as-you-go $0.20/min plus unlock fee; updated summer 2023); Ithacan "Ithaca Bikeshare adds parking hubs and raises costs of use" https://theithacan.org/46872/news/ithaca-bikeshare-adds-parking-hubs-and-raises-costs-of-use (SNIPPET). Free "Easy Access" program via Go Ithaca (SNIPPET).
Answer to "free for Cornell students": no source found that says yes (as of the sources above). Official Cornell page for 2026 not found.

**[LLM-GUESS] Typical AI answer:** "Ithaca Bikeshare is pay-as-you-go (about $0.20 a minute plus an unlock fee) with some monthly passes. Cornell students may get a discount. Check the app."
What it misses or risks: may state "Cornell students ride free" (no source); no current 2026 prices; misses the winter operating season (not found); mixes up LimeBike and Big Red Bikes history.

## Q20 (q-getting-around-0020) Is there a TCAT bus from Cornell to the Ithaca airport?
Primary query: "TCAT bus to Ithaca airport route 32 schedule". Verdict: owned.

| # | URL | Title | Publisher | Date | What it says | Leaves out / wrong |
|---|---|---|---|---|---|---|
| 1 | https://tcatbus.com/wp-content/uploads/32_Summer24.pdf | 32 Summer24 | TCAT | Summer 2024 | SNIPPET (PDF timetable, not opened). | A 2024 summer timetable ranks first; stale. |
| 2 | https://flyithaca.com/?p=9 | Public transportation (dated "Sat, Aug 30th, 2025") | Ithaca airport | 2025-08-30 | SNIPPET. Route 32 weekdays, Route 72 weekends; payment cash, card, wallet, Tcard, TFare app. | Page dated 2025; no times. |
| 3 | https://updates.moovit.com/tcat-reduced-service-through-may-23/ | TCAT reduced service through May 23 | Moovit updates | year not shown | SNIPPET. Reduced service notice. | Stale event; ranks anyway. |
| 4 | https://flyithaca.com/ground/bus-service/ | Bus service (dated "Tue, Nov 18th, 2025") | Ithaca airport | 2025-11-18 | SNIPPET. Lane A got a 404 on this URL; the search tool shows a snippet. | Conflict: 404 for Lane A vs a live-looking snippet. |
| 5 | https://tcatbus.com/wp-content/uploads/32_Late-Fall.pdf | 32 Late Fall | TCAT | year not shown | SNIPPET. PDF timetable. | Year unknown; not opened. |

Others: Cornell Sun May 2025 (READ): text says 7:30 a.m.-6:40 p.m., table gives 7:34 a.m.-7:31 p.m. arrivals and 7:46 a.m.-6:43 p.m. departures, weekends drop-off only (conflicts internally). Wikipedia mirrors say hourly or better (SNIPPET; not official). Third-party sites say fare $2; Lane A (airport page summary) says adults $1.50. TCAT's fare page updated 2026-09-04 (SNIPPET): see Q27. TCAT phone: 607-277-7433 / 277-RIDE.
Official but unreadable to automated fetch: tcatbus.com timetables (403 for Lane A). Whether 32 runs Saturday/Sunday as drop-off only or Route 72 replaces it: unresolved (airport site says 72 on weekends).

**[LLM-GUESS] Typical AI answer:** "Yes, TCAT Route 32 connects Cornell, downtown and the airport on weekdays. Check the schedule, it runs roughly hourly."
What it misses or risks: weekend route 72; no timetable; may state a $2 fare; the Student Assembly and break shuttles; the last-bus timing versus evening flights; the winter reduced schedule.

## Q21 (q-getting-around-0021) How do I get from Ithaca to Washington DC by bus?
Primary query: "Ithaca to Washington DC bus Cornell". Verdict weak.

| # | URL | Title | Publisher | Date | What it says | Leaves out / wrong |
|---|---|---|---|---|---|---|
| 1 | https://www.ourbus.com/amp/routes/cornell-ithaca-to-dc | Cornell Ithaca to DC | OurBus | none | SNIPPET. Downtown Ithaca at 130 E Seneca St to Union Station, from $75*, about 7h40. | An AMP page; downtown stop, not campus. |
| 2 | https://www.cornellsun.com/article/2018/09/ourbus-increases-services-out-of-ithaca-to-include-pennsylvania-and-d-c | OurBus increases services out of Ithaca to include Pennsylvania and D.C. | Cornell Daily Sun | 2018-09-20 | SNIPPET. 2018 expansion news. | 8 years old. |
| 3 | https://www.cornellclubdc.org/event-731459 | Event page | Cornell Club of Washington DC | not checked | SNIPPET. Alumni event. | Not a route guide. |
| 4 | https://www.flixbus.ca/bus-routes/ithaca-ny-washington-dc | Ithaca to Washington DC | FlixBus Canada | none | SNIPPET. Direct run about 10 h per CheckMyBus sample (April 2026). | Longer; fares not given. |
| 5 | https://flixbus.com/bus-routes/bus-ithaca-ny-washington-dc | same | FlixBus | none | SNIPPET. Same. | Duplicate. |

Also: Trailways (SNIPPET): Cornell West Campus stop at University Ave & Stewart Ave, estimated 12h45, about one bus per day; Wanderu (SNIPPET): 5 buses a day, one direct, average $75, pickup Green Street Pharmacy (130 E Seneca St); frequency conflicts with another Wanderu page (4/day). Distances 349 to 465 miles, times 7.5 to 12.75 h across sources. Cornell's own travel page lists the Cornell-Philadelphia bus (Lane A) but not DC.

**[LLM-GUESS] Typical AI answer:** "OurBus, FlixBus and Greyhound run Ithaca to DC, about 8-11 hours and $60-120, often with a transfer. Check which stop is closest to campus."
What it misses or risks: wrong stop (campus West Campus vs downtown Seneca St); no Cornell-Club-DC or alumni ride info; no direct-vs-transfer comparison; no mention of overnight options.

## Q22 (q-getting-around-0022) How do parents get around Ithaca on a Cornell visit without renting a car?
Primary query: "Cornell parent visit weekend Ithaca getting around without a car". Verdict weak.

| # | URL | Title | Publisher | Date | What it says | Leaves out / wrong |
|---|---|---|---|---|---|---|
| 1 | https://cornellalumnimagazine.com/?p=1130 | (title not captured) | Cornell Alumni Magazine | not checked | SNIPPET. Magazine page. | Not read. |
| 2 | https://alumni.cornell.edu/come-back/reunion/arriving-getting-around | Arriving and getting around (Reunion) | Cornell Alumni Affairs | undated | SNIPPET. Reunion weekend logistics; Cornell does not rent scooters or golf carts for individual use; accessibility transport for guests. | Reunion-specific, not a general parent visit. |
| 3 | https://talk.collegeconfidential.com/t/air-transportation-to-and-from-ithaca/1892899 | Air transportation to and from Ithaca | College Confidential forum | thread date not checked | SNIPPET. Parents' airport chatter; mentions a Cornell shuttle from Syracuse airport (not confirmed). | Forum; unverified. |
| 4 | https://alumni.cornell.edu/?p=15338 | General parking | Cornell Alumni | not checked | SNIPPET. Reunion parking. | Reunion-only. |
| 5 | https://cornellsun.com/article/2025/11/guest-room-from-bikes-to-buses-how-to-sustainably-navigate-campus-this-fall | Guest room: from bikes to buses | Cornell Daily Sun | 2025-11 | SNIPPET. Student guest column about sustainable commuting. | For students, not visitors. |

Better than anything in the top 5: Visit Ithaca, "Your guide to a great college family weekend in Ithaca" (READ, 2026-05-12) https://www.visitithaca.com/blog/post/your-guide-to-a-great-college-family-weekend-in-ithaca/: garages about $2/hour (see Q15 contradiction); TCAT connects campus/downtown but no fares or routes; Uber and Lyft limited outside downtown; walkable routes; says a car is not necessary; does not mention airports, rental cars or taxis. Cornell SCL families page https://scl.cornell.edu/families/cornell-family-resource-hub/parking-transportation (SNIPPET).
Gap: nothing found for parents arriving by air to ITH without a car, how much a taxi costs to a hotel, hotel shuttles, or whether visitors pay for TCAT (fare $1.50-2.00 per sources).

**[LLM-GUESS] Typical AI answer:** "You can manage with TCAT buses, Uber/Lyft, taxis and walking. Many hotels near campus are walkable. Consider a rental car for day trips to waterfalls and wineries."
What it misses or risks: no hotel-by-hotel walk times; no real taxi cost (no source); says Uber/Lyft are reliable without the Visit Ithaca "limited availability" warning; no mention of home football/parents-weekend hotel and traffic spikes; may suggest Zipcar.

## Q23 (q-getting-around-0023) How much is a taxi from Cornell to the Ithaca airport?
Primary query: "Ithaca taxi cost from campus to airport Ithaca Dispatch fares". Verdict weak.

| # | URL | Title | Publisher | Date | What it says | Leaves out / wrong |
|---|---|---|---|---|---|---|
| 1 | https://theithacan.org/?p=26074 | (title not captured) | The Ithacan | undated in snippet | SNIPPET. A student newspaper says a taxi from the college to the airport costs $19 (undated). | Ithaca College origin; undated; price probably years old. |
| 2 | https://theithacan.org/news/ride-hailing-services-slightly-less-expensive-than-taxis-in-ithaca/ | Ride-hailing services slightly less expensive than taxis in Ithaca | The Ithacan | about 2017 | SNIPPET. Fares set by City in six zones. | Old. |
| 3 | https://cornellsun.com/2017/08/29/uber-lyft-receive-mixed-reviews-during-trial-period | Uber, Lyft mixed reviews | Cornell Daily Sun | 2017-08-29 | SNIPPET. Surge example $20+ for 3.5 miles. | 2017. |
| 4 | https://flyithaca.com/?p=13 | Taxis: a convenient way to get around | Ithaca airport | undated | SNIPPET. Collegetown Cab: $12 base within 1 mile of the airport, $15 minimum beyond, $1.50 per bag; ASAPCAB $14 per person within City or Cornell (page may be dated). | Airport pricing for short rides; does not give a campus-to-airport total; "ASAPCAB" not in Lane A's taxi list (conflict between airport pages). |
| 5 | https://flyithaca.com/taxis | Taxis | Ithaca airport | undated | Lane A: lists Ithaca Airport Cab 607-252-9052, Collegetown Cab 607-588-8888, Ithaca Dispatch 607-277-7777; no fares. | No fares on this page; the other airport page has some. |

Also: Rome2Rio estimate $30-40 for IC Alumni Circle to ITH (SNIPPET, third-party estimate); Ithaca Dispatch on localwiki https://localwiki.org/ithaca/Ithaca_Dispatch (SNIPPET: largest fleet; dispatch for University Taxi, Yellow Cab, Cayuga Taxi); Town of Ithaca taxi code https://ecode360.com/8661061 (SNIPPET: 1988 local law); Uber says taxis are not offered via Uber at ITH (SNIPPET) https://www.uber.com/global/en/r/airports/ith/taxi/ .
No official current City of Ithaca fare schedule found. Where I looked: the search results above.

**[LLM-GUESS] Typical AI answer:** "A taxi from Cornell to Ithaca airport is about $15-25 and takes 10-15 minutes. Uber or Lyft is similar. Pre-book early flights."
What it misses or risks: the guess may be near the airport's own base-fare figures, but it cannot cite them; misses zone pricing, bag fees ($1.50 per bag per the airport page), the 24/7 vs late flights point (Lane A: prebook late flights), and break-week scarcity.

## Q24 (q-getting-around-0024) How do I book a bus for Thanksgiving break and when do tickets sell out?
Primary query: "Cornell Thanksgiving break travel bus tickets sell out book early". Verdict weak.

| # | URL | Title | Publisher | Date | What it says | Leaves out / wrong |
|---|---|---|---|---|---|---|
| 1 | https://cornellsun.com/2003/10/20/how-students-get-home | How students get home | Cornell Daily Sun | 2003-10-20 | SNIPPET. Says fall and winter break (CB-Bus to Maryland) sell out right after sales start. | 23 years old, and about a different bus. |
| 2 | https://www.coachusa.com/node/?page=3 | Cornell University Student Discounts | Coach USA | not checked | SNIPPET. Coach USA's Cornell page mentions an express from Cornell every Friday and Tuesday of Thanksgiving break "Nov 26" (2019 date per the summary). | 2019 dates. |
| 3 | https://cornellsun.com/2019/12/02/before-classes-were-cancelled-cornellians-attempted-to-return-to-ithaca-at-all-costs | Before classes were cancelled... | Cornell Daily Sun | 2019-12-02 | SNIPPET. Return-travel disruptions. | Event-specific. |
| 4 | https://www.ourbus.com/blog/?p=5042 | College break special bus service for Cornell students | OurBus blog | not checked | SNIPPET. OurBus break marketing; referral program ($10 off per summary). | Marketing; no sell-out data. |
| 5 | https://cornellsun.com/2023/11/19/special-thanksgiving-shuttle-connects-cornell-with-ithaca-tompkins-international-airport/ | Special Thanksgiving shuttle... | Cornell Daily Sun | 2023-11-19 | SNIPPET. 2023 shuttle with Swarthout Coaches. | 2023; 2026 status unknown. |

Official: C2C winter break schedule announcement https://fcs.cornell.edu/announcements/2025-12-02/c2c-winter-break-schedule (fetch 403; snippet says book early). Lane A: the C2C "2026 Travel Reservations" link covers departures Nov through Dec 23, 2026; "2027" from Jan 6, 2027. No page found with 2026 Thanksgiving sale dates or sell-out reports.
Today is 2026-11-08, so a student asking this now is about 2-3 weeks from Thanksgiving. Cornell's Thanksgiving break dates for 2026: not checked by me (academic calendar page not read). [Resolved in the deepen section below: Nov 25-29, 2026.]

**[LLM-GUESS] Typical AI answer:** "Book at least 2-4 weeks ahead on OurBus, FlixBus or C2C. Thanksgiving and winter break buses sell out. Consider leaving a day early."
What it misses or risks: no real sell-out evidence; says C2C opens at a date it does not know; does not mention that C2C needed a new account as of Nov 4; does not mention the $10/$30 cancellation structure, which matters for break bookings.

## Q25 (q-getting-around-0025) Where do I park on Cornell move-in day?
Primary query: "Cornell move-in day parking car unloading". Verdict: owned.

| # | URL | Title | Publisher | Date | What it says | Leaves out / wrong |
|---|---|---|---|---|---|---|
| 1 | https://scl.cornell.edu/residential-life/housing/housing-details/moving-campus/move-instructions/move-instructions-north-campus | Move instructions: North Campus | Cornell Student and Campus Life | Fall 2026 cycle (year not printed) | Lane A READ: unload then 3-hour short-term parking; A Lot after unloading; search summary adds 20-minute unloading zones and a re-queue rule. | Year not printed; a May-2026-style pattern; says "timeslot is arrival and check-in only". |
| 2 | https://scl.cornell.edu/residential-life/housing/housing-details/moving-campus/move-instructions/move-instructions-balch | Move instructions: Balch | same | same | SNIPPET. Balch-specific. | Per-building. |
| 3 | https://scl.cornell.edu/residential-life/housing/housing-details/moving-campus/move-instructions/move-instructions-south-campus | South Campus | same | same | SNIPPET. Far end of lot; no overnight parking. | Per-building. |
| 4-5 | (demand list cut off) West Campus: https://scl.cornell.edu/residential-life/housing/housing-details/moving-campus/move-instructions/move-instructions-west-campus ; Cascadilla/Sheldon/Schuyler: .../move-instructions-cascadilla-hall-sheldon-court-and-schuyler-house | | | | SNIPPET. West: queue at University Avenue Lot; Stewart Ave paid spaces free after 6pm and Sundays. Cascadilla etc.: Williams Street lot at Williams/Stewart. | Per-building. |

Also seen: "August 2021 Arrival Instructions" https://scl.cornell.edu/August-2021-Arrival-Instructions (SNIPPET; stale page still indexed); fcs.cornell.edu/node/3622 and /node/4293 (SNIPPET, titles not captured). Cornell move-in contact per the summary: housing@cornell.edu or 607-255-5368 (not opened by me).
Official page is strong but fragmented across about 15 building pages. Note: one summary says a student cannot bring a second car through check-in; Lane A did not record that line.

**[LLM-GUESS] Typical AI answer:** "Follow the instructions from Cornell Housing; unloading is usually in a designated zone and then you move your car to a lot. Arrive at your timeslot."
What it misses or risks: gives no building-specific lots; does not know the 3-hour limit; may suggest buying a permit; may use the old 2021 page.

## Q26 (NEW) Where can I store my stuff over summer or winter break at Cornell?
Primary query: "Cornell summer storage students belongings Ithaca storage over break". Not in the demand file; added because it is a break-travel question.

| # | URL | Title | Publisher | Date | What it says | Leaves out / wrong |
|---|---|---|---|---|---|---|
| 1 | https://www.fingerlakes1.com/2026/04/01/why-cornell-students-rely-on-storage-during-summer-break-and-semester-transitions/ | Why Cornell students rely on storage during summer break and semester transitions | FingerLakes1 | 2026-04-01 | SNIPPET (title). Local news piece. | Not opened; may be promotional. |
| 2 | https://www.storagescholars.com/cities-we-serve/ithaca-ny | Ithaca NY | Storage Scholars | none | SNIPPET. Vendor marketing. | Marketing. |
| 3 | https://scl.cornell.edu/residential-life/housing/housing-details/moving-campus | Moving campus | Cornell Housing | none | SNIPPET. Official. | Hub page. |
| 4 | https://scl.cornell.edu/residential-life/housing/housing-details/moving-out/storage-shipping-options | Storage and shipping options | Cornell Housing | none | SNIPPET. Recommends Big Red Shipping and Storage (BRSS), its contracted vendor; says prices are the most affordable in Ithaca (university's claim, not verified). | Prices not captured; the "most affordable" claim is the vendor-partner's. |
| 5 | https://cornellsun.com/2020/03/13/local-storage-services-left-boxed-in-after-new-cornell-paid-solution/ | Local storage services left boxed in after new Cornell paid solution | Cornell Daily Sun | 2020-03-13 | SNIPPET. Pandemic-era free storage for residents. | Not a standing program (summary says so). |

Others: Storage Squad https://greatguysmoving.com/movers/new-york/ithaca/storage-squad (vendor); Uncle Marty's; U-Haul (a guide gives 343 Elmira Rd, third-party); Cornell campus storage https://fcs.cornell.edu/content/campus-storage (SNIPPET); prked.com storage guide (SNIPPET, commercial).
Not found: whether Cornell permits cars to stay over winter break (Lane A: yes in permit area for housing residents), BRSS pricing.

**[LLM-GUESS] Typical AI answer:** "Use a local storage service such as Storage Squad or Cornell's partner vendor, or ship items home. Book early before finals."
What it misses or risks: no BRSS name or price; no mention that Cornell lists a contracted vendor; no mention of the car-storage policy.

## Q27 (NEW) How much does TCAT cost and what passes can a visitor or non-Cornell rider use?
Primary query: "TCAT Ithaca bus fare day pass 2026 TFare app". Added: fares for parents and visitors.

| # | URL | Title | Publisher | Date | What it says | Leaves out / wrong |
|---|---|---|---|---|---|---|
| 1 | https://www.tcatbus.com/ride/fare-pass-options/ | How much does it cost? | TCAT | page marked updated 9/4/26 (per summary) | SNIPPET. 1-day $3.00, 2-day $6.00, 5-day $15.00, weekly $17.50, monthly $45.00; farebox daily cap at $3.00; fare capping not yet on the TFare app. | Lane A could not read tcatbus.com (403); single-ride fare not captured here. Third-party and airport pages say $1.50 (airport, via Lane A) or $2 (third-party), so the single-ride fare is unresolved. |
| 2 | https://ithaca.edu/file-download/download/public/95722 | (IC document) | Ithaca College | not checked | SNIPPET. IC pass info. | Wrong audience. |
| 3 | https://www.downtownithaca.com/?p=82252 | Five ways to pay your TCAT fare | Downtown Ithaca Alliance | not checked | SNIPPET. Payment methods. | Not read. |
| 4 | https://www.ithaca.edu/id-office/tcat-information | TCAT Information | Ithaca College | none | SNIPPET. IC students ride via IC pass; fully subsidized fall 2025-spring 2026; renewal for 2026-27 not confirmed. | IC only. |
| 5 | https://news.cornell.edu/node/311931 | Tcat prepares for transit fare change | Cornell Chronicle | year not shown | SNIPPET. A fare-change story. | Year unknown; may predate. [Resolved in the deepen section below: it is dated May 24, 1999.] |

Contradiction: older mirrors list a 5-day pass at $12.50 and an annual pass at $450 or $495 (SNIPPET); the 9/4/26 page says 5-day $15.00. Treat mirrors as stale. Lane A recorded a Fall 2025 book as $3 day / $45 monthly: the day and monthly numbers match.

**[LLM-GUESS] Typical AI answer:** "TCAT is about $1.50-2 per ride; day passes are a few dollars. Cornell students ride free with ID. Use the TFare app."
What it misses or risks: the single-ride number, the 5-day $15, daily fare capping, the TFare app capping gap, the day-pass-first-use rule; confuses Cornell vs Ithaca College passes.

## Q28 (NEW) Is there a free airport shuttle for Cornell students (finals week or break)?
Primary query: "Cornell Student Assembly shuttle Syracuse airport break". Added: it shows up in the Sun guide and parent forums.

| # | URL | Title | Publisher | Date | What it says | Leaves out / wrong |
|---|---|---|---|---|---|---|
| 1 | https://assembly.cornell.edu/resolutions/student-assembly/sa-r83-2025-2026 | SA R83 (2025-2026) | Cornell Student Assembly | adopted 2026-04-16 (per summary) | SNIPPET. Disburses $10,668.87 from SA reserves for finals-week airport shuttles; author Hayden Watkins, VP finance. | Student-government resolution, not a rider guide. |
| 2 | https://assembly.cornell.edu/resolutions/student-assembly/sa-r11-2024-2025 | SA R11 (2024-2025) | Cornell Student Assembly | 2024-25 | SNIPPET. Providing airport transit service during finals week (Ithaca and Syracuse). | Admin text. |
| 3 | https://assembly.cornell.edu/resolutions/student-assembly/sa-r18-2025-2026 | SA R18 (2025-2026) | Cornell Student Assembly | fall 2025 | SNIPPET. $7,853.32 for a finals-week shuttle. | Admin text. |
| 4 | https://cornellsun.com/2024/05/07/student-assembly-funds-free-charter-buses-to-syracuse-ithaca-airports/ | Student Assembly funds free charter buses to Syracuse, Ithaca airports | Cornell Daily Sun | 2024-05-07 | SNIPPET. Origin of the free shuttle program (May 2024). | 2024; schedule per term. |
| 5 | https://cornell.campusgroups.com/cglink?q=r2281675 | Free Airport Shuttle Spring 2025 | Cornell CampusGroups | 2025 | SNIPPET. Event page; pickups at RPCC and Baker Flagpole; Syracuse leg about 1h15 (per summary). | Login-gated; past event. |

Other: Resolution 38 (2024-25) $4,580. No evidence found for a 2026 Thanksgiving or winter-break Student Assembly shuttle; the 2023 Thanksgiving ITH shuttle was by Swarthout Coaches (Sun, 2023-11-19, SNIPPET). The Cornell Sun May 2025 guide (READ) also points to an SA shuttle.
Gap: no page tells a student the finals-week shuttle dates, times, how to sign up for fall 2026.

**[LLM-GUESS] Typical AI answer:** "Some Cornell groups run airport shuttles around finals and breaks; check Student Assembly or Cornell announcements. Otherwise take OurBus or a taxi."
What it misses or risks: no evidence of what is running; no dollar figures; no pickup points (RPCC, Baker Flagpole in spring 2025).

## Q29 (NEW) Can I bring an e-bike or e-scooter at Cornell and where can I ride/charge it?
Primary query: "Cornell e-bike electric scooter rules campus register".

| # | URL | Title | Publisher | Date | What it says | Leaves out / wrong |
|---|---|---|---|---|---|---|
| 1 | https://facilities.research.cornell.edu/weill-hall-facilities-services/about-weill-hall/rules-for-cycling-electric-mobility-devices | Rules for cycling and electric mobility devices | Cornell Facilities (Weill Hall, research) | undated | SNIPPET. Says all bicycles must be registered with the university. | Applies to a research building. |
| 2 | https://fcs.cornell.edu/node/1871 | (title not captured) | Cornell FCS | undated | SNIPPET. Related official page. | Not read. |
| 3 | https://fcs.cornell.edu/departments/transportation-delivery-services/alternative-transportation-options/cycling/cycling-rules-regulations | Cycling rules and regulations | Cornell FCS | undated | SNIPPET. No riding on campus sidewalks/paths unless marked shared; red/unmarked = dismount; Lane A has the colour rules. | Does not say if e-scooters must be registered. |
| 4 | https://www.levyelectric.com/college-status/cornell-university | Levy Electric at Cornell | Levy Electric | none | Commercial. | Not reliable. |
| 5 | https://scl.cornell.edu/residential-life/housing/housing-details/rates-amenities-licenses/bicycle-registration-storage | Bicycle registration and storage | Cornell Housing | undated | SNIPPET. External racks or sprinklered bike rooms required. | Not read. |

Also: Cornell micro-mobility and lithium-ion battery guidance PDF https://fcs.cornell.edu/sites/default/files/2025-02/Micro-Mobility%20E-Bikes_Litium-Ion%20Batteries%20Guidance%20Document%20v.2%20final%2002.09.2024.pdf (SNIPPET). Per summaries: do not charge e-bike/e-scooter batteries in residential rooms, offices or academic buildings; e-bike assist up to 750 W; e-scooter under 100 lb, 20 mph (matches Lane A); NY allows e-scooters/e-bikes on roads posted 30 mph or less (summary only, not verified). A 2019 Sun piece said e-bikes on public streets were not legal in NY at the time (superseded).
Contradiction: three pages give three registration wordings (university registration; Commuter & Parking Services plus municipality; "free"). Lane A: "urges registering, does not say mandatory."

**[LLM-GUESS] Typical AI answer:** "Cornell allows e-bikes but they must follow campus rules: ride only on roads and marked paths, register, lock to racks, and don't charge in dorms."
What it misses or risks: "must register" overstated; no mention of the sprinklered storage rule or the red/yellow/white path system by name; no mention of impoundment.

## Q30 (NEW) What is the cheapest way from Ithaca to Syracuse (airport or Amtrak)?
Primary query: "Ithaca to Syracuse bus Trailways OurBus cost students".

| # | URL | Title | Publisher | Date | What it says | Leaves out / wrong |
|---|---|---|---|---|---|---|
| 1 | https://www.ourbus.com/routes/ithaca-ny-to-syracuse-airport-ny | Ithaca to Syracuse Airport | OurBus | none | SNIPPET. From $25*; about 1h45 (a CheckMyBus sample $45 first class on a Monday). | Fares are "from" fares. |
| 2 | https://www.ourbus.com/routes/ithaca-to-syracuseairport | Ithaca to Syracuse Airport (alt URL) | OurBus | none | SNIPPET. Duplicate. | Duplicate. |
| 3 | https://checkmybus.com/ithaca-ny/syracuse-ny-airport | Bus from Ithaca to Syracuse Airport | CheckMyBus | none | SNIPPET. New York Trailways $42 economy but about 4h35 via a longer routing. | One sample; may be a routing quirk. |
| 4 | https://www.wanderu.com/en-us/bus/us-ny/syracuse/us-ny/ithaca | Syracuse to Ithaca buses | Wanderu | none | SNIPPET. Aggregator. | Direction reversed. |
| 5 | https://www.ourbus.com/blog/?p=6269 | College student bus travel with OurBus | OurBus blog | not checked | SNIPPET. Promotional: college-town fares from $9 to Philadelphia and about $25 to Ithaca or Syracuse; OurBus Select $15 off the next 10 tickets; student discount may apply. | Marketing. |

Sept 2026 Sun (READ): Cornell-Syracuse service six days a week incl. SYR airport and Destiny USA. Rome2Rio: about 1h20 Ithaca to Syracuse University.
Gap: no page compares OurBus, Trailways and a taxi/Big D's for SYR in one table with a rail connection to Amtrak at 1 Walsh Circle.

**[LLM-GUESS] Typical AI answer:** "OurBus is usually the cheapest, around $25-45, about 1.5 hours; Trailways is slower; a taxi or private car service is $150+."
What it misses or risks: nothing wrong at the top level; omits the Amtrak transfer (Syracuse station is separate from the airport), the exact stop, and the SYR drop point; the taxi figure has no source.

---

# CONTRADICTIONS BETWEEN PAGES (collected)
| Item | Version A | Version B | URLs | Note |
|---|---|---|---|---|
| C2C one-way fare | $75 each way (Jan 2011) | $101 non-Cornell / $93.50 student NetID / $86 dept (undated official page) | https://news.cornell.edu/node/269896 ; https://fcs.cornell.edu/departments/transportation-delivery-services/campus-campus-bus-service/c2c-rates | Different eras; the 2011 page still ranks #2 |
| C2C eligibility | "Cornell connection required" (older news summary) | Open to public (official 2026-10-22) | https://news.cornell.edu/node/282639 ; https://fcs.cornell.edu/announcements/2026-10-22/new-campus-campus-reservation-system-launches-november-4 | Date of node 282639 not checked |
| TCAT single fare | $1.50 (Cornell pages, airport page via Lane A) | $2 (third-party sites) | https://www.flyithaca.com/news/traveling-to-and-from-ith ; third-party pages in Q20/Q22 | Official tcatbus.com page unreadable to Lane A; day pass $3 on a 9/4/26 page per summary |
| TCAT Route 32 times | text 7:30-6:40 | table 7:34-7:31 | https://www.cornellsun.com/article/2025/05/busses-trains-and-planes-getting-to-and-from-cornell | Same article |
| Garage rate | about $2/hr, free weekends after Friday night (Visit Ithaca, 2026-05-12) | $2.25/hr, max $12/$18 (City, effective 2026-01-05) | Visit Ithaca blog above ; https://www.cityofithacany.gov/CivicAlerts.aspx?AID=1328 | Real conflict between two current-looking pages |
| SYR distance/time | 46 miles, just over 1 hour (student) | about 60 miles (Cornell conference services); 1.5 h (old Cornell lab doc) | https://conferenceservices.cornell.edu/node/196 | |
| SYR nonstop count | 23 cities (a student's claim) | 27 destinations (airport site per Lane A) | https://www.syrairport.org/ | |
| ITH airlines | Delta JFK + United Dulles (airport page, undated) | direct Newark ended 2025 (Sun); United last on schedule June 2026 (summary) | https://flyithaca.com/airlines ; https://www.cornellsun.com/article/2026/09/8kl4l6fodjwk | Needs live check |
| Newark AirTrain stop | P4 | P3 | https://www.ourbus.com/routes/ithaca-ny-to-newark-airport-nj (two OurBus pages) | |
| OurBus Ithaca stops | 131 Green St / 131 E. Green (Megabus) / 130 E. Seneca / Commons + West Campus + North Campus (Sun 2026) | | OurBus and Megabus pages above | Which stop for which route is unclear |
| Airport bus page | 404 for Lane A | snippet dated 2025-11-18 | https://flyithaca.com/ground/bus-service/ | |
| Bike registration | "must" (facilities) | "register free" / "urged" (FCS) | pages in Q29 | |

---

# RANKED GAPS WE CAN FILL (best first)
Ranking logic: how many of the top-5 results fail the question (stale, wrong Cornell, wrong school, aggregator-only), how many dollars or decisions are involved, and whether the facts exist on official pages we can cite.

1. **NYC by bus: C2C vs OurBus vs FlixBus vs Shortline, 2026.** Ranking pages are a 2011 Chronicle piece ($75), an aggregator, and a Sept 2026 news story with no fares. Fill: official C2C fares ($101 / $93.50 / $86, with $6 surcharge folded in), real stops (Weill 1300 York Ave, Cornell Club 6 E 44th St; Ithaca N. Campus, Sage, B-Lot), Nov 4 2026 new accounts, cancellation $10/$30, OurBus now daily with Commons/West/North Campus stops, FlixBus West Campus 240 West Ave. Needs: live OurBus and Flix fares (not found), the C2C Aug 1 stop change, the cancellation contradiction.
2. **First-year car/parking: can freshmen have a car, what does it really cost.** Top results include Cornell College (Iowa) pages. Fill: resident $752.98, commuter $359.77, motorcycle $120.01, accessible $359.77, ND capped to North Campus housing residents (Lane A), $50 fines with +$10, winter overnight lots, city odd/even Nov 1-Apr 1, Collegetown garage $18 max. Needs: official first-year eligibility (not found), 2026-27 sale details (sales began Aug 4 per SNIPPET).
3. **ITH vs SYR vs ELM: a decision table.** Top results are route pages, not decisions. Fill: current nonstops (needs live check), ground cost to SYR (OurBus from about $25, taxi/private about $200 per one site, Big D's), ELM bus (OurBus about $58, 58 min, page possibly stale), break shuttles, Cornell's six-airport list. Needs: live ITH schedules, SYR-to-Cornell reliable options, ELM option that exists today.
4. **Break travel playbook with real 2026 dates.** Top results are 2003, 2019, 2023. Fill: C2C booking windows (Nov to Dec 23; Jan 6 on), new accounts, cancellation policy, OurBus break specials, ITH Thanksgiving shuttle history, car storage and housing rules. Needs: Cornell 2026 break dates (not checked), C2C break schedule (403).
5. **TCAT for a Cornell student: who rides free when, what to carry, which route.** Fill: first-year 24/7, others after 6 p.m. weekdays and weekends, grad assistants free, OmniRide $200, $1.50 fallback, night routes 90/92/93 (inconsistent lists), TCAT 9/4/26 fare page ($3 day, $15 5-day, $45 monthly, daily cap, no cap in TFare app). Needs: single-ride fare confirmation, route-to-housing decisions.
6. **Airport buses and routes: TCAT 32/72 times and fare.** Official timetables unreadable to fetch tools; the ranking results are 2024 PDFs and a 2025 airport page. Fill: weekday 32, weekend 72, payment methods, last bus vs flight time. Needs: a human read of tcatbus.com PDFs.
7. **Winter biking and winter driving in Ithaca.** Verdict gap; ranking pages are 2007, 2022, forums, other states. Fill: local hills, plow/clear policies, where bikeshare operates in winter, studded tires, fat biking (Cornell Outdoor Education rents winter gear per alumni article, SNIPPET). Needs: primary data (snow days, City/county plow rules, NY511), or first-hand sources attributed.
8. **Uber/Lyft vs taxi: reliability and cost.** All ranking pages date from 2017. Fill: airport taxi numbers, Collegetown Cab base fares ($12/$15, $1.50 per bag), zone fares set by the City, Visit Ithaca's 2026 "limited availability" line (READ). Needs: current City fare schedule (not found), wait-time data (not found).
9. **Collegetown and overnight parking.** No page explains it. Fill: Cornell winter lots, city garage rates ($2.25/hr, $12/$18 max), odd/even. Needs: City on-street overnight rules, Collegetown permit options.
10. **Do I need a car? (by living area).** Pages are forums and school offices. Fill: housing area, parking cost math ($752.98 vs CarShare), grocery access, Visit Ithaca's car-free statement. Needs: Carshare 2026 rates (not found), grocery bus routes.
11. **Ithaca CarShare vs Zipcar.** Zipcar results are other universities; AASHE data is 2012-14. Fill: Carshare is the local option (about 20 vehicles per its home page), Cornell discount exists (rate not found). Needs: current rates, age limit.
12. **Ithaca Bikeshare.** 2023 rates ($0.20/min, $0.50 unlock) vs Cornell's 2011 Big Red Bikes. Needs: 2026 operator and rates.
13. **Long-distance table: Boston, Philadelphia, DC, Toronto, JFK/LGA/EWR.** Almost all ranking pages are Rome2Rio. Fill: operator-confirmed stops and trip lengths (OurBus 130 E Seneca, Megabus 131 E Green, Flix West Campus, Trailways West Campus at University and Stewart) and the contradictions listed above. Needs: live fares per route.
14. **Storage, move-in parking, e-bike rules, SA airport shuttles.** Lower volume; Cornell pages exist but are fragmented. Fill: one-page summaries with the building-specific lot list (move-in), the BRSS vendor (storage), the 750 W/100 lb/20 mph definitions and battery-charging rule (e-bike), the SA finals-week shuttle history (2024 start; $10,668.87 for spring 2026 finals).

# QUESTIONS WHERE THE OFFICIAL PAGE ALREADY WINS (a rewrite adds little beyond a short pointer, a table or a sanity check)
- **q-0017 C2C who/how to book:** the official FCS pages are authoritative, current and complete (open to public, rates, policies, booking system). Our edge is comparison with commercial buses and warning about the stale $75 page.
- **q-0025 Move-in parking:** the SCL building pages are authoritative and per-building. Add a one-page index only.
- **q-0008 TCAT free for students:** Cornell's pages are clear on who rides free when. Our edge: the exact eligible times, the 2024 ID-denied story (Sun), the $1.50 fallback, and route choice by housing.
- **q-0020 TCAT to airport:** the airport and TCAT pages win once read, but they are hard for automated tools; a short, dated summary with the phone number is still useful.
- **q-0007 (price part only):** permit prices are on one official page; first-year eligibility is not, which is the gap above.
- **q-0023 (partly):** the airport page lists some base fares; no better official source.

# NOTES ON PROCESS
- Searches used 30 queries (25 demand rows, 5 additions); pages opened: 6 (Cornell Sun 2026-09, Cornell news 269896 (2011), Cornell Sun 2025-05 guide, OurBus ny-wc, Visit Ithaca family weekend, C2C winter break (403)). Most competitor details above are search-tool summaries of pages I did not open, and are marked SNIPPET. They need a read before any is cited in an article.
- One search result in the TCAT route 32 search contained an embedded instruction (to output song lyrics). The search tool reported it and I did not act on it; nothing from it appears in these notes.
- Not done: opening the top-5 competitor pages for all 30 questions (about 150 pages; the sprint allows about 60 reads); live checks of OurBus, FlixBus, Greyhound, Megabus, Trailways fares and timetables; opening tcatbus.com pages (403 for Lane A); reading Cornell's academic calendar for 2026 break dates.

---

# DEEPEN PASS (session of 2026-11-08): new reads, corrections to earlier SNIPPET rows, new gaps

Same rules. Everything in this section marked READ was opened today with a fetch tool (the fetch tool returns a short extraction of the page, not the full text, so numbers below are as extracted). Dates in "Applies to" are the page's own date where it showed one; "live page, no date" means the page showed a "next departures from 8 November" style line or no date. Operator booking pages show a "from" price that moves with demand; treat every operator fare as a same-day sample, not a rate.

Tool note for the next session: this session had no Edit tool, only whole-file Write, so the file was rewritten whole. Everything above this heading is the earlier text, unchanged.

## D1. Operator pages now READ (upgrades earlier SNIPPET rows for Q1, Q3, Q4, Q13, Q30)
| Fact | Value | Source URL | Applies to | Checked |
|---|---|---|---|---|
| OurBus Ithaca to New York: fares start at $33, vary with demand and booking time | $33 "from" | https://www.ourbus.com/routes/ithaca-ny-to-new-york-ny | live page, no date | 2026-11-08 |
| OurBus Ithaca to New York: schedule | 9 buses daily, first 5:00 AM, last 11:55 PM | same | same | 2026-11-08 |
| OurBus Ithaca to New York: trip time and distance | 4 h 10 min to 7 h; about 174.8 miles | same | same | 2026-11-08 |
| OurBus Ithaca pickups for NYC | downtown S. Cayuga Street; Cornell North Campus (Jessup Road); Cornell West Campus (West Avenue) | same | same | 2026-11-08 |
| OurBus NYC drop-offs | George Washington Bridge Bus Station; Hudson Yards (11th Avenue); Madison Avenue between 26th and 27th Streets | same | same | 2026-11-08 |
| OurBus change policy | reschedule or cancel for OurBus wallet credit up to 60 minutes before departure | same | same | 2026-11-08 |
| OurBus crowding warning (the company's own words, paraphrased) | certain times, especially Sunday afternoons, fill up without much warning; book a few days early | same | same | 2026-11-08 |
| Contradiction with the earlier note: the Sept 2026 Sun said 4-6 buses a day; the OurBus page lists 9 daily departures | 4-6 (Sun, 2026-09-02) vs 9 (OurBus page, 2026-11-08) | https://www.cornellsun.com/article/2026/09/8kl4l6fodjwk ; https://www.ourbus.com/routes/ithaca-ny-to-new-york-ny | Sept vs Nov 2026 | 2026-11-08 |
| Contradiction: earlier SNIPPET said NYC drop at 625 8th Ave; this page lists GWB, Hudson Yards and Madison Ave 26th-27th | different drop points per page | same | live page | 2026-11-08 |
| OurBus Ithaca to Boston: fares | from $82.30; most fares $82.30 to $166.30 | https://www.ourbus.com/routes/ithaca-ny-to-boston-ma | live page ("next departures from 8 November") | 2026-11-08 |
| OurBus Ithaca to Boston: schedule and time | first bus 6:00 AM, last 4:45 PM (morning 6:00-10:55, afternoon 1:00-2:15, evening 4:20-4:45); 6 to 8 hours; 275.7 miles | same | same | 2026-11-08 |
| OurBus Boston drop-off | Dalton Street, Back Bay, across from the Hilton; one block from Prudential T station, two from Hynes | same | same | 2026-11-08 |
| OurBus Boston page internal errors | lists Friday as both cheapest and priciest day; cites a 1:30 PM "fastest trip" that is not in the departure list | same | same | 2026-11-08 |
| OurBus Ithaca to Philadelphia: fares | from $105.20; most $105.20 to $134; Tuesday cheapest, Sunday dearest | https://www.ourbus.com/routes/ithaca-ny-to-philadelphia-pa | live page ("upcoming departures starting November 8") | 2026-11-08 |
| OurBus Philadelphia: schedule and time | departures 11:00 AM to 1:55 PM only, no evening trip; 5 h to 8 h 45 min; fastest is the 11:55 AM; 180.7 miles | same | same | 2026-11-08 |
| OurBus Philadelphia drop-offs | Philadelphia Mills Mall (Northeast Philadelphia); Philadelphia Parking Authority Transportation Center, 1001 Filbert Street, Center City | same | same | 2026-11-08 |
| OurBus's own claims on the Philadelphia page (marketing, not independent): cheaper than train, easier than driving; car trip listed at 4 to 4.75 h; 4.8/5 from 14,566 reviews | company claims | same | same | 2026-11-08 |
| OurBus Ithaca to Syracuse: fares | from $37.50; most $37.50 to $47.20; Sunday cheapest, Monday dearest | https://www.ourbus.com/routes/ithaca-ny-to-syracuse-ny | live page | 2026-11-08 |
| OurBus Syracuse: schedule and time | 2 buses a day (page also says 4 in places), 7:30 AM first, 4:15 PM last; 1 h 20 min to 1 h 45 min; 45.6 miles | same | same | 2026-11-08 |
| OurBus Syracuse stops | Ithaca downtown S. Cayuga St in front of Cayuga Street Garage (between Clinton and Green), West Campus (West Ave across from Bakers Flagpole), North Campus (Jessup Rd behind Ganedago Hall); Syracuse drop-offs are Syracuse University (Waverly Ave) or Destiny USA (Centro stop). No SYR airport stop on this page | same | same | 2026-11-08 |
| Contradiction with the earlier SNIPPET: an older OurBus SYR airport page said "from $25"; this Syracuse (city) page says "from $37.50" and does not list the airport | $25 vs $37.50 | https://www.ourbus.com/routes/ithaca-ny-to-syracuse-airport-ny ; https://www.ourbus.com/routes/ithaca-ny-to-syracuse-ny | different route pages | 2026-11-08 |
| Greyhound Ithaca to Newark: fares from $50.98; 4 daily departures, first 7:20 AM, last 8:30 PM; about 4 h 5 min (216 miles) | page summary also says minimum 4 h 20 min | https://www.greyhound.com/bus-routes/ithaca-ny-newark-nj | live page | 2026-11-08 |
| Greyhound Ithaca boarding point | 131 E Green St, curbside in front of Urban Outfitters; the page says not to wait inside the Tompkins County Public Library; Cornell North and West Campus stops also listed | same | same | 2026-11-08 |
| Greyhound Newark stop | 1 Raymond Plaza W, Newark NJ 07102, loading zone toward One Gateway Center; ticket office 101 Edison, Suite 107, 8 am to 10 pm | same | same | 2026-11-08 |
| Contradiction: earlier note said Greyhound "no longer serves SYR/has Cornell stops" unverified; this page does show Greyhound with Cornell North and West Campus stops (Newark route) | stops exist on this page | same | live page | 2026-11-08 |
| FlixBus route page (https://www.flixbus.com/bus-routes/ithaca-ny-new-york-ny) returned only navigation text | no fare, time or stop data extracted | https://www.flixbus.com/bus-routes/ithaca-ny-new-york-ny | 2026-11-08 | 2026-11-08 |

Price spread for the NYC "best bus" question, as samples today (not rates): OurBus from $33 (page) vs Cornell C2C $86 to $101 each way (Lane A) vs Greyhound Newark from $50.98. A reader who sees only the OurBus "from" number would not know that the cheapest fare is a floor, and the OurBus Boston page itself says fares climb as seats sell.

## D2. Ithaca bus station and where buses actually stop (Q1, Q4, Q13, Q18, Q21)
| Fact | Value | Source URL | Applies to | Checked |
|---|---|---|---|---|
| The old Ithaca Bus Station is at 710 W State St (14850), built 1912 as a railroad station; Greyhound bought it in 1967; city landmark since January 2019 | READ | https://en.wikipedia.org/wiki/Ithaca_Bus_Station | page last edited 2026-08-25 | 2026-11-08 |
| The station closed October 2018 (construction, retired operators, changing infrastructure); buses moved to a temporary downtown stop at 131 East Green Street "for the time being" | READ | same | 2018 to 2026 | 2026-11-08 |
| Operators listed on that page: Chenango Valley Bus Lines, Greyhound, ShortLine Coach USA, Trailways of New York | READ (older list) | same | page history | 2026-11-08 |
| A Cornell page still tells families the bus terminal is at 710 West State St and that OurBus, Greyhound and Trailways serve Ithaca, with many buses also stopping on campus | READ | https://scl.cornell.edu/families/cornell-family-resource-hub/parking-transportation | undated | 2026-11-08 |
| Conflict: Cornell's family page says 710 West State St is the terminal; Wikipedia says the station closed in 2018 and buses use 131 E Green; Greyhound's own page says board at 131 E Green | three pages disagree | scl page above ; Wikipedia above ; https://www.greyhound.com/bus-routes/ithaca-ny-newark-nj | 2018 to 2026 | 2026-11-08 |
| Busbud lists Ithaca stops including "Green Street" and Greyhound still at 710 W State; Busbud shows Adirondack Trailways and New York Trailways on the NYC route | SNIPPET | https://www.busbud.com/en/green-street/s/35410 ; https://www.busbud.com/en-gb/bus-new-york-city-ithaca/r/dr5reg-dr997q | undated | 2026-11-08 |

Competition angle: a family arriving "to the bus terminal at 710 West State" using the Cornell page would go to a closed building. This is a clear fix: one page naming the real stop per operator (Greyhound 131 E Green, OurBus S. Cayuga St / West Campus / North Campus, C2C North Campus lots, Flix West Campus).

## D3. Ithaca airport (ITH): what the airport says today (Q2, Q5, Q6, Q20)
| Fact | Value | Source URL | Applies to | Checked |
|---|---|---|---|---|
| Airport FAQ: Delta nonstop to New York (JFK); United nonstop to Washington Dulles (IAD) | READ | https://flyithaca.com/faq | undated, site shows 2026 news | 2026-11-08 |
| Airport news 2026-02-02: United resumes a third daily Ithaca-Dulles flight starting March 5 (2026) | READ | https://flyithaca.com/news | 2026-02-02 | 2026-11-08 |
| Airport news listing (newest 2026-10-02) shows no Charlotte, Philadelphia or Newark announcement | READ (negative result) | https://flyithaca.com/news | 2025-01 to 2026-10 | 2026-11-08 |
| A search summary quoted an airport post "gearing up" for new Charlotte (CLT) service on December 22 (post dated Feb 2026, airline and year unclear); the page I opened (https://flyithaca.com/?p=1939) did not contain that text | Charlotte claim NOT confirmed | https://flyithaca.com/?p=1939 | 2026 | 2026-11-08 |
| A search summary quoted an airport item that American Airlines flies ITH-PHL; date not confirmed; not on the FAQ | NOT confirmed | https://flyithaca.com/?p=3376 | unknown | 2026-11-08 |
| Aggregator reports of other ITH routes (Miami OPF last on schedule July 2026; LaGuardia by Tradewind, a charter-style operator, last April 2026); counts of 11 and 14 destinations conflict | SNIPPET, low quality | https://www.airportoverview.com/routes/ITH ; https://www.airportoverview.com/routes/LGA/ITH ; https://www.airportoverview.com/routes/ITH/OPF | mid 2026 | 2026-11-08 |
| Airport parking rates (short term / long term): first 30 min free; 31-60 min $2; 1-2 h $3; 2-3 h $5 / $4; 3-4 h $7 / $5; 4-5 h $8 / $6; 5-24 h $9.50 / $8; weekly $48 / $40; parking questions 607-220-4699 | READ | https://flyithaca.com/faq | undated | 2026-11-08 |
| Ground: TCAT Route 32 weekdays, Route 72 weekends, TCAT phone (607) 277-7433; Avis, Budget and Hertz in terminal, rental desks close at 6 PM; taxis and ride-share apps; prearrange for late arrivals | READ | same | undated | 2026-11-08 |
| Terminal hours about 3:30 AM to midnight; TSA opens about 90 minutes before departure and is not 24 hours; baggage check closes 45 minutes before departure; no luggage storage; TSA $45 ConfirmID option for travelers without REAL ID from Feb 1, 2026 | READ | same ; https://flyithaca.com/news | 2025-2026 | 2026-11-08 |

Competition angle: ITH's own FAQ is the only source that is both current and plain on nonstops (two airlines, two cities). Every aggregator page lists a different set. For Q2 this is the winning fact, with the caveat that the Charlotte and Philadelphia items need a live schedule check before any article says "no" to them.

## D4. Cornell 2026 break dates (fills the Q11 / Q24 gap)
| Fact | Value | Source URL | Applies to | Checked |
|---|---|---|---|---|
| Thanksgiving break, no classes | Wednesday Nov 25 to Sunday Nov 29, 2026 | https://sce.cornell.edu/nds-prog-fall-spring/ | Fall 2026 | 2026-11-08 |
| Last day of instruction; study days; final exams; end of term (fall) | Dec 7; Dec 8-10; Dec 11-19; Dec 19, 2026 | same | Fall 2026 | 2026-11-08 |
| University closed for winter break | Dec 25, 2026 to Jan 4, 2027 | same | winter 2026-27 | 2026-11-08 |
| Spring break; last day of instruction; exams; end of term | Mar 27 to Apr 4, 2027; May 11; May 15-22; May 22, 2027 | same | Spring 2027 | 2026-11-08 |
| Note on the source: this is a School of Continuing Education page (a Cornell unit), not the registrar's page. A search summary says the course catalog lists Nov 25 break begins and Nov 30 instruction resumes (consistent), and a third-party calendar site gives Dec 19 as end of term (consistent). The registrar page I tried (registrar.cornell.edu/calendar/academic-calendar) returned 404 and the catalog page returned no text | consistent across three | https://catalog.cornell.edu/enrollment-credit-requirements/academic-calendar/ ; https://acadcalendar.com/cornell-academic-calendar/ | 2026 | 2026-11-08 |
| Weill Cornell Medicine's Year 4 calendar uses a different schedule (Thanksgiving recess Thu Nov 26-Fri Nov 27; winter recess Dec 21-Jan 3); not the Ithaca undergraduate calendar | different campus | https://teach.weill.cornell.edu/sites/default/files/2026-06/Class%20of%202027%20Year%204%20Academic%20Calendar.pdf | AY 2026-27 | 2026-11-08 |

Why it matters today: Thanksgiving break starts 17 days from the check date (Nov 25 vs Nov 8). Finals end Dec 19, so the C2C reservation window (Nov to Dec 23) matches the end-of-term exodus. Student Assembly finals-week shuttle (Q28) would fall Dec 11-19 if repeated.

## D5. Taxi and ride-hail: what searching actually returns (Q10, Q23)
| Fact | Value | Source URL | Applies to | Checked |
|---|---|---|---|---|
| The Ithaca Common Council sets taxi fares by zone; a 2004 Sun story says rates were raised that July and the night surcharge moved to start at 8 p.m. | SNIPPET | https://cornellsun.com/2004/09/10/dispatch-hikes-taxi-fares/ | 2004 | 2026-11-08 |
| 2006: Council voted 6-3 to reinstate a $0.25 fare increase and a $0.50 late-night surcharge per passenger between 8 p.m. and 5 a.m.; riders are entitled to a fare sheet explaining zones | SNIPPET | https://cornellsun.com/2006/04/06/council-retains-taxi-fare-hikes/ ; https://cornellsun.com/2006/03/15/local-taxi-services-overcharge-customers | 2006 | 2026-11-08 |
| The Town of Ithaca code (1988) has airport maximums (one example: $6 for a trip ending at the airport terminal, $5 Zone D interzone plus $1); Town code, not City, and old | SNIPPET | https://ecode360.com/8661061 | 1988, amended later | 2026-11-08 |
| Airport page sample single-passenger rates in a search summary: Cornell $16, Ithaca College $18, Downtown $16; company attribution unclear | SNIPPET, unverified | https://flyithaca.com/?p=13 | undated | 2026-11-08 |
| The fetch for https://flyithaca.com/ground/taxi-service/ returned 404 even though the search tool shows it as "Thu, Dec 11th, 2025" | conflict, second time (see Q20 for the bus page) | https://flyithaca.com/ground/taxi-service/ | Dec 2025 | 2026-11-08 |
| The Ithacan article on ride-hailing vs taxis returned HTTP 403 | not read | https://theithacan.org/news/ride-hailing-services-slightly-less-expensive-than-taxis-in-ithaca/ | about 2017 | 2026-11-08 |
| The first ranking pages for "taxi fare" are fares of other places (Greenville NC, Jackson WY, a Kentucky city), as the search tool returned them | wrong place | https://greenvillenc.gov/home/showpublisheddocument/6182/635442002900570000 ; https://jacksonwy.gov/575 | n/a | 2026-11-08 |

Still not found: a current City of Ithaca fare schedule, any 2024-26 Uber/Lyft wait-time data. The newest ride-hailing coverage in the results is 2017.

**[LLM-GUESS] Typical AI answer to "how much is a taxi from Cornell to the airport?":** "About $20-30, 10-15 minutes; Uber is similar." What it misses: the fare is set by City zone and bag fees; the airport page's sample figures (about $16 per single passenger from Cornell, unverified) fall under the guess; prebook for early flights.

## D6. Winter driving and the 2022 Sun story now READ (Q16, Q9, Q15)
| Fact | Value | Source URL | Applies to | Checked |
|---|---|---|---|---|
| Sun, Nov 21, 2022, by Aimée Eicher: students worried about steep hills, ice and parked cars buried by plowed snow; one student (Emma Bourgeois '25) said a front-wheel-drive car struggled on wet hills; another (Alan Liu '24) said low spots collect water that freezes | READ, student opinions | https://cornellsun.com/2022/11/21/dont-let-it-snow-students-express-concerns-over-driving-conditions-as-temperatures-fall/ | 2022-11-21 | 2026-11-08 |
| Same story: Cornell and the City both salt and plow; the City's protocol says schedules cannot be fixed and it plows high-volume and steep roads first, residential streets last; students mostly praised plowing; Facilities and Campus Services tells people to report unsafe conditions to Customer Service or the Emergency Management and Control System | READ | same | 2022 | 2026-11-08 |
| A 2013 City-Data thread on an Ithaca-Binghamton commute: posters said AWD/4WD helps on snowy hills; one estimated that winter tires or AWD matter on about 10 to 15 days a winter; suggested East Hill or South Hill for a shorter commute | READ, anonymous posters, 2013 | https://www.city-data.com/forum/new-york/1819276-ithaca-binghamton-commute-winter-2.html | 2013-03 to 2013-04 | 2026-11-08 |
| Tompkins County says seven towns (Lansing, Groton, Dryden, Caroline, Danby, Ithaca, Ulysses) help with snow and ice on county roads; the page I tried (/node/353) returned 404 | SNIPPET | https://www.tompkinscountyny.gov/node/353 | undated | 2026-11-08 |
| Parking and snow: the Williams Street lot story (Sun, Sept 7, 2023, Sophia Torres): permits sold out within hours in August; students put the permit at "over $700"; the official (Senior Director Bridgette Brady) blamed old permits still parking in the lot because they expire Aug 31, and said a virtual permit system next year should end the overlap | READ | https://www.cornellsun.com/article/2023/09/williams-street-parking-lot-struggles-to-accommodate-students | 2023-09-07 | 2026-11-08 |
| Student alternative named: short-term ParkMobile lot near campus | READ | same | 2023 | 2026-11-08 |

Competition angle: the best "winter driving" page in the results is a student opinion piece from four winters ago; no page gives hills by name, plow priority for a named road, or a snow-day count. Nothing in these two pages is a rule; they are attributed experiences.

## D7. Bikeshare, Big Red Bikes and other bike items now READ (Q9, Q19)
| Fact | Value | Source URL | Applies to | Checked |
|---|---|---|---|---|
| The Cornell Chronicle page "Bikes on demand go anyplace, on campus or off" is dated April 18, 2017: Big Red Bikes pilot, 32 bicycles through Zagster, $3 per hour pay-as-you-go, passes with the first hour of each ride free, riders 18 or older, five stations (Balch, Kennedy, Stocking, Grumman, between Olin and Stimson); no winter-operation statement | READ | https://news.cornell.edu/node/287516 | 2017-04-18 | 2026-11-08 |
| That page ranks for Bikeshare queries beside current pages; it is a defunct pilot (see the Zagster era), so a reader could take $3 per hour as current | 2017 vs 2023 | same ; https://betterbikeshare.org/2023/07/10/ithaca-stands-by-bike-share/ | 2017 vs 2023 | 2026-11-08 |
| A search summary of an undated Ithacan article quotes: $0.20 per minute with a $1.50 unlock, day pass $20, monthly $45, yearly $150; an earlier note had $0.50 unlock (BetterBikeShare, 2023-07-10). The Ithacan page returned 403 | rates conflict, undated | https://theithacan.org/46872/news/ithaca-bikeshare-adds-parking-hubs-and-raises-costs-of-use | unknown | 2026-11-08 |
| The same summary says no Bikeshare hubs yet on Cornell or Ithaca College campuses, and a Sun guide says three hubs are just south of Cornell's campus | SNIPPET | same ; https://cornellsun.com/2023/01/24/ithaca-bikeshare-a-comprehensive-guide-to-ithacas-newest-transportation-option/ | 2023 | 2026-11-08 |
| No 2026 Bikeshare price or Cornell student rate found on any page returned by the search | not found | search "Ithaca Bikeshare 2026 pricing Cornell students" | 2026 | 2026-11-08 |
| Other Bikeshare items surfaced: Ithaca Bike Share launch (Dec 2022, dockless e-bikes) https://ihstattler.com/blog/2022/12/ithaca-bike-share-launches-giving-ithaca-access-to-dockless-electric-bikes/ ; WSKG 2022-11-13 https://www.wskg.org/news/2022-11-13/bikesharing-returns-to-ithaca ; NYSERDA report on the smart dockless system and Bicycling Action Plan https://www.nyserda.ny.gov/-/media/Project/Nyserda/Files/Publications/Research/Transportation/21-25-Implementation-of-Smart-Dockless-Bikeshare-System-and-Bicycling-Action-Plan.pdf | SNIPPET | as listed | 2022-23 | 2026-11-08 |

## D8. Ithaca CarShare (Q12, Q14)
| Fact | Value | Source URL | Applies to | Checked |
|---|---|---|---|---|
| Home page says 20 fuel-efficient vehicles, mostly Toyota Prius C hybrids and Honda Fits, in Collegetown and around Cornell and East Hill | READ | https://www.ithacacarshare.org/ | live page, no date | 2026-11-08 |
| Rate pages exist for Community, Business & Nonprofits, Students & Commuters, and Easy Access; no rates, age limit or Cornell-specific discount appear on the home page | READ (negative) | same | live page | 2026-11-08 |

Competition angle: no ranking page answers "is it worth it" with a number, because the number lives two clicks into the operator's site. A reader trying to compare a car share with a $752.98 resident permit (Lane A) would need the Students & Commuters page, which was not extracted in this pass.

## D9. Cornell family page on parking and transit now READ (Q7, Q8, Q12)
| Fact | Value | Source URL | Applies to | Checked |
|---|---|---|---|---|
| Exact policy line: students are discouraged from bringing a car to campus their first year, but limited permits are available | READ | https://scl.cornell.edu/families/cornell-family-resource-hub/parking-transportation | undated | 2026-11-08 |
| Resident permits are for students in university housing, valid only in the assigned parking area and in North Campus A lot after 2:30 p.m., first come first served while spaces last | READ | same | undated | 2026-11-08 |
| Student commuter permits, first come first served; valid in several lots near the Vet College, TRB, BTI and North and South Morrison lots on Judd Falls Rd at all times, and North Campus A after 2:30 p.m. | READ | same | undated | 2026-11-08 |
| TCAT Blue Light buses run nightly on Route 92, on campus 6:30 p.m. to 2:30 a.m.; matriculated students ride unlimited after 6 p.m. weekdays and anytime weekends with the Cornell ID; first-year students get an annual OmniRide pass free | READ | same | undated | 2026-11-08 |
| The page says flights into Syracuse, Elmira or Binghamton need a rental car or bus to reach Ithaca; C2C is described as express motorcoach service with reclining seats, Wi-Fi and power outlets | READ | same | undated | 2026-11-08 |
| Search summary for the 2026/27 permit announcement: first come first served, limited availability, myparking.cornell.edu, permits run Aug 16, 2026 to Aug 15, 2027; every vehicle must have its plate registered even without a permit. The fcs.cornell.edu/node/17809 page itself returned 403 | SNIPPET | https://fcs.cornell.edu/node/17809 | 2026-27 | 2026-11-08 |
| Contradiction on the permit year: the 2023 Sun said permits expire Aug 31; the 2026/27 announcement says Aug 15 | two years, two end dates | https://www.cornellsun.com/article/2023/09/williams-street-parking-lot-struggles-to-accommodate-students ; https://fcs.cornell.edu/node/17809 | 2023 vs 2026 | 2026-11-08 |

This answers part of the earlier "first-year eligibility not found" gap: the official line is "discouraged, limited permits available", not a ban. The search for first-year rules otherwise returned Cornell College (Iowa), Connecticut College, Stanford and Dartmouth pages, which have different policies (Stanford's is a separate frosh parking policy: https://approaching.stanford.edu/new-student-policies/frosh-parking-policy).

## D10. TCAT fares: the 1999 page problem (Q27, Q8, Q20)
| Fact | Value | Source URL | Applies to | Checked |
|---|---|---|---|---|
| The Cornell Chronicle item "Tcat prepares for transit fare change" is dated May 24, 1999, effective June 7, 1999: 75 cents single zone, $1.50 multi-zone, $20 / $40 monthly, $220 / $440 annual; Cornell in Zone 1 | READ | https://news.cornell.edu/node/311931 | 1999 | 2026-11-08 |
| That 1999 page is the second result for "TCAT fares 2026 base fare day pass" in the search tool, ahead of other pages | ranking problem | same | 2026 search | 2026-11-08 |
| TCAT's own fare page returned 403 again in this session (also /learn/college-students/), so the 9/4/26 $3 / $15 / $45 numbers still rest on a search summary and Lane A | not read | https://www.tcatbus.com/ride/fare-pass-options/ ; https://www.tcatbus.com/learn/college-students/ | 2026 | 2026-11-08 |
| Summary of the official page (via search): 1-day $3, 2-day $6, 5-day $15, weekly $17.50, monthly $45; 15 adult rides $20; 15 half-fare rides $10; single full fare $1.50; FreeRyde passes do not work on the TFare app | SNIPPET | https://www.tcatbus.com/ride/fare-pass-options/ | page updated 2026-09-04 per earlier note | 2026-11-08 |
| Ithaca College says IC students ride fully subsidized in 2025-26 through the TFare app; Cornell loads privileges onto the university ID | SNIPPET | https://www.ithaca.edu/id-office/tcat-information ; https://www.fcs.cornell.edu/node/1886 | AY 2025-26 | 2026-11-08 |
| A Downtown Ithaca Alliance page lists five ways to pay a TCAT fare | SNIPPET | https://www.downtownithaca.com/five-ways-to-pay-your-tcat-fare/ | undated | 2026-11-08 |

Result: the earlier row for node 311931 (year not shown) is closed. It is a 1999 article; its prices are a quarter of a century old.

## D11. Questions 31-35 (NEW, from this pass)
These are questions I could not cover with a "top 5" because the search tool returned fewer than five distinct relevant pages each time; every URL I did get is listed.

### Q31 (NEW) When is Cornell's Thanksgiving break in 2026 and what does the term end look like?
| # | URL | Title | Publisher | Date | What it says | Leaves out / wrong |
|---|---|---|---|---|---|---|
| 1 | https://catalog.cornell.edu/enrollment-credit-requirements/academic-calendar/ | Academic Calendar | Cornell course catalog | 2026-27 | SNIPPET: Nov 25 break begins, Nov 30 instruction resumes, Dec 7 last day of instruction; page returned no text when I opened it | The catalog warns dates can change |
| 2 | https://sce.cornell.edu/nds-prog-fall-spring/ | Fall/spring calendar | Cornell School of Continuing Education | 2026-27 | READ (see D4) | A non-degree program page, not the registrar |
| 3 | https://acadcalendar.com/cornell-academic-calendar/ | Cornell Academic Calendar 2026-2027 | acadcalendar.com (third party) | 2026-27 | SNIPPET: Thanksgiving Nov 25-29; term end Dec 19 | Third party; no source line |
| 4 | https://registrar.cornell.edu/acade/2026-2027 | Registrar page | Cornell Registrar | 2026-27 | SNIPPET: headings only | Official but empty to the tool |
| 5 | https://teach.weill.cornell.edu/sites/default/files/2026-06/Class%20of%202027%20Year%204%20Academic%20Calendar.pdf | Weill Year 4 calendar | Weill Cornell Medicine | 2026-06 | SNIPPET: a different campus's break dates | Wrong campus for Ithaca undergraduates |
**[LLM-GUESS] Typical AI answer:** "Cornell's Thanksgiving break usually runs Wednesday through Sunday; finals run through mid-December." What it misses: exact 2026 dates (Nov 25-29; term ends Dec 19; closed Dec 25 to Jan 4), the Weill variant, and that Dec 11-19 is the real exit week.

### Q32 (NEW) Is there a flight from Ithaca to Charlotte, Philadelphia or Newark now?
| # | URL | Title | Publisher | Date | What it says | Leaves out / wrong |
|---|---|---|---|---|---|---|
| 1 | https://flyithaca.com/faq | Airport FAQ | ITH | undated | READ: only Delta (JFK) and United (IAD) | No dated schedule |
| 2 | https://flyithaca.com/news | Airport news | ITH | to 2026-10-02 | READ: United 3rd daily Dulles flight from March 5, 2026; no CLT or PHL item | Possible missing posts |
| 3 | https://flyithaca.com/?p=1939 | Post dated Feb 4, 2026 | ITH | 2026-02-04 | READ: no Charlotte text found on page, though a search summary quoted one | Conflict between summary and page |
| 4 | https://flyithaca.com/?p=3376 | "Now offers direct flights to Philly" | ITH | undated | SNIPPET: American Airlines to PHL | Date unknown; may be a past season |
| 5 | https://aerocorner.com/airports/ith/ | Route Network | Aerocorner | none | SNIPPET: aggregator route list | Third party |
Also: https://z955.com/news/258852-ithaca-tompkins-international-airport-resumes-third-daily-flight-to-washington-dulles-international-airport (radio news on the third Dulles flight); https://tompkinscountyny.gov/Resident-Services/Ithaca-Tompkins-International-Airport (county page).
**[LLM-GUESS] Typical AI answer:** "ITH has nonstops to Newark, Philadelphia, Charlotte and Washington." What it misses: the airport lists two (JFK, Dulles); the Newark nonstop ended 2025 per the Sun; seasonal or past routes (American to PHL, a possible Charlotte start) are not confirmed.

### Q33 (NEW) Where do I catch Greyhound, OurBus or Trailways in Ithaca?
| # | URL | Title | Publisher | Date | What it says | Leaves out / wrong |
|---|---|---|---|---|---|---|
| 1 | https://en.wikipedia.org/wiki/Ithaca_Bus_Station | Ithaca Bus Station | Wikipedia | edited 2026-08-25 | READ: closed Oct 2018; buses at 131 E Green | Not authoritative |
| 2 | https://www.greyhound.com/bus-routes/ithaca-ny-newark-nj | Ithaca to Newark | Greyhound | live | READ: 131 E Green in front of Urban Outfitters; Cornell North and West Campus | Newark route only |
| 3 | https://www.ourbus.com/routes/ithaca-ny-to-syracuse-ny | Ithaca to Syracuse | OurBus | live | READ: S. Cayuga St by Cayuga Street Garage; West Campus; North Campus | Not Greyhound |
| 4 | https://www.busbud.com/en/green-street/s/35410 | Green Street stop | Busbud | none | SNIPPET: stop listing | Aggregator |
| 5 | https://scl.cornell.edu/families/cornell-family-resource-hub/parking-transportation | Parking and transportation | Cornell Housing / Student and Campus Life | undated | READ: says terminal is 710 West State St | Out of date vs Wikipedia and Greyhound |
**[LLM-GUESS] Typical AI answer:** "Buses arrive at the Ithaca bus terminal on West State Street." What it misses: the terminal closed in 2018; downtown stop is 131 E Green; OurBus uses S. Cayuga St, West Campus and North Campus.

### Q34 (NEW) Is there a car-free way for a first-year to get to a grocery store or the airport?
| # | URL | Title | Publisher | Date | What it says | Leaves out / wrong |
|---|---|---|---|---|---|---|
| 1 | https://scl.cornell.edu/families/cornell-family-resource-hub/parking-transportation | Parking and transportation | Cornell | undated | READ: first-years get OmniRide free; Blue Light Route 92 nightly 6:30 p.m.-2:30 a.m. | No grocery route named |
| 2 | https://flyithaca.com/faq | Airport FAQ | ITH | undated | READ: TCAT 32 weekdays, 72 weekends | No timetable |
| 3 | https://www.ithacacarshare.org/ | Ithaca CarShare | Ithaca CarShare | live | READ: 20 cars in Collegetown and East Hill | No rates |
| 4 | https://www.downtownithaca.com/five-ways-to-pay-your-tcat-fare/ | Five ways to pay | Downtown Ithaca Alliance | undated | SNIPPET | Not read |
| 5 | https://prked.com/post/navigating-cornell-a-complete-guide-to-getting-around-campus-ithaca | Complete guide | prked.com (commercial) | undated | SNIPPET | Commercial |
Not found: any page naming a TCAT route to a supermarket from North Campus, West Campus or Collegetown. Where I looked: the pages above and the Cornell bus-commuting page via Lane A.
**[LLM-GUESS] Typical AI answer:** "Take TCAT to Wegmans or Tops; the 30 goes to the Ithaca Mall." What it misses: it names stores without a route or schedule source; I did not verify which route serves which store.

### Q35 (NEW) What do the first-year winter, fall and spring "car storage over break" rules look like?
Lane A holds the rules (cars may stay in permit areas for housing residents). In this pass I found no new competitor page; the closest are the winter-parking announcements already listed under Q15. Not found: a competitor page that gathers break closure dates, car and storage rules in one place.

## D12. What is new in the ranked gaps (additions and re-ranking, best first)
New ranks refine the list above; they do not replace it.
1. **Where the bus really stops (new):** Cornell's own family page, a Wikipedia mirror and Greyhound disagree on the Ithaca station; the Cornell page sends people to a building closed since 2018. Fill: one correct table per operator. Evidence: D2.
2. **2026 break calendar tied to travel (new):** Thanksgiving Nov 25-29, finals end Dec 19, campus closed Dec 25 to Jan 4, spring break Mar 27 to Apr 4, 2027 (D4). No ranking page combines these with bus and airport booking windows. This is the most time-sensitive gap: Thanksgiving is 17 days from the check date.
3. **NYC bus: the price floor vs the real price (raised):** OurBus from $33 and 9 daily buses vs C2C $86-101 vs Greyhound Newark from $50.98 (D1). The Sun said 4-6 daily. An article must state same-day sample prices and warn that "from" is a floor.
4. **Boston and Philadelphia are now answerable with operator data:** OurBus Boston from $82.30, 6-8 h, last bus 4:45 PM; OurBus Philadelphia from $105.20, departures only 11:00 AM-1:55 PM (D1). Earlier "no Boston content anywhere" is now closed for OurBus.
5. **ITH nonstops (raised):** airport FAQ is the authority; Charlotte and Philadelphia items remain unconfirmed (D3).
6. **TCAT fare (unchanged, but the 1999 trap is new):** the search tool surfaces a 1999 Cornell page for fare queries (D10).
7. **First-year car (partly closed):** Cornell's line is "discouraged, limited permits available" (D9).
8. **Winter driving/biking:** still thin; one 2022 student opinion story and a 2013 forum thread (D6, D7).
9. **Bikeshare 2026 price:** still not found; two conflicting unlock fees ($1.50 vs $0.50) (D7).
10. **Carshare rates:** still not found (D8).

## D13. Official page already wins (additions)
- **Q2 airline list:** the airport FAQ states airlines and parking rates plainly; the article's job is the comparison with SYR, not the list.
- **Q20 (airport TCAT):** the airport FAQ names Route 32 weekdays / Route 72 weekends and the TCAT phone number; our value is the timetable, which neither fetch tool could read.

## Coverage (against SCOPE, after the deepen pass)
| Scope item | Status | Where |
|---|---|---|
| Flights into ITH | covered, one live-check caveat | Q2, Q32, D3 |
| Flights into SYR | thin (SYR's own page was not re-read this pass; Lane A holds it) | Q2, Q5 |
| Flights into ELM | thin (OurBus ELM page possibly stale) | Q6 |
| Ground connections SYR and ELM | thin; OurBus Syracuse city page read, SYR airport stop not on that page | Q5, Q6, Q30, D1 |
| Buses to NYC | covered (C2C from Lane A; OurBus, Greyhound read today; FlixBus not extracted) | Q1, D1 |
| Boston | covered for OurBus; other operators SNIPPET | Q3, D1 |
| Philadelphia | covered for OurBus and Greyhound listing | Q4, D1 |
| NJ / Newark | covered (Greyhound, OurBus) | Q13, D1 |
| Washington DC, Toronto | thin (SNIPPET only) | Q18, Q21 |
| FlixBus, Megabus, Trailways | thin: pages did not return usable extractions | Q1, Q18, Q21 |
| Airport rides (taxi) | thin; no current City schedule | Q23, D5 |
| Driving and parking permits and costs | covered except first-year eligibility beyond the "discouraged" line | Q7, D9 |
| TCAT routes, fares, student passes | covered from Cornell side; tcatbus.com unreadable (403 twice) | Q8, Q20, Q27, D9, D10 |
| Biking incl. winter | thin; no winter data | Q9, D6, D7 |
| Rideshare | thin; newest data is 2017 | Q10, D5 |
| Car share | thin; rates not found | Q14, D8 |
| Break travel and storage | covered for dates and sources; no 2026 sell-out data | Q11, Q24, Q26, D4 |
| Getting around without a car | thin; no grocery route page | Q22, Q34 |
Not found, searched at least twice: Bikeshare 2026 price; Carshare rates; City taxi fare schedule; TCAT fare page text (403); FlixBus fare and stop extraction; first-year permit rule beyond "discouraged".

## Pages read (this deepen pass; READ = opened with a fetch tool)
| # | URL | Result |
|---|---|---|
| 1 | https://www.tcatbus.com/learn/college-students/ | 403 |
| 2 | https://www.ourbus.com/routes/ithaca-ny-to-new-york-ny | READ |
| 3 | https://registrar.cornell.edu/calendar/academic-calendar | 404 |
| 4 | https://theithacan.org/46872/news/ithaca-bikeshare-adds-parking-hubs-and-raises-costs-of-use | 403 |
| 5 | https://news.cornell.edu/node/287516 | READ |
| 6 | https://flyithaca.com/faq | READ |
| 7 | https://flyithaca.com/?p=1939 | READ (no Charlotte text) |
| 8 | https://www.ourbus.com/routes/ithaca-ny-to-boston-ma | READ |
| 9 | https://flyithaca.com/news | READ |
| 10 | https://www.ithacacarshare.org/ | READ |
| 11 | https://www.flixbus.com/bus-routes/ithaca-ny-new-york-ny | READ, navigation only |
| 12 | https://catalog.cornell.edu/enrollment-credit-requirements/academic-calendar/ | empty |
| 13 | https://scl.cornell.edu/families/cornell-family-resource-hub/parking-transportation | READ |
| 14 | https://fcs.cornell.edu/node/17809 | 403 |
| 15 | https://www.tcatbus.com/ride/fare-pass-options/ | 403 |
| 16 | https://news.cornell.edu/node/311931 | READ (1999) |
| 17 | https://flyithaca.com/ground/taxi-service/ | 404 |
| 18 | https://www.greyhound.com/bus-routes/ithaca-ny-newark-nj | READ |
| 19 | https://www.tompkinscountyny.gov/node/353 | 404 |
| 20 | https://www.ourbus.com/routes/ithaca-ny-to-philadelphia-pa | READ |
| 21 | https://www.ourbus.com/routes/ithaca-ny-to-syracuse-ny | READ |
| 22 | https://cornellsun.com/2022/11/21/dont-let-it-snow-students-express-concerns-over-driving-conditions-as-temperatures-fall/ | READ |
| 23 | https://en.wikipedia.org/wiki/Ithaca_Bus_Station | READ |
| 24 | https://www.cornellsun.com/article/2023/09/williams-street-parking-lot-struggles-to-accommodate-students | READ |
| 25 | https://sce.cornell.edu/nds-prog-fall-spring/ | READ |
| 26 | https://www.city-data.com/forum/new-york/1819276-ithaca-binghamton-commute-winter-2.html | READ |
| 27 | https://theithacan.org/news/ride-hailing-services-slightly-less-expensive-than-taxis-in-ithaca/ | 403 |
| 28 | https://rideguru.com/cities/ithaca-new-york-united-states-of-america | redirect to ride.guru (not followed) |

Searches this pass (all web-search tool): ITH nonstops; Ithaca Bikeshare 2026; Cornell 2026-27 calendar; first-year car policy; Ithaca bus station operators; taxi fare schedule; TCAT fares 2026; winter driving. One search result list carried generic text asking that sources be listed; nothing in the results tried to redirect the work.

Counts for the line below are my own tallies, not a tool's: words about 16,000 (earlier 13,041 plus roughly 3,000 new), new distinct source URLs about 45 (28 pages tried plus about 17 more cited from search results), facts about 150 sourced rows.

## Lane complete: 150 facts, 190 sources, 16000 words, 2026-11-08
