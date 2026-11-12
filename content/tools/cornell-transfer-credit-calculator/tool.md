---
title: "Cornell transfer credit calculator: credits lost, semesters"
meta: "Enter credits, college, AP/IB and course load; see how many credits Cornell can accept, how many you lose and how many semesters you need."
topic: transfer
updated: 2026-11-11
numbers_as_of: 2026-11-11
queue_id: q-transfer-0029
kind: tool
readers: [transfer, transfer-junior, transfer-community-college, transfer-engineering]
brief: intel/transfer/brief.md
sources:
  - {url: "https://registrar.cornell.edu/students/credit-evaluation-services", title: "Cornell University Registrar: Credit evaluation services", accessed: "2026-11-11"}
  - {url: "https://faq.enrollment.cornell.edu/kb/article/327-how-are-my-transfer-credits-evaluated/", title: "Cornell Enrollment FAQ: How are my transfer credits evaluated?", accessed: "2026-11-11"}
  - {url: "https://as.cornell.edu/registrar/transferring-credits", title: "Cornell Arts and Sciences Registrar: Transferring credits", accessed: "2026-11-11"}
  - {url: "https://as.cornell.edu/admissions/admissions-requirements-and-process", title: "Cornell Arts and Sciences: Admissions requirements and process", accessed: "2026-11-11"}
  - {url: "https://www.duffield.cornell.edu/admissions/transfer-applicants/requirements", title: "Cornell Duffield Engineering: Transfer applicant requirements, 2026-27", accessed: "2026-11-11"}
  - {url: "https://cals.cornell.edu/education/admissions/undergraduate-admissions/transfer-applicants", title: "Cornell CALS: Transfer applicants", accessed: "2026-11-11"}
  - {url: "https://www.ilr.cornell.edu/sites/default/files-d8/2026-02/transfer-guidelines-fa-26-final.pdf", title: "Cornell ILR: Transfer guidelines, fall 2026", accessed: "2026-11-11"}
  - {url: "https://business.cornell.edu/admissions/undergraduate/bs-hotel-administration/application-requirements/", title: "Cornell Nolan School of Hotel Administration: Application requirements", accessed: "2026-11-11"}
  - {url: "https://www.human.cornell.edu/admissions/transfer", title: "Cornell Human Ecology: Transfer admissions", accessed: "2026-11-11"}
  - {url: "https://publicpolicy.cornell.edu/undergraduate/apply/transfer-applicants/external-transfers/", title: "Cornell Brooks School: External transfers", accessed: "2026-11-11"}
  - {url: "https://aap.cornell.edu/undergraduate-admissions/transfer-applicants/", title: "Cornell AAP: Transfer applicants", accessed: "2026-11-11"}
  - {url: "https://news.cornell.edu/stories/2026/03/board-trustees-approves-2026-27-budget-parameters", title: "Cornell Chronicle: Board of Trustees approves 2026-27 budget parameters", accessed: "2026-11-11"}
  - {url: "https://finaid.cornell.edu/cost-attend", title: "Cornell Financial Aid: Cost of attendance", accessed: "2026-11-11"}
index: true
---

Cornell accepts at most 60 transfer credits in most of its colleges, AP and IB included, and you must still earn at least 60 credits at Cornell. This calculator applies your college's caps to the credits you will bring, then tells you the most Cornell can accept, how many credits you lose, how many semesters you need at Cornell and how many semesters of college that makes in all. If the total runs past eight semesters, it prices the extra time at 2026-27 tuition and fees. Up to 60 credits, nothing is lost; a 90-credit junior keeps 60, loses 30 and spends ten semesters in college.

```tool cornell-transfer-credit-calculator
```

## Who it is for

- **Sophomore transfers** with two semesters done, who want to confirm they lose nothing and still finish in eight semesters.
- **Junior transfers** with four or more semesters or an associate's degree, deciding whether junior entry costs them a semester or a year.
- **Community college students**, whose credits count the same way: Cornell cannot deny equivalency because a course was taken at a community college or online ([Registrar](https://registrar.cornell.edu/students/credit-evaluation-services)).
- **Engineering and computer science applicants**, who face a 66-credit cap, a 33-credit limit per full-time year and graduation totals of 123 to 137 credits.

## The inputs

- **Cornell college.** Each college sets its own cap and AP/IB limit. Computer science comes through Engineering (B.S.) or Arts and Sciences (B.A.).
- **Calendar.** Semesters or quarters. Quarter credits convert at two-thirds: 90 quarter credits are 60 semester credits.
- **College credits earned before Cornell.** Courses only, not AP or IB. Count letter-graded courses with a C or better from a regionally accredited school; those are the ones that can transfer ([Registrar](https://registrar.cornell.edu/students/credit-evaluation-services)).
- **Full-time terms completed.** Semesters or quarters. This sets your time in college before Cornell and, for Engineering, the 33-credits-a-year limit.
- **AP, IB or A-Level credits.** What you hope Cornell grants under its own score rules. Exam credit is not automatic, and where an exam and a course overlap, only the course counts.
- **Credits a Cornell semester.** Defaults to 15. Change it to the load you plan to carry.
- **New York resident.** Changes tuition only at the contract colleges (CALS, Human Ecology, ILR, Brooks, Dyson).

## The numbers and the math

1. Convert quarters: semester credits = quarter credits x 2/3; semesters elsewhere = quarters x 2/3.
2. Apply the AP/IB limit: exam credits counted = the smaller of your exam credits and the college's limit (CALS 15, ILR 12, Hotel 15, Human Ecology 15 pre-college credits; other colleges count exam credit inside the main cap with no separate limit).
3. Engineering only: course credits counted = the smaller of your course credits and 33 x full-time years elsewhere.
4. Credits accepted = the smaller of (courses counted + exam credits counted) and the cap: 60, Engineering 66, Architecture 64.
5. Credits lost = everything you brought minus credits accepted.
6. Credits still needed at Cornell = credits to graduate minus credits accepted, but never fewer than 60 (Architecture 90).
7. Cornell semesters = credits still needed / your load, rounded up, and never fewer than four in Arts and Sciences, ILR and Brooks.
8. Total semesters = semesters elsewhere + Cornell semesters. Anything past eight (ten for the five-year B.Arch.) is extra time.
9. Extra cost = extra semesters x half a year's tuition and fees: endowed $73,946 + $1,024 = $74,970 a year, $37,485 a semester; New York resident at a contract college $49,816 + $1,024 = $50,840 a year, $25,420 a semester.

Worked example, Arts and Sciences, 90 credits over six semesters: accepted = min(90, 60) = 60; lost = 30; still needed = 120 - 60 = 60; Cornell semesters = 60 / 15 = 4, which is also the residence floor; total = 6 + 4 = 10 semesters, two more than eight. That extra year costs $74,970 in endowed tuition and fees before housing and aid.

Engineering example: two full-time years elsewhere x 33 = 66, the whole cap. A third year adds nothing.

| Number | Value | Applies to | Source |
|---|---|---|---|
| Transfer credit cap, most colleges | 60 semester credits, exam credit included | 2025 policy; checked 2026-11-11 | [Registrar](https://registrar.cornell.edu/students/credit-evaluation-services); [Enrollment FAQ](https://faq.enrollment.cornell.edu/kb/article/327-how-are-my-transfer-credits-evaluated/) |
| Engineering cap | 66 total, including AP, IB, GCE and CASE | 2026-27 | [Duffield](https://www.duffield.cornell.edu/admissions/transfer-applicants/requirements) |
| Engineering per-year limit | 33 credits per full-time year | 2026-27 | [Duffield](https://www.duffield.cornell.edu/admissions/transfer-applicants/requirements) |
| Architecture cap | 64 | checked 2026-11-11 | [Registrar](https://registrar.cornell.edu/students/credit-evaluation-services) |
| Minimum credits at Cornell | 60 (Architecture 90) | checked 2026-11-11 | [Registrar](https://registrar.cornell.edu/students/credit-evaluation-services) |
| Minimum semesters at Cornell | 4 in Arts and Sciences, ILR and Brooks | current; ILR fall 2026 | [A&S](https://as.cornell.edu/admissions/admissions-requirements-and-process); [ILR](https://www.ilr.cornell.edu/sites/default/files-d8/2026-02/transfer-guidelines-fa-26-final.pdf); [Brooks](https://publicpolicy.cornell.edu/undergraduate/apply/transfer-applicants/external-transfers/) |
| Credits to graduate, Arts and Sciences | 120 (100 must be A&S credits) | checked 2026-11-11 | [A&S Registrar](https://as.cornell.edu/registrar/transferring-credits) |
| Credits to graduate, Engineering | 123 to 137, by major | checked 2026-11-11 | [Registrar](https://registrar.cornell.edu/students/credit-evaluation-services) |
| Credits to graduate, Architecture | 154 over five years | checked 2026-11-11 | [Registrar](https://registrar.cornell.edu/students/credit-evaluation-services) |
| AP/IB limit, CALS | 15 (test plus transfer up to 60) | current | [CALS](https://cals.cornell.edu/education/admissions/undergraduate-admissions/transfer-applicants) |
| AP limit, ILR | 12 | fall 2026 | [ILR](https://www.ilr.cornell.edu/sites/default/files-d8/2026-02/transfer-guidelines-fa-26-final.pdf) |
| AP/IB/GCE limit, Hotel | 15 | 2026-27 | [Hotel](https://business.cornell.edu/admissions/undergraduate/bs-hotel-administration/application-requirements/) |
| Pre-college credit limit, Human Ecology | 15 | current | [Human Ecology](https://www.human.cornell.edu/admissions/transfer) |
| Quarter to semester credits | x 2/3 (Human Ecology writes 0.67) | checked 2026-11-11 | [Registrar](https://registrar.cornell.edu/students/credit-evaluation-services) |
| Tuition, endowed colleges and all non-NY students | $73,946 a year | 2026-27 (approved March 23, 2026) | [Cornell Chronicle](https://news.cornell.edu/stories/2026/03/board-trustees-approves-2026-27-budget-parameters) |
| Tuition, NY residents at contract colleges | $49,816 a year | 2026-27 | [Cornell Chronicle](https://news.cornell.edu/stories/2026/03/board-trustees-approves-2026-27-budget-parameters) |
| Mandatory fees | $1,024 a year ($424 activity, $600 Cornell Health) | 2026-27 figures | [Financial Aid](https://finaid.cornell.edu/cost-attend) |
| Extra year, endowed, tuition and fees | $74,970 ($37,485 a semester, our arithmetic) | 2026-27 | from the rows above |
| Extra year, NY contract, tuition and fees | $50,840 ($25,420 a semester, our arithmetic) | 2026-27 | from the rows above |

## Assumptions and what the tool does not cover

- The result is a ceiling. Each college evaluates course by course after admission: about 80% similar to a Cornell course, C or better, syllabus and official transcript ([Registrar](https://registrar.cornell.edu/students/credit-evaluation-services)). CALS and AAP give no credit evaluation before admission.
- Courses that transfer only as electives can still leave requirements unmet, which can add Cornell semesters the tool does not count.
- Courses that never transfer: orientation, study skills, career development, math below precalculus, remedial courses and MOOCs; courses seven or more years old generally do not either ([Registrar](https://registrar.cornell.edu/students/credit-evaluation-services)).
- Engineering's 33 a year is applied to course credits and the 66 to courses plus exams together. Engineering counts exam credit only above its thresholds: a 5 on AP Calculus BC, AP Chemistry or AP Physics C Mechanics ([Duffield](https://www.duffield.cornell.edu/admissions/transfer-applicants/requirements)).
- Exam credit must be requested in writing from your college registrar by the last day of instruction of your first Cornell semester ([Registrar](https://registrar.cornell.edu/students/credit-evaluation-services)).
- Loads above 15 credits a semester assume Cornell lets you carry them. They cannot get you under the four-semester floor in Arts and Sciences, ILR and Brooks.
- Extra cost uses 2026-27 rates; 2027-28 rates are confirmed before early April 2027. It leaves out housing, food, health insurance and aid.
- For CALS, ILR, Hotel, Human Ecology, Brooks, Dyson and AAP's Art and Planning programs, the tool uses the Arts and Sciences total of 120 credits to graduate and says so in the result. Confirm your college's own total with its registrar.
- In CALS, Hotel, Human Ecology, Dyson, Engineering and AAP the tool applies only the 60-credit rule. Ask your college about any semester residence rule and the most credits you may carry a semester.
- AAP is not accepting external transfer applications for the fall 2027 B.Arch. ([AAP](https://aap.cornell.edu/undergraduate-admissions/transfer-applicants/)); the Architecture option shows the rules for later years.

## How to read the result

The bold line is the answer: the most credits Cornell can accept, how many you lose, the semesters you need at Cornell and the total semesters of college. If that total passes eight, the bold line says by how much, and a line below prices each extra semester at 2026-27 tuition and fees. The lines under it show why credits were lost (an AP limit, Engineering's per-year limit or the total cap), the credit math for your Cornell semesters, and one rule from your college that most often costs transfers credit. For Engineering the semesters show as a range, from the 123-credit majors to the 137-credit ones. If you are choosing between applying now and waiting a year, run both: at 60 credits or fewer, waiting usually loses nothing; past 60, every 15 credits adds about a semester.

## Related guides

- [Transferring to Cornell: the complete guide for fall 2027](/transfer/transferring-to-cornell-guide/)
- [How many credits transfer to Cornell? Caps and evaluation](/transfer/cornell-transfer-credit-how-many-credits-transfer/)
- [Do AP and IB credits count when you transfer to Cornell?](/transfer/cornell-transfer-ap-ib-exam-credit/)
- [Transferring to Cornell as a junior: credits and housing](/transfer/cornell-transfer-as-a-junior/)
- [Community college to Cornell: the transfer guide](/transfer/community-college-to-cornell/)
- [Transferring to Cornell Engineering or computer science](/transfer/cornell-engineering-transfer-guide/)
- [What a transfer year at Cornell costs, 2026-27](/transfer/cornell-transfer-cost-first-year/)
