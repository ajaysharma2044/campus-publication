---
title: "OmniRide break-even calculator: $200 pass vs $1.50 fares"
meta: "Enter your Cornell status, paid daytime TCAT rides a week and weeks of riding; get pass or pay-as-you-go, each yearly cost and the 134-ride break-even."
topic: getting-around
updated: 2026-11-08
numbers_as_of: 2026-11-08
queue_id: q-getting-around-0060
kind: tool
readers: [upper-year-no-car, off-campus, grad-student, transfer-spring, low-budget]
brief: intel/getting-around/brief.md
sources:
  - {url: "https://fcs.cornell.edu/departments/transportation-delivery-services/sustainable-transportation-options/bus-services-privileges-passes", title: "Cornell Transportation and Delivery Services: Bus services, privileges and passes", accessed: "2026-11-08"}
  - {url: "https://sustainable.cornell.edu/focus-areas/transportation/bus-commuting", title: "Cornell Sustainability: Bus commuting", accessed: "2026-11-08"}
  - {url: "https://www.cornellsun.com/article/2024/11/non-first-year-cornell-students-no-longer-able-to-access-tcat-for-free", title: "Cornell Daily Sun: Non-first-year Cornell students no longer able to access TCAT for free (Nov 2024)", accessed: "2026-11-08"}
  - {url: "https://www.downtownithaca.com/five-ways-to-pay-your-tcat-fare/", title: "Downtown Ithaca Alliance: Five ways to pay your TCAT fare", accessed: "2026-11-08"}
  - {url: "https://www.tcatbus.com/ride/fare-pass-options/", title: "TCAT: Fare and pass options (search summary; page returned 403)", accessed: "2026-11-08"}
---

This calculator tells you whether Cornell's discounted TCAT pass, OmniRide, costs less than paying $1.50 a ride. You enter who you are at Cornell, how many paid bus rides you take in a week, and for how many weeks. It tells you first whether you ride free already. If you don't, it multiplies your rides by the fare, sets that against the $200 pass, and tells you which is cheaper and by how much.

```tool omniride-break-even-calculator
```

## Who it is for

Sophomores, juniors and seniors without a car. Off-campus renters who take Route 10 or another route to class. Master's and professional students after their first year. Spring entrants and transfers working out when their free year ends. Anyone counting every $10. PhD students and graduate assistants can stop at the first answer: their OmniRide pass is free.

## The inputs

- **Your status this year.** Cornell's rules differ by status:
  - Fall first-years ride free any time until Aug 31 of the next year.
  - Spring entrants ride free from Jan 1 to Dec 31 of the year they start.
  - Transfers count as first-years, according to the Cornell Sun's November 2024 report.
  - PhD students and graduate assistants get OmniRide free.
  - Everyone else rides free only after 6 p.m. on weekdays and all weekend.
- **Paid rides a week.** Count each time you board a bus on a weekday before 6 p.m. Leave out evening and weekend rides, which are free for registered students. A round trip to class is two rides.
- **Weeks you ride.** Count the weeks in the pass year, which ends Aug 31, when you ride at that rate. The default of 30 is a rough academic year. That figure is our assumption, not a Cornell number. Add summer weeks if you stay in Ithaca. Spring entrants should count only the weeks from Jan 1 to Aug 31 after their free year ends.

## The numbers and the math

The math is one multiplication. Paid rides a week × weeks × $1.50 is your pay-as-you-go cost for the year. If that is more than $200, OmniRide wins. The break-even is $200 / $1.50 = 133.3 rides. Fares come in whole rides, so the pass starts saving money at 134 paid rides. Over 30 weeks that works out to 134 / 30 = 4.47, or about 4.5 paid rides a week, so roughly 5 a week (brief 10.14). Some examples:

- 3 rides a week for 30 weeks is 90 rides, or $135. Pay as you go, and keep $65.
- 5 rides a week for 30 weeks is 150 rides, or $225. Buy the pass, and save $25.
- 10 rides a week (to class and back every weekday) for 30 weeks is 300 rides, or $450. Buy the pass, and save $250.

TCAT's fare page reportedly caps what you pay at the farebox at $3 a day, which is two full fares. That makes a heavy rider's cash cost lower. The page could not be read directly, so the calculator shows the capped figure only as a second line, and only when you enter more than 10 rides a week. It assumes your rides are spread evenly over five weekdays. At most 5 × $3 = $15 a week, which over 30 weeks is $450.

| Number | Value | Applies to | Source |
|---|---|---|---|
| OmniRide (Cornell discounted annual pass) | $200 a year, prorated monthly, expires Aug 31 | Cornell page undated; checked 2026-11-08 | [Cornell bus passes page](https://fcs.cornell.edu/departments/transportation-delivery-services/sustainable-transportation-options/bus-services-privileges-passes) |
| TCAT cash fare | $1.50 a ride | Undated pages; checked 2026-11-08 | [Cornell bus passes page](https://fcs.cornell.edu/departments/transportation-delivery-services/sustainable-transportation-options/bus-services-privileges-passes); [Downtown Ithaca](https://www.downtownithaca.com/five-ways-to-pay-your-tcat-fare/) |
| OmniRide refund fee | $40 kept on a prorated refund, until Mar 31 | Cornell page undated; checked 2026-11-08 | [Cornell bus passes page](https://fcs.cornell.edu/departments/transportation-delivery-services/sustainable-transportation-options/bus-services-privileges-passes) |
| Farebox daily cap | $3 a day (two $1.50 fares); not yet on the TFare app | Page reportedly updated 2026-09-04; search summary, not read (403) | [TCAT fare and pass options](https://www.tcatbus.com/ride/fare-pass-options/) |
| Break-even | 134 paid rides (200 / 1.50 = 133.3) | Our calc, 2026-11-08 | Brief 10.14, from the two numbers above |
| Rides a week to break even over 30 weeks | About 4.5 (134 / 30 = 4.47) | Our calc; 30 weeks is an assumption | Brief 10.14 |
| Largest possible refund | Less than $160 (200 - 40; the refund is prorated, so it is lower the later you return the pass) | Our calc, 2026-11-08 | From the numbers above |

Who rides free, from the same sources:

- **First-years.** Free any time with a Cornell ID. Fall entrants are covered from fall registration to Aug 31 of the next year. Spring entrants are covered Jan 1 to Dec 31 of the same year. There are no extensions ([Cornell](https://fcs.cornell.edu/departments/transportation-delivery-services/sustainable-transportation-options/bus-services-privileges-passes), [Cornell Sustainability](https://sustainable.cornell.edu/focus-areas/transportation/bus-commuting)).
- **Transfers.** Free as first-years. This comes from the Cornell Sun reporter's own statement in November 2024. TCAT's general manager is quoted only on the free evening and weekend rides ([Cornell Sun](https://www.cornellsun.com/article/2024/11/non-first-year-cornell-students-no-longer-able-to-access-tcat-for-free)). Confirm with Transportation Services at 607-255-4600.
- **After the first year.** Free after 6 p.m. on weekdays and all day Saturday and Sunday, as long as you stay registered.
- **PhD students and graduate assistants.** OmniRide is free.

## Assumptions and what the tool does not cover

- The 30-week default is our assumption, not a Cornell or TCAT figure (brief 10.14). Use your own count.
- Every paid ride is priced at $1.50. The $0.75 half fare applies to riders 60 and over and riders with disabilities. The calculator does not model it.
- The $3 daily cap comes from a search summary of TCAT's page, because tcatbus.com returned a 403 error every time we tried it. Treat it as unconfirmed.
- If your Cornell ID fails at the farebox during free hours, drivers override it, according to a November 2024 report. Outside free hours you pay $1.50 cash, exact change.
- The public monthly pass ($45) and the 15-ride card ($20) are reported in the same TCAT search summary. The calculator leaves them out because the question is OmniRide or cash.
- Not in the brief: the prorated OmniRide price for a pass bought after the fall, and the formula for the prorated refund. Cornell shows the current price when you buy at MyParking.Cornell.Edu.
- Not in the brief: whether every new master's student counts as a "new student" for the free pass. The Johnson MBA page says TCAT is free in the first year.
- Not in the brief: a 2026 TCAT timetable. Plan your ride count from your own class schedule.

## How to read the result

The first line in bold is the answer: free for you, pay as you go, or buy OmniRide, with the dollars saved for the year. The lines under it show your pay-as-you-go total, the pass price, the 134-ride break-even and the number of rides a week that break-even means over the weeks you entered. If your total sits within a few rides of 134, either choice costs about the same. In that case the refund rule decides it. Until Mar 31 you can return the pass for a prorated refund less $40. After that the $200 is spent. Spring entrants see the cash cost from Jan 1 to Aug 31. Their OmniRide price for that stretch is prorated, so compare the cash total with the price Cornell shows at checkout. The date under the result is the day we checked Cornell's page. Cornell sets the price, so check MyParking.Cornell.Edu before you pay.

## Related guides

- [Getting to Ithaca and around Cornell, 2026-27](/getting-around/getting-to-ithaca-and-around-cornell/), the full topic guide
- [Is TCAT free for Cornell students? Hours, routes, passes](/getting-around/tcat-free-for-cornell-students-hours-routes/)
- [Getting around Cornell after first year without a car](/getting-around/getting-around-cornell-upper-years-no-car/)
- [Getting around Ithaca as an off-campus Cornell renter](/getting-around/getting-around-ithaca-off-campus-renters/)
- [Getting around Ithaca as a Cornell grad student](/getting-around/getting-around-ithaca-cornell-grad-students/)
- [The cheapest ways to get home and around Cornell](/getting-around/cheapest-ways-to-get-around-cornell/)
