---
title: "Ithaca Carshare calculator: Just In Case or It's My Car"
meta: "Enter hours, miles and vehicle to get the yearly cost of each Ithaca Carshare student plan with tax, the break-even and whether you qualify."
topic: getting-around
updated: 2026-11-11
numbers_as_of: 2026-11-11
queue_id: q-getting-around-0061
kind: tool
readers: [upper-year-no-car, grad-student, off-campus, staying-over-break, summer-in-ithaca]
brief: intel/getting-around/brief.md
sources:
  - {url: "https://www.ithacacarshare.org/students-commuters", title: "Ithaca Carshare: Students and commuters", accessed: "2026-11-11"}
  - {url: "https://www.ithacacarshare.org/rates", title: "Ithaca Carshare: Rates", accessed: "2026-11-11"}
  - {url: "https://www.ithacacarshare.org/eligibility", title: "Ithaca Carshare: Eligibility", accessed: "2026-11-11"}
  - {url: "https://fcs.cornell.edu/departments/transportation-delivery-services/parking-campus/parking-students", title: "Cornell Transportation and Delivery Services: Student parking", accessed: "2026-11-11"}
  - {url: "https://sustainable.cornell.edu/campus-initiatives/transportation/ride-car-sharing", title: "Cornell Sustainability: Ride and car sharing", accessed: "2026-11-11"}
index: true
---

Below about 78 hours of driving a year, the Just In Case student plan is the cheaper Ithaca Carshare plan; above it, It's My Car wins. Before tax the line sits at about 93 hours. Put in your hours, miles and vehicle and the tool gives the year's total for each plan, with the $20 sign-up, mileage and the 20% tax on usage, then tells you whether Carshare will approve you and how the total compares with a $752.98 Cornell parking permit.

```tool ithaca-carshare-plan-calculator
```

## Who it is for

Cornell students without a car: upper-years on campus or in Collegetown, grad students, off-campus renters, and anyone staying in Ithaca over a break or for the summer who needs a car for groceries, a hardware run or a day trip. Cornell helps subsidize annual memberships for undergraduate and graduate students; Ithaca College and TC3 students qualify too ([Ithaca Carshare](https://www.ithacacarshare.org/students-commuters)).

## The inputs

- **Hours of driving a year.** Total time booked across the year. Carshare caps hourly charges at 10 hours per 24 hours, so a full-day trip counts as 10 at most.
- **Miles a year.** Total miles in Carshare vehicles. Mileage is billed on both plans.
- **Vehicle.** Car (42 cents a mile), minivan (44 cents) or pickup truck (52 cents).
- **Months you need it.** Leave at 12 for a school year. Set fewer (a summer, a winter break) and the tool also prices the monthly community plans, which carry no student discount.
- **Already a member?** New drivers pay the one-time, non-refundable $20 sign-up; renewing members do not.
- **Age, years licensed, license from outside the US.** These drive the eligibility check, not the price.

## The numbers and the math

For each plan: **total = membership fee + sign-up + (hours x hourly rate + miles x mileage rate) x 1.20.** The 1.20 is 8% New York sales tax plus the 12% special passenger car rental tax ([rates](https://www.ithacacarshare.org/rates)).

Break-even between the two student plans: It's My Car costs $280 more up front ($310 minus $30) and saves $3 an hour ($9 minus $6). Before tax that is 280 / 3 = 93.3 hours. With the 20% tax on the hourly charge it is 280 / (3 x 1.20) = 280 / 3.60 = 77.8 hours. Miles cost the same on both plans, so they do not move the line.

Worked example (the tool's defaults: 20 hours, 100 miles, a car, joining): Just In Case = 30 + 20 + (20 x 9 + 100 x 0.42) x 1.20 = 30 + 20 + 222 x 1.20 = $316.40. It's My Car = 310 + 20 + (20 x 6 + 42) x 1.20 = 310 + 20 + 194.40 = $524.40.

Against a permit: the resident permit is $752.98 a year, so $752.98 minus the $310 It's My Car fee and the $20 sign-up leaves $422.98, which buys about 70 hours at $6 before tax, or about 59 hours at $7.20 with tax, before mileage ([Cornell](https://fcs.cornell.edu/departments/transportation-delivery-services/parking-campus/parking-students)).

| Number | Value | Applies to | Source |
|---|---|---|---|
| Just In Case, student annual | $30 a year ($45 off) | Current, 2026-11-11 | [students-commuters](https://www.ithacacarshare.org/students-commuters) |
| It's My Car, student annual | $310 a year ($45 off); includes gas or EV charging, maintenance, insurance | Current, 2026-11-11 | [students-commuters](https://www.ithacacarshare.org/students-commuters) |
| Just In Case, monthly (community) | $7.50 a month | Current, 2026-11-11 | [rates](https://www.ithacacarshare.org/rates) |
| It's My Car, monthly (community) | $35 a month | Current, 2026-11-11 | [rates](https://www.ithacacarshare.org/rates) |
| Community annual (for reference, not in the tool) | Just In Case $75; It's My Car $355 | Current, 2026-11-11 | [rates](https://www.ithacacarshare.org/rates) |
| Hourly rate | Just In Case $9; It's My Car $6 | Current, 2026-11-11 | [rates](https://www.ithacacarshare.org/rates) |
| Sign-up | $20 per driver, one time, non-refundable | Current, 2026-11-11 | [rates](https://www.ithacacarshare.org/rates) |
| Mileage | Car 42 cents; van 44 cents; truck 52 cents | Current, 2026-11-11 | [rates](https://www.ithacacarshare.org/rates) |
| Taxes on usage | 8% NY sales tax + 12% rental tax = 20% | Current, 2026-11-11 | [rates](https://www.ithacacarshare.org/rates) |
| Daily cap | Hourly charges capped at 10 h per 24 h (not on highest-demand cars) | Current, 2026-11-11 | [rates](https://www.ithacacarshare.org/rates) |
| Minimum age; license | 18; full unrestricted license held 2+ years; no suspension in 3 years | Current, 2026-11-11 | [eligibility](https://www.ithacacarshare.org/eligibility) |
| Under 21 | Spotless record; own policy with at least $300,000 per accident liability; Younger Driver Insurance Consent Form | Current, 2026-11-11 | [eligibility](https://www.ithacacarshare.org/eligibility) |
| 21 and over | At most 2 accidents or violations in 3 years; no DUI or DWI in 7 years | Current, 2026-11-11 | [eligibility](https://www.ithacacarshare.org/eligibility) |
| Resident parking permit | $752.98 a year | Current, 2026-11-11 | [Cornell TDS](https://fcs.cornell.edu/departments/transportation-delivery-services/parking-campus/parking-students) |
| Commuter B permit | $359.77 a year | Current, 2026-11-11 | [Cornell TDS](https://fcs.cornell.edu/departments/transportation-delivery-services/parking-campus/parking-students) |
| Break-even, student plans | 93.3 h before tax; 77.8 h with tax on hours | Our calc, 2026-11-11 | The steps above |

## Assumptions and what it does not cover

- Carshare adds the 20% tax to hourly and mileage charges ([rates](https://www.ithacacarshare.org/rates)); the tool applies it there only, not to membership or sign-up fees.
- The 10-hour daily cap is not applied for you. Enter at most 10 hours for any day you keep a car 24 hours. Highest-demand cars do not get the cap.
- One driver. Student annual plans cover up to two drivers; a second driver's sign-up is another $20.
- Monthly plans are priced only when you set fewer than 12 months, at full community price, since student discounts apply only to annual plans.
- Eligibility is a summary of the official page. Carshare decides. Under 21 without your own insurance policy, the application cannot be approved. A foreign license needs an official driving record; an International Driving Permit is not accepted as one, and some countries cannot be approved. Carshare uses both 2-year and 3-year lookbacks, so call (607) 277-3210 if your record is borderline.
- The permit comparison counts the permit alone, not a car, gas, insurance or tickets.
- Late-return and damage fees are not part of the estimate. Ask Carshare about them, and about mid-year pricing if you join partway through the year.

## How to read the result

The bold row in the table is your cheapest option at the hours and miles you entered. The break-even line tells you how far you are from switching: if you are near 78 hours, small changes in how often you drive flip the answer, and Just In Case costs less up front if you guess wrong. If the eligibility list says "Not eligible", sort that out before paying the $20, which is non-refundable. If your Carshare total comes close to $752.98, you are driving enough that owning a car deserves a real look.

Pick-up is at four on-campus pods and four in Collegetown and nearby ([Cornell Sustainability](https://sustainable.cornell.edu/campus-initiatives/transportation/ride-car-sharing)); apply at reserve.ithacacarshare.org/orientation.

## Related guides

- [Getting to Ithaca and around Cornell, 2026-27](/getting-around/getting-to-ithaca-and-around-cornell/)
- [Ithaca Carshare for Cornell students: plans, cost, rules](/getting-around/ithaca-carshare-cornell-students-cost/)
- [Getting around Cornell after first year without a car](/getting-around/getting-around-cornell-upper-years-no-car/)
- [Getting around Ithaca as an off-campus Cornell renter](/getting-around/getting-around-ithaca-off-campus-renters/)
- [Getting around Ithaca as a Cornell grad student](/getting-around/getting-around-ithaca-cornell-grad-students/)
- [Staying in Ithaca over Cornell breaks: housing, food, rides](/getting-around/staying-in-ithaca-over-cornell-breaks/)
- [Cornell student parking permits: cost, rules, who qualifies](/getting-around/cornell-student-parking-permit-cost-rules/)
