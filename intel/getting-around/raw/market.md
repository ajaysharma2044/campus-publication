# Lane B: Market and data. Getting to Ithaca and getting around it

Checked date: rows say 2026-11-07 or 2026-11-08 (session crossed midnight). Raw notes, appended as found. Paraphrased.
Caveat on tool: WebFetch returns a model-written extract of each page, not raw text. Treat numbers as "as extracted"; verify before publishing.

## 0. Method notes
- Corpus check: grep of corpus/ for TCAT, airport, parking-permit, C2C pages found almost nothing useful (only fcs.cornell.edu announcements 2018-2025 about parking/transit events, and fcs.cornell.edu/departments/transportation-delivery-services). tcatbus.com and flyithaca.com are NOT in the corpus; fetched live.
- Bash is disabled in this session; used Glob/Grep/Read/WebFetch/WebSearch only. No bulk scraping.
- Fetch failures: tcatbus.com (all pages tried: learn/college-students, about/about-tcat, ride/fare-pass-options) HTTP 403; flyithaca.com/ground/bus-service/ 404; fcs.cornell.edu/node/17809 403; C2C rates-policies guessed URL 404; busbud.com route page 403; ourbus.com route page and flixbus.com route page return JS shells with no data.
- Public-data gaps so far: no official current C2C fare table reachable; no official TCAT fare page reachable (third-party reports only); no Greyhound/Trailways fare; OurBus fares are JS-rendered.
- (Deepen session 2026-11-08: the C2C fare gap is now resolved, see section 14. Edit was disabled in the deepen session, so the file was rewritten whole with the earlier text kept unchanged and sections 14 onward appended.)

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
- (Deepen session 2026-11-08 resolved the C2C fare gap: see section 14. Other gaps listed here remain unless a later section says otherwise.)
- Not covered (turn budget): Cornell winter parking rules, TCAT route list and 2026-27 service changes, break storage prices, rental cars at ITH, Ithaca Commons parking garage rates, Ithaca College bus page, Trailways terminal details (710 W State St per Cornell families page only), Cornell Sun 2023 Williams St lot article.

<!-- ===================== DEEPEN SESSION 2026-11-08 (appended) ===================== -->
Method note for sections 14 to 24: pages read one at a time with WebFetch (model-written extract; verify numbers) or taken from search-result summaries (marked "search summary"). Checked date 2026-11-08 for every row. Tcatbus.com still 403 and the fcs.cornell.edu C2C terms page 403 (the C2C policies page worked).

## 14. Cornell C2C fares, rules and stops (official, resolves the earlier gap)
Rates page: https://fcs.cornell.edu/departments/transportation-delivery-services/campus-campus-bus-service/c2c-rates (no effective date stated on page; page links the new reservation system starting 2026-11-04).
| Fact | Value | Source URL | Applies to | Checked |
|---|---|---|---|---|
| Non-Cornell passenger fare | $101 one way; $202 round trip | rates page above | undated; current as of 2026-11-08 read | 2026-11-08 |
| Cornell faculty, staff, students (valid NetID registered in the C2C account) | $93.50 one way; $187 round trip | same | same | 2026-11-08 |
| Cornell or Weill Medical account; department-paid business traveler | $86 one way; $172 round trip | same | same | 2026-11-08 |
| Temporary surcharge | $6 per one-way ticket, already included in the listed fares; reason given: higher fuel and toll costs; no end date stated | same | undated | 2026-11-08 |
| Student discount size | $101 minus $93.50 = $7.50 per one-way trip for a Cornell student vs the public (my arithmetic) | same | same | 2026-11-08 |
| Weill NetID note | Weill CWID numbers are not recognised by the booking system; Weill staff must request a NetID from the IT Service Desk | same | same | 2026-11-08 |
| Infants and seat-taking items | under 2 on lap ride free; age 2 and up need a paid reservation; a stroller or backpack that takes a seat counts as a passenger | same | same | 2026-11-08 |
| Change and cancel processing fee | amount not on the rates page (see policies below) | same | | 2026-11-08 |
| Cancellation fee | $10 per seat if cancelled at least 8 hours before travel; $30 per seat within 8 hours | https://fcs.cornell.edu/departments/transportation-delivery-services/campus-campus-bus-service/c2c-policies-regulations | undated | 2026-11-08 |
| Changes | date or time change allowed up to 8 hours before departure; changing only the stop on the same bus is free; a change inside 8 hours costs $30 per seat per change | same | undated | 2026-11-08 |
| Missed bus | whole fare forfeited; the return leg is not cancelled automatically | same | undated | 2026-11-08 |
| Luggage | two suitcases below deck plus two small carry-ons per passenger; a bike in a box counts as one suitcase | same | undated | 2026-11-08 |
| Pets | companion animals must stay in a carrier on lap or at feet; a carrier that takes a seat needs a paid seat; service animals exempt | same | undated | 2026-11-08 |
| Minors | page says 12 and under need an adult but a refusal policy mentions unaccompanied minors under 13: internal inconsistency on the page | same | undated | 2026-11-08 |
| Ithaca stops | N. Campus: 217 Jessup Rd, shelters in front of Robert Purcell Community Center; Sage Hall: 114 Feeney Way, TCAT shelter near East Ave and Campus Rd across from Statler Hall; B-Lot (Vet College): 930 Campus Rd, shelter on the southeast side of B Lot | https://fcs.cornell.edu/departments/transportation-delivery-services/campus-campus-bus-service/c2c-departure-schedule-stop-locations | undated | 2026-11-08 |
| NYC stops | Weill Medical: 1300 York Ave main entrance across from 69th St; Cornell Club: 6 East 44th St between Fifth and Madison. No F Train stop listed (consistent with the Aug 1, 2026 discontinuation seen in search) | same | undated | 2026-11-08 |
| Ride length | about 4.5 to 5 hours from the last Ithaca stop (B-Lot) to Cornell Club | same | undated | 2026-11-08 |
| Departure times seen | Ithaca stops at 5:30/5:45/6:00 am, 7:30/7:45/8:00 am, 9:30/9:45/10:00 am, 11:30/11:45/12:00 pm, 5:30/5:45/6:00 pm; NYC side 5:45 am to 6:30 pm in many slots; the page table is garbled in extraction so day-to-time mapping is NOT reliable (3 Ithaca stops are 15 minutes apart: North Campus, Sage, B-Lot) | same | undated | 2026-11-08 |
| Boarding rule | arrive at least 10 minutes early; drivers do not leave early; schedules may change for events or closures | same and https://fcs.cornell.edu/departments/transportation-delivery-services/campus-campus-bus-service/c2c-frequently-asked-questions | undated | 2026-11-08 |
| B-Lot parking for riders | riders without a valid permit can buy temporary parking for up to 14 days at a time; free parking needs a B Lot Reservation form; student SC and B permits valid in B Lot | FAQ URL above | undated | 2026-11-08 |
| Winter overnight parking | Dec 1 to Apr 1, 5 pm to 7:30 am, rules apply when snow is forecast | schedule page above | winter | 2026-11-08 |
| Reservation systems | trips Nov through Dec 23, 2026: https://c2cbus.ipp.cornell.edu/ ; trips on/after Jan 6, 2027: https://c2cbus.transportation.cornell.edu/ ; new system launch 2026-11-04 | https://fcs.cornell.edu/departments/transportation-delivery-services/campus-campus-bus-service | 2026-27 | 2026-11-08 |
Comparison computed from these rows (my arithmetic): a Cornell student pays $93.50 each way on C2C, which is 3.7 times the OurBus "from" fare of $25 (Aug 2026 sample, section 15) and about 2.1 times the ShortLine student fare found in older data; round-trip on C2C $187 vs about $50 on OurBus at the "from" price.
Search-snippet history of C2C prices (not read in full, context only): $99 one way / $149 round trip in 2004 (https://cornellsun.com/2004/08/26/connecting-campuses); $75 each way 2011 (section 12). So the nominal fare rose from $75 (2011) to $101 public / $93.50 student (2026), +35% public over 15 years including the $6 surcharge (my arithmetic).

## 15. OurBus fare table and student deals (blog, fares are dynamic)
Source: https://www.ourbus.com/blog/?p=6269 (blog published 2026-08-04; fares, times and frequencies checked against live OurBus pages by the blog on 2026-08-17; OurBus says fares are dynamic).
| Route | "From" fare | Trip time | Buses per day |
|---|---|---|---|
| NYC to Ithaca | $25 | 4 to 5 hr | 9 to 10 |
| NYC to Syracuse | $25 | about 4 hr 30 | 3 to 4 |
| NYC to Binghamton | $18 | 3 to 3.5 hr | 9 to 10 |
| NYC to Philadelphia | $9 | 1 hr 20 to 2 hr 15 | 19 to 20 |
| NYC to Boston | $19 | 4 to 4.5 hr | up to 20 |
| NYC to Washington DC | $17 | 4 to 4.5 hr | 11 to 17 |
| NYC to Baltimore | $17 | about 3 hr 40 | 5 to 6 |
| NYC to Worcester | $25.54 all-in | about 3 hr 30 | 2 to 3 |
| NYC to Buffalo | live pricing only | 7.5 to 8.5 hr | 5 to 6 |
| Fact | Value | Source URL | Applies to | Checked |
|---|---|---|---|---|
| OurBus Select | $15 off each of the next 10 intercity tickets (up to $150); signup asks for a college name | https://www.ourbus.com/blog/?p=6269 | Aug 2026 | 2026-11-08 |
| OurBus student discount | separate verification-based discount; no amount on the page | same | Aug 2026 | 2026-11-08 |
| Peak dates to book early | Wednesday before Thanksgiving; last day of December finals; the Friday spring break begins | same | 2026-27 | 2026-11-08 |
| Note on blog numbers | blog says fares top out near $26 while its table shows $25.54 for Worcester; and "from" fares are the cheapest seat, not an average | same | | 2026-11-08 |
| Boston, Philadelphia from Ithaca | NOT in the table (table is NYC-origin). OurBus pages exist for other Ithaca routes (e.g. Ithaca to Princeton https://www.ourbus.com/routes/ithaca-to-princeton ; Ithaca to Newark Airport https://www.ourbus.com/routes/ithaca-ny-to-newark-airport-nj) but no fares were readable | search results | | 2026-11-08 |
Price range summary for Ithaca to NYC by operator on one page of facts: OurBus "from" $25 (blog, Aug 2026); Busbud cheapest $27 and average about $56 (section 6); Greyhound "from" $43.98 (section 16); ShortLine $50 one way (section 17); FlixBus 36.98 EUR (section 6); C2C $93.50 student / $101 public (section 14). Observed dates differ (Aug 2026 to Nov 2026) and one-way "from" prices are the cheapest advance fare, so this is not a like-for-like comparison.

## 16. Greyhound Ithaca to New York (official route page)
Source: https://www.greyhound.com/bus-routes/ithaca-ny-new-york-ny (page undated; read 2026-11-08)
| Fact | Value | Source URL | Applies to | Checked |
|---|---|---|---|---|
| Cheapest fare | from $43.98 | same | read 2026-11-08, no travel date | 2026-11-08 |
| Shortest trip | about 4 hr 20 min; about 227 miles | same | | 2026-11-08 |
| Departures | 5 buses a day; first 7:20 am; last 8:30 pm | same | | 2026-11-08 |
| Ithaca stations | 131 E Green St (curbside in front of Urban Outfitters; do not wait inside the public library); Cornell North Campus 121 Jessup Rd; Cornell West Campus 240 West Ave in front of Mennen Hall | same | | 2026-11-08 |
| NYC stations (13) | Port Authority 625 8th Ave; Midtown 300 W 31st; Midtown West 215-221 W 36th; Hudson Yards 600 W 34th; Hudson Yards Trailways 556 W 33rd; GW Bridge 4211 Broadway; Upper Manhattan 4149 Broadway; Chinatown 28 Allen St; Downtown 145 Canal; Jamaica 91-91 144th Pl; Flushing 41-32 Kissena Blvd; Brooklyn 3rd Ave at 38th; White Plains 11 Ferris Ave | same | | 2026-11-08 |
| Luggage | one carry-on (16x12x7 in, up to 25 lb) and one checked bag free; Flexible fare adds a second free checked bag | same | | 2026-11-08 |
| Observation | Greyhound's departure times (7:20 first, 8:30 last), station list and the Ithaca stops are identical to the FlixBus page (7:20 first, 20:30 last; same stops, section 6): consistent with one combined FlixBus-Greyhound network (my inference; neither page states it) | this URL vs https://global.flixbus.com/bus-routes/bus-ithaca-ny-new-york-ny | | 2026-11-08 |
| Old terminal | Wikipedia lists the Ithaca Bus Station at 710 W State St as closed (no year); a mirror says buses board at 131 E Green St "for the time being". The Cornell families page still names 710 West State St (undated): contradiction, treat the Cornell page as out of date | https://en.wikipedia.org/wiki/Ithaca_Bus_Station vs https://scl.cornell.edu/families/cornell-family-resource-hub/parking-transportation | | 2026-11-08 (secondary) |
| Older fare anecdote | FlyerTalk poster quoted about $32 one way on a Greyhound internet fare; undated, stale | https://www.flyertalk.com/forum/mid-atlantic/1229876-cheap-bus-travel-between-ithaca-nyc-2-printerfriendly.html | undated | 2026-11-08 (search summary) |
| Greyhound NYC pickup per its own page | southwest corner of W 31st St and 8th Ave | https://www.greyhound.com/en-us/bus-from-new-york-to-ithaca | undated | 2026-11-08 (search summary) |

## 17. Ithaca College family transportation page and ShortLine/Coach USA
Source: https://www.ithaca.edu/orientation/family-and-guest-resources/transportation (undated; Ithaca College page)
| Fact | Value | Source URL | Applies to | Checked |
|---|---|---|---|---|
| Airports | ITH about 10 minutes (7 miles) from campus; SYR about 1 hr 15 min (65 miles) | same | undated | 2026-11-08 |
| Airlines at ITH on that page | lists American, United and Delta; contradicts flyithaca.com/airlines (Delta and United only; American suspended ITH-PHL in 2022): the IC page is out of date on American | same vs https://flyithaca.com/airlines | | 2026-11-08 |
| ShortLine (Coach USA) | 9 daily schedules to NYC; 4 daily to Westchester, Long Island, Queens, Hudson Valley; listed price $50 one way | same | undated | 2026-11-08 |
| ShortLine student fares (old) | regular $54.50 one way; student "Go Anytime" $46.35 one way / $92.65 round trip; "TGIF" $45 one way / $90 round trip; TGIF began 2019-08-30 | https://www.coachusa.com/node/322 | 2019 (STALE) | 2026-11-08 |
| ShortLine discount rules (old) | Go Anytime: one reduced ticket per student, bought at a terminal; TGIF applies to outbound Friday or break travel, return Sun to Tue | same | 2019 | 2026-11-08 |
| ShortLine Ithaca stop | Ithaca Bus Terminal (name on the 2019 page); current terminal location not confirmed | same | 2019 | 2026-11-08 |
| College Express | bus between Ithaca and NJ, NYC, Queens, Long Island on weekends and breaks; NO fare found anywhere; one undated forum poster reported a poor experience (single anecdote) | https://www.ithaca.edu/orientation/family-and-guest-resources/transportation ; https://talk.collegeconfidential.com/t/transportation-to-from-long-island/1794328 (search summary) | undated | 2026-11-08 |
| Train | nearest Amtrak city is Syracuse about 60 miles north (per IC page) | IC page above | undated | 2026-11-08 |
| Finger Lakes Rideshare | rides board at zimride.com/ithaca per IC page; not checked whether still active | IC page above | undated | 2026-11-08 |
| Ithaca College TCAT | rides free for eligible IC riders for the Fall 2026/Spring 2027 academic year; riders without the app or phone pay $1.50 a trip; IC ID no longer works on the bus since 2024-09-01; use TFare app | https://www.ithaca.edu/id-office/tcat-information | AY 2026-27 | 2026-11-08 |
| IC graduate student travel page | exists (not read): https://www.ithaca.edu/academics/graduate-and-professional-studies/graduate-student-life/travel-and-transportation | search result | | 2026-11-08 |

## 18. Downtown Ithaca bus-stop move on 2026-11-09 (time-sensitive)
Sources: https://www.fingerlakes1.com/2026/11/03/ithaca-and-tcat-will-move-downtown-bus-stops-nov-9/ (2026-11-03) and https://www.fingerlakes1.com/2026/11/06/ourbus-moves-ithaca-stop-to-south-cayuga-street-monday-as-tcat-shifts-stops/ (2026-11-06). Both are FingerLakes1 staff reports relaying a City of Ithaca release.
| Fact | Value | Source URL | Applies to | Checked |
|---|---|---|---|---|
| Date | changes take effect Monday 2026-11-09 | both | 2026-11-09 | 2026-11-08 |
| OurBus Ithaca stop | moves from East Seneca St to 235 S. Cayuga St beside the South Cayuga garage; city says a short walk from the Commons with TCAT connections and more parking | 2026-11-06 article | from 2026-11-09 | 2026-11-08 |
| Intercity stop (general) | relocates to the 200 block of South Cayuga St; the 11-03 article names no operators | 2026-11-03 article | from 2026-11-09 | 2026-11-08 |
| Whether Greyhound/FlixBus/Trailways move too | NOT STATED in either article (only OurBus named); their pages still say 131 E Green St | both vs section 16 | | 2026-11-08 |
| TCAT East Seneca stop 1 | moves about 60 yards east to between Dewitt Mall and Tompkins Financial; routes 11, 11S, 13, 14, 15, 17, 20, 21, 31W, 40, 43, 51, 52, 65, 67 | both | from 2026-11-09 | 2026-11-08 |
| TCAT East Seneca stop 2 | East Seneca at North Tioga (former intercity spot): routes 30, 30W, 90 | both | from 2026-11-09 | 2026-11-08 |
| Route 10 | stays on North Tioga St | both | | 2026-11-08 |
| Reason | ease congestion and respond to merchant problems since the Seneca Street garage closed in spring 2026 | 2026-11-03 article | | 2026-11-08 |
| Cayuga Street Garage | 245 S. Cayuga St, more than 300 spaces, within 5 minutes' walk of the Commons | 2026-11-03 article | | 2026-11-08 |
| Updates | TCAT will post on its website, Bus Tracker and the MyStop app | both | | 2026-11-08 |
Note: the Seneca Street garage closed in spring 2026 per this article, but the Dec 2025 rate article (section 19) still lists Seneca garage rates: the garage rates for Seneca are therefore not currently usable.

## 19. City of Ithaca downtown parking rates (from 2026-01-05)
Sources: https://www.fingerlakes1.com/2025/12/19/ithaca-raises-parking-rates-downtown/ (2025-12-19; relays city release; quotes Deputy City Manager Dominick Recckio and Mayor Robert Cantelmo); search summary of https://www.fingerlakes1.com/2025/11/12/free-saturday-parking-to-end-in-ithaca-in-2026/
| Fact | Value | Source URL | Applies to | Checked |
|---|---|---|---|---|
| Garage hourly rate | $2.25/hour at Green Street, Dryden Road, Seneca Street and Cayuga Street (Cayuga managed by Premium Parking) | first URL | from 2026-01-05 | 2026-11-08 |
| Daily maximum | $12 at Green, Seneca, Cayuga; $18 at Dryden Road | same | from 2026-01-05 | 2026-11-08 |
| Street meters | $2.50/hour at ParkMobile and electronic pay-station zones; $1.50/hour coin-only meters farther out ("for now") | same | from 2026-01-05 | 2026-11-08 |
| Saturday | free Saturday parking ended with the 2026 budget; Sunday still free (search summary; the Dec 19 article does not discuss Saturdays) | https://www.fingerlakes1.com/2025/11/12/free-saturday-parking-to-end-in-ithaca-in-2026/ | 2026 | 2026-11-08 (search summary) |
| City source | a City of Ithaca parking website is cited by the article; not read | first URL | | 2026-11-08 |
| Seneca garage status | closed since spring 2026 per Nov 2026 article (section 18) | 2026-11-03 article | | 2026-11-08 |
| Prior rate | NOT found (article gives none); rates earlier in 2025 not recorded | | | |

## 20. Cornell short-term and visitor parking
Source: https://fcs.cornell.edu/departments/transportation-delivery-services/parking-campus/short-term-parking-options (page shows a note that two pay stations were out of service as of 9/08/2026)
| Fact | Value | Source URL | Applies to | Checked |
|---|---|---|---|---|
| Pay-by-app | ParkMobile; text PARK to 77223 or use app; $0.45 convenience fee per transaction including extensions | same | 2026 | 2026-11-08 |
| Purchase limits | minimum 1 hour; loading areas (Zone 4125) 30-minute limit; maximum 8 hours, or by the day; most lots' parking day ends at 7:30 am; B lot uses a 24-hour day; multi-day in most locations | same | 2026 | 2026-11-08 |
| Tang Welcome Center (Zone 4119) | $1.50/hour, $10.00/day (pay station out of service as of 9/08/2026 per page note) | same | 2026 | 2026-11-08 |
| Botanic Gardens Nevin Center (Zone 4120) | $1.50/hour, 3-hour limit | same | 2026 | 2026-11-08 |
| Daily Decision | demand-priced parking in outer lots, open to all first come, no price on page; $0.45 fee applies | same | 2026 | 2026-11-08 |
| Payment hours in commuter lots | Mon to Fri 7:30 am to 5:00 pm year-round including holidays and breaks; some lots permit-only evenings and weekends | same | 2026 | 2026-11-08 |
| Resident areas (FH, ND, SW, WD) | permit or ParkMobile payment 24/7 | same | 2026 | 2026-11-08 |
| Johnson Museum | metered/ParkMobile parking limited to museum guests during hours; register vehicle at reception | same | 2026 | 2026-11-08 |
| Visit Cornell visitors | can prepay via confirmation email; no prices on page | same | 2026 | 2026-11-08 |
| Office | Transportation Services, 116 Maple Ave, Ithaca NY 14850-4902; 607-255-4600; Mon to Fri 7:30 am to 12 pm (so the 2026 hours equal those in section 4) | same | 2026 | 2026-11-08 |
| Gap | per-lot hourly and daily rates (A, B, etc.) are only in a PDF map; not read | | | |

## 21. ITH airport parking (official)
Source: https://flyithaca.com/parking (undated; read 2026-11-08; parking phone 607-220-4699)
| Duration | Short-term lot | Long-term lot |
|---|---|---|
| First 30 minutes | free | free |
| 31 to 60 minutes | $2.00 | $2.00 |
| 1 to 2 hours | $3.00 | $3.00 |
| 2 to 3 hours | $5.00 | $4.00 |
| 3 to 4 hours | $7.00 | $5.00 |
| 4 to 5 hours | $8.00 | $6.00 |
| 5 to 24 hours (daily) | $9.50 | $8.00 |
| Weekly | $48.00 | $40.00 |
| Fact | Value | Source URL | Applies to | Checked |
|---|---|---|---|---|
| How to pay | ticket at entry; card at exit gate; cash at the machine inside the terminal | https://flyithaca.com/parking | undated | 2026-11-08 |
| Rental cars | page says several companies operate at the airport but names none; /car-rentals page not read; /rental-cars returned 404 | https://flyithaca.com/parking ; https://flyithaca.com/rental-cars (404) | | 2026-11-08 |
| Comparison with SYR | ITH long-term daily $8.00 vs SYR economy daily max $14 and garage $22 (section 7); ITH weekly $40 (long-term). My arithmetic: a one-week trip costs $40 at ITH (long-term) vs $98 at SYR economy at the daily max (7 x $14), but the SYR figure ignores any weekly rate not shown | flyithaca.com/parking vs syrairport.org/parking | | 2026-11-08 |

## 22. Storage and shipping at break (move-out market)
| Fact | Value | Source URL | Applies to | Checked |
|---|---|---|---|---|
| Big Red Shipping and Storage (BRSS) | Cornell's contracted vendor, year-round; full-service storage in a climate-controlled facility and shipping; free pickup and delivery to your room; no prices on the Cornell page; limited slots; call 607-524-3130 or brss@studentagencies.com; Cornell calls it "the most affordable in Ithaca" (Cornell's claim) | https://scl.cornell.edu/residential-life/housing/housing-details/moving-out/storage-shipping-options | spring 2026 move-out | 2026-11-08 |
| Move-out deadline | unclaimed items left when no resident is present are donated after the building closes at 2:00 pm Sunday 2026-05-17 | same | 2026 | 2026-11-08 |
| Cornell storage | Cornell itself does not provide storage; staff cannot grant building access for pickups | same | | 2026-11-08 |
| Other providers named in search | Storage Squad (https://greatguysmoving.com/movers/new-york/ithaca/storage-squad); Uncle Marty's Shipping Office on the Commons; Storage Scholars; Bolt Storage in Freeville (link in a FingerLakes1 piece) | search results and https://www.fingerlakes1.com/2026/04/01/why-cornell-students-rely-on-storage-during-summer-break-and-semester-transitions/ | 2026 | 2026-11-08 |
| Storage Scholars Ithaca page | no Ithaca price given; "2025 Avg" $172 per month marketing figure not tied to Ithaca; advises booking by early April before finals; DIY benchmark for Ithaca stated as $350 to $550+ (self-storage, truck, supplies) while its table shows other numbers: internal inconsistency; phone (336) 815-0100 | https://www.storagescholars.com/cities-we-serve/ithaca-ny | 2025-26 | 2026-11-08 |
| Storage Scholars blog general ranges (Feb 2026; company blog, marketing) | self-storage units $120 to $600 for the season; student storage services $150 to $400 with pickup; transport $40 to $100 each way; typical five boxes plus fridge $250 to $350 | search summary of https://www.storagescholars.com/blog/college-storage-cost-calculator-pricing | Feb 2026 | 2026-11-08 (secondary) |
| FingerLakes1 piece | published 2026-04-01; no prices; says Cornell enrollment about 26,000 to 27,000; many facilities offer month-to-month and climate control | https://www.fingerlakes1.com/2026/04/01/why-cornell-students-rely-on-storage-during-summer-break-and-semester-transitions/ | 2026 | 2026-11-08 |
| Gap | no Ithaca-specific dated price sample for storage found; BRSS prices not published on pages reachable | | | |

## 23. Bikeshare detail (dated 2023) and car share
| Fact | Value | Source URL | Applies to | Checked |
|---|---|---|---|---|
| Launch pricing (Cornell Sun, 2023-01-24, updated 2023-02-21) | pay as you go 15 cents per minute plus $1 unlock; day pass $20; monthly $45; annual $150 | https://cornellsun.com/2023/01/24/ithaca-bikeshare-a-comprehensive-guide-to-ithacas-newest-transportation-option/ | Jan 2023 (STALE) | 2026-11-08 |
| Later pricing | Better Bike Share July 2023: $0.50 unlock and $0.20/min (section 11): the two sources conflict because prices changed; The Ithacan reported "adds parking hubs and raises costs" (amounts not read) https://theithacan.org/46872/news/ithaca-bikeshare-adds-parking-hubs-and-raises-costs-of-use (403 for me) | | 2023 | 2026-11-08 |
| Fleet, hubs (2023) | about 100 class 1 e-bikes from Drop Mobility, top speed 16 mph; 4 hubs (Collegetown Bagels on College Ave; Oak Ave and Dryden Rd; Maplewood Apartments; Stewart and University near Alice Cook House); bikes may be left anywhere in the service area; returning to a hub waives the unlock fee next trip | same Sun URL | 2023 | 2026-11-08 |
| Fleet number conflict | 85 bikes (Better Bike Share, 2023-07) vs about 100 (Sun, 2023-01): different dates and rounding | two URLs above | 2023 | 2026-11-08 |
| Winter service | not stated in the Sun guide | Sun URL | | 2026-11-08 |
| Official site | ithacabikeshare.org named by the extract; not fetched | | | |
| Carshare history | 2008 plans: "It's My Car" $200/yr plus $4.95/hr and $0.20/mile; "Just in Case" $50/yr plus $7.95/hr and $0.20/mile (Cornell Sun 2008 via search summary https://cornellsun.com/2008/08/11/carshare-program-fosters-sustainable-transportation-ithaca); IC student rate 2010 $15 application fee; Carshare office 607-277-3210 on a 2008 notice | search summary | 2008-2010 (STALE) | 2026-11-08 |
| Carshare today | Ithaca College page says Ithaca Carshare offers 24/7 access to fuel-efficient cars, a minivan and a pickup truck (ithacacarshare.org); a Nov 2026 city notice mentions an Ithaca Carshare parking space on E Seneca St | https://www.ithaca.edu/orientation/family-and-guest-resources/transportation ; https://www.fingerlakes1.com/2026/11/03/ithaca-and-tcat-will-move-downtown-bus-stops-nov-9/ | 2026 | 2026-11-08 |
| Current carshare rates | NOT FOUND | | | 2026-11-08 |

## 24. TCAT context, Elmira link and other fare facts
| Fact | Value | Source URL | Applies to | Checked |
|---|---|---|---|---|
| Cornell share of TCAT ridership | Cornell Chronicle: about 70% of TCAT riders are Cornell community; four-year Cornell-TCAT service agreement; service levels evaluated three times a year on the five Cornell-oriented routes (article date not shown) | https://news.cornell.edu/node/279091 (search summary) | undated | 2026-11-08 |
| Uniform $1.50 fare start | uniform $1.50 adult fare ($0.75 half fare) from Aug 25, 2019 | https://cornellsun.com/2019/06/29/tcat-approves-plan-to-eliminate-geography-based-fees (search summary) | 2019 | 2026-11-08 |
| Service change rhythm | TCAT publishes schedule changes about three times a year; no fall 2026 or 2026-27 route or fare change announcement found | https://tcatbus.com/about/about-tcat/ (403; search summary) | | 2026-11-08 |
| Funding context | Ithaca-Tompkins County Transportation Council Feb 2026 agenda lists $488,031 federal funds available in state FY 26-27 and flags uncertainty | https://www.tompkinscountyny.gov/files/content/county/v/67/all-departments/ithaca-tompkins-county-transportation-council/meeting-schedule/agenda-0226-for-february-policy-committee-meeting-draft-1.pdf (search summary) | 2026 | 2026-11-08 |
| ELM to Ithaca bus | Busbud page: about $58, about 58 minutes, run by OurBus (aggregator; date unknown); an OurBus Ithaca-Elmira page appears to be a 2020-era Cornell quarantine route, so availability uncertain | https://www.busbud.com/en/poi/elmira-corning-regional-elm-airport/dr3rf6c ; https://www.ourbus.com/amp/routes/ithaca-to-elmira-cornell-university-quarantine | unknown | 2026-11-08 (search summary) |
| ELM to Ithaca drive | about 36 miles, about 45 to 46 minutes | https://www.airport.guide/kelm/ny/tompkins-co/ithaca (search summary) | | 2026-11-08 |
| CTRAN route #30 Elmira-Ithaca | exists on the Chemung transit map; fare and Ithaca leg not read | https://ridectran.com/wp-content/uploads/CTRAN-Schedule20-Final-PRD2.pdf (search summary) | | 2026-11-08 |
| Way2Go brochure | county transportation options brochure (2022) exists | https://www.tompkinscountyny.gov/ar/files2/itctc/image/Way2Go_Transportation_Options_Brochure_2022_Web.pdf (not read) | 2022 | 2026-11-08 |
| Cornell transport news | "Express service with luxury touches" Cornell Chronicle piece on C2C (date unknown, not read) | https://news.cornell.edu/node/282639 | | 2026-11-08 |

## 25. Recurring and hidden costs for a student without a car (computed from sourced rows only)
All figures are my arithmetic from the cited rows; no new sources.
| Scenario | Computation | Result | Inputs from |
|---|---|---|---|
| Cornell resident student with a car, annual permit | $752.98 permit | $752.98 for 2026-27 (about $63 per month over 12 months) | section 4 |
| Commuter permit | $359.77 | about $30 per month | section 4 |
| Annual OmniRide vs daily fares | $200 pass vs $1.50 a ride | breaks even at about 133 paid rides (200 / 1.5) | section 5a |
| Roundtrip to NYC by C2C as a student | 2 x $93.50 | $187 | section 14 |
| Roundtrip to NYC by OurBus at "from" price | 2 x $25 | $50 (cheapest advance fare; Thanksgiving week likely higher, not verified) | section 15 |
| One-week ITH parking (long-term) | 7 x $8.00 vs weekly $40.00 | weekly rate $40 is cheaper than 7 days ($56) | section 21 |
| Downtown Ithaca garage, 4 hours | 4 x $2.25 | $9.00 (under the $12 daily max) | section 19 |
| C2C change within 8 hours of departure | $30 per seat | a $93.50 ticket plus a $30 change is $123.50 | section 14 |

## 26. Coverage
Scope items: covered / thin / not found.
- Flights into ITH: thin (airlines and phone numbers; no fares; two routes only). SYR: covered for parking and routes, no fares. ELM: thin (distance and aggregator bus price only).
- NYC buses: covered for C2C (official fares), OurBus (Aug 2026 table), Greyhound (page fare), ShortLine (undated $50 and stale 2019), FlixBus (euro). Boston, Philadelphia, NJ from Ithaca: thin (NYC-origin table only; Ithaca-Princeton and Ithaca-Newark route pages exist but no fares read). Trailways: not found (named by Cornell page and Omio only; no fare, no stop).
- Airport rides: thin (taxi phone numbers; 2017 fare sample is the latest; TCAT route 32 times from a 2025 student article; no current taxi or shuttle fare found).
- Driving and parking: covered for Cornell student permits, short-term parking, fines (2023), city garages (2026), ITH and SYR airport parking. Not found: Cornell per-lot hourly rates (PDF), faculty and staff tiers, Ithaca College permit price (only a search summary of $500).
- TCAT: thin (fare $1.50 and passes from secondary sources, official site 403, route list not found; Nov 9 stop moves covered).
- Biking incl. winter: thin (2023 bikeshare prices; winter biking not found).
- Rideshare and car share: thin (2017 rideshare sample; carshare no current rate).
- Break travel and storage: thin (BRSS no price; broad ranges only from a marketing blog; no Thanksgiving 2026 shuttle found).
- Getting around without a car: partial (TCAT, bikeshare, carshare, C2C) with the price gaps above.
Public data missing or stale: C2C day-by-day schedule (table garbled), TCAT official fares, Trailways fares, taxi and Uber fares since 2017, bikeshare and carshare 2026 prices, storage quotes, Cornell lot-level rates. I did not reach the 40-source or 20-new-source depth for every scope item; several fetches were 403 (tcatbus.com, fcs.cornell.edu C2C terms, theithacan.org).

## 27. Pages read table (deepen session; read one at a time, 2026-11-08)
| URL | Result |
|---|---|
| https://fcs.cornell.edu/departments/transportation-delivery-services/campus-campus-bus-service | read; links list |
| https://fcs.cornell.edu/departments/transportation-delivery-services/campus-campus-bus-service/c2c-rates | read; fares |
| https://fcs.cornell.edu/departments/transportation-delivery-services/campus-campus-bus-service/c2c-policies-regulations | read; fees, luggage |
| https://fcs.cornell.edu/departments/transportation-delivery-services/campus-campus-bus-service/c2c-frequently-asked-questions | read |
| https://fcs.cornell.edu/departments/transportation-delivery-services/campus-campus-bus-service/c2c-departure-schedule-stop-locations | read; table garbled |
| https://fcs.cornell.edu/departments/transportation-delivery-services/campus-campus-bus-service/c2c-terms-conditions | 403 |
| https://www.tcatbus.com/ride/fare-pass-options/ | 403 |
| https://www.ourbus.com/blog/?p=6269 | read; fare table |
| https://www.ithaca.edu/orientation/family-and-guest-resources/transportation | read |
| https://www.ithaca.edu/id-office/tcat-information | read |
| https://www.ithaca.edu/orientation/orientation-faqs/parking | read; wrong page, no parking prices |
| https://www.greyhound.com/bus-routes/ithaca-ny-new-york-ny | read |
| https://fcs.cornell.edu/departments/transportation-delivery-services/parking-campus/short-term-parking-options | read |
| https://cornellsun.com/2023/01/24/ithaca-bikeshare-a-comprehensive-guide-to-ithacas-newest-transportation-option/ | read |
| https://theithacan.org/46872/news/ithaca-bikeshare-adds-parking-hubs-and-raises-costs-of-use | 403 |
| https://www.fingerlakes1.com/2025/12/19/ithaca-raises-parking-rates-downtown/ | read |
| https://www.cornellsun.com/article/2025/05/busses-trains-and-planes-getting-to-and-from-cornell | read; no prices |
| https://www.fingerlakes1.com/2026/11/06/ourbus-moves-ithaca-stop-to-south-cayuga-street-monday-as-tcat-shifts-stops/ | read |
| https://www.fingerlakes1.com/2026/11/03/ithaca-and-tcat-will-move-downtown-bus-stops-nov-9/ | read |
| https://flyithaca.com/parking | read |
| https://flyithaca.com/rental-cars | 404 |
| https://scl.cornell.edu/residential-life/housing/housing-details/moving-out/storage-shipping-options | read |
| https://www.fingerlakes1.com/2026/04/01/why-cornell-students-rely-on-storage-during-summer-break-and-semester-transitions/ | read; no prices |
| https://www.storagescholars.com/cities-we-serve/ithaca-ny | read |
| https://www.syrairport.org/parking/ | re-read; rates confirmed |
| https://www.coachusa.com/node/322 | read; 2019 data |
Also used from search summaries only (not opened): see URLs marked "search summary" in sections 14 to 24.

## Lane complete: 135 facts, 60 sources, 6200 words, 2026-11-08
