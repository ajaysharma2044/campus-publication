---
title: "Thanksgiving bus fare premium from Ithaca, 2026"
meta: "Lowest advertised Ithaca bus fares for 51 priced dates on 3 routes, read Nov 8, 2026: Thanksgiving week ran 27.9% to 37.9% higher, mean +33.4%."
topic: getting-around
updated: 2026-11-08
as_of: 2026-11-08
sample_size: 63
method: "Day-by-day lowest one-way fares copied from four checkmybus route pages on 2026-11-08, split into before Thanksgiving week and Thanksgiving week, averaged per period, and compared as a percent change."
queue_id: q-getting-around-0066
kind: dataset
readers: [low-budget, first-year, beyond-nyc, far-from-home]
brief: intel/getting-around/brief.md
sources:
  - {url: "https://www.checkmybus.com/ithaca-ny/binghamton-ny", title: "checkmybus: Ithaca, NY to Binghamton, NY", accessed: "2026-11-08"}
  - {url: "https://www.checkmybus.com/ithaca-ny/rochester-ny", title: "checkmybus: Ithaca, NY to Rochester, NY", accessed: "2026-11-08"}
  - {url: "https://www.checkmybus.com/ithaca-ny/washington-dc", title: "checkmybus: Ithaca, NY to Washington, DC", accessed: "2026-11-08"}
  - {url: "https://www.checkmybus.com/ithaca-ny/syracuse-ny", title: "checkmybus: Ithaca, NY to Syracuse, NY", accessed: "2026-11-08"}
  - {url: "https://www.ourbus.com/blog/?p=6269", title: "OurBus blog: NYC to Ithaca schedule and peak travel days", accessed: "2026-11-08"}
---

On three bus routes out of Ithaca, the cheapest seat for Thanksgiving week (Mon Nov 23 to Fri Nov 27, 2026) cost 27.9% to 37.9% more than the cheapest seat earlier in November. The average jump was +33.4%. Those figures come from 51 dated fares on the Binghamton, Rochester and Washington DC routes, all read on Nov 8, 2026, two to three weeks before the trips.

In dollars: the lowest Binghamton fare went from an average of $11.10 to $14.20. Rochester went from $19.00 to $25.50, and DC from $67.71 to $93.40. The single priciest day on Rochester and on DC was Wednesday Nov 25, the day before Thanksgiving. [OurBus also names that Wednesday as a peak travel day](https://www.ourbus.com/blog/?p=6269).

This table is for anyone paying their own way home for the break. That includes first-years booking a holiday bus for the first time and students headed past New York City to Philadelphia, DC or Boston. It also helps if you fly out of Syracuse or Rochester and need a bus to connect. NYC fares were not sampled. The NYC guide covers that route.

## Summary by route

| Route | Fares before the week | Mean before | Fares in the week | Mean in the week | Premium | Mean, all dates | Source |
|---|---|---|---|---|---|---|---|
| Ithaca to Binghamton | 10 (Nov 7 to 20) | $11.10 | 5 (Nov 23 to 27) | $14.20 | +27.9% | $12.13 (median $13), n = 15 | [checkmybus](https://www.checkmybus.com/ithaca-ny/binghamton-ny) |
| Ithaca to Rochester | 11 (Nov 3 to 20) | $19.00 | 6 (Nov 21 to 27) | $25.50 | +34.2% | $21.29, n = 17 | [checkmybus](https://www.checkmybus.com/ithaca-ny/rochester-ny) |
| Ithaca to Washington DC | 14 (Nov 7 to 21) | $67.71 | 5 (Nov 23 to 27) | $93.40 | +37.9% | $74.47, n = 19 | [checkmybus](https://www.checkmybus.com/ithaca-ny/washington-dc) |
| Three routes, unweighted | 35 | | 16 | | +33.4% | 51 priced dates | Our calc |
| Ithaca to Syracuse (not split) | | | | | | $26.00 (median $26), n = 12 | [checkmybus](https://www.checkmybus.com/ithaca-ny/syracuse-ny) |

All fares are one way, in US dollars, read on 2026-11-08.

## Method

1. On 2026-11-08, open the checkmybus route page for each route: [Binghamton](https://www.checkmybus.com/ithaca-ny/binghamton-ny), [Rochester](https://www.checkmybus.com/ithaca-ny/rochester-ny), [Washington DC](https://www.checkmybus.com/ithaca-ny/washington-dc) and [Syracuse](https://www.checkmybus.com/ithaca-ny/syracuse-ny).
2. Copy the day-by-day "lowest fare" table for each travel date shown. Leave out dates with no fare. On DC that means Nov 13, 22 and 28.
3. Treat Nov 23 to 27 as Thanksgiving week. Thanksgiving Day 2026 is Thursday Nov 26.
4. Split each route's dates into "before" and "Thanksgiving week." Binghamton has no fares for Nov 21 or 22. Rochester counts Nov 21 in Thanksgiving week. DC counts Nov 21 as before. Each row in the table below shows which group it fell in.
5. Average each group:
   - Binghamton before: 111 / 10 = $11.10. Week: 71 / 5 = $14.20.
   - Rochester before: 209 / 11 = $19.00. Week: 153 / 6 = $25.50.
   - DC before: 948 / 14 = $67.71. Week: 467 / 5 = $93.40.
6. Divide the week mean by the before mean:
   - Binghamton: 14.20 / 11.10 = 1.279, so +27.9%.
   - Rochester: 25.50 / 19.00 = 1.342, so +34.2%.
   - DC: 93.40 / 67.71 = 1.379, so +37.9%.
7. Average the three premiums without weighting: (27.93 + 34.21 + 37.93) / 3 = 100.07 / 3 = 33.4% (unrounded premiums; the rounded 27.9, 34.2 and 37.9 would give 33.3%).
8. All-date means: Binghamton 182 / 15 = $12.13 (median $13). Rochester 362 / 17 = $21.29. DC 1,415 / 19 = $74.47.
9. Syracuse: 12 fares, sum 312, mean $26.00, median $26. Sorted: 10, 13, 15, 20, 24, 25, 27, 27, 33, 36, 41, 41. It has no before and after split, because the page gives two prices for Nov 8: $41 in its table and $12 in its listing.

## The table

Every observation, matching `thanksgiving-bus-fare-premium-ithaca-2026.csv` row for row. "lowest_fare" is the cheapest one-way seat the page showed for that travel date, in usd_one_way.

| route | travel_date | weekday | period | lowest_fare | unit | read_date | source_url | notes |
|---|---|---|---|---|---|---|---|---|
| Ithaca to Binghamton | 2026-11-07 | Saturday | before_thanksgiving_week | 9 | usd_one_way | 2026-11-08 | https://www.checkmybus.com/ithaca-ny/binghamton-ny | |
| Ithaca to Binghamton | 2026-11-08 | Sunday | before_thanksgiving_week | 14 | usd_one_way | 2026-11-08 | https://www.checkmybus.com/ithaca-ny/binghamton-ny | |
| Ithaca to Binghamton | 2026-11-10 | Tuesday | before_thanksgiving_week | 9 | usd_one_way | 2026-11-08 | https://www.checkmybus.com/ithaca-ny/binghamton-ny | |
| Ithaca to Binghamton | 2026-11-12 | Thursday | before_thanksgiving_week | 14 | usd_one_way | 2026-11-08 | https://www.checkmybus.com/ithaca-ny/binghamton-ny | |
| Ithaca to Binghamton | 2026-11-14 | Saturday | before_thanksgiving_week | 8 | usd_one_way | 2026-11-08 | https://www.checkmybus.com/ithaca-ny/binghamton-ny | |
| Ithaca to Binghamton | 2026-11-16 | Monday | before_thanksgiving_week | 8 | usd_one_way | 2026-11-08 | https://www.checkmybus.com/ithaca-ny/binghamton-ny | |
| Ithaca to Binghamton | 2026-11-17 | Tuesday | before_thanksgiving_week | 12 | usd_one_way | 2026-11-08 | https://www.checkmybus.com/ithaca-ny/binghamton-ny | |
| Ithaca to Binghamton | 2026-11-18 | Wednesday | before_thanksgiving_week | 9 | usd_one_way | 2026-11-08 | https://www.checkmybus.com/ithaca-ny/binghamton-ny | |
| Ithaca to Binghamton | 2026-11-19 | Thursday | before_thanksgiving_week | 13 | usd_one_way | 2026-11-08 | https://www.checkmybus.com/ithaca-ny/binghamton-ny | |
| Ithaca to Binghamton | 2026-11-20 | Friday | before_thanksgiving_week | 15 | usd_one_way | 2026-11-08 | https://www.checkmybus.com/ithaca-ny/binghamton-ny | |
| Ithaca to Binghamton | 2026-11-23 | Monday | thanksgiving_week | 15 | usd_one_way | 2026-11-08 | https://www.checkmybus.com/ithaca-ny/binghamton-ny | |
| Ithaca to Binghamton | 2026-11-24 | Tuesday | thanksgiving_week | 12 | usd_one_way | 2026-11-08 | https://www.checkmybus.com/ithaca-ny/binghamton-ny | |
| Ithaca to Binghamton | 2026-11-25 | Wednesday | thanksgiving_week | 16 | usd_one_way | 2026-11-08 | https://www.checkmybus.com/ithaca-ny/binghamton-ny | |
| Ithaca to Binghamton | 2026-11-26 | Thursday | thanksgiving_week | 14 | usd_one_way | 2026-11-08 | https://www.checkmybus.com/ithaca-ny/binghamton-ny | Thanksgiving Day |
| Ithaca to Binghamton | 2026-11-27 | Friday | thanksgiving_week | 14 | usd_one_way | 2026-11-08 | https://www.checkmybus.com/ithaca-ny/binghamton-ny | |
| Ithaca to Rochester | 2026-11-03 | Tuesday | before_thanksgiving_week | 17 | usd_one_way | 2026-11-08 | https://www.checkmybus.com/ithaca-ny/rochester-ny | |
| Ithaca to Rochester | 2026-11-07 | Saturday | before_thanksgiving_week | 18 | usd_one_way | 2026-11-08 | https://www.checkmybus.com/ithaca-ny/rochester-ny | |
| Ithaca to Rochester | 2026-11-08 | Sunday | before_thanksgiving_week | 22 | usd_one_way | 2026-11-08 | https://www.checkmybus.com/ithaca-ny/rochester-ny | |
| Ithaca to Rochester | 2026-11-09 | Monday | before_thanksgiving_week | 18 | usd_one_way | 2026-11-08 | https://www.checkmybus.com/ithaca-ny/rochester-ny | |
| Ithaca to Rochester | 2026-11-10 | Tuesday | before_thanksgiving_week | 21 | usd_one_way | 2026-11-08 | https://www.checkmybus.com/ithaca-ny/rochester-ny | |
| Ithaca to Rochester | 2026-11-11 | Wednesday | before_thanksgiving_week | 17 | usd_one_way | 2026-11-08 | https://www.checkmybus.com/ithaca-ny/rochester-ny | |
| Ithaca to Rochester | 2026-11-12 | Thursday | before_thanksgiving_week | 21 | usd_one_way | 2026-11-08 | https://www.checkmybus.com/ithaca-ny/rochester-ny | |
| Ithaca to Rochester | 2026-11-14 | Saturday | before_thanksgiving_week | 17 | usd_one_way | 2026-11-08 | https://www.checkmybus.com/ithaca-ny/rochester-ny | |
| Ithaca to Rochester | 2026-11-16 | Monday | before_thanksgiving_week | 17 | usd_one_way | 2026-11-08 | https://www.checkmybus.com/ithaca-ny/rochester-ny | |
| Ithaca to Rochester | 2026-11-19 | Thursday | before_thanksgiving_week | 18 | usd_one_way | 2026-11-08 | https://www.checkmybus.com/ithaca-ny/rochester-ny | |
| Ithaca to Rochester | 2026-11-20 | Friday | before_thanksgiving_week | 23 | usd_one_way | 2026-11-08 | https://www.checkmybus.com/ithaca-ny/rochester-ny | |
| Ithaca to Rochester | 2026-11-21 | Saturday | thanksgiving_week | 26 | usd_one_way | 2026-11-08 | https://www.checkmybus.com/ithaca-ny/rochester-ny | Counted in Thanksgiving week for Rochester only; the DC series counts Nov 21 as before |
| Ithaca to Rochester | 2026-11-23 | Monday | thanksgiving_week | 24 | usd_one_way | 2026-11-08 | https://www.checkmybus.com/ithaca-ny/rochester-ny | |
| Ithaca to Rochester | 2026-11-24 | Tuesday | thanksgiving_week | 26 | usd_one_way | 2026-11-08 | https://www.checkmybus.com/ithaca-ny/rochester-ny | |
| Ithaca to Rochester | 2026-11-25 | Wednesday | thanksgiving_week | 30 | usd_one_way | 2026-11-08 | https://www.checkmybus.com/ithaca-ny/rochester-ny | Highest Rochester fare in the series |
| Ithaca to Rochester | 2026-11-26 | Thursday | thanksgiving_week | 21 | usd_one_way | 2026-11-08 | https://www.checkmybus.com/ithaca-ny/rochester-ny | Thanksgiving Day |
| Ithaca to Rochester | 2026-11-27 | Friday | thanksgiving_week | 26 | usd_one_way | 2026-11-08 | https://www.checkmybus.com/ithaca-ny/rochester-ny | |
| Ithaca to Washington DC | 2026-11-07 | Saturday | before_thanksgiving_week | 61 | usd_one_way | 2026-11-08 | https://www.checkmybus.com/ithaca-ny/washington-dc | |
| Ithaca to Washington DC | 2026-11-08 | Sunday | before_thanksgiving_week | 72 | usd_one_way | 2026-11-08 | https://www.checkmybus.com/ithaca-ny/washington-dc | |
| Ithaca to Washington DC | 2026-11-09 | Monday | before_thanksgiving_week | 53 | usd_one_way | 2026-11-08 | https://www.checkmybus.com/ithaca-ny/washington-dc | |
| Ithaca to Washington DC | 2026-11-10 | Tuesday | before_thanksgiving_week | 59 | usd_one_way | 2026-11-08 | https://www.checkmybus.com/ithaca-ny/washington-dc | |
| Ithaca to Washington DC | 2026-11-11 | Wednesday | before_thanksgiving_week | 89 | usd_one_way | 2026-11-08 | https://www.checkmybus.com/ithaca-ny/washington-dc | |
| Ithaca to Washington DC | 2026-11-12 | Thursday | before_thanksgiving_week | 75 | usd_one_way | 2026-11-08 | https://www.checkmybus.com/ithaca-ny/washington-dc | No fare shown for Nov 13 |
| Ithaca to Washington DC | 2026-11-14 | Saturday | before_thanksgiving_week | 59 | usd_one_way | 2026-11-08 | https://www.checkmybus.com/ithaca-ny/washington-dc | |
| Ithaca to Washington DC | 2026-11-15 | Sunday | before_thanksgiving_week | 89 | usd_one_way | 2026-11-08 | https://www.checkmybus.com/ithaca-ny/washington-dc | |
| Ithaca to Washington DC | 2026-11-16 | Monday | before_thanksgiving_week | 51 | usd_one_way | 2026-11-08 | https://www.checkmybus.com/ithaca-ny/washington-dc | |
| Ithaca to Washington DC | 2026-11-17 | Tuesday | before_thanksgiving_week | 49 | usd_one_way | 2026-11-08 | https://www.checkmybus.com/ithaca-ny/washington-dc | Lowest DC fare in the series |
| Ithaca to Washington DC | 2026-11-18 | Wednesday | before_thanksgiving_week | 78 | usd_one_way | 2026-11-08 | https://www.checkmybus.com/ithaca-ny/washington-dc | |
| Ithaca to Washington DC | 2026-11-19 | Thursday | before_thanksgiving_week | 81 | usd_one_way | 2026-11-08 | https://www.checkmybus.com/ithaca-ny/washington-dc | |
| Ithaca to Washington DC | 2026-11-20 | Friday | before_thanksgiving_week | 65 | usd_one_way | 2026-11-08 | https://www.checkmybus.com/ithaca-ny/washington-dc | |
| Ithaca to Washington DC | 2026-11-21 | Saturday | before_thanksgiving_week | 67 | usd_one_way | 2026-11-08 | https://www.checkmybus.com/ithaca-ny/washington-dc | Counted as before for DC; the Rochester series counts Nov 21 in Thanksgiving week; no fare shown for Nov 22 |
| Ithaca to Washington DC | 2026-11-23 | Monday | thanksgiving_week | 89 | usd_one_way | 2026-11-08 | https://www.checkmybus.com/ithaca-ny/washington-dc | |
| Ithaca to Washington DC | 2026-11-24 | Tuesday | thanksgiving_week | 92 | usd_one_way | 2026-11-08 | https://www.checkmybus.com/ithaca-ny/washington-dc | |
| Ithaca to Washington DC | 2026-11-25 | Wednesday | thanksgiving_week | 100 | usd_one_way | 2026-11-08 | https://www.checkmybus.com/ithaca-ny/washington-dc | Highest DC fare in the series |
| Ithaca to Washington DC | 2026-11-26 | Thursday | thanksgiving_week | 97 | usd_one_way | 2026-11-08 | https://www.checkmybus.com/ithaca-ny/washington-dc | Thanksgiving Day |
| Ithaca to Washington DC | 2026-11-27 | Friday | thanksgiving_week | 89 | usd_one_way | 2026-11-08 | https://www.checkmybus.com/ithaca-ny/washington-dc | No fare shown for Nov 28 |
| Ithaca to Syracuse | | | not_split | 10 | usd_one_way | 2026-11-08 | https://www.checkmybus.com/ithaca-ny/syracuse-ny | Page order 1 of 12; series covers travel dates 2026-11-06 to 2026-11-26; per-row dates not recorded |
| Ithaca to Syracuse | | | not_split | 41 | usd_one_way | 2026-11-08 | https://www.checkmybus.com/ithaca-ny/syracuse-ny | Page order 2 of 12; per-row dates not recorded |
| Ithaca to Syracuse | | | not_split | 24 | usd_one_way | 2026-11-08 | https://www.checkmybus.com/ithaca-ny/syracuse-ny | Page order 3 of 12; per-row dates not recorded |
| Ithaca to Syracuse | | | not_split | 15 | usd_one_way | 2026-11-08 | https://www.checkmybus.com/ithaca-ny/syracuse-ny | Page order 4 of 12; per-row dates not recorded |
| Ithaca to Syracuse | | | not_split | 27 | usd_one_way | 2026-11-08 | https://www.checkmybus.com/ithaca-ny/syracuse-ny | Page order 5 of 12; per-row dates not recorded |
| Ithaca to Syracuse | | | not_split | 20 | usd_one_way | 2026-11-08 | https://www.checkmybus.com/ithaca-ny/syracuse-ny | Page order 6 of 12; per-row dates not recorded |
| Ithaca to Syracuse | | | not_split | 27 | usd_one_way | 2026-11-08 | https://www.checkmybus.com/ithaca-ny/syracuse-ny | Page order 7 of 12; per-row dates not recorded |
| Ithaca to Syracuse | | | not_split | 13 | usd_one_way | 2026-11-08 | https://www.checkmybus.com/ithaca-ny/syracuse-ny | Page order 8 of 12; per-row dates not recorded |
| Ithaca to Syracuse | | | not_split | 36 | usd_one_way | 2026-11-08 | https://www.checkmybus.com/ithaca-ny/syracuse-ny | Page order 9 of 12; per-row dates not recorded |
| Ithaca to Syracuse | | | not_split | 33 | usd_one_way | 2026-11-08 | https://www.checkmybus.com/ithaca-ny/syracuse-ny | Page order 10 of 12; per-row dates not recorded |
| Ithaca to Syracuse | | | not_split | 41 | usd_one_way | 2026-11-08 | https://www.checkmybus.com/ithaca-ny/syracuse-ny | Page order 11 of 12; per-row dates not recorded |
| Ithaca to Syracuse | | | not_split | 25 | usd_one_way | 2026-11-08 | https://www.checkmybus.com/ithaca-ny/syracuse-ny | Page order 12 of 12; per-row dates not recorded |

## Caveats

- **Small sample, one capture.** There are 63 fares in all: 51 on the three split routes (15 + 17 + 19) and 12 on Syracuse. They come from one aggregator, read on one day (2026-11-08). The premium averages three routes without weighting.
- **Advertised floors, not fares paid.** Each number is the cheapest seat the page showed for that date. A typical fare runs higher. On Ithaca to NYC, the cheapest advertised seat was about 40% of a typical average fare in a Nov 8 reading (brief 10.6).
- **Prices can still rise.** Thanksgiving-week dates were two to three weeks out when read. Fares may climb further as seats sell, so +33% is a floor-to-floor gap at that point, not a final figure.
- **Uneven "before" sets.** The before groups mix weekdays and weekends differently by route. Rochester counts Sat Nov 21 in Thanksgiving week and DC counts it as before. Binghamton has no Nov 21 or 22 fare.
- **NYC not sampled.** Ithaca to New York City is not in this table. Applying +33% to NYC fares is an assumption, not a measurement.
- **Syracuse not split.** The page gives two prices for Nov 8 ($41 in its table, $12 in its listing), so Syracuse shows a mean and median only. Not in the brief: the travel date of each Syracuse fare.
- **No return trips.** Sunday Nov 29 and the days after the break are not in the sample. Not in the brief: fares for the return weekend.
- Not in the brief: booked fares, carrier names for each daily low, Boston, Philadelphia and Toronto day-by-day series, and Cornell's 2026-27 break calendar. Thanksgiving week here is Nov 23 to 27, built around Thanksgiving Day on Thu Nov 26.

## How to cite

Footnote Daily, "Thanksgiving bus fare premium from Ithaca, 2026," dataset, updated 2026-11-08, observations read 2026-11-08 from checkmybus route pages (n = 63; 51 used for the premium). Data file: thanksgiving-bus-fare-premium-ithaca-2026.csv.

## Change log

- 2026-11-08: first release.

## Related guides

- [Getting to Ithaca and around Cornell, 2026-27](/getting-around/getting-to-ithaca-and-around-cornell/), the topic's main guide
- [Cornell Thanksgiving travel: when to book and what it costs](/getting-around/cornell-thanksgiving-break-bus-tickets-when-to-book/)
- [The cheapest ways to get home and around Cornell](/getting-around/cheapest-ways-to-get-around-cornell/)
- [Getting to and around Ithaca as a Cornell first-year](/getting-around/getting-around-cornell-first-year/)
- [Ithaca to Boston, Philadelphia, DC or Toronto by bus](/getting-around/ithaca-bus-to-boston-philadelphia-dc-toronto/)
- [NYC to Cornell by bus: C2C, OurBus, FlixBus, Greyhound](/getting-around/nyc-to-cornell-bus-c2c-ourbus-flixbus-greyhound/)
- [Flying home from Cornell: airports, rides, bags, timing](/getting-around/flying-home-from-cornell-airports-rides/)
- [Staying in Ithaca over Cornell breaks: housing, food, rides](/getting-around/staying-in-ithaca-over-cornell-breaks/)
- [All getting-around guides](/getting-around/)
