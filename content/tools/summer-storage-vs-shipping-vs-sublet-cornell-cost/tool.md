---
title: "Summer storage vs shipping vs sublet calculator for Cornell renters"
meta: "Enter your lease, months away, rent, sublet price and what you'd pack; get the cheapest summer plan: keep and sublet, store with BRSS, self-store or ship."
topic: housing
updated: 2026-11-11
numbers_as_of: 2026-11-10
idea_id: 19
kind: tool
readers: [off-campus, away-semester, international, low-budget, upper-year-no-car]
brief: intel/off-campus-housing/brief.md
sources:
  - {url: "http://www.bigredboxes.com/BRSS_Pricing", title: "Big Red Shipping & Storage: Pricing (no year printed)", accessed: "2026-11-10"}
  - {url: "https://www.boltstorage.com/self-storage/freeville-ny", title: "Bolt Storage: 1401 Dryden Road unit prices", accessed: "2026-11-10"}
  - {url: "https://ithacarenting.com/collegetown/", title: "Ithaca Renting: Collegetown properties, prices and sublet rules", accessed: "2026-11-10"}
  - {url: "https://sites.lawschool.cornell.edu/tenants-advocacy/breaking-a-lease", title: "Cornell Law School Tenants Advocacy Program: Breaking a lease", accessed: "2026-11-10"}
  - {url: "https://www.nysenate.gov/legislation/laws/RPP/226-B", title: "New York State Senate: Real Property Law section 226-B, right to sublease or assign", accessed: "2026-11-10"}
  - {url: "https://drydensouth.com/availability/", title: "Dryden South: Availability", accessed: "2026-11-10"}
  - {url: "https://www.ourbus.com/colleges/ithaca-ny-c-cornell-university", title: "OurBus: OurBus for Cornell University", accessed: "2026-11-10"}
  - {url: "https://scl.cornell.edu/residential-life/housing/housing-and-residential-life-and-faculty-involvement-campus/moving-out/storage-shipping-options", title: "Cornell Student & Campus Life: Storage and shipping options", accessed: "2026-11-10"}
  - {url: "https://scl.cornell.edu/residential-life/housing/housing-and-residential-life-and-faculty-involvement-campus/rates-amenities-licenses/academic-year-housing-license-2027-2028", title: "Cornell Student & Campus Life: Academic year housing license 2027-2028", accessed: "2026-11-10"}
---

This calculator finds the cheapest way to get through a summer away from your Ithaca apartment. You tell it whether your lease keeps running while you're gone, how many months you'll be away, your share of the rent, what a subtenant would pay you, and what you would pack. It then prices four plans: leave your things in your room (and sublet it furnished if you can), store them with Big Red Shipping and Storage (BRSS), rent a self-storage unit, or ship them home. All prices are as of Nov. 10, 2026.

```tool summer-storage-vs-shipping-vs-sublet-cornell-cost
```

## Who it is for

- **Off-campus renters** on a 12-month lease who leave Ithaca for June, July and August.
- **Renters between leases**, whose lease ends before the next one starts and who need somewhere for their things.
- **Students going abroad for a semester**, who face the same choice for longer.
- **International students**, for whom shipping home is the costly option.
- **Students without a car**, who can't easily reach a self-storage unit.

Dorm residents should use the [move-out storage and shipping guide](/cornell/getting-around/cornell-move-out-storage-shipping-options/) instead. Cornell's housing license offers no storage and bars residents from subletting or transferring their room ([Cornell housing license 2027-28](https://scl.cornell.edu/residential-life/housing/housing-and-residential-life-and-faculty-involvement-campus/rates-amenities-licenses/academic-year-housing-license-2027-2028)).

```reader "If you're graduating or leaving Ithaca for good"
Storage only delays the problem, so the choice is shipping, carrying, selling or donating. Price one-way shipping only. If your lease runs past your last day, [Cornell Law School's tenant guide](https://sites.lawschool.cornell.edu/tenants-advocacy/breaking-a-lease) says assigning the lease, which hands it over entirely, is generally better than subletting when you won't move back in, because it ends your liability for the new tenant's rent and damage. In a building of four or more units, the landlord can refuse an assignment without cause; if that refusal is unreasonable, you can be released from the lease on 30 days' notice ([RPL 226-b](https://www.nysenate.gov/legislation/laws/RPP/226-B)).
```

```reader "If you're going abroad for a semester"
Your time away runs four or five months, past BRSS's 3 to 4 month term, so ask BRSS for a quote or use a month-to-month unit. A semester sublet uses up Ithaca Renting's one sublet term for that stretch. The [away-semester guide](/start/away-semester/) covers the rest of your checklist.
```

```reader "If you're an international student"
Shipping abroad costs the most once BRSS adds its international and customs fees. Store in Ithaca, or leave your things in a sublet room if your lease runs all summer. You must be present for a BRSS pickup ([Cornell Student & Campus Life](https://scl.cornell.edu/residential-life/housing/housing-and-residential-life-and-faculty-involvement-campus/moving-out/storage-shipping-options)), so book a slot before your flight date.
```

## The inputs

- **Does your lease keep running?** Check its dates: Ithaca Renting's leases run one year and start in June, July or August on fixed dates that can't be changed, and at Dryden South, 205 Dryden Road, every 2027-28 lease starts June 1 and runs 12 months ([Ithaca Renting](https://ithacarenting.com/collegetown/); [Dryden South](https://drydensouth.com/availability/)). If yes, you owe the summer rent whatever you do. Your room is already storage you pay for. If no, everything has to go somewhere.
- **Coming back in the fall?** If yes, shipping is paid twice: home in May and back in August.
- **Months away.** The default of 3 is June, July and August. BRSS prices a 3 to 4 month term.
- **Your share of rent.** The default, $1,246.25 a month, is the median per-bed price of an Ithaca Renting Collegetown 4-bedroom for 2027-28.
- **Sublet rent.** What your subtenant would pay you each month. No typical Ithaca summer sublet price is published, so this starts blank. Use a real offer or listings like yours.
- **Sublet fee.** Defaults to $20. Ithaca Renting's Collegetown page lists both a $15 fee and a $20 fee, so the tool uses the higher one.
- **Your things.** Boxes and loose items in BRSS's six price tiers. The default is six large boxes and one mini fridge.
- **Self-storage price.** Defaults to $84 a month, a 5x5 drive-up unit at Bolt Storage, 1401 Dryden Road.
- **Shipping quote.** Starts blank. BRSS ships by FedEx at rates set at pickup and posts no shipping prices, so get a quote and enter it.

## The numbers and the math

The formulas:

- **Rent owed while away** = your rent x months. It counts only if your lease runs through the summer.
- **Sublet income** = sublet rent x months - sublet fee.
- **BRSS storage** = (small boxes x $39) + (large boxes x $49) + (small items x $49) + (medium items x $75) + (large items x $100) + (giant items x $150).
- **Self-storage** = monthly price x months.
- **Shipping** = your one-way quote, x 2 if you come back.
- **Your summer** = rent owed - sublet income + the cost of the storage plan you pick. Leaving your things in a room you already rent adds $0.
- **Shipping break-even** = BRSS total / 2. A one-way quote below that beats BRSS for a round trip.

A worked example. You rent a bed in an Ithaca Renting Collegetown 4-bedroom at $1,246.25 a month. You'll be away June, July and August, and a subtenant will pay you $900 a month. Rent owed is $1,246.25 x 3 = $3,738.75. Sublet income is $900 x 3 - $20 = $2,680. Storage adds $0 if your six boxes and mini fridge stay in the room, $84 x 3 = $252 in a Bolt 5x5 unit, or 6 x $49 + $75 = $369 with BRSS. Without a sublet, the full rent stands. The four totals:

```figure
kind: cost_table
title: "One summer, three months away: rent, sublet income and storage"
rows:
  - {label: "Things stay in your room, room sublet furnished", value: "$1,058.75"}
  - {label: "Self-storage unit ($84 a month), room sublet empty", value: "$1,310.75"}
  - {label: "BRSS storage ($369), room sublet empty", value: "$1,427.75"}
  - {label: "Things stay in your room, no sublet", value: "$3,738.75"}
```
Sources: Ithaca Renting Collegetown per-bed median and sublet fee; BRSS price list; Bolt Storage, 1401 Dryden Road. Totals are summer rent, minus sublet income where a sublet applies, plus storage.

| Number | Value | Applies to | Source |
|---|---|---|---|
| BRSS small box (0 to 2 cu ft) | $39 | 3 to 4 month term, pickup, storage and delivery included; no year printed | [BRSS pricing](http://www.bigredboxes.com/BRSS_Pricing) |
| BRSS large box (2 to 4 cu ft) | $49 | Same | [BRSS pricing](http://www.bigredboxes.com/BRSS_Pricing) |
| BRSS small item (carry-on, microwave, nightstand) | $49 | Same | [BRSS pricing](http://www.bigredboxes.com/BRSS_Pricing) |
| BRSS medium item (mini fridge, large suitcase, desk chair, TV) | $75 | Same | [BRSS pricing](http://www.bigredboxes.com/BRSS_Pricing) |
| BRSS large item (rug, instrument, skis) | $100 | Same | [BRSS pricing](http://www.bigredboxes.com/BRSS_Pricing) |
| BRSS giant item (dresser, mattress, desk, couch) | $150 | Same | [BRSS pricing](http://www.bigredboxes.com/BRSS_Pricing) |
| BRSS shipping | FedEx rates set at pickup; extra fees for international shipments | No amounts posted | [BRSS pricing](http://www.bigredboxes.com/BRSS_Pricing) |
| Bolt Storage 5x5 drive-up unit | $84 a month, month to month, 10 days' notice to move out, insurance required | 1401 Dryden Road, Freeville; checked Nov. 10, 2026 | [Bolt Storage](https://www.boltstorage.com/self-storage/freeville-ny) |
| Ithaca Renting Collegetown 4-bedroom, per bed | $1,246.25 median | 2027-28 | [Ithaca Renting Collegetown](https://ithacarenting.com/collegetown/) |
| Ithaca Renting Collegetown sublet fee | $15 in one place, $20 in another, on the same page | Checked Nov. 10, 2026 | [Ithaca Renting Collegetown](https://ithacarenting.com/collegetown/) |
| Sublet fees in general | Allowed only if the lease lists one and it is reasonable; credit or background check fees allowed | Cornell Law guide, updated Feb. 2026 | [Cornell Law School](https://sites.lawschool.cornell.edu/tenants-advocacy/breaking-a-lease) |
| Sublet liability | You stay responsible for the lease after a sublet | New York | [RPL 226-b](https://www.nysenate.gov/legislation/laws/RPP/226-B) |

## When shipping beats storage

For the worked example, BRSS storage is $369, so a one-way shipping quote must come in under $184.50 to win the round trip. Per box, a large box stores for $49, so shipping it each way must cost under $24.50 ([BRSS pricing](http://www.bigredboxes.com/BRSS_Pricing)). Carrying an extra box on the bus costs more than storing it: OurBus allows one suitcase up to 50 pounds free, and each extra bag is $30, prepaid ([OurBus](https://www.ourbus.com/colleges/ithaca-ny-c-cornell-university)). A box carried home and back as an extra bag costs $60, more than the $49 to store it. Shipping makes sense when you need the things over the summer, or when you aren't coming back.

## Assumptions and what the tool does not cover

- No typical summer sublet rent for Ithaca is published, so the tool never assumes one. A sublet that fills only some of the months lowers your income; enter the average you expect.
- BRSS charges extra for overweight, oversized or fragile items, late reschedules, missed appointments and non-BRSS boxes. It posts no amounts, so the tool leaves them out.
- The self-storage figure leaves out the cost of getting there. Bolt's 1401 Dryden Road site is about 6 minutes from Cornell by car, by Bolt's estimate. It also leaves out the insurance Bolt requires.
- Some landlords make you keep the electricity on while you sublet or store things in the apartment. Ithaca Renting does, at least enough to keep the fridge running, and it charges its sublet fee if anyone uses the apartment over the summer, even for free ([Ithaca Renting](https://ithacarenting.com/collegetown/)). The electricity bill is not counted.
- Storage Squad and Uncle Marty's are not in the tool, because their price tiers don't line up with BRSS's. The guide works through both.

## How to read the result

The bold line names the cheapest plan and what your summer costs under it. The next line names the runner-up and how much more it costs. Under that, every total shows its math. If your lease runs all summer, the rent line is the same for every plan, so the real choice is whether you sublet and whether your things can stay. If two plans sit within about $50, decide on convenience: BRSS picks up from your door, while a storage unit needs a car. If your things stay in a sublet room, write into the sublease what stays, where, and who pays if it is damaged, and lock valuables away or take them home.

## Related guides

- [Storage vs shipping vs subletting: which costs least](/cornell/housing/summer-storage-vs-shipping-vs-sublet-cornell-cost/)
- [How to sublet your Ithaca apartment for the summer](/cornell/housing/cornell-summer-sublet-how-to-sublet-apartment-ithaca/)
- [Ithaca sublet request timeline](/tools/ithaca-sublet-request-timeline/)
- [Cornell move-out: storage, shipping and loading zones](/cornell/getting-around/cornell-move-out-storage-shipping-options/)
