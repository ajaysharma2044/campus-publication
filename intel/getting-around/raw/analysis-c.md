# Lane E analysis, part 3 (appended 2026-11-08; continues analysis.md and analysis-b.md)

## 6. More dated sources read

| Fact | Value | Source URL | Applies to | Checked |
|---|---|---|---|---|
| Taxi vs Uber, College to The Commons | taxi city base rate $11; UberX $7.35 (Mon 5 pm), $9.59 (Sat 1:45 am); UberXL $10.50 / $14.18 | https://theithacan.org/news/ride-hailing-services-slightly-less-expensive-than-taxis-in-ithaca/ (The Ithacan, Celisa Calacal, 2017-09-19) | 2017 only; stale | 2026-11-08 |
| Taxi vs Uber, College to airport | taxi base $19; UberX $17.49 (Tue 12:30 pm); UberXL $27.56 | same | 2017 only; stale | 2026-11-08 |
| Attributed opinion | Ithaca Dispatch co-owner John Kadar called surge pricing "very expensive"; Uber driver Mark Anbinder said some riders waited about half an hour | same | 2017 | 2026-11-08 |
| Ithaca Bikeshare pricing | unlock $1.50 (was $1), $0.20/min (was $0.15), day pass $20, monthly $45, yearly $150, $1 fee if not parked in a hub | https://theithacan.org/46872/news/ithaca-bikeshare-adds-parking-hubs-and-raises-costs-of-use (2023-03-22) | 2023; current prices NOT FOUND | 2026-11-08 |
| Bikeshare winter operation, Cornell student discount | not found in that article; Cornell Chronicle 2018-era page "Bike-share program gives Cornellians a free ride" is a different (Lime-era) program: https://news.cornell.edu/node/270417 | not read | | |
| Ithaca Carshare current rates | NOT FOUND (search returned 2008-2010 pages only: $4.95/hr + $0.20/mile in 2010 IC plan) | https://web2.ithaca.edu/intercom-archive/article.php/20100826141953733/print.html (snippet) | 2010 | 2026-11-08 |
| Williams St / Stewart Ave lot | permits sold out within hours of Aug first-come sale; ~"$700+" annual permit; student Deana Druz '24 and Sasha Planinsic '25 described daily hunting (their words, as quoted by the Sun); Senior Director Bridgette Brady blamed old permits still valid until Aug 31 | https://www.cornellsun.com/article/2023/09/williams-street-parking-lot-struggles-to-accommodate-students (2023-09-07) | fall 2023 | 2026-11-08 |
| Student Sun guide | NYC options: C2C, FlixBus, OurBus, Megabus, Wanderu to compare; Syracuse via Student Assembly shuttle or bus; Route 32 weekday service to ITH, weekends drop-off only (author's reading); author reports delays and being left at stations | https://www.cornellsun.com/article/2025/05/busses-trains-and-planes-getting-to-and-from-cornell (Melanie Delfosse, 2025-05-04) | 2025-05 anecdote | 2026-11-08 |
| Admissions FAQ | "six regional airports" within short driving distance, list not on page | https://faq.enrollment.cornell.edu/kb/article/319-where-is-the-nearest-airport/ (corpus, fetched 2026-11-06) | 2026-11 | 2026-11-08 |
| C2C finance rule for employees | university pricing requires a profile on C2C website; C2C is the preferred mode between Ithaca and the NYC campuses | https://finance.cornell.edu/travel/transportation | 2026-11-08 | 2026-11-08 |
| Failed fetches | tcatbus.com (403 twice), fcs.cornell.edu/node/17809 (403), flyithaca.com/ground/bus-service (404), 32_Late-Fall.pdf (404), ourbus.com route page (JS only, no data), web.archive.org (blocked by fetch tool) | | | 2026-11-08 |

## 7. Analysis C: what a student's year of getting around costs, by situation

Question: how much does a Cornell student spend per academic year on local transport, with a car versus without?
Method: use only the official prices read above; list every input; show arithmetic; leave out any item whose price was not found rather than guess.

Inputs (all from https://fcs.cornell.edu/departments/transportation-delivery-services/parking-campus/parking-students, page undated, read 2026-11-08, unless stated):
- Resident permit R = $752.98. Commuter B permit C = $359.77. Motorcycle M = $120.01.
- TCAT is free to first-years (sustainable.cornell.edu bus-commuting page); after the first year free after 6 pm weekdays and all weekend; otherwise discounted pass priced at myparking.cornell.edu (price NOT FOUND).
- Ithaca Bikeshare yearly pass Y = $150 (2023 price, The Ithacan 2023-03-22).
- Fine for no permit/payment: $50 (+$10 if unpaid after 10 days), 2023-09-04.

| Situation | Items | Calculation | Annual total | Confidence |
|---|---|---|---|---|
| A. First-year, no car, TCAT only | TCAT free | $0 | $0 plus any C2C/airport rides | official text |
| B. Upper-year, no car, TCAT evenings/weekends only | $0 for free hours; daytime weekday rides at $1.50 cash (snippet, unverified) | $1.50 x rides | depends on use; 100 weekday daytime rides = $150.00 | estimate; assumes cash fare |
| C. No car, bikeshare yearly pass | $150 | $150 | $150 (2023 price) | dated 2023 |
| D. Resident student with car | permit | $752.98 | $752.98 | official, undated page |
| E. Commuting student with B permit | permit | $359.77 | $359.77 | official, undated page |
| F. Car + one unpaid-permit ticket | D + fine | $752.98 + $50.00 | $802.98 | arithmetic on 2 dated figures |

Derived comparisons (estimates, arithmetic shown):
- Resident permit per month if held 12 months: $752.98 / 12 = $62.75. Per day over 365: $752.98 / 365 = $2.06.
- Resident permit vs bikeshare yearly: $752.98 / $150 = 5.02, about five times.
- B permit vs bikeshare: $359.77 / $150 = 2.40.
- Break-even versus taxis: using the 2017 base taxi fare College-to-airport $19, $752.98 / $19 = 39.6, so about 40 one-way airport taxi rides cost the same as one resident permit at 2017 prices. This mixes a 2026 permit with a 2017 taxi price and is not a measurement; it shows scale only.
- Break-even versus TCAT cash: $752.98 / $1.50 = 502 rides at the cash fare.
Result: on the figures found, the cheapest local setup is first-year TCAT (free); a car permit is the largest recurring local transport line ($360 to $753) before gas, insurance and fines (not priced here).
Sample size: none; these are price-list calculations as of 2026-11-08.
Caveats: parking page undated (summarized by the fetch tool; digits should be re-read); permit availability is limited and first come, first served (sold out within hours at the Williams St lot in 2023 per the Sun); 2026/27 sales opened Aug 4, 2026 per search snippet; C2C base fare, OmniRide price, TCAT current fare and current bikeshare prices not confirmed; insurance, gas and campus-adjacent private parking not included.

## 8. Analysis D: ITH versus other airports, what we can and cannot compute
- Scheduled nonstops confirmed on the airport's own airlines page (https://flyithaca.com/airlines, undated, read 2026-11-08): Delta to JFK (daily) and United to IAD. American Charlotte unresolved (Feb 2026 snippet said Dec 22 start; the airlines page does not list American).
- Airport parking cost for a trip: see 2c in analysis-b.md ($40 per week long-term).
- Not computed: fares ITH vs SYR vs ELM and drive-time-plus-fare comparisons. Reason: no dated fare samples or official shuttle prices were found. Next step for another pass: sample Google Flights for a fixed date pair (record each fare, route, date and time of the query), and read Cornell Student Assembly shuttle page and SYR ground-transportation page.

## 9. Open items for the next pass (nothing invented; each is "not found")
1. TCAT current fare and pass prices (tcatbus.com 403; try Ithaca College page https://www.ithaca.edu/id-office/tcat-information, Downtown Ithaca page https://www.downtownithaca.com/five-ways-to-pay-your-tcat-fare/).
2. C2C base fares by route, Boston and Philadelphia service (page links to a "C2C Rates" page not read; the $75 and $50 figures are unverified snippets).
3. Whether first-year students may bring cars (no rule found on FCS student page).
4. Route 32 official timetable (PDF URLs 404; current TCAT route page not found).
5. Current Ithaca Bikeshare, Carshare, taxi (City of Ithaca base rates) prices.
6. Bus fare samples (FlixBus, OurBus, Greyhound, Trailways) to NYC, Boston, Philadelphia, EWR: no official price pages readable by the fetch tool; need dated samples.
7. Thread counts (Reddit/Student Doctor/College Confidential) for "do I need a car at Cornell": not started; candidate threads from demand file: https://forums.studentdoctor.net/threads/cars.962192/ and reddit mirror https://reddit.sentinel-team.org/subreddits/Cornell/snapshots/2026-05-20T16%3A45%3A27.30298Z (unread).
8. Corpus note: corpus has no TCAT or parking-price pages for this topic (only FCS announcements 2018-2025 and admissions FAQ 319).
