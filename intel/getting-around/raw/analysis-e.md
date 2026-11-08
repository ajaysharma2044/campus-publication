# Lane E analysis, part 5 (deepen pass, 2026-11-08; continues analysis.md, -b, -c, -d)

All "Checked" = 2026-11-08. Fetch tool summarizes pages; a checker should open each URL and confirm digits.

## 14. Dated bus fare samples read on 2026-11-08 (aggregator and operator pages)

Method: one page per route read once on 2026-11-08. Fares are what the page showed that day for the dates it displayed, not booked prices. Aggregators mix "from" prices, averages and live fares, so each row says which.

| Route | Carrier / source | Fare shown | Travel date or basis | Duration / frequency / stops | Source URL |
|---|---|---|---|---|---|
| SYR airport to Ithaca | OurBus (via checkmybus aggregator) | $48 (8:00 pm), $51 (1:05 pm), $51 (6:30 pm) | Sun 2026-11-08 | direct 1h35m to 1h40m; 3 direct trips that day; stops E Seneca St Ithaca | https://www.checkmybus.com/syracuse-ny-airport/ithaca-ny |
| Same, with transfer | unnamed carrier via Syracuse Regional Transit Center | $32 economy | Sun 2026-11-08 | 3h00 (8:35 am to 11:35 am) | same |
| Ithaca to SYR airport | OurBus route page | "from $46.7"; most fares $46.7 to $62.1; Sunday cheapest, Monday dearest | page viewed 2026-11-08 | 51.4 miles; 1h25m to 2h05m; page contradicts itself (3 buses/day vs 10); pickups North Campus (Jessup Rd behind Ganedago Hall), West Campus (West Ave across from Baker Flagpole), Cayuga St Garage; drop-off SYR Terminal A | https://www.ourbus.com/routes/ithaca-ny-to-syracuse-airport-ny |
| Ithaca to NYC | OurBus route page | "from $33" | page viewed 2026-11-08 | 9 buses/day, first 5:00 am, last 11:55 pm; 4h10m to 7h; 174.8 miles; NYC drops: GWB Bus Station Level 3 Slip 2, Hudson Yards (11th Ave, W 35-36th), Madison Ave 26th-27th | https://www.ourbus.com/routes/ithaca-ny-to-new-york-ny |
| Ithaca to NYC | Wanderu, six carriers | carrier "from": OurBus $25, Coach USA $28.98, Megabus $29, FlixBus $30, Greyhound $37, Adirondack Trailways $43. Carrier averages: Megabus $44.77, Coach USA $44.54, Trailways $57.13, OurBus $69.23, FlixBus $73.50, Greyhound $82.31 | sample week Sun 2026-11-08 to Sat 11-14; page says cheapest date Nov 19, 2026; Nov monthly average about $66; January about $41 | departures/day: OurBus 20, Megabus 8, Coach USA 13 (14 weekends), FlixBus 5, Greyhound 2, Trailways 1; page totals contradict (37, 17, 49); NYC arrivals include Port Authority, GWB, JFK T8, LGA B; Ithaca stations incl. 131 E Green St | https://www.wanderu.com/en/bus/us-ny/ithaca/us-ny/new-york/ |
| Ithaca to Boston | FlixBus only (checkmybus) | $44 to $88 (FAQ). Fri 11/6 $51, Tue 11/17 $46, Fri 11/20 $101 | fares 2026-11-04 to 11-20; page found 2026-10-18 | direct 8h05m to 12h05m; about 11 buses/day, 1:00 pm to 7:15 pm; via Syracuse RTC legs $10 + $44 | https://www.checkmybus.com/ithaca-ny/boston-ma |
| Ithaca to Philadelphia | FlixBus direct; Greyhound via Binghamton | lowest $41 (Wed 2026-11-18); FlixBus direct $44 Mon 2026-11-09 (9:00 am 9h00; 1:00 pm 7h50); Binghamton connection $9 FlixBus + $41 Greyhound | 2026-11-09 to 11-18 | connection about 1h10m longer | https://www.checkmybus.com/ithaca-ny/philadelphia-pa |

Contradictions flagged: Boston page's "lowest $44 via Syracuse transfer" does not equal its listed legs ($10 + $44 = $54). Wanderu trip totals disagree three ways. OurBus own page says "from $33" for Ithaca-NYC while Wanderu's OurBus "from" is $25 on the same day (different date basis). Aggregator figures are signals, not official prices.

### Analysis F: Ithaca to NYC fares across six carriers (Wanderu, 2026-11-08)
Question: what is the typical advertised low fare, and how spread out are average fares?
Method: use the page's six carrier "from" prices and six carrier averages; compute by hand.
"From" sorted: 25.00, 28.98, 29.00, 30.00, 37.00, 43.00. Sum = 192.98. Mean = 192.98 / 6 = $32.16. Median = (29.00 + 30.00) / 2 = $29.50. Range $25 to $43.
Averages sorted: 44.54, 44.77, 57.13, 69.23, 73.50, 82.31. Sum = 371.48. Mean = 371.48 / 6 = $61.91. Median = (57.13 + 69.23) / 2 = $63.18. Range $44.54 to $82.31.
Lowest "from" over mean average: 25 / 61.91 = 0.404, so the advertised floor is about 40% of the typical average.
OurBus share of departures: 20 / 49 = 40.8% (carrier counts summed; the page's own totals disagree).
Result: n = 6 carriers, one aggregator, one day. Advertised low about $25 to $43; averages $45 to $82. NOT a measured booked price. Wanderu claims booking about 14 days ahead is cheapest.
Caveats: averages cover unknown dates; no Thanksgiving or winter-break week sampled; one aggregator.

### Analysis G: bus cost per mile to Syracuse airport
Data: 51.4 miles (OurBus page); fares $46.7 low, $62.1 high (OurBus page); Sunday sample $48 and $51 (checkmybus).
Calculation: 46.7 / 51.4 = $0.91 per mile; 62.1 / 51.4 = $1.21; 51 / 51.4 = $0.99. Round trip low 2 x 46.7 = $93.40; high 2 x 62.1 = $124.20.
A search aggregator estimated a taxi at about $200 (unofficial, undated) and a College Confidential post mentioned an $85 shuttle (undated): neither used in the math.
Result: about $0.91 to $1.21 per mile advertised. Caveat: one route, one day.

## 15. OurBus expansion and student experience (Cornell Sun)

| Fact | Value | Source URL | Applies to | Checked |
|---|---|---|---|---|
| OurBus expansion | starting Tuesday Sept 1, 2026 (article of Sept 2 cites a Monday press release): 4 to 6 daily Ithaca-Manhattan trips, 7 days a week; new trips stop at Ithaca Commons, West Campus, North Campus; before, campus stops mostly around major breaks | https://www.cornellsun.com/article/2026/09/8kl4l6fodjwk (Coral Platt, Giselle Redmond, 2026-09-02) | fall 2026 | 2026-11-08 |
| Syracuse service | Cornell to Syracuse six days a week incl. Hancock airport and Destiny USA | same | fall 2026 | 2026-11-08 |
| Weekend routes | add Fresh Meadows (Queens), Melville (Long Island), Cortland, Binghamton, Middletown, Nanuet; start Thursday | same | fall 2026 | 2026-11-08 |
| Ridership claim | OurBus reports a 20% rise in Ithaca-NYC ridership, spring 2026 (company claim) | same | spring 2026 | 2026-11-08 |
| Why demand rose (article's framing) | higher fuel prices; the 2025 loss of ITH's direct flight to Newark | same | | 2026-11-08 |
| Attributed quote | OurBus co-founder Axel Hellman: a 20-minute walk downtown matters with luggage at early or late hours | same | | 2026-11-08 |
| OurBus background | at Cornell since 2017; a broker, owns no buses; Rally OurBus after 2021 merger; Hellman said 64,000 passengers in October 2023; said 89% of buses from Cornell on time over fall break 2023 (company claims) | https://www.cornellsun.com/article/2023/11/inside-ourbus-cornellians-preferred-method-of-travel (Dina Shlufman, 2023-11-09, updated 2024-01-21) | fall 2023 | 2026-11-08 |
| Student experiences (attributed) | Rena Weintraub '27: fall break trip arrived 4+ hours late, Wi-Fi and AC not working; Maia Mehring '27: app ETA an hour off, cancellation gives credit not cash, saw a ticket holder turned away on an overbooked bus; Hannah Friedman '25: easy booking, affordable, many empty seats | same | fall 2023 | 2026-11-08 |

## 16. Cornell MBA living-in-Ithaca page (official, "© 2026", otherwise undated)

Source: https://business.cornell.edu/students/by-program/mba-students/living-in-ithaca/ (old URL johnson.cornell.edu/.../transportation 301s here)

| Fact | Value | Checked |
|---|---|---|
| Walking and biking | many walk from downtown, hills; bike registration with Cornell no fee; showers at Sage Hall classroom level | 2026-11-08 |
| TCAT | stops in front of Sage Hall; CU ID is the pass; free first year; after that free weekday evenings after 6 pm and all weekend | 2026-11-08 |
| C2C | express to Cornell Club NYC, Weill Cornell Medicine and the F train at Roosevelt Island; pickup at Sage Hall any day; no price listed | 2026-11-08 |
| Parking | campus parking in business hours needs a permit; short-term parking for occasional visitors; Lyft, Uber and local cabs serve the area | 2026-11-08 |
| Airports | ITH served by Delta and United; Syracuse about 1h15 away with more airlines; ground transport must be arranged in advance | 2026-11-08 |

## 17. Student-thread patterns (College Confidential, small sample)

Sample: 2 Cornell threads read in full by the fetch tool. n is tiny; this is not a representative count.

| Thread | Dates | Replies | URL |
|---|---|---|---|
| "Should I bring a car?" | 2016-04-23 to 2016-05-13 | 15 | https://talk.collegeconfidential.com/t/should-i-bring-a-car/1811430 |
| "Traveling to and from Cornell" | 2014-07-05 to 2014-07-07 | 12 | https://talk.collegeconfidential.com/t/traveling-to-and-from-cornell/1599797 |

Tally for "should I bring a car" (distinct posters, my reading): against 6 (Ranza123, blprof, jfx246, Wittmann, 3rdsontocollege, oldfort for the younger daughter), for 3 (KloudKoder, oldfort for the older daughter after an off-campus job, mdcmom for groceries). So 6 of 9 argument-holders (67%) advised against; oldfort counted in both columns, so 9 argument entries from 8 posters.
Specific attributed claims: blprof cited a $750/year North Campus pass (compare official $752.98 in 2026, +0.4%: 752.98/750 = 1.004); jfx246 said classroom buildings lack their own parking; one poster said Ithaca Carshare required 18+ with a two-year license (poster's claim, 2016, unverified).
2014 thread attributed prices: Greyhound Ithaca-Rochester about $25 (cbear2017); Syracuse shuttle $25 per ticket sold 30 days ahead (comom2013); campus-to-ITH bus free (comom2013); flying to NYC about $200 cheaper than flying to Ithaca (Latuza). All 12 years stale.
Caveats: 2014 and 2016 posts; self-selected parents; counts are of arguments, not of students.
