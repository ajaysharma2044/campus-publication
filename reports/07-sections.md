# Phase 7: the empty sections (2026-11-11)

7a. The transfer section was built with the v3 pipeline (scripts/v3: research in five lanes, brief, readers, plan, write, check, publish) as topic `transfer` in topics.yml, data-first: a Common Data Set section D dataset with its CSV and trend chart, one page per undergraduate college (the college structure confirmed from Cornell's site during research), the Guaranteed Transfer option, community college transfer, credit evaluation by college, housing (linking the existing page), orientation, a first-semester checklist, and a deadlines tool. Every page carries the v3 publish requirements (lint, lead photo or figures, reader blocks, sources) and passed the check step before publish.sh took it.

- Transfer pages on disk: 38 (Counter({'spoke': 23, 'reader_guide': 6, 'tool': 5, 'dataset': 3, 'pillar': 1}))
- Published: 38 (articles 30, tools 5, datasets 3); not yet published: none
- Common Data Set dataset published: yes: /datasets/cornell-transfer-admissions-data-2017-2026/
- Start paths that include the transfer section: 13
- Acceptance (at least 10 published pages including the CDS dataset): PASS
- TransferringUp rule (no promotion in any body; the only mention is the labeled line in the author bio): pages mentioning it: none

## Required pages (scripts/prelaunch/transfer_plan_check.py)

```
51 plan rows; parse problems: none
  MISSING  admissions overview (pillar)
  ok       CALS page                                spoke         cornell-cals-transfer-requirements
  ok       Arts and Sciences page                   spoke         cornell-arts-and-sciences-transfer-requirements
  ok       Engineering page                         reader_guide  cornell-engineering-transfer-guide
  ok       Human Ecology page                       spoke         cornell-human-ecology-transfer-requirements
  ok       ILR page                                 spoke         cornell-ilr-transfer-requirements
  ok       Nolan Hotel page                         spoke         cornell-hotel-school-transfer-requirements
  ok       Dyson page                               spoke         cornell-dyson-transfer-requirements
  ok       Brooks page                              spoke         cornell-brooks-school-transfer-requirements
  ok       AAP page                                 spoke         cornell-aap-transfer-requirements
  MISSING  CDS section D dataset
  ok       Guaranteed Transfer option               spoke         cornell-guaranteed-transfer-pathways
  ok       community college transfer               spoke         cornell-guaranteed-transfer-pathways
  ok       transfer credit evaluation               spoke         cornell-transfer-credit-how-many-credits-transfer
  ok       orientation                              spoke         cornell-transfer-orientation-move-in
  ok       first-semester checklist                 tool          cornell-transfer-application-checklist
  ok       deadlines tool or timeline               tool          cornell-transfer-timeline
  ok       transfer housing link (existing page)    reader_guide  cornell-transfer-as-a-junior
2 required page(s) missing
```

## Transfer pages

| URL | Kind | Queue status | Title |
|---|---|---|---|
| /transfer/community-college-to-cornell/ | reader_guide | published | Community college to Cornell: the transfer guide for 2027 |
| /transfer/cornell-aap-transfer-requirements/ | spoke | published | Cornell AAP transfer requirements: portfolio, GPA, B.Arch. |
| /transfer/cornell-arts-and-sciences-transfer-requirements/ | spoke | published | Transferring into Cornell Arts and Sciences: the rules |
| /transfer/cornell-brooks-school-transfer-requirements/ | spoke | published | Cornell Brooks School transfer: courses, GPA and timing |
| /transfer/cornell-cals-transfer-requirements/ | spoke | published | Transferring into Cornell CALS: majors, courses and GPA |
| /transfer/cornell-contract-colleges-ny-resident-transfer/ | spoke | published | NY resident transfers: Cornell contract college tuition |
| /transfer/cornell-dyson-transfer-requirements/ | spoke | published | Cornell Dyson transfer requirements: courses, GPA, dates |
| /transfer/cornell-engineering-transfer-guide/ | reader_guide | published | Cornell Engineering and CS transfer requirements, fall 2027 |
| /transfer/cornell-financial-aid-transfer-students/ | spoke | published | Cornell financial aid for transfers: need-based, no merit |
| /transfer/cornell-guaranteed-transfer-pathways/ | spoke | published | Is there a guaranteed transfer to Cornell? Every pathway |
| /transfer/cornell-hotel-school-transfer-requirements/ | spoke | published | Cornell Hotel School transfer: courses, GPA and dates |
| /transfer/cornell-human-ecology-transfer-requirements/ | spoke | published | Transferring into Cornell Human Ecology: courses and GPA |
| /transfer/cornell-ilr-transfer-requirements/ | spoke | published | Transferring into Cornell ILR: courses, GPA and essays |
| /transfer/cornell-spring-transfer-fall-only/ | spoke | published | Can you transfer to Cornell for spring? Fall only now |
| /transfer/cornell-transfer-acceptance-rate/ | spoke | published | Cornell transfer acceptance rate: 11.7% in fall 2025 |
| /transfer/cornell-transfer-ap-ib-exam-credit/ | spoke | published | Do AP and IB credits count when you transfer to Cornell? |
| /transfer/cornell-transfer-application-materials/ | spoke | published | Cornell transfer application: every piece and who does it |
| /transfer/cornell-transfer-as-a-junior/ | reader_guide | published | Transferring to Cornell as a junior: credits and housing |
| /transfer/cornell-transfer-cost-first-year/ | spoke | published | Cornell transfer cost 2026-27: $95,218 to $99,169 billed |
| /transfer/cornell-transfer-course-enrollment-academics/ | spoke | published | Cornell transfer course enrollment: add/drop and academics |
| /transfer/cornell-transfer-credit-how-many-credits-transfer/ | spoke | published | How many credits transfer to Cornell? Caps and evaluation |
| /transfer/cornell-transfer-deadlines-decision-dates/ | spoke | published | Cornell transfer deadlines for fall 2027 and decision dates |
| /transfer/cornell-transfer-gpa-requirements-by-college/ | spoke | published | What GPA you need to transfer to Cornell, by college |
| /transfer/cornell-transfer-low-income-budget/ | reader_guide | published | Transferring to Cornell on a tight budget: what aid covers |
| /transfer/cornell-transfer-option-guide/ | reader_guide | published | Cornell Transfer Option: is it guaranteed, and what now? |
| /transfer/cornell-transfer-orientation-move-in/ | spoke | published | Cornell transfer orientation and move-in, day by day |
| /transfer/international-transfer-to-cornell/ | reader_guide | published | International transfer to Cornell: aid, credit and F-1 steps |
| /transfer/making-friends-as-a-cornell-transfer/ | spoke | published | Making friends as a Cornell transfer: what worked |
| /transfer/transferring-to-cornell-guide/ | pillar | published | Transferring to Cornell: the complete guide for fall 2027 |
| /transfer/veterans-transferring-to-cornell/ | spoke | published | Veterans and older students transferring to Cornell |
| /tools/cornell-transfer-application-checklist/ | tool | published | Cornell transfer application checklist by college |
| /tools/cornell-transfer-cost-calculator/ | tool | published | Cornell transfer cost calculator: required year, 2026-27 |
| /tools/cornell-transfer-credit-calculator/ | tool | published | Cornell transfer credit calculator: credits lost, semesters |
| /tools/cornell-transfer-eligibility-quiz/ | tool | published | Can I transfer to Cornell? Eligibility and college quiz |
| /tools/cornell-transfer-timeline/ | tool | published | Cornell transfer timeline: your dates, Nov 2026 to Dec 2027 |
| /datasets/cornell-transfer-admissions-data-2017-2026/ | dataset | published | Cornell transfer admissions, 2017 to 2026: 12 terms |
| /datasets/cornell-transfer-rules-by-college-2026-27/ | dataset | published | Cornell transfer rules by college, 2026-27: 9 colleges |
| /datasets/cornell-transfer-year-cost-by-room-2026-27/ | dataset | published | Cornell transfer year cost by room, 2026-27: 13 options |

## Start paths

- /start/accessibility/: Cornell students with a disability: start here
- /start/internal-transfer/: Switching colleges inside Cornell: start here
- /start/international/: International students at Cornell: start here
- /start/low-budget/: Tight budget: start here for Cornell rent, travel, transfer
- /start/ny-resident/: New York residents transferring to Cornell: start here
- /start/parent/: Cornell parents: start here for travel, housing, transfer
- /start/student-family/: With a partner or kids at Cornell: housing and transfer
- /start/transfer-community-college/: Community college transfers to Cornell: start here
- /start/transfer-engineering/: Engineering and CS transfers to Cornell: start here
- /start/transfer-junior/: Junior transfers to Cornell: start here
- /start/transfer-option/: Cornell Transfer Option holders: start here
- /start/transfer-spring/: Cornell transfers: start here for applying, housing, travel
- /start/veteran-nontraditional/: Veterans and older transfers to Cornell: start here

## 7b. Other hubs

Rule: a hub with fewer than five quality articles is hidden from navigation and stays unindexed (Phase 9 keeps every page noindex until a wave releases it). Hidden topics are set with `hidden: true` in site/site.config.ts (Phase 3); their pages still build at their URLs.

| Topic | Published queue rows (all kinds) | Articles on disk | Navigation |
|---|---|---|---|
| academics | 2 | 17 | hidden |
| alumni | 1 | 1 | hidden |
| careers | 1 | 1 | hidden |
| daily-life | 14 | 14 | visible |
| dining | 22 | 21 | visible |
| getting-around | 69 | 42 | visible |
| health-safety | 5 | 5 | visible |
| housing | 224 | 193 | visible |
| money | 14 | 19 | visible |
| parents | 0 | 1 | hidden |
| transfer | 51 | 30 | visible |

- Visible hubs with fewer than 5 articles: none
- Hidden hubs: ['academics', 'alumni', 'careers', 'parents']

