---
title: "Cornell bus home cost calculator: C2C vs OurBus, FlixBus"
meta: "Enter round trips a year, NetID or public fare, Thanksgiving and bags; get your year's bus cost home on C2C, OurBus, FlixBus and Greyhound, 2026 fares."
topic: getting-around
updated: 2026-11-08
numbers_as_of: 2026-11-08
queue_id: q-getting-around-0059
kind: tool
readers: [first-year, upper-year-no-car, low-budget, parent, international]
brief: intel/getting-around/brief.md
sources:
  - {url: "https://fcs.cornell.edu/departments/transportation-delivery-services/campus-campus-bus-service/c2c-rates", title: "Cornell FCS: C2C rates", accessed: "2026-11-08"}
  - {url: "https://fcs.cornell.edu/departments/transportation-delivery-services/campus-campus-bus-service/c2c-policies-regulations", title: "Cornell FCS: C2C policies and regulations", accessed: "2026-11-08"}
  - {url: "https://www.wanderu.com/en/bus/us-ny/ithaca/us-ny/new-york/", title: "Wanderu: Ithaca to New York bus", accessed: "2026-11-08"}
  - {url: "https://www.checkmybus.com/ithaca-ny/binghamton-ny", title: "CheckMyBus: Ithaca to Binghamton", accessed: "2026-11-08"}
  - {url: "https://www.checkmybus.com/ithaca-ny/rochester-ny", title: "CheckMyBus: Ithaca to Rochester", accessed: "2026-11-08"}
  - {url: "https://www.checkmybus.com/ithaca-ny/washington-dc", title: "CheckMyBus: Ithaca to Washington DC", accessed: "2026-11-08"}
  - {url: "https://www.ourbus.com/colleges/ithaca-ny-c-cornell-university", title: "OurBus: Cornell University page", accessed: "2026-11-07"}
  - {url: "https://www.cornellsun.com/2024/02/01/got-baggage-inside-cornells-luggage-transport-woes", title: "Cornell Daily Sun: Got baggage? Inside Cornell's luggage transport woes", accessed: "2026-11-08"}
  - {url: "https://www.greyhound.com/bus-routes/ithaca-ny-new-york-ny", title: "Greyhound: Ithaca to New York", accessed: "2026-11-08"}
  - {url: "https://www.ourbus.com/routes/ithaca-ny-to-new-york-ny", title: "OurBus: Ithaca to New York route", accessed: "2026-11-08"}
---

This calculator adds up what your bus trips between Cornell and New York City cost for the school year. Pick how many round trips you take, whether you ride C2C with a NetID or at the public fare, which commercial bus you would take instead, whether one trip is at Thanksgiving, and how many large bags you bring. It gives the year's total on Cornell's Campus-to-Campus (C2C) bus and on OurBus, FlixBus and Greyhound, each at the cheapest advertised seat and at the average fare, plus how much more C2C costs, what Thanksgiving adds, and the bag fees we have prices for. With the defaults (4 round trips, NetID, one Thanksgiving trip, 1 bag), C2C costs $748 and OurBus $216.65 at the floor or about $599.95 at the average.

```tool cornell-bus-home-cost-calculator
```

## Who it is for

- **First-years** deciding between C2C from North Campus and the OurBus or FlixBus trips that leave from the same campus stops.
- **Upper-years without a car** paying their own way home.
- **Students on a tight budget**, for whom C2C's $68.50 extra each way over the $25 OurBus floor (NetID fare) adds up fast.
- **Parents** paying for a student's trips, or riding C2C themselves at the public fare.
- **International students** who land in New York and take a bus up, or go to the city at short breaks.

## The inputs

- **Round trips home to NYC this school year** (1 to 12, default 4). Each round trip is two one-way rides.
- **Your C2C fare.** NetID is the price for Cornell students, faculty and staff signed in with a NetID: $93.50 one way. Public is $101, for anyone without a NetID. There is no separate student-only fare. The commercial buses charge everyone the same.
- **Commercial bus to compare with C2C.** OurBus, FlixBus or Greyhound. The table always shows all three; this choice sets the headline comparison.
- **Is one round trip at Thanksgiving?** If yes, one of your round trips is priced with the Thanksgiving-week premium on the commercial buses. C2C's posted fare stays the same.
- **Large bags each way.** 1, 2 or 3 checked or below-deck bags. Carry-ons are not counted.

## Every number and formula

The tool does this, so you can redo it by hand:

- One-way rides = round trips × 2.
- C2C for the year = one-way rides × the C2C fare ($93.50 NetID or $101 public).
- A commercial bus at the floor = one-way rides × its "from" fare. At the average = one-way rides × its average fare.
- Thanksgiving, if yes: add 2 × the one-way fare × 0.333 to each commercial total (one round trip at +33.3%). The range shown uses 0.279 and 0.379.
- OurBus bags: (bags − 1) × $30 × one-way rides. Greyhound and FlixBus extra-bag fees and a third C2C suitcase have no price in our data, so they are flagged, not added.
- C2C premium = C2C total − the commercial total, and C2C total ÷ the commercial total.

Example with the defaults: 8 one-way rides. C2C is 8 × $93.50 = $748. OurBus at the floor is 8 × $25 = $200, plus 2 × $25 × 0.333 = $16.65 for Thanksgiving, so $216.65; at the average, 8 × $69.23 = $553.84 plus $46.11, so $599.95. C2C costs $531.35 more than OurBus at the floor (3.5 times) and $148.05 more at the average (1.2 times).

| Number | Value | Applies to | Source |
|---|---|---|---|
| C2C fare with a NetID | $93.50 one way, $187 round trip; includes a temporary $6 fuel and toll surcharge with no end date | Page undated; read 2026-11-08 | [Cornell FCS C2C rates](https://fcs.cornell.edu/departments/transportation-delivery-services/campus-campus-bus-service/c2c-rates) |
| C2C public fare | $101 one way, $202 round trip; includes the $6 surcharge | Page undated; read 2026-11-08 | [Cornell FCS C2C rates](https://fcs.cornell.edu/departments/transportation-delivery-services/campus-campus-bus-service/c2c-rates) |
| C2C luggage | 2 suitcases below deck plus 2 small carry-ons per passenger | Page undated; read 2026-11-08 | [C2C policies](https://fcs.cornell.edu/departments/transportation-delivery-services/campus-campus-bus-service/c2c-policies-regulations) |
| OurBus, Ithaca to NYC | From $25; average $69.23 | Wanderu sample, week of 2026-11-08 to 11-14 | [Wanderu](https://www.wanderu.com/en/bus/us-ny/ithaca/us-ny/new-york/) |
| FlixBus, Ithaca to NYC | From $30; average $73.50 | same | [Wanderu](https://www.wanderu.com/en/bus/us-ny/ithaca/us-ny/new-york/) |
| Greyhound, Ithaca to NYC | From $37; average $82.31 | same | [Wanderu](https://www.wanderu.com/en/bus/us-ny/ithaca/us-ny/new-york/) |
| Average of six carriers' average fares | $61.91 (range $44.54 to $82.31; n = 6 carriers, 1 day) | 2026-11-08 | [Wanderu](https://www.wanderu.com/en/bus/us-ny/ithaca/us-ny/new-york/) |
| OurBus "from" on its own route page | From $33 | Page viewed 2026-11-08 | [OurBus route page](https://www.ourbus.com/routes/ithaca-ny-to-new-york-ny) |
| Greyhound "from" on its own route page | From $43.98 (an earlier view said $37.98) | Read 2026-11-08 | [Greyhound route page](https://www.greyhound.com/bus-routes/ithaca-ny-new-york-ny) |
| Thanksgiving-week premium on lowest fares | +33.3% mean; +27.9% Binghamton (n = 15 dates), +34.2% Rochester (n = 17), +37.9% DC (n = 19); 51 priced dates | Read 2026-11-08, travel dates Nov 3 to 27, 2026 | [Binghamton](https://www.checkmybus.com/ithaca-ny/binghamton-ny), [Rochester](https://www.checkmybus.com/ithaca-ny/rochester-ny), [DC](https://www.checkmybus.com/ithaca-ny/washington-dc) |
| OurBus bags | 1 large bag guaranteed per ticket; extra bags only if space remains | 2024-02-01 | [Cornell Daily Sun](https://www.cornellsun.com/2024/02/01/got-baggage-inside-cornells-luggage-transport-woes) |
| OurBus extra bag fee | $30 prepaid per extra bag (search summary; page not opened) | Page undated; checked 2026-11-07 | [OurBus Cornell page](https://www.ourbus.com/colleges/ithaca-ny-c-cornell-university) |
| Greyhound bags | 1 carry-on (16 × 12 × 7 in, up to 25 lb) and 1 checked bag free; a Flexible fare adds a second free checked bag | Page undated; read 2026-11-08 | [Greyhound route page](https://www.greyhound.com/bus-routes/ithaca-ny-new-york-ny) |

The tool uses the Wanderu floors for all three commercial carriers so they come from the same page on the same day. The operators' own pages showed higher floors that day: OurBus from $33 and Greyhound from $43.98. At $33, four OurBus round trips cost $264 instead of $200.

## Assumptions and what it does not cover

- **The floor is the cheapest seat a page advertised**, not a fare you will get. On Nov 8, 2026 the cheapest advertised seat was about 40% of a typical average fare.
- **The averages cover unknown dates** and come from one aggregator on one day (n = 6 carriers). No break week was sampled.
- **The Thanksgiving premium is an assumption for NYC.** It was measured on Ithaca fares to Binghamton, Rochester and DC, with dates 2 to 3 weeks out, so fares may rise more as the break gets closer. The tool applies the same +33.3% to the average fare too.
- **C2C only goes to NYC.** It has no Boston or Philadelphia route.
- **Not in our data:** FlixBus bag allowance and fees; Greyhound's extra-bag fee and the price of its Flexible fare; what C2C does with a third suitcase; peak-day high fares; the amount of OurBus's student discount; Coach USA, Megabus and Trailways bag rules. Those carriers had floors of $28.98, $29 and $43 on Nov 8, 2026 but are left out of the calculator.
- **Not included:** subway, TCAT or taxi rides to and from the stops, C2C's $10 or $30 cancellation and change fees, and OurBus rescheduling fees (cancellations give credit, not cash).
- Prices are not adjusted for inflation.

## How to read the result

The first line is your year's total on C2C and on the bus you picked. Read the floor as the best case if you book early and get the cheapest seat; read the average as a more typical spend. The C2C premium tells you what you pay for C2C's two free suitcases and its East Side stops (Weill Cornell at 1300 York Ave and the Cornell Club at 6 E 44th St) instead of the commercial buses' stops (Greyhound and FlixBus at Port Authority and on the West Side; OurBus at the GWB, Hudson Yards and Madison Ave at 26th). Trip times are about the same: C2C runs about 4.5 to 5 hours from B Lot; OurBus 4 h 10 min to 7 h; Greyhound 4 h 20 min at the fastest.

If the C2C premium is more than you want to spend, book the commercial bus early (Wanderu claims about 14 days ahead is cheapest) and book Thanksgiving now. If you carry two big bags, C2C may close part of the gap: OurBus charges $30 for each extra bag each way. If you have a NetID, sign in with it: the public fare costs $7.50 more a trip.

## Related guides

- [Getting to Ithaca and around Cornell, 2026-27](/getting-around/getting-to-ithaca-and-around-cornell/)
- [NYC to Cornell by bus: C2C, OurBus, FlixBus, Greyhound](/getting-around/nyc-to-cornell-bus-c2c-ourbus-flixbus-greyhound/)
- [Cornell Campus-to-Campus bus: who can ride, how to book](/getting-around/cornell-c2c-bus-booking-fares-rules/)
- [Cornell Thanksgiving travel: when to book and what it costs](/getting-around/cornell-thanksgiving-break-bus-tickets-when-to-book/)
- [The cheapest ways to get home and around Cornell](/getting-around/cheapest-ways-to-get-around-cornell/)
- [Getting to and around Ithaca as a Cornell first-year](/getting-around/getting-around-cornell-first-year/)
- [Getting around Cornell after first year without a car](/getting-around/getting-around-cornell-upper-years-no-car/)
- [Getting to Cornell and home as an international student](/getting-around/getting-to-cornell-international-students/)
- [Getting to and around Cornell for parents and visitors](/getting-around/getting-around-cornell-parents-visitors/)
