---
title: "Is this lease fee legal? Ithaca deposit and fee checker"
meta: "Enter your rent, deposit and each fee your Ithaca landlord asks for; see which are over New York caps, your deposit due date and the 2x penalty."
topic: housing
updated: 2026-11-08
numbers_as_of: 2026-11-08
queue_id: q-housing-0063
kind: tool
readers: [sophomore, upper-year-renter, international, parent, low-budget, alum-landlord]
brief: intel/off-campus-housing/brief.md
sources:
  - {url: "https://www.nysenate.gov/legislation/laws/GOB/7-108", title: "New York General Obligations Law 7-108: security deposits", accessed: "2026-11-08"}
  - {url: "https://www.nysenate.gov/legislation/laws/GOB/7-103", title: "New York General Obligations Law 7-103: deposits held in trust, interest", accessed: "2026-11-11"}
  - {url: "https://www.nysenate.gov/legislation/laws/RPP/238-A", title: "New York Real Property Law 238-a: fees, background checks, late fees", accessed: "2026-11-08"}
  - {url: "https://www.nysenate.gov/legislation/laws/RPP/235-I", title: "New York Real Property Law 235-i: replacement keys", accessed: "2026-11-08"}
  - {url: "https://sites.lawschool.cornell.edu/tenants-advocacy/security-deposits", title: "Cornell Law School Tenants Advocacy: security deposits", accessed: "2026-11-08"}
  - {url: "https://sites.lawschool.cornell.edu/tenants-advocacy/building-issues-maintenance", title: "Cornell Law School Tenants Advocacy: building issues and maintenance (small claims)", accessed: "2026-11-08"}
  - {url: "https://ag.ny.gov/resources/individuals/tenants-homeowners/tenants", title: "New York Attorney General: tenants' rights", accessed: "2026-11-08"}
  - {url: "https://scl.cornell.edu/residential-life/housing/living-off-campus/housing-search-process/moving-and-out", title: "Cornell Off-Campus Living: moving in and out", accessed: "2026-11-08"}
  - {url: "https://finaid.cornell.edu/living-campus", title: "Cornell Financial Aid: living off campus", accessed: "2026-11-08"}
  - {url: "https://ithacarenting.com/collegetown/", title: "Ithaca Renting: Collegetown listings, 2027-28", accessed: "2026-11-08"}
  - {url: "https://cornellsun.com/2024/07/10/landlords-and-advocates-grapple-with-good-cause-eviction-law-at-public-hearing", title: "Cornell Daily Sun: landlords and advocates grapple with Good Cause Eviction law", accessed: "2026-11-08"}
index: false
---

This checker takes the rent on your lease and each charge your landlord wants, and tells you, line by line, whether New York law allows it and by how much it is over. It also turns your move-out date into the date your deposit is due back (14 days later), the window for a move-out inspection, what a court can add if the deposit is kept on purpose (up to twice the deposit), and whether the claim fits in Ithaca small claims court ($5,000). The limits are New York State law as read on Nov 8, 2026; they apply to an Ithaca lease the same way they apply anywhere in the state.

```tool ithaca-lease-fee-deposit-checker
```

## Who it is for

- **A sophomore signing a junior-year lease** this fall: check the deposit, application and cleaning charges before you pay anything at signing.
- **A junior or senior already renting**: check a late fee or key charge now, and get your deposit due date for a July 31 move-out.
- **An international student signing from abroad**: see whether a request to prepay months of rent runs into the one-month cap.
- **A parent paying the deposit**: check the up-front total. Cornell aid does not cover security deposits or first and last month's rent ([Cornell Financial Aid](https://finaid.cornell.edu/living-campus)).
- **A student on a tight budget**: every banned fee you refuse is money you keep.
- **An alum who rents to students**: the same limits, from the landlord's side.

## The inputs

- **Monthly rent**: the rent you pay under the lease. If your lease is per bed, use your share. The default, $1,246.25, is the median per-bed price for a Collegetown four-bedroom at [Ithaca Renting](https://ithacarenting.com/collegetown/) for 2027-28, read Nov 8, 2026.
- **Security deposit**: what the landlord asks you to hold as a deposit.
- **Rent paid in advance**: any rent beyond the first month that you pay up front, such as "last month's rent".
- **Pet deposit**: counts toward the same cap.
- **Application fee**: any charge for processing, reviewing or accepting an application.
- **Background or credit check fee**, and whether you can hand over a check from the past 30 days.
- **Cleaning fee**: a separate cleaning charge or cleaning deposit, not a deduction from your security deposit later.
- **Late fee** and **days late**.
- **Key copy charge**, what the copy cost the landlord if you know, and whether this is more than the third copy of the same key this calendar year.
- **Move-out date**: the day you hand back the keys. The default is July 31, 2027, because most Ithaca student leases end July 31 ([Cornell Daily Sun, 2024](https://cornellsun.com/2024/07/10/landlords-and-advocates-grapple-with-good-cause-eviction-law-at-public-hearing)).

## The rules and the math

Each line is a limit applied to your number. You can redo all of it by hand.

- **Deposit**: deposit + rent advance + pet deposit must be no more than one month's rent ([GOL 7-108](https://www.nysenate.gov/legislation/laws/GOB/7-108)). A non-refundable deposit is not allowed at any amount ([Cornell Law guide](https://sites.lawschool.cornell.edu/tenants-advocacy/security-deposits)). On a $1,246.25 rent, a $1,246.25 deposit is legal; adding a $1,246.25 "last month" makes $2,492.50, which is $1,246.25 over.
- **Application fee**: $0. New York bans any payment for processing, reviewing or accepting an application ([RPL 238-a](https://www.nysenate.gov/legislation/laws/RPP/238-A)).
- **Background or credit check**: the actual cost or $20, whichever is less, and $0 if you provide a check from the past 30 days. The landlord must first give you a copy of the check and the invoice ([RPL 238-a](https://www.nysenate.gov/legislation/laws/RPP/238-A)).
- **Cleaning fee**: $0 as a separate fee ([Cornell Law guide](https://sites.lawschool.cornell.edu/tenants-advocacy/security-deposits), citing RPL 238-a). At move-out, excessive cleaning and trash removal can come out of the deposit; routine cleaning to ready the unit for the next tenant cannot.
- **Late fee**: none until rent is more than 5 days late; then the lesser of $50 or 5% of monthly rent ([RPL 238-a](https://www.nysenate.gov/legislation/laws/RPP/238-A)). Cap = min($50, 0.05 x rent). On $1,246.25 rent, 5% is $62.31, so the cap is $50. Below $1,000 rent, the 5% figure is the cap. Late fees cannot be deducted from the deposit ([Cornell Law guide](https://sites.lawschool.cornell.edu/tenants-advocacy/security-deposits)).
- **Key copy**: at most 110% of what the copy cost the landlord; the cap stops applying after more than three copies of the same key in a calendar year ([RPL 235-i](https://www.nysenate.gov/legislation/laws/RPP/235-I)). Cap = 1.10 x cost. If you do not know the cost, the tool shows the lowest cost that would make the charge legal: charge / 1.10.
- **Deposit due date**: move-out date + 14 days. The landlord must return the deposit, or what is left plus an itemized statement, by then, or loses the right to keep any part ([GOL 7-108](https://www.nysenate.gov/legislation/laws/GOB/7-108)). A July 31, 2027 move-out puts the due date at Aug 14, 2027.
- **Move-out inspection**: when either side gives notice to end the tenancy, the landlord must tell you in writing that you can ask for one. If you ask, it happens between two weeks and one week before the end, with at least 48 hours' written notice ([GOL 7-108](https://www.nysenate.gov/legislation/laws/GOB/7-108)).
- **Penalty**: for a willful violation, punitive damages of up to twice the deposit; the landlord must prove any amount kept was reasonable ([GOL 7-108](https://www.nysenate.gov/legislation/laws/GOB/7-108)). Figure = 2 x (security deposit + pet deposit).
- **Small claims**: up to $5,000 in Ithaca City Court, 118 East Clinton Street; $3,000 in town and village courts ([Cornell Law guide](https://sites.lawschool.cornell.edu/tenants-advocacy/building-issues-maintenance)).

| Number | Value | Applies to | Source |
|---|---|---|---|
| Deposit + rent advance + pet deposit cap | One month's rent | New York, as read 2026-11-08 | [GOL 7-108](https://www.nysenate.gov/legislation/laws/GOB/7-108) |
| Application fee allowed | $0 | New York, as read 2026-11-08 | [RPL 238-a](https://www.nysenate.gov/legislation/laws/RPP/238-A) |
| Background check cap | Lesser of actual cost or $20 | New York, as read 2026-11-08 | [RPL 238-a](https://www.nysenate.gov/legislation/laws/RPP/238-A) |
| Recent check that waives the fee | From the past 30 days | New York, as read 2026-11-08 | [RPL 238-a](https://www.nysenate.gov/legislation/laws/RPP/238-A) |
| Separate cleaning fee allowed | $0 | Cornell Law guide, Feb 2026 | [Cornell Law guide](https://sites.lawschool.cornell.edu/tenants-advocacy/security-deposits) |
| Late fee grace period | More than 5 days late | New York, as read 2026-11-08 | [RPL 238-a](https://www.nysenate.gov/legislation/laws/RPP/238-A) |
| Late fee cap | Lesser of $50 or 5% of monthly rent | New York, as read 2026-11-08 | [RPL 238-a](https://www.nysenate.gov/legislation/laws/RPP/238-A) |
| Key copy cap | 110% of actual cost; not after more than 3 copies of a key in a calendar year | New York, as read 2026-11-08 | [RPL 235-i](https://www.nysenate.gov/legislation/laws/RPP/235-I) |
| Deposit return deadline | 14 days after you vacate | New York, as read 2026-11-08 | [GOL 7-108](https://www.nysenate.gov/legislation/laws/GOB/7-108) |
| Move-out inspection window | 2 weeks to 1 week before the end; 48 hours' written notice | New York, as read 2026-11-08 | [GOL 7-108](https://www.nysenate.gov/legislation/laws/GOB/7-108) |
| Willful-violation penalty | Up to 2x the deposit | New York, as read 2026-11-08 | [GOL 7-108](https://www.nysenate.gov/legislation/laws/GOB/7-108) |
| Small claims, Ithaca City Court | $5,000 | Cornell Law guide, Feb 2026 | [Cornell Law guide](https://sites.lawschool.cornell.edu/tenants-advocacy/building-issues-maintenance) |
| Small claims, town and village courts | $3,000 | Cornell Law guide, Feb 2026 | [Cornell Law guide](https://sites.lawschool.cornell.edu/tenants-advocacy/building-issues-maintenance) |
| Default rent (Collegetown 4BR median per bed) | $1,246.25 a month | 2027-28 leases, read 2026-11-08 | [Ithaca Renting](https://ithacarenting.com/collegetown/) |
| Default move-out date | July 31 (most leases end then) | 2024 report | [Cornell Daily Sun](https://cornellsun.com/2024/07/10/landlords-and-advocates-grapple-with-good-cause-eviction-law-at-public-hearing) |

## Assumptions and what it does not cover

- The deposit cap does not apply to seasonal rentals or to owner-occupied co-op units ([GOL 7-108](https://www.nysenate.gov/legislation/laws/GOB/7-108)). Cornell's own housing is a license with no security deposit, so this tool is for private leases.
- If your rent is increased, the landlord may collect more money from you, but the deposit still cannot exceed the new one month's rent ([NY Attorney General](https://ag.ny.gov/resources/individuals/tenants-homeowners/tenants)). Enter the new rent.
- In buildings with six or more units the deposit must sit in an interest-bearing New York account, and the landlord may keep a 1% annual administrative fee ([NY Attorney General](https://ag.ny.gov/resources/individuals/tenants-homeowners/tenants)). The law sets no fixed rate: the account earns the prevailing rate for such deposits, and the interest is paid to you each year, applied to rent, or held until the deposit is returned ([GOL 7-103](https://www.nysenate.gov/legislation/laws/GOB/7-103)). The tool does not compute interest.
- What counts as damage beyond normal wear is a question of fact. The tool tells you the deadline and the limits, not whether a particular deduction is fair. Deductions are allowed for unpaid rent, damage beyond normal wear, unpaid utilities owed to the landlord, moving and storing belongings you left, and excessive cleaning ([Cornell Law guide](https://sites.lawschool.cornell.edu/tenants-advocacy/security-deposits)).
- Cornell's move-out page says "charges for cleaning services will be deducted" ([Cornell](https://scl.cornell.edu/residential-life/housing/living-off-campus/housing-search-process/moving-and-out)). The Cornell Law guide says a separate cleaning fee is banned and only cleaning beyond routine turnover can be deducted. The tool follows the law guide.
- The tool does not check monthly pet rent (as opposed to a pet deposit), parking or amenity fees, guarantor or co-signer fees, or broker fees.
- Nothing you type is stored or sent anywhere. This is not legal advice. For a free review of your lease or a dispute, call the Cornell Law tenant hotline at 607-301-1560.

## How to read the result

The top line counts the charges over the limit and adds up how much more than the law allows you are being asked to pay at signing (deposit excess, application fee, background-check excess, cleaning fee). Each line below names the charge, says **legal** or **over the limit**, shows the math, and links the statute, so you can forward the line to your landlord or a parent.

"Getting the deposit back" gives the date the deposit or an itemized list is due, the dates to request a move-out inspection, twice your deposit as the most a court can add for a willful violation, and whether your deposit fits in small claims. If the due date passes with nothing from the landlord, send a demand letter, then try CDRC mediation (607-273-9347), then small claims at Ithaca City Court or a complaint to the New York Attorney General ([Cornell Law guide](https://sites.lawschool.cornell.edu/tenants-advocacy/security-deposits)).

## Related guides

- [Off-campus housing at Cornell: the 2026-27 guide](/housing/cornell-off-campus-housing-guide/)
- [Ithaca security deposit rules: the cap, 14 days, banned fees](/housing/ithaca-security-deposit-rules-tenants/)
- [Moving out of an Ithaca apartment: inspection to deposit](/housing/moving-out-ithaca-apartment-deposit-back/)
- [Reading an Ithaca lease before you sign: what to check](/housing/how-to-read-ithaca-lease-before-signing/)
- [Renting near Cornell as an international student: deposits, documents, timing](/housing/off-campus-housing-cornell-international-students/)
- [Already renting near Cornell: renewals, repairs and deposits](/housing/off-campus-housing-cornell-juniors-seniors-renting/)
- [Off-campus housing at Cornell: a parent's guide](/housing/cornell-off-campus-housing-for-parents/)
- [Renting to students in Ithaca: a landlord's legal checklist](/housing/becoming-ithaca-landlord-student-rental-rules/)
