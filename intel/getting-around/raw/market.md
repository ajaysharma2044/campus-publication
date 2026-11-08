# Lane B: Market and data. Getting to Ithaca and getting around it

Checked date: rows say 2026-11-07 or 2026-11-08 (session crossed midnight). Raw notes, appended as found. Paraphrased.
Caveat on tool: WebFetch returns a model-written extract of each page, not raw text. Treat numbers as "as extracted"; verify before publishing.

## 0. Method notes
- Corpus check: grep of corpus/ for TCAT, airport, parking-permit, C2C pages found almost nothing useful (only fcs.cornell.edu announcements 2018-2025 about parking/transit events, and fcs.cornell.edu/departments/transportation-delivery-services). tcatbus.com and flyithaca.com are NOT in the corpus; fetched live.
- Bash is disabled in this session; used Glob/Grep/Read/WebFetch/WebSearch only. No bulk scraping.
- Fetch failures: tcatbus.com (all pages tried: learn/college-students, about/about-tcat, ride/fare-pass-options) HTTP 403; flyithaca.com/ground/bus-service/ 404; fcs.cornell.edu/node/17809 403; C2C rates-policies guessed URL 404; busbud.com route page 403; ourbus.com route page and flixbus.com route page return JS shells with no data.
- Public-data gaps so far: no official current C2C fare table reachable; no official TCAT fare page reachable (third-party reports only); no Greyhound/Trailways fare; OurBus fares are JS-rendered.

## 1. Cornell Campus-to-Campus (C2C) bus

| Fact | Value | Source URL | Applies to | Checked |
|---|---|---|---|---|
| Booking method | Online in a browser, no app; everyone needs a new account in the new system, even past riders; one reservation can cover several passengers; interactive seat selection | https://fcs.cornell.edu/departments/transportation-delivery-services/campus-campus-bus-service | page undated; new system launches 2026-11-04 | 2026-11-07 |
| Who gets discounts | Cornell students, faculty, staff sign in via Cornell single sign-on to get eligible discounts; public books at standard public fare | same | same | 2026-11-07 |
| Reservation links split | Trips departing Nov through Dec 23, 2026 use the "2026" link (incl. changes); trips on/after Jan 6, 2027 use the "2027" link | same | winter break 2026-27 | 2026-11-07 |
| Transition does not change schedules, rates, stops, amenities | stated by page | same | same | 2026-11-07 |
| Contact | 607-254-8747; c2cbus@cornell.edu; office 209 Solidago Rd (311 E Palm Rd), M-F 8:00-4:00 | same | undated | 2026-11-07 |
| Business travel | chargeable to a department, not by procurement card | same | undated | 2026-11-07 |
| Fares/schedule | NOT on the main page (links to separate pages not fetched) | same | | 2026-11-07 |
| Student discounted promo: $50 one-way, described as a $32.50 discount (implies regular $82.50, my arithmetic, not stated) | promo "through Sunday, April 5" (year not given; announcement URL dated 2020-03-14 -> STALE, likely 2020) | https://fcs.cornell.edu/node/3001 and https://fcs.cornell.edu/announcements/2020-03-14/c2c-student-discounted-rate-through-april-5 | 2020 (stale) | 2026-11-07 |
| NYC stops listed on that old page | Cornell Club (44th & Madison, near Grand Central), F Train to Tech Campus (64th & 3rd), Weill Cornell (69th & York) | https://fcs.cornell.edu/node/3001 | old/undated | 2026-11-07 |
| Search snippet: "fares hold steady at $75 per person each way" | undated Cornell news item; need date | https://news.cornell.edu/node/269896 (not read in full) | unknown | 2026-11-07 |
| Search snippet: from Aug 1, 2026 the NYC F Train stop discontinued, extra departure times added on some days | seen only in search summary; verify | via search | 2026-08-01 | 2026-11-07 |

## 2. OurBus expansion (Cornell Sun, 2026-09-02)
Source: https://www.cornellsun.com/article/2026/09/8kl4l6fodjwk (Coral Platt, Giselle Redmond; cites an OurBus press release; fares NOT mentioned).
| Fact | Value | Applies to | Checked |
|---|---|---|---|
| Frequency | 4 to 6 buses/day, 7 days/week, campus to Manhattan (previously Cornell stops mostly around major breaks) | from week of 2026-09-02 | 2026-11-07 |
| Campus stops of new trips | Ithaca Commons, West Campus, North Campus | same | 2026-11-07 |
| Demand claim | OurBus reported a 20% ridership rise Ithaca-NYC in Spring 2026; co-founder Axel Hellman attributed demand to higher fuel prices and the 2025 loss of ITH's direct Newark flight (attribution: Hellman/OurBus, not independently verified) | Spring 2026 | 2026-11-07 |
| Syracuse | Cornell-Syracuse service to 6 days/week, stops at Syracuse Hancock Airport and Destiny USA | fall 2026 | 2026-11-07 |
| Weekend routes | add stops in Fresh Meadows (Queens), Melville (LI), Cortland, Binghamton, Middletown, Nanuet | fall 2026 | 2026-11-07 |
| Relationship to C2C | Sun article does not use the term C2C; Hellman says OurBus in regular contact with Cornell transportation dept | | 2026-11-07 |

## 3. Airport ITH
| Fact | Value | Source URL | Applies to | Checked |
|---|---|---|---|---|
| Delta | direct ITH-JFK, daily (Delta Connection) | https://flyithaca.com/airlines | page undated | 2026-11-07 |
| United | nonstop ITH-IAD (Washington Dulles); airlines page gives no frequency | https://flyithaca.com/airlines | undated | 2026-11-07 |
| United IAD frequency | third daily flight added Oct 2025 (morning, afternoon, evening); IAD route began March 2025; announced 2025-08-14 | https://www.tompkinscountyny.gov/News-articles/Ithaca-Tompkins-International-Airport-to-add-third-daily-flight-to-Washington-D.C.-starting-in-October-2025 | Oct 2025 onward | 2026-11-07 |
| Taughannock Aviation | private jet charter, 1-800-876-1551 | https://flyithaca.com/airlines | undated | 2026-11-07 |
| Airline phones | Delta res 1-800-221-1212; Delta baggage 1-800-325-8224; United res 1-800-864-8331; United arrivals/departures 1-800-824-6200; United baggage 1-800-335-2247 | https://flyithaca.com/airlines | undated | 2026-11-07 |
| American Airlines | airport's 2022 notice: American suspended ITH-PHL effective Sept 6 (2022); older airport copy may still mention American -> possibly outdated | https://www.tompkinscountyny.gov/News-articles/ITH-Seeking-to-Retain-American-Airlines-Following-its-Announcement-to-Suspend-Area-Flights | 2022 | 2026-11-07 |
| Newark (United Express) | Wikipedia table says ended 2025-03-29; Sun (Sept 2026) says Newark flight lost in 2025 | https://en.wikipedia.org/wiki/Ithaca_Tompkins_International_Airport ; Sun URL above | 2025 | 2026-11-07 (secondary, verify) |
| ITH taxis | Ithaca Airport Cab 607-252-9052 (all payment types, no card fee); Collegetown Cab 607-588-8888 (online booking, app); Ithaca Dispatch 607-277-7777. No fares published on page | https://flyithaca.com/taxis | undated | 2026-11-07 |
| Contradiction note | flyithaca.com/ground/bus-service/ 404s although search results list it (search also lists tcatbus.com PDFs 32_Summer24.pdf, 32_Late-Fall.pdf for route 32; not fetched) | | | 2026-11-07 |

## 4. Cornell parking: student permits
Source: https://fcs.cornell.edu/departments/transportation-delivery-services/parking-campus/parking-students (page undated; rates "set as of July 1", year not stated; 2026/27 sales announcement says permits run 2026-08-16 to 2027-08-15, so prices presumed 2026-27; verify)
| Permit | Annual price | Eligibility | Valid where | Proration |
|---|---|---|---|---|
| FH (Hasbrouck) | $752.98 | univ housing residents there | FH lot; A Lot after 2:30 pm | daily from Sept 1 |
| ND (North Campus) | $752.98 | North Campus residents, extremely limited | ND lot; A Lot all times | daily from Sept 1 |
| SW (South) | $752.98 | South Campus residents | SW lot; A Lot after 2:30 pm | daily from Sept 1 |
| WD (West) | $752.98 | West Campus residents | WD lot; A Lot after 2:30 | daily from Sept 1 |
| B commuter | $359.77 | commuters only | B lot; A after 2:30 | daily from Aug 16 |
| AP accessible | $359.77 | via Student Disability Services | permit-restricted spaces except reserved/MT | not stated |
| M motorcycle | $120.01 | motorcycles, scooters, mopeds | M spaces | monthly |
- Resident and commuter permits limited availability; recalled if eligibility lost. Commuter lots: Vet College B, TRB, South and North Morrison, BTI.
- First-year cars: Cornell families page says first-years are discouraged from bringing a car, but limited permits are available (quote, short): https://scl.cornell.edu/families/cornell-family-resource-hub/parking-transportation (undated). The student parking page lists no separate first-year permit.
- Annual permits refundable only if returned by March 31; M and temporary permits not refundable; no cash refunds.
- Full-assistantship grad students can buy faculty/staff permits (outer tier A or E no fee for non-resident commuters; perimeter O etc).
- Sales: 2026/27 student sales began Tue Aug 4, 2026, 9:00 am, first come first served; myparking.cornell.edu (from search summary of https://fcs.cornell.edu/node/17809, 403 for me).
- Citation amounts: not on page. Cornell Sun 2023-09-04: fines rose first time since 2014: https://cornellsun.com/2023/09/04/on-campus-parking-violation-fines-increase-for-first-time-since-2014/ (not yet read).
- Contacts: transportation@cornell.edu; 607-255-4600 (M-F 7:30-12).
- Comparison: Ithaca College first-year parking permit $500 for 2026-27 (search summary of https://www.ithaca.edu/orientation/orientation-faqs/parking; not read directly).

## 5. TCAT
### 5a. Cornell privileges
Source: https://fcs.cornell.edu/departments/transportation-delivery-services/sustainable-transportation-options/bus-services-privileges-passes (undated)
| Fact | Value |
|---|---|
| New first-year degree students | unlimited TCAT rides; privileges expire Aug 31 (fall entrants) or Dec 31 (spring entrants) |
| Registered students enrolled a year+ | free on all TCAT buses after 6 pm weekdays and all day weekends; may buy discounted OmniRide pass |
| PhD students / graduate assistants | free OmniRide pass |
| Annual OmniRide pass | $200/yr, prorated monthly; current rate shown at purchase on myparking.cornell.edu; valid to Aug 31 of following year; refunds through Mar 31 minus $40 fee; may take 24h to activate |
| Cash fare if CU ID not accepted | $1.50 |
| Contacts | TCAT 607-277-RIDE (M-F 7:30-5); Transportation Services 607-255-4600 |
| Other regional operators | Chemung County Transit (Elmira/Horseheads/Ithaca); Cortland Public Transit (Cornell, TC3, Dryden) |
Families page (https://scl.cornell.edu/families/cornell-family-resource-hub/parking-transportation, undated): Blue Light buses run nightly on route 92, 6:30 pm-2:30 am, year-round; intercity buses (OurBus, Greyhound, Trailways) use a terminal at 710 West State St, many also stop on campus; flights into SYR, ELM or BGM need rental car or bus; hotels often sell out for Family Weekend and Commencement.

### 5b. TCAT public fares (two secondary sources; official tcatbus.com 403'd)
| Fact | Value | Source URL | Applies to | Checked |
|---|---|---|---|---|
| Standard fare | $1.50 all ages | https://www.downtownithaca.com/five-ways-to-pay-your-tcat-fare/ (Downtown Ithaca Alliance; undated page) | undated | 2026-11-08 |
| Reduced fare | $0.75 seniors 60+ and riders with disabilities (tell driver before tapping) | same | undated | 2026-11-08 |
| Kids under 12 | free with paying adult (FreeRyde) | same | undated | 2026-11-08 |
| Ways to pay | exact-change cash; tap contactless card/phone; TFare app (QR expires after a minute); rechargeable T-card from tcatbus.com/store; disposable T-card at retailers | same | undated | 2026-11-08 |
| Passes (search summary of official page https://www.tcatbus.com/ride/fare-pass-options/, which I could not open) | day $3.00; 2-day $6.00; 5-day $15.00; monthly $45.00; 15-ride adult card $20.00; 15-ride half-fare $10.00 | search result summary only | unknown date; VERIFY | 2026-11-08 |
| Route 10 aggregator | exact fare $1.50 incl. one transfer; schedule data updated 2026-09-24 | rideschedules.com (search summary only) | 2026-09-24 | 2026-11-08 |
| Head office | 737 Willow Ave, Ithaca; 607-277-RIDE | search summary | undated | 2026-11-08 |
| Funding | March 2026 report: TCAT told County Legislature (Feb 2026) of service/staffing improvements but warned of funding uncertainty | https://cpo.soar.com/articles/7591896/Tompkins-County/New-York/Tompkins-County-transit-agency-reports-service-and-staffing-improvements-but-warns-of-funding-uncertainty (search summary; not read) | 2026-02/03 | 2026-11-08 |
| Stale fare history | 1999 zone fares 75c/$1.50, monthly $20/$40 (https://news.cornell.edu/node/311931); do not use | | 1999 | 2026-11-08 |

## 6. Intercity bus market: Ithaca <-> NYC (sample, secondary sources only)
| Fact | Value | Source URL | Applies to | Checked |
|---|---|---|---|---|
| FlixBus Ithaca-NYC | "from" price 36.98 EUR (page in euro; not USD); min 5 trips/day; min duration 4h20; first dep 07:20, last 20:30 | https://global.flixbus.com/bus-routes/bus-ithaca-ny-new-york-ny | page footer 2026; no travel date | 2026-11-08 |
| FlixBus Ithaca stops | 131 E Green St; Cornell North Campus 121 Jessup Rd; Cornell West Campus 240 West Ave | same | 2026 | 2026-11-08 |
| FlixBus NYC stops (13) | Port Authority, Midtown 300 W 31st, Jamaica, Flushing, Hudson Yards (two), GW Bridge, Chinatown, Downtown 145 Canal, Midtown West, Upper Manhattan, Brooklyn 3rd Ave/38th, White Plains | same | 2026 | 2026-11-08 |
| Busbud (search summary): NYC->Ithaca cheapest $27, avg ~$56, avg trip 4h55, fastest 3h50 by OurBus | https://busbud.com/en/bus-new-york-ithaca/r/dr5reg-dr997q (403 for me) | unknown date | 2026-11-08 |
| Rome2rio estimates | OurBus $20-75; Midtown bus to Ithaca $35-75 | https://www.rome2rio.com/s/Ithaca/Manhattan | unknown date | 2026-11-08 |
| Operators named by Omio | FlixBus, OurBus, Greyhound, Trailways (Adirondack/NY Trailways), Infobus | https://www.omio.com/buses/ithaca-ny/new-york-ny | unknown | 2026-11-08 |
| Greyhound fare/duration | not found (route page only FAQ headings) | https://www.greyhound.com/bus-routes/new-york-ny-ithaca-ny | | 2026-11-08 |

<!-- merged from market.md.part2 -->
(empty: created by mistake; all content is in market.md)

<!-- merged from market-sections-7-12.md -->
# Lane B continuation: sections 7-12 (append to market.md sections 0-6)

Checked 2026-11-08 unless noted. WebFetch extracts are model-summarized; verify numbers before publishing.

## 7. Syracuse (SYR) airport
| Fact | Value | Source URL | Applies to | Checked |
|---|---|---|---|---|
| Parking, garage | up to 1h $10; 1-3h $13; 3-6h $15; 6-24h $22; daily max $22 | https://www.syrairport.org/parking/ | page gives no effective date (contact 315-455-3550) | 2026-11-08 |
| Parking, Blue Lot (terminal) | $7 / $9 / $11 / $16; daily max $16 | same | undated | 2026-11-08 |
| Parking, Red and Purple economy | $6 / $8 / $9 / $14; daily max $14 | same | undated | 2026-11-08 |
| Nonstop destinations | page lists 24 destination cities (27 airports), 8 airlines (inferred from logos; extract's own airline counts self-corrected, so treat counts as approximate) | https://syrairport.org/destinations/ | undated | 2026-11-08 |
| Airlines and example routes | American (BOS, CLT, ORD, DFW, MIA, PHL, DCA); Delta (ATL, DTW, MSP, JFK, LGA); United (ORD, DEN, IAD); JetBlue (BOS, FLL, JFK, MCO); Allegiant, Breeze, Sun Country, Frontier (Florida/leisure) | same | undated | 2026-11-08 |
| Contrast with ITH | SYR offers American (PHL, CLT, DFW, MIA...), Delta ATL/DTW/MSP, JetBlue BOS; ITH offers only JFK (Delta) and IAD (United) | flyithaca.com/airlines vs syrairport.org/destinations | | 2026-11-08 |
| Delta ATL 4th daily from June 7, 2026; I-81 northbound roadwork from May 3, 2026 affects evening/early-morning travel; consolidated rental car facility under construction | CNY Signal (search summary; not read) https://cnysignal.com/hancock-airport-adds-flights-and-a-construction-zone-for-summer-2026-plan-accordingly | summer 2026 | 2026-11-08 |
| Conflicting third-party parking numbers (daily $8, $10, $13, $15 on aggregators) | not matching official page | search results | | 2026-11-08 |
| SYR to Cornell | no official price found. OurBus serves Syracuse Hancock Airport and Destiny USA from Cornell stops, 6 days/week from Sept 2026 (Cornell Sun, above). Cornell families page says SYR/ELM/BGM flights need rental car or bus. | | | 2026-11-08 |

## 8. Elmira (ELM) airport
| Fact | Value | Source URL | Applies to | Checked |
|---|---|---|---|---|
| Location | ~7 mi NW of Elmira, ~8 mi E of Corning (Wikipedia-derived) | https://en.wikipedia.org/wiki/Elmira/Corning_Regional_Airport (search summary) | | 2026-11-08 |
| Route counts conflict | aggregators say 5, 10 or 16 destinations; Allegiant and others named; Detroit named as busiest | https://www.airportoverview.com/routes/ELM ; https://aerocorner.com/airports/elm/ | undated | 2026-11-08 |
| ELM to Ithaca ground options, distance, fares | NOT FOUND in public summaries. Cornell families page mentions only that ELM requires rental car or bus; Chemung County Transit (Elmira/Horseheads/Ithaca) exists per Cornell page. Not verified whether it reaches the airport. | | | 2026-11-08 |
| Official airport site | not fetched (budget); gap | | | |

## 9. Break shuttles (Cornell Student Assembly)
| Fact | Value | Source URL | Applies to | Checked |
|---|---|---|---|---|
| Finals-week airport shuttles, free to undergraduates, to Syracuse and Ithaca airports: 20 buses; register by May 12 11 pm; pickups Baker Flagpole and RPCC; first-come first-served; Resolution 76 moved $18,000 to Dean of Students office | https://cornellsun.com/2024/05/07/student-assembly-funds-free-charter-buses-to-syracuse-ithaca-airports/ | May 15-18, 2024 | 2026-11-08 |
| 2025-26 finals-week shuttle funding: $10,668.87 disbursement, SA Resolution 83, adopted 2026-04-16; earlier $7,853.32 | https://assembly.cornell.edu/resolutions/student-assembly/sa-r83-2025-2026 ; https://assembly.cornell.edu/resolutions/student-assembly/sa-r18-2025-2026 (search summaries; not opened) | spring 2026 | 2026-11-08 |
| Thanksgiving or winter-break 2026 Cornell shuttle | NOT FOUND (no published RSVP or fare found) | | | 2026-11-08 |
| Cornell Sun 2025 guide (Melanie Delfosse, 2025-05-04): TCAT route 32 to airport weekdays outbound arrivals 7:34 am-7:31 pm, inbound departures 7:46 am-6:43 pm; Saturday inbound 8:46 am-7:46 pm; Sunday inbound 8:46 am-6:46 pm (schedule may have changed; it is a student-writer's summary) | https://www.cornellsun.com/article/2025/05/busses-trains-and-planes-getting-to-and-from-cornell | 2025 | 2026-11-08 |

## 10. Taxi, Uber/Lyft: only dated samples exist
| Fact | Value | Source URL | Applies to | Checked |
|---|---|---|---|---|
| Ithacan fare sample (Celisa Calacal, 2017-09-19): Uber college-to-Commons Mon 5 pm UberX $7.35, XL $10.50; Sat 1:45 am X $9.59, XL $14.18; college-to-airport Tue 12:30 pm Uber $17.49, XL $27.56; taxi college-to-airport $19; taxi city-to-college base $11. Sample size not stated; "college" = Ithaca College | https://theithacan.org/news/ride-hailing-services-slightly-less-expensive-than-taxis-in-ithaca/ | 2017 (STALE, 9 years) | 2026-11-08 |
| Current Cornell-to-airport taxi price | NOT FOUND; airport page says call operators. No current fare sample exists in public data | https://flyithaca.com/taxis | | 2026-11-08 |
| Uber/Lyft trial in Ithaca began mid-2017 (Cornell Sun) | https://cornellsun.com/2017/07/01/uber-lyft-begin-trial-period-in-ithaca/ (search only) | 2017 | |

## 11. Bikes and car share
| Fact | Value | Source URL | Applies to | Checked |
|---|---|---|---|---|
| Ithaca Bikeshare | nonprofit (Center for Community Transportation); 85 electric bikes; launched Nov 2022; annual $150 unlimited hour-long trips; unlock $0.50; $0.20/min (up from $0.15); $1 fee if not returned to hub; low-income Easy Access free via Go Ithaca; 34,000+ trips in months after launch, 250-275/day in good weather; no student discount, hoped for Cornell expansion | https://betterbikeshare.org/2023/07/10/ithaca-stands-by-bike-share/ | article 2023-07-10 (STALE; no 2026 pricing found; official site not located: ithacabikeshare.com does not resolve) | 2026-11-08 |
| Bikeshare on campus | Cornell Sun 2023: few/no hubs on campus; Better Bike Share says ~60% of trips on campus | https://cornellsun.com/2023/01/24/ithaca-bikeshare-a-comprehensive-guide-to-ithacas-newest-transportation-option/ (search summary) | 2023 | 2026-11-08 |
| Ithaca Carshare | nonprofit; resumed March 2024 after May 2023 suspension; 12 cars then (30 before), goal 20; director Liz Field; no rates in article | https://cornellsun.com/2024/03/25/ithaca-carshare-officially-returns-to-operation | 2024-03-24 | 2026-11-08 |
| Cornell page | Ithaca CarShare discounted memberships for students and employees; 4 on-campus pickup spots plus 4 in Collegetown/nearby; no prices | https://sustainable.cornell.edu/campus-initiatives/transportation/ride-car-sharing | undated | 2026-11-08 |
| Old IC student rate ($15 application fee, $4.95/hr) | 2010, stale | https://web2.ithaca.edu/intercom-archive/article.php/20100826141953733.html | 2010 | 2026-11-08 |
| Winter biking | Not researched in this lane beyond candidate sources: https://cornellsun.com/2007/11/12/cyclists-persevere-through-wintry-weather ; https://sustainable.cornell.edu/news/rules-road-biking-season | | | |

## 12. Parking fines and price history
| Fact | Value | Source URL | Applies to | Checked |
|---|---|---|---|---|
| Cornell fines from 2023-09-01 | permit/payment violations $35 -> $50 (85% of violations; $10 late fee after 10 days); fire lane, life-safety, accessible space or aisle $150 with tow; boot release $150 | https://cornellsun.com/2023/09/04/on-campus-parking-violation-fines-increase-for-first-time-since-2014/ | 2023-09-01 (may have changed) | 2026-11-08 |
| Resident permit price in that article | $752.86 (2023) vs $752.98 on current student parking page: nearly identical; suggests prices flat or the current page is stale. Flag for verification | Sun URL above vs https://fcs.cornell.edu/departments/transportation-delivery-services/parking-campus/parking-students | 2023 vs undated | 2026-11-08 |
| Old C2C fare | $75 each way from 2011 (Cornell Chronicle, expanded schedule from 2011-01-13), STALE | https://news.cornell.edu/node/269896 | 2011 | 2026-11-08 |

## 13. Gaps and stale data summary
- No official current C2C fare table; the only official fares found are 2011 ($75) and a 2020 student promo ($50 one-way).
- No official TCAT fare page readable (403); fares ($1.50, passes) come from a Downtown Ithaca Alliance page (undated) and a search summary.
- No Greyhound or Trailways fares; OurBus and FlixBus fares are JS-rendered; only aggregator ranges ($20-75).
- Taxi and rideshare fares: latest sample is 2017.
- Bikeshare and carshare: latest prices 2023/2010; none for 2026.
- ELM to Ithaca: no ground option data.
- Not covered (turn budget): Cornell winter parking rules, TCAT route list and 2026-27 service changes, break storage prices, rental cars at ITH, Ithaca Commons parking garage rates, Ithaca College bus page, Trailways terminal details (710 W State St per Cornell families page only), Cornell Sun 2023 Williams St lot article.
