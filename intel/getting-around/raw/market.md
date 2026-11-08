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
