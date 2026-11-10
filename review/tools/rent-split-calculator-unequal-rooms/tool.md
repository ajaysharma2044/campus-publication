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
  - {url: "https://scl.cornell.edu/residential-life/housing/campus-living/living-campus/study-abroad/housemate-compatibility-questionnaire", title: "Cornell Off-Campus Living: Housemate compatibility questionnaire", accessed: "2026-11-10"}
  - {url: "https://sites.lawschool.cornell.edu/tenants-advocacy/understanding-your-lease", title: "Cornell Law School Tenants Advocacy: Understanding your lease (February 2026)", accessed: "2026-11-10"}
---

This calculator splits one apartment's rent among roommates whose bedrooms are not the same. You enter the total rent, the size of the whole apartment and the size of each bedroom. You also say which rooms have a private bathroom, a window and a closet, and what your group thinks each perk is worth. The tool splits the shared space evenly, charges each person for their own bedroom floor, then moves money from the people without a perk to the people with it. The shares always add up to the full rent.

```tool rent-split-calculator-unequal-rooms
```

## Who it is for

Sophomores pricing a junior-year lease with friends, before anyone claims the big room. Upper-year renters whose group is renewing and wants to rebalance. Low-budget students who would take the smallest room for a lower share. Parents who co-sign and want to see why their student's share differs from a roommate's. Grad students sharing a house in Fall Creek or downtown.

## The inputs

- **Total rent.** The whole unit's rent a month. Many Collegetown landlords quote per bed, so multiply the per-bed price by the number of bedrooms. Leave utilities out; split those evenly.
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

| Room | Base (size) | Bath shift | Share a month |
|---|---|---|---|
| Room 1, 150 sq ft, private half bath | $1,418.18 | +$80.63 | $1,498.81 |
| Room 2, 130 sq ft | $1,323.64 | -$26.88 | $1,296.76 |
| Room 3, 120 sq ft | $1,276.36 | -$26.88 | $1,249.49 |
| Room 4, 100 sq ft | $1,181.82 | -$26.88 | $1,154.94 |
| Total | $5,200.00 | $0.00 | $5,200.00 |

Each room's share is computed before rounding, so a row can differ from base plus shift by a cent.

| Number | Value | Applies to | Source |
|---|---|---|---|
| Collegetown Plaza Premium 4BR, 1.5 baths | $1,250 to $1,350 per bed a month (midpoint $1,300) | 2027-28, read 2026-11-10 | [Ithaca Renting Collegetown](https://ithacarenting.com/collegetown/) |
| Collegetown Plaza Premium 4BR, 1 bath | $1,185 to $1,200 per bed a month (midpoint $1,192.50) | 2027-28, read 2026-11-10 | [Ithaca Renting Collegetown](https://ithacarenting.com/collegetown/) |
| Default private-bath value | $107.50 a month ($1,300 - $1,192.50) | Our calc on the two rows above | [Ithaca Renting Collegetown](https://ithacarenting.com/collegetown/) |
| Example unit rent | $5,200 a month (4 x $1,300) | Our calc | From the first row |
| Joint and several leases | Most local leases bind housemates "jointly and severally": each is responsible for the others' rent and damages | Page as read 2026-11-10 | [Cornell Off-Campus Living](https://scl.cornell.edu/residential-life/housing/campus-living/living-campus/study-abroad/housemate-compatibility-questionnaire) |
| Contribution | A tenant who pays more than their share can sue the co-tenant who failed to pay | February 2026 | [Cornell Law Tenants Advocacy](https://sites.lawschool.cornell.edu/tenants-advocacy/understanding-your-lease) |

## Assumptions and what the tool does not cover

- The $107.50 bathroom value is one landlord's price gap between two layouts in one building, both labeled Premium. It is a yardstick, not a rule. Your group can set any value.
- No landlord in our data prices a window or a closet on its own, so both default to $0.
- Square footage treats every foot of shared space the same. A big living room you never use counts as much as the kitchen.
- One person per bedroom. A couple sharing a room should enter it once and split that share between them.
- Utilities, internet and parking are left out. Split them evenly or by use.
- The split is a deal among roommates. The landlord can still collect the whole rent from any of you on a joint lease.

## How to read the result

The bold line gives the largest and smallest monthly share and the gap between them, next to the even split. The table shows each room's share a month, over the lease, and how far it sits from an even split. The lines under it show the shared-space math and each perk's shift, so the whole group can check the numbers. If a share drops below zero, your perk values are too large for the rent. When the group agrees, write the split down and have everyone sign it.

## Related guides

- [How to split rent fairly with unequal rooms](/cornell/housing/rent-split-calculator-unequal-rooms/)
- [Finding off-campus roommates at Cornell: joint liability](/cornell/housing/cornell-off-campus-roommates-joint-liability/)
- [What a month off campus costs at Cornell](/cornell/housing/what-a-month-off-campus-costs-cornell/)
- [Ithaca rent + commute calculator](/tools/ithaca-rent-commute-calculator/)
