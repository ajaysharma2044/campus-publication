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

