---
title: "Rent split calculator for unequal rooms"
meta: "Enter the rent, the apartment and bedroom sizes, and who gets a private bath, window or closet; get each roommate's fair share, with the math shown."
topic: housing
updated: 2026-11-10
numbers_as_of: 2026-11-10
idea_id: 18
kind: tool
readers: [sophomore, off-campus, low-budget, parent, grad-student]
brief: intel/off-campus-housing/brief.md
sources:
  - {url: "https://ithacarenting.com/collegetown/", title: "Ithaca Renting: Collegetown properties (per-bed prices, 2027-28)", accessed: "2026-11-10"}
  - {url: "https://scl.cornell.edu/residential-life/housing/living-off-campus/tenant-best-practices/study-abroad/housemate-compatibility-questionnaire", title: "Cornell Off-Campus Living: Housemate compatibility questionnaire", accessed: "2026-11-10"}
  - {url: "https://sites.lawschool.cornell.edu/tenants-advocacy/understanding-your-lease", title: "Cornell Law School Tenants Advocacy: Understanding your lease (February 2026)", accessed: "2026-11-10"}
  - {url: "https://www.nysenate.gov/legislation/laws/GOB/7-108", title: "New York General Obligations Law 7-108, Security deposits", accessed: "2026-11-10"}
  - {url: "https://scl.cornell.edu/residential-life/housing/living-off-campus/community-resources", title: "Cornell Off-Campus Living: Resources", accessed: "2026-11-10"}
  - {url: "https://sites.lawschool.cornell.edu/tenants-advocacy/tenants-rights/", title: "Cornell Law School Tenants Advocacy: Tenants' rights", accessed: "2026-11-10"}
redirect_from:
  - /cornell/housing/rent-split-calculator-unequal-rooms/
  - /housing/rent-split-calculator-unequal-rooms/
index: false
---

This calculator splits one apartment's rent among roommates whose bedrooms are not the same. You enter the total rent, the size of the whole apartment and the size of each bedroom. You also say which rooms have a private bathroom, a window and a closet, and what your group thinks each perk is worth. The tool splits the shared space evenly, charges each person for their own bedroom floor, then moves money from the people without a perk to the people with it. The shares always add up to the full rent.

```tool rent-split-calculator-unequal-rooms
```

## Who it is for

Sophomores pricing a junior-year lease with friends, before anyone claims the big room. Upper-year renters whose group is renewing and wants to rebalance. Low-budget students who would take the smallest room for a lower share. Parents who co-sign and want to see why their student's share differs from a roommate's. Grad students sharing a house in Fall Creek or downtown.

## The inputs

- **Total rent.** The whole unit's rent a month. Many Collegetown landlords quote per bed, so multiply the per-bed price by the number of bedrooms. Leave utilities out of the total and split them evenly, because electricity and internet track use, not room size. The exception is a roommate who runs a space heater or a window air conditioner all winter or summer. Ithaca Renting includes heat and hot water at its properties but charges electricity to tenants at most of them ([Ithaca Renting](https://ithacarenting.com/collegetown/)).
- **Bedrooms.** Two to six, one person in each.
- **Whole apartment, square feet.** Look for it on the listing or the lease. Leave it blank and the tool ignores room size.
- **Lease length.** Used only for the yearly column.
- **Perk values.** The extra a month for a private bathroom, a window and a closet. Only the bathroom has a market yardstick; the other two are your group's call.
- **Each room.** Its floor area in square feet (length x width in feet), whether its bathroom is private, and whether it has a window and a closet. Count a private bathroom's floor as part of that bedroom.

## The numbers and the math

**Step 1, size.** Shared space is the whole apartment minus all the bedrooms. Each person pays for an equal slice of it plus their own bedroom. A room's base share = rent x (bedroom sq ft + shared sq ft / number of people) / apartment sq ft.

**Step 2, perks.** Say a perk is worth P a month and k of the n rooms have it. Each room with it pays P x (n - k) / n more. Each room without it pays P x k / n less. A room with the perk ends up exactly P above a room without it, and the total rent does not move. If every room has the perk, or none does, it changes nothing.

**Step 3, cents.** Shares are rounded to the cent. Any leftover cent goes to the largest share so the total matches the rent.

The default example is a Collegetown Plaza Premium 4-bedroom, 1.5-bath unit at 111 Dryden Rd. It lists at $1,250 to $1,350 per bed a month for 2027-28; the midpoint, $1,300, makes the unit 4 x $1,300 = $5,200 a month. The setup sizes (a 1,100 sq ft apartment with bedrooms of 150, 130, 120 and 100 sq ft, Room 1 with the private half bath) are an example to replace with your own measurements.

With those inputs, shared space is 1,100 - 500 = 600 sq ft, or 150 each. Room 1's base is (150 + 150) / 1,100 x $5,200 = $1,418.18. The bathroom perk at $107.50 adds $107.50 x 3 / 4 = $80.63 to Room 1 and takes $107.50 x 1 / 4 = $26.88 off each other room.

| Room | Base (size) | Bath shift | Share a month | Vs. even split of $1,300 |
|---|---|---|---|---|
| Room 1, 150 sq ft, private half bath | $1,418.18 | +$80.63 | $1,498.81 | +$198.81 |
| Room 2, 130 sq ft | $1,323.64 | -$26.88 | $1,296.76 | -$3.24 |
| Room 3, 120 sq ft | $1,276.36 | -$26.88 | $1,249.49 | -$50.51 |
| Room 4, 100 sq ft | $1,181.82 | -$26.88 | $1,154.94 | -$145.06 |
| Total | $5,200.00 | $0.00 | $5,200.00 | $0.00 |

Each room's share is computed before rounding, so a row can differ from base plus shift by a cent. The biggest room with the bath pays $343.87 a month more than the smallest. Over a 12-month lease, the Room 4 tenant saves $145.06 x 12 = $1,740.72 against an even split of the [Ithaca Renting](https://ithacarenting.com/collegetown/) rent.

```reader "If you're a sophomore signing for junior year"
Settle who gets which room, and what each pays, before anyone signs. Once the lease is signed the group has no lever, and the person who claimed the big room first has no reason to pay more. Measure the rooms on the showing, or ask the landlord for a floor plan. More on the year ahead is on the [sophomore start page](/start/sophomore/).
```

```reader "If you're on a tight budget"
Offer to take the smallest room, or the one without the bathroom, in exchange for a lower share. In the example above that saves $145.06 a month. Check the room in person first: a small room still needs space for a bed, a desk and your things for a full year.
```

```reader "If you're a parent co-signing"
Your student's share in the group's split does not limit what you sign for. Read the guaranty itself to see whether it covers your student's share or the whole unit's rent.
```

| Number | Value | Applies to | Source |
|---|---|---|---|
| Collegetown Plaza Premium 4BR, 1.5 baths | $1,250 to $1,350 per bed a month (midpoint $1,300) | 2027-28, read 2026-11-10 | [Ithaca Renting Collegetown](https://ithacarenting.com/collegetown/) |
| Collegetown Plaza Premium 4BR, 1 bath | $1,185 to $1,200 per bed a month (midpoint $1,192.50) | 2027-28, read 2026-11-10 | [Ithaca Renting Collegetown](https://ithacarenting.com/collegetown/) |
| Default private-bath value | $107.50 a month ($1,300 - $1,192.50) | Our calc on the two rows above | [Ithaca Renting Collegetown](https://ithacarenting.com/collegetown/) |
| Example unit rent | $5,200 a month (4 x $1,300) | Our calc | From the first row |
| Joint and several leases | Most local leases bind housemates "jointly and severally": each is responsible for the others' rent and damages | Page as read 2026-11-10 | [Cornell Off-Campus Living](https://scl.cornell.edu/residential-life/housing/living-off-campus/tenant-best-practices/study-abroad/housemate-compatibility-questionnaire) |
| Contribution | A tenant who pays more than their share can sue the co-tenant who failed to pay | February 2026 | [Cornell Law Tenants Advocacy](https://sites.lawschool.cornell.edu/tenants-advocacy/understanding-your-lease) |

### What a better room costs

Collegetown Plaza has a third four-bedroom layout: the Deluxe 4-bedroom with two bathrooms, listed at $1,295 to $1,395 per bed a month for 2027-28 (midpoint $1,345). The Deluxe label can also mean better finishes, so its higher price says less about bathrooms alone ([Ithaca Renting](https://ithacarenting.com/collegetown/)).

The same landlord prices rooms, not just apartments. At 210 Dryden Rd, where tenants rent single rooms around shared kitchens and baths, a Standard Room lists at $695 to $810 a month and a Premium Room at $850 to $950. At the midpoints, $752.50 and $900, the better room costs $147.50 more: one landlord charges more for a better room than for an extra half bath ([Ithaca Renting](https://ithacarenting.com/collegetown/)).

```figure
kind: cost_table
title: What better rooms cost at Ithaca Renting, per bed a month, 2027-28
rows:
  - {label: "Collegetown Plaza Premium 4BR, 1 bath", value: "$1,185 to $1,200 (midpoint $1,192.50)"}
  - {label: "Collegetown Plaza Premium 4BR, 1.5 baths", value: "$1,250 to $1,350 (midpoint $1,300)"}
  - {label: "Collegetown Plaza Deluxe 4BR, 2 baths", value: "$1,295 to $1,395 (midpoint $1,345)"}
  - {label: "210 Dryden Rd Standard Room", value: "$695 to $810 (midpoint $752.50)"}
  - {label: "210 Dryden Rd Premium Room", value: "$850 to $950 (midpoint $900)"}
```

Source: Ithaca Renting's Collegetown page, asking rents. Midpoints are (low + high) / 2.

## Assumptions and what the tool does not cover

- The $107.50 bathroom value is one landlord's price gap between two layouts in one building, both labeled Premium. It is a yardstick, not a rule. Your group can set any value.
- No landlord in our data prices a window or a closet on its own, so both default to $0. A room with no window may be a small office or den sold as a bedroom, so ask the landlord before you sign.
- Square footage treats every foot of shared space the same. A big living room you never use counts as much as the kitchen.
- One person per bedroom. A couple sharing a room should enter it once and split that share between them.
- Utilities, internet and parking are left out; the Total rent input above says how to split them.
- The split is a deal among roommates. The landlord can still collect the whole rent from any of you on a joint lease.
- If the landlord already prices each room separately, the landlord has set the split and each person pays their own room's price. The calculator is for a group renting a whole unit at one total rent. Before you sign, check whether the lease is joint or by the room; our guide on [how to read an Ithaca lease](/cornell/housing/how-to-read-ithaca-lease-before-signing/) shows where to look.

## How to read the result

The bold line gives the largest and smallest monthly share and the gap between them, next to the even split. The table shows each room's share a month, over the lease, and how far it sits from an even split. The lines under it show the shared-space math and each perk's shift, so the whole group can check the numbers. If a share drops below zero, your perk values are too large for the rent. When the group agrees, write the split down and have everyone sign it.

## What goes wrong, and how to fix it

**Nobody measured.** A group guesses at sizes, then fights about them in September. Fix: measure every bedroom on the same day with the same tape, and write the numbers into the agreement.

**The perk values come late.** Once rooms are picked, everyone argues for the value that helps them. Fix: agree on the dollar value of each perk before anyone chooses a room. Then choose.

**The deposit is split evenly.** The rent split is uneven but the deposit is not, so the shares don't match. Fix: split the deposit by the same shares. In New York a deposit can't be more than one month's rent, and the landlord must return it with an itemized list within 14 days after you move out ([N.Y. General Obligations Law 7-108](https://www.nysenate.gov/legislation/laws/GOB/7-108)). Agree in writing how the group will divide any deductions. The rules for getting it back are in our [security deposit guide](/cornell/housing/ithaca-security-deposit-rules-tenants/).

**Someone wants to renegotiate mid-year.** Fix: write into the agreement that the split holds for the full lease unless everyone agrees in writing to change it.

If a dispute stalls, the Community Dispute Resolution Center mediates roommate conflicts at 607-273-9347 ([Cornell Off-Campus Living resources](https://scl.cornell.edu/residential-life/housing/living-off-campus/community-resources)). For legal questions about a lease, call the Cornell Law Tenants Advocacy hotline at 607-301-1560 ([Tenants Advocacy](https://sites.lawschool.cornell.edu/tenants-advocacy/tenants-rights/)).

## Related guides

- [How to split rent fairly with unequal rooms](/tools/rent-split-calculator-unequal-rooms/)
- [Finding off-campus roommates at Cornell: joint liability](/cornell/housing/cornell-off-campus-roommates-joint-liability/)
- [What a month off campus costs at Cornell](/cornell/housing/what-a-month-off-campus-costs-cornell/)
- [Collegetown rent per bed, 2027-28 (dataset)](/datasets/collegetown-rent-per-bed-2027-28/)
- [Ithaca rent + commute calculator](/tools/ithaca-rent-commute-calculator/)
