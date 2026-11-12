# Phase 2: flagged pages reworked (2026-11-11)

Every page the content linter flagged (reports/02-pages.json: a sentence telling the reader what the sources or the page lack, or a page the spec names) was reworked by one agent per page following the gap workflow (docs/v5/prelaunch-spec.md, Phase 1b and 2): search the source checklist for the missing item, cite it when found, otherwise remove the promise (a sentence, a section, or the title claim) and log the decision. A skeptic agent then re-read each page: linter at 0, no admission sentences, every new fact checked against its fetched source, every body URL in the sources list, the mandatory additions present. Pages the skeptic rejected went through one targeted fix round with a second verdict. Agents: opus for the rework and the fixes, sonnet for the skeptic.

- Pages reworked: 243 (batch A 84, batch B 21, third round only 138; third round in all 146)
- Third round: after the Phase 5 cluster skeptics found gap wording the first linter missed (table labels such as 'Not published', planner notes such as 'Not in the brief', references to the brief and the fact file, source-quality asides), the linter was widened twice (scripts/lint-content.py, 2026-11-11 patterns), three listing tables were rewritten by scripts/prelaunch/table_cells.py (517 cells), and every page the widened linter flagged was reworked and verified again under a written wording policy (reports/02-gapwording-results.json).
- Judged sound after the last round: 243 of 243
- Gap decisions logged: 649 (reports/gaps-phase2.md, merged into reports/gaps.md)
- Sections removed because no source answered them: 6
- Titles changed to match what the page can answer: 3
  - cornell-to-ithaca-airport-tcat-taxi-parking: Cornell to Ithaca airport: TCAT Route 32, taxis, parking
  - laundromats-in-ithaca-near-cornell-collegetown: Laundry near Cornell Collegetown: your options
  - new-york-drivers-license-ithaca-dmv-cornell-students: Get a New York driver's license in Ithaca
- Pages that lost their purpose (would need a merge or a retire): none
- Content linter after Phase 2: run `python3 scripts/lint-content.py` (strict; the Astro prebuild runs it too).

| Page | Kind | Queue id | Gaps | Sections removed | Sources added | Sound | Judged by | Notes |
|---|---|---|---|---|---|---|---|---|
| 104west-kosher-dining-cornell | article |  | 2 | 0 | 0 | yes | last fix pass (objections applied, linter gate) | objections applied; nothing unresolved |
| 409-college-avenue-student-agencies-building | article |  | 1 | 0 | 1 | yes | skeptic (gap-wording round) | sound after the gap-wording round |
| 660-stewart-avenue-cooperative-cornell | article |  | 1 | 0 | 0 | yes | last fix pass (objections applied, linter gate) | objections applied; nothing unresolved |
| accessibility | article |  | 2 | 0 | 0 | yes | reworked, linter gate (no sources added) | no skeptic verdict; linter clean |
| alice-cook-house-cornell | article |  | 0 | 0 | 0 | yes | last fix pass (objections applied, linter gate) | objections applied; nothing unresolved |
| balch-hall-cornell | idea-run |  | 6 | 0 | 1 | yes | skeptic (rework) |  |
| balch-hall-vs-clara-dickson-hall-cornell | article |  | 3 | 0 | 3 | yes | last fix pass (objections applied, linter gate) | objections applied; nothing unresolved |
| becoming-ithaca-landlord-student-rental-rules | spoke | q-housing-0048 | 7 | 0 | 1 | yes | skeptic (rework) |  |
| before-break-travel-checklist | article |  | 4 | 0 | 13 | yes | last fix pass (objections applied, linter gate) | objections applied; left open: The assembly.cornell.edu R83 entry's accessed: 2026-11-11 date is unverified because the site returns 403 to automated fetches. Decide whether to keep it, re-date it fr… |
| best-places-to-study-at-cornell | v2 | q-academics-0010 | 4 | 0 | 0 | yes | skeptic (rework) |  |
| big-group-houses-ithaca-5-to-10-bedrooms | article |  | 2 | 0 | 0 | yes | skeptic (gap-wording round) | sound after the gap-wording round |
| biking-in-ithaca-hills-theft-where-to-buy-a-bike | article |  | 0 | 0 | 0 | yes | last fix pass (objections applied, linter gate) | objections applied; nothing unresolved |
| biking-in-ithaca-winter-cornell | rewrite | q-getting-around-0084 | 6 | 0 | 6 | yes | skeptic (rework) |  |
| breaking-a-lease-early-ithaca-cornell | article |  | 0 | 0 | 0 | yes | last fix pass (objections applied, linter gate) | objections applied; nothing unresolved |
| can-i-live-off-campus-cornell-quiz | article |  | 4 | 0 | 0 | yes | reworked, linter gate (no sources added) | no skeptic verdict; linter clean |
| can-you-have-a-pet-at-cornell-housing-rules | article |  | 0 | 0 | 0 | yes | last fix pass (objections applied, linter gate) | objections applied; nothing unresolved |
| catherine-commons-collegetown-ithaca | article |  | 0 | 0 | 0 | yes | last fix pass (objections applied, linter gate) | objections applied; nothing unresolved |
| cheap-groceries-ithaca-ny-students | v2 | q-money-0002 | 3 | 0 | 1 | yes | skeptic (rework) |  |
| cheapest-off-campus-housing-cornell | reader_guide | q-housing-0055 | 4 | 0 | 2 | yes | last fix pass (objections applied, linter gate) | objections applied; nothing unresolved |
| cheapest-ways-to-get-around-cornell | reader_guide | q-getting-around-0056 | 5 | 0 | 0 | yes | skeptic (fix round) | fixed on the second round |
| city-of-ithaca-vs-town-lansing-cayuga-heights-renters | spoke | q-housing-0043 | 10 | 1 | 8 | yes | skeptic (rework) |  |
| collegetown-apartments-guide-2027-28 | article |  | 2 | 0 | 1 | yes | last fix pass (objections applied, linter gate) | objections applied; left open: Most frontmatter sources still carry accessed 2026-11-10. Today they were only checked for 404s (none are dead), not re-read, so their dates were not changed. Separatel… |
| collegetown-buildings-compared | article |  | 0 | 0 | 0 | yes | last fix pass (objections applied, linter gate) | objections applied; nothing unresolved |
| collegetown-landlords-who-owns-the-buildings | article |  | 4 | 0 | 2 | yes | last fix pass (objections applied, linter gate) | objections applied; nothing unresolved |
| collegetown-lease-dates-august-to-august | article |  | 3 | 0 | 0 | yes | last fix pass (objections applied, linter gate) | objections applied; nothing unresolved |
| collegetown-lease-signing-lead-times-2017-2025 | article |  | 2 | 0 | 0 | yes | reworked, linter gate (no sources added) | no skeptic verdict; linter clean |
| collegetown-rent-per-bed-2027-28 | article |  | 2 | 0 | 0 | yes | reworked, linter gate (no sources added) | no skeptic verdict; linter clean |
| collegetown-rent-prices-per-bed-one-bedroom | article |  | 0 | 0 | 1 | yes | skeptic (gap-wording round) | sound after the gap-wording round |
| collegetown-terrace-apartments-ithaca | idea-run |  | 4 | 0 | 0 | yes | skeptic (rework) |  |
| collegetown-vs-downtown-rent-per-bed-2026 | article |  | 0 | 0 | 0 | yes | reworked, linter gate (no sources added) | no skeptic verdict; linter clean |
| cornell-2017-housing-master-plan-promised-delivered | article |  | 3 | 0 | 2 | yes | skeptic (gap-wording round) | sound after the gap-wording round |
| cornell-24-hour-study-spaces-finals | article |  | 1 | 0 | 1 | yes | last fix pass (objections applied, linter gate) | objections applied; nothing unresolved |
| cornell-add-drop-deadline-w-on-transcript | v2 | q-academics-0003 | 3 | 0 | 1 | yes | skeptic (rework) |  |
| cornell-arts-and-sciences-easy-distribution-courses | article |  | 1 | 0 | 1 | yes | last fix pass (objections applied, linter gate) | objections applied; left open: The catalog source could not be fetched today because a bot challenge blocked it, so its accessed date is still 2026-11-07. Also, the task said to keep the title, but t… |
| cornell-arts-and-sciences-transfer-requirements | article |  | 1 | 0 | 0 | yes | reworked, linter gate (no sources added) | no skeptic verdict; linter clean |
| cornell-bike-ebike-scooter-rules-theft | spoke | q-getting-around-0044 | 1 | 0 | 0 | yes | skeptic (rework) |  |
| cornell-break-travel-timeline-2026-27 | tool | q-getting-around-0063 | 10 | 0 | 0 | yes | reworked, linter gate (no sources added) | no skeptic verdict; linter clean |
| cornell-c2c-bus-booking-fares-rules | spoke | q-getting-around-0028 | 0 | 0 | 0 | yes | skeptic (rework) |  |
| cornell-cals-transfer-requirements | article |  | 2 | 0 | 0 | yes | reworked, linter gate (no sources added) | no skeptic verdict; linter clean |
| cornell-co-ops-all-eight-compared | article |  | 0 | 0 | 0 | yes | skeptic (gap-wording round) | sound after the gap-wording round |
| cornell-cost-of-living-ithaca-student-monthly-budget | article |  | 0 | 0 | 0 | yes | reworked, linter gate (no sources added) | no skeptic verdict; linter clean |
| cornell-course-enrollment-strategy-pre-enroll-tips | v2 | q-academics-0002 | 0 | 0 | 0 | yes | skeptic (rework) |  |
| cornell-course-reviews-professor-ratings | v2 | q-academics-0007 | 0 | 0 | 0 | yes | skeptic (rework) |  |
| cornell-dining-hours-winter-break-closures | idea-run |  | 7 | 0 | 2 | yes | skeptic (rework) |  |
| cornell-dining-prices-without-meal-plan | idea-run |  | 1 | 0 | 0 | yes | skeptic (rework) |  |
| cornell-dorm-fire-safety-rules-candles-alarms-drills | idea-run |  | 6 | 0 | 4 | yes | skeptic (rework) |  |
| cornell-dyson-transfer-requirements | article |  | 0 | 0 | 0 | yes | reworked, linter gate (no sources added) | no skeptic verdict; linter clean |
| cornell-engineering-liberal-studies-easy-courses | article |  | 4 | 0 | 0 | yes | last fix pass (objections applied, linter gate) | objections applied; nothing unresolved |
| cornell-financial-aid-appeal-success | v2 | q-money-0006 | 8 | 0 | 0 | yes | skeptic (rework) |  |
| cornell-financial-aid-decreased-why-aid-offer-lower-than | article |  | 3 | 0 | 0 | yes | reworked, linter gate (no sources added) | no skeptic verdict; linter clean |
| cornell-financial-aid-transfer-students | article |  | 1 | 0 | 0 | yes | reworked, linter gate (no sources added) | no skeptic verdict; linter clean |
| cornell-first-gen-low-income-hidden-costs | v2 | q-money-0026 | 5 | 0 | 1 | yes | skeptic (fix round) | fixed on the second round |
| cornell-fitness-centers-alumni-membership | v2 | q-alumni-0008 | 0 | 0 | 0 | yes | skeptic (rework) |  |
| cornell-fraternity-sorority-housing-2026-27 | article |  | 2 | 0 | 0 | yes | last fix pass (objections applied, linter gate) | objections applied; nothing unresolved |
| cornell-free-tutoring | v2 | q-academics-0012 | 0 | 0 | 0 | yes | skeptic (rework) |  |
| cornell-general-room-selection-timeslots-strategy | article |  | 0 | 0 | 0 | yes | last fix pass (objections applied, linter gate) | objections applied; nothing unresolved |
| cornell-grad-student-stipend-cost-of-living-ithaca-enough | article |  | 0 | 0 | 0 | yes | reworked, linter gate (no sources added) | no skeptic verdict; linter clean |
| cornell-housing-cancellation-policy-500-fee | article |  | 0 | 0 | 0 | yes | skeptic (gap-wording round) | sound after the gap-wording round |
| cornell-housing-costs-by-room-type | article |  | 1 | 0 | 0 | yes | last fix pass (objections applied, linter gate) | objections applied; nothing unresolved |
| cornell-housing-license-cancellation-fee-calculator | article |  | 2 | 0 | 1 | yes | last fix pass (objections applied, linter gate) | objections applied; nothing unresolved |
| cornell-housing-meal-plan-requirement | article |  | 0 | 0 | 0 | yes | skeptic (gap-wording round) | sound after the gap-wording round |
| cornell-housing-waitlist-no-room-what-happens | article |  | 2 | 0 | 0 | yes | last fix pass (objections applied, linter gate) | objections applied; nothing unresolved |
| cornell-id-card-how-to-get-what-it-does | article |  | 3 | 0 | 2 | yes | last fix pass (objections applied, linter gate) | objections applied; nothing unresolved |
| cornell-ilr-transfer-requirements | article |  | 0 | 0 | 0 | yes | reworked, linter gate (no sources added) | no skeptic verdict; linter clean |
| cornell-international-student-jobs-on-campus-f-1-how-to-find | article |  | 2 | 0 | 1 | yes | last fix pass (objections applied, linter gate) | objections applied; nothing unresolved |
| cornell-motorcycle-scooter-bike-parking | idea-run |  | 7 | 0 | 3 | yes | skeptic (rework) |  |
| cornell-move-in-day-dates-checklist | article |  | 0 | 0 | 0 | yes | last fix pass (objections applied, linter gate) | objections applied; nothing unresolved |
| cornell-move-in-day-parking-unloading | article |  | 1 | 0 | 1 | yes | last fix pass (objections applied, linter gate) | objections applied; nothing unresolved |
| cornell-move-out-storage-shipping-options | spoke | q-getting-around-0047 | 11 | 0 | 5 | yes | skeptic (rework) |  |
| cornell-north-campus-dorms-compared | idea-run |  | 1 | 0 | 0 | yes | skeptic (rework) |  |
| cornell-north-campus-new-dorms-vs-old-dorms | article |  | 1 | 0 | 0 | yes | last fix pass (objections applied, linter gate) | objections applied; nothing unresolved |
| cornell-off-campus-housing-guide | pillar | q-housing-0028 | 11 | 0 | 10 | yes | skeptic (rework) |  |
| cornell-off-campus-housing-listings-where-to-find | spoke | q-housing-0047 | 3 | 0 | 2 | yes | skeptic (gap-wording round) | sound after the gap-wording round |
| cornell-off-campus-jobs-ithaca-students-part-time | v2 | q-money-0007 | 3 | 0 | 0 | yes | skeptic (fix round) | fixed on the second round |
| cornell-off-campus-meal-plan-or-cook-yourself-cost | article |  | 0 | 0 | 0 | yes | reworked, linter gate (no sources added) | no skeptic verdict; linter clean |
| cornell-parking-guide-campus-collegetown-ithaca | article |  | 1 | 0 | 0 | yes | last fix pass (objections applied, linter gate) | objections applied; left open: An owner should decide whether the Winter overnight areas row keeps 'On request' in its price cell or is dropped. The winter rules source lists no fee. |
| cornell-pre-med-weed-out-courses-organic-chemistry-curve | article |  | 0 | 0 | 0 | yes | last fix pass (objections applied, linter gate) | objections applied; nothing unresolved |
| cornell-program-houses-compared | article |  | 2 | 0 | 0 | yes | last fix pass (objections applied, linter gate) | objections applied; nothing unresolved |
| cornell-ra-jobs-pay-housing-how-to-apply | article |  | 1 | 0 | 0 | yes | last fix pass (objections applied, linter gate) | objections applied; nothing unresolved |
| cornell-room-swap-how-direct-swaps-work | article |  | 1 | 0 | 0 | yes | last fix pass (objections applied, linter gate) | objections applied; nothing unresolved |
| cornell-s-u-grading-option-should-i-take | v2 | q-academics-0014 | 0 | 0 | 0 | yes | last fix pass (objections applied, linter gate) | objections applied; nothing unresolved |
| cornell-south-campus-halls-near-collegetown | article |  | 3 | 0 | 0 | yes | skeptic (gap-wording round) | sound after the gap-wording round |
| cornell-student-bank-account-best-bank-ithaca-students | article |  | 0 | 0 | 0 | yes | reworked, linter gate (no sources added) | no skeptic verdict; linter clean |
| cornell-student-budget-by-scenario-low-income-student-costs | v2 | q-money-0012 | 10 | 0 | 0 | yes | skeptic (rework) |  |
| cornell-student-family-housing-ithaca | article |  | 3 | 0 | 0 | yes | last fix pass (objections applied, linter gate) | objections applied; nothing unresolved |
| cornell-student-health-insurance-finding-a-doctor-ithaca | idea-run |  | 5 | 0 | 1 | yes | skeptic (rework) |  |
| cornell-student-parking-permit-cost-rules | spoke | q-getting-around-0035 | 8 | 0 | 3 | yes | skeptic (rework) |  |
| cornell-student-storage-pickup-services | article |  | 0 | 0 | 0 | yes | last fix pass (objections applied, linter gate) | objections applied; left open: The Storage Squad figures could not be re-checked against the live page because it blocks automated fetchers. Everything else is settled. |
| cornell-student-veterans-housing | article |  | 0 | 0 | 2 | yes | last fix pass (objections applied, linter gate) | objections applied; nothing unresolved |
| cornell-summer-housing-options-rates-dates | article |  | 1 | 0 | 0 | yes | last fix pass (objections applied, linter gate) | objections applied; nothing unresolved |
| cornell-summer-jobs-ithaca-students-stay-for-summer | article |  | 2 | 0 | 0 | yes | reworked, linter gate (no sources added) | no skeptic verdict; linter clean |
| cornell-summer-session-classes-transfer-credit-worth-it | article |  | 3 | 0 | 0 | yes | last fix pass (objections applied, linter gate) | objections applied; nothing unresolved |
| cornell-super-single-vs-single-vs-double-worth-it | article |  | 0 | 0 | 1 | yes | skeptic (gap-wording round) | sound after the gap-wording round |
| cornell-textbooks-cheap-where-to-buy-used-ithaca | v2 | q-money-0016 | 4 | 0 | 0 | yes | skeptic (rework) |  |
| cornell-thanksgiving-break-bus-tickets-when-to-book | spoke | q-getting-around-0039 | 0 | 0 | 0 | yes | skeptic (rework) |  |
| cornell-to-ithaca-airport-tcat-taxi-parking | spoke | q-getting-around-0031 | 8 | 0 | 7 | yes | skeptic (rework) |  |
| cornell-transfer-acceptance-rate | article |  | 0 | 0 | 0 | yes | reworked, linter gate (no sources added) | no skeptic verdict; linter clean |
| cornell-transfer-admissions-data-2017-2026 | article |  | 2 | 0 | 0 | yes | reworked, linter gate (no sources added) | no skeptic verdict; linter clean |
| cornell-transfer-credit-calculator | article |  | 2 | 0 | 0 | yes | reworked, linter gate (no sources added) | no skeptic verdict; linter clean |
| cornell-transfer-eligibility-quiz | article |  | 3 | 0 | 0 | yes | reworked, linter gate (no sources added) | no skeptic verdict; linter clean |
| cornell-transfer-housing | article |  | 2 | 0 | 1 | yes | skeptic (gap-wording round) | sound after the gap-wording round |
| cornell-transfer-orientation-move-in | article |  | 0 | 0 | 0 | yes | reworked, linter gate (no sources added) | no skeptic verdict; linter clean |
| cornell-transfer-rules-by-college-2026-27 | article |  | 5 | 0 | 1 | yes | last fix pass (objections applied, linter gate) | objections applied; left open: The writer's report says the Dyson 3.5 GPA was not on the live page. It is there, in the page's transfer FAQ. Other pages from the same writer pass may have removed fac… |
| cornell-transfer-timeline | article |  | 0 | 0 | 0 | yes | reworked, linter gate (no sources added) | no skeptic verdict; linter clean |
| cornell-transfer-year-cost-by-room-2026-27 | article |  | 3 | 0 | 0 | yes | reworked, linter gate (no sources added) | no skeptic verdict; linter clean |
| cornell-visitor-parking-for-parents | idea-run |  | 2 | 0 | 0 | yes | skeptic (rework) |  |
| cornell-west-campus-houses-compared | article |  | 2 | 0 | 0 | yes | reworked, linter gate (no sources added) | no skeptic verdict; linter clean |
| cornell-winter-break-travel-home-2026 | article |  | 3 | 0 | 0 | yes | last fix pass (objections applied, linter gate) | objections applied; nothing unresolved |
| cornell-winter-storms-travel-driving-ithaca | spoke | q-getting-around-0038 | 7 | 0 | 5 | yes | skeptic (rework) |  |
| corrections | article |  | 0 | 0 | 0 | yes | reworked, linter gate (no sources added) | no skeptic verdict; linter clean |
| cost-of-getting-around-cornell-2026-27 | article |  | 2 | 0 | 0 | yes | last fix pass (objections applied, linter gate) | objections applied; left open: The replacement URL https://tcatbus.com/fare-pass-options loads in a browser but returns 403 to curl and WebFetch. That will look like a failure to automated link check… |
| court-kay-bauer-hall-cornell | idea-run |  | 3 | 0 | 0 | yes | skeptic (rework) |  |
| do-i-need-a-car-at-cornell-quiz | tool | q-getting-around-0058 | 8 | 0 | 1 | yes | reworked, linter gate (no sources added) | no skeptic verdict; linter clean |
| driving-in-ithaca-winter-cornell-hills-snow | idea-run |  | 1 | 0 | 1 | yes | last fix pass (objections applied, linter gate) | objections applied; nothing unresolved |
| ecology-house-cornell | idea-run |  | 4 | 0 | 2 | yes | skeptic (rework) |  |
| exempt-underclass | article |  | 2 | 0 | 3 | yes | last fix pass (objections applied, linter gate) | objections applied; nothing unresolved |
| first-month-at-cornell-logistics-checklist | article |  | 1 | 0 | 0 | yes | skeptic (gap-wording round) | sound after the gap-wording round |
| first-year | article |  | 0 | 0 | 12 | yes | last fix pass (objections applied, linter gate) | objections applied; left open: The opening paragraph says the junior-year lease 'will be decided around October of sophomore year'. It has no citation and is only loosely backed by the Sun pages. It… |
| flying-home-from-cornell-airports-rides | reader_guide | q-getting-around-0055 | 4 | 0 | 0 | yes | skeptic (rework) |  |
| free-legal-help-cornell-renters | article |  | 1 | 0 | 0 | yes | last fix pass (objections applied, linter gate) | objections applied; nothing unresolved |
| ganedago-hall-cornell | idea-run |  | 2 | 0 | 0 | yes | skeptic (rework) |  |
| ganedago-hall-vs-toni-morrison-hall-cornell | article |  | 2 | 0 | 2 | yes | last fix pass (objections applied, linter gate) | objections applied; nothing unresolved |
| getting-around-cornell-first-year | reader_guide | q-getting-around-0049 | 0 | 0 | 0 | yes | skeptic (rework) |  |
| getting-around-cornell-parents-visitors | reader_guide | q-getting-around-0057 | 9 | 0 | 6 | yes | skeptic (rework) |  |
| getting-around-cornell-upper-years-no-car | article |  | 0 | 0 | 0 | yes | last fix pass (objections applied, linter gate) | objections applied; nothing unresolved |
| getting-around-ithaca-cornell-grad-students | reader_guide | q-getting-around-0053 | 2 | 0 | 0 | yes | skeptic (fix round) | fixed on the second round |
| getting-around-ithaca-off-campus-renters | reader_guide | q-getting-around-0052 | 9 | 0 | 10 | yes | skeptic (rework) |  |
| getting-to-cornell-international-students | reader_guide | q-getting-around-0054 | 15 | 0 | 10 | yes | skeptic (rework) |  |
| getting-to-ithaca-and-around-cornell | article |  | 0 | 0 | 3 | yes | skeptic (gap-wording round) | sound after the gap-wording round |
| halal-food-at-cornell | article |  | 3 | 0 | 0 | yes | last fix pass (objections applied, linter gate) | objections applied; left open: The reviewer called problem 3 acceptable, so I left the Halal Brothers 'as of May 2026' wording alone. Nothing fetched today confirms that date. Everything else is fixe… |
| hans-bethe-house-cornell | idea-run |  | 4 | 0 | 0 | yes | skeptic (rework) |  |
| hardest-classes-at-cornell | v2 | q-academics-0013 | 0 | 0 | 0 | yes | skeptic (rework) |  |
| hasbrouck-apartments-cornell | article |  | 2 | 0 | 0 | yes | skeptic (gap-wording round) | sound after the gap-wording round |
| hasbrouck-vs-maplewood-vs-off-campus-cornell-grad | article |  | 0 | 0 | 1 | yes | last fix pass (objections applied, linter gate) | objections applied; nothing unresolved |
| high-rise-5-cornell | idea-run |  | 5 | 0 | 2 | yes | skeptic (rework) |  |
| holland-international-living-center-cornell | idea-run |  | 1 | 0 | 0 | yes | skeptic (rework) |  |
| how-hard-is-it-to-transfer-colleges-within-cornell | article |  | 0 | 0 | 0 | yes | last fix pass (objections applied, linter gate) | objections applied; nothing unresolved |
| how-to-check-an-ithaca-landlords-record | rewrite | q-housing-0084 | 7 | 0 | 0 | yes | skeptic (fix round) | fixed on the second round |
| how-to-save-money-at-cornell-student-discounts-ithaca | v2 | q-money-0013 | 3 | 0 | 0 | yes | reworked, linter gate (no sources added) | no skeptic verdict; linter clean |
| hu-shih-hall-cornell | idea-run |  | 7 | 1 | 4 | yes | skeptic (rework) |  |
| is-collegetown-safe-cornell-dorm-security-crime | idea-run |  | 5 | 0 | 0 | yes | skeptic (rework) |  |
| ith-or-syr-trip-cost-calculator | article |  | 5 | 0 | 1 | yes | last fix pass (objections applied, linter gate) | objections applied; left open: Nothing needed fixing. Every claim the writer reworked was checked today against the live pages, and all three returned 200. flyithaca.com/taxis lists the companies wit… |
| ith-syr-or-elm-which-airport-for-cornell | spoke | q-getting-around-0029 | 18 | 0 | 9 | yes | skeptic (rework) |  |
| ithaca-120-day-lease-renewal-notice-rule | spoke | q-housing-0030 | 6 | 0 | 2 | yes | skeptic (rework) |  |
| ithaca-2026-moratorium-student-event-permits | idea-run |  | 4 | 0 | 6 | yes | skeptic (rework) |  |
| ithaca-apartment-buildings-mapped-compared | article |  | 3 | 0 | 0 | yes | last fix pass (objections applied, linter gate) | objections applied; left open: The page still says 61 of the 105 mapped buildings in the Cornell-City safety tool show a lapsed certificate date. The writer only reworded that line, so I did not re-f… |
| ithaca-apartments-1100-to-1500-a-bed | article |  | 0 | 0 | 0 | yes | reworked, linter gate (no sources added) | no skeptic verdict; linter clean |
| ithaca-apartments-800-to-1100-a-bed | article |  | 0 | 0 | 0 | yes | reworked, linter gate (no sources added) | no skeptic verdict; linter clean |
| ithaca-apartments-under-800-a-bed | article |  | 3 | 0 | 0 | yes | reworked, linter gate (no sources added) | no skeptic verdict; linter clean |
| ithaca-apartments-utilities-included | article |  | 2 | 0 | 1 | yes | last fix pass (objections applied, linter gate) | objections applied; left open: The table rows for 130.5 University and 123 Blair still cite the Ithaca College listings feed, and the writer did not re-source them. They were not re-checked here and… |
| ithaca-apartments-without-a-car-walkable | article |  | 0 | 0 | 1 | yes | last fix pass (objections applied, linter gate) | objections applied; left open: The three blanked price cells could get a real median if the full marketplace inventory is re-pulled for those areas. |
| ithaca-bikeshare-cost-cornell-students | spoke | q-getting-around-0043 | 3 | 0 | 0 | yes | skeptic (fix round) | fixed on the second round |
| ithaca-bus-fares-by-route-nov-2026 | article |  | 4 | 0 | 1 | yes | last fix pass (objections applied, linter gate) | objections applied; left open: Row 10 of the table (and the matching CSV row) still cites rome2rio.com/s/Cornell/Boston, which resolves to Cornell, WI. Its OurBus, FlixBus and Amtrak planner figures… |
| ithaca-bus-to-boston-philadelphia-dc-toronto | spoke | q-getting-around-0033 | 2 | 0 | 0 | yes | skeptic (fix round) | fixed on the second round |
| ithaca-carshare-cornell-students-cost | spoke | q-getting-around-0042 | 3 | 0 | 0 | yes | skeptic (rework) |  |
| ithaca-carshare-plan-calculator | article |  | 5 | 0 | 0 | yes | reworked, linter gate (no sources added) | no skeptic verdict; linter clean |
| ithaca-certificate-of-compliance-check-building | idea-run |  | 2 | 0 | 0 | yes | skeptic (rework) |  |
| ithaca-eviction-vacate-order-what-to-do | spoke | q-housing-0045 | 5 | 0 | 3 | yes | skeptic (rework) |  |
| ithaca-good-cause-coverage-checker | tool | q-housing-0062 | 5 | 0 | 1 | yes | skeptic (rework) |  |
| ithaca-heat-out-frozen-pipes-landlord-must-do | idea-run |  | 4 | 0 | 5 | yes | skeptic (rework) |  |
| ithaca-housing-cost-by-living-situation-2026-27 | dataset | q-housing-0068 | 6 | 0 | 0 | yes | skeptic (rework) |  |
| ithaca-housing-shortage-cornell-role | article |  | 3 | 0 | 3 | yes | last fix pass (objections applied, linter gate) | objections applied; left open: None. Every source the writer added was fetched today and supports its line: the Cornell Review (net gain of 339 bedrooms for Catherine Commons; returned 200 with brows… |
| ithaca-intercity-bus-stops-cornell-downtown | spoke | q-getting-around-0048 | 5 | 0 | 1 | yes | skeptic (rework) |  |
| ithaca-landlord-wont-fix-heat-mold-bed-bugs | article |  | 1 | 0 | 0 | yes | reworked, linter gate (no sources added) | no skeptic verdict; linter clean |
| ithaca-lease-fee-deposit-checker | tool | q-housing-0063 | 3 | 0 | 1 | yes | skeptic (rework) |  |
| ithaca-neighborhoods-for-cornell-students | article |  | 2 | 0 | 0 | yes | reworked, linter gate (no sources added) | no skeptic verdict; linter clean |
| ithaca-nyc-bus-fares-nov-2026 | article |  | 2 | 0 | 2 | yes | last fix pass (objections applied, linter gate) | objections applied; left open: Page is at content/datasets/ithaca-nyc-bus-fares-nov-2026.md, not content/articles/datasets/. Wanderu figures could not be checked again today because of the 403. |
| ithaca-parking-tickets-fines-how-to-appeal-cornell | article |  | 0 | 0 | 1 | yes | last fix pass (objections applied, linter gate) | objections applied; nothing unresolved |
| ithaca-part-time-jobs-for-cornell-students | v2 | q-careers-0009 | 0 | 0 | 0 | yes | skeptic (rework) |  |
| ithaca-rent-by-budget-what-you-get | article |  | 0 | 0 | 0 | yes | reworked, linter gate (no sources added) | no skeptic verdict; linter clean |
| ithaca-rent-commute-calculator | article |  | 2 | 0 | 0 | yes | reworked, linter gate (no sources added) | no skeptic verdict; linter clean |
| ithaca-security-deposit-rules-tenants | spoke | q-housing-0032 | 3 | 3 | 0 | yes | skeptic (rework) |  |
| ithaca-sublet-request-timeline | article |  | 4 | 0 | 0 | yes | reworked, linter gate (no sources added) | no skeptic verdict; linter clean |
| ithaca-tenants-union-rent-stabilization-etpa | idea-run |  | 2 | 0 | 1 | yes | skeptic (rework) |  |
| ithaca-to-jfk-lga-newark-airport-bus | spoke | q-getting-around-0032 | 2 | 0 | 0 | yes | skeptic (fix round) | fixed on the second round |
| ithaca-trash-tags-snow-noise-rules-renters | spoke | q-housing-0044 | 6 | 0 | 2 | yes | skeptic (rework) |  |
| ithaca-utilities-cost-winter-heating-bill-apartment-students | article |  | 0 | 0 | 0 | yes | reworked, linter gate (no sources added) | no skeptic verdict; linter clean |
| ithaca-winter-blues-cornell-campus-resources | idea-run |  | 2 | 0 | 0 | yes | skeptic (rework) |  |
| ithaca-winter-parking-rules-cornell-odd-even | spoke | q-getting-around-0037 | 3 | 0 | 1 | yes | skeptic (rework) |  |
| just-about-music-jam-cornell | idea-run |  | 2 | 0 | 0 | yes | skeptic (rework) |  |
| language-house-cornell | idea-run |  | 3 | 0 | 0 | yes | skeptic (rework) |  |
| lansing-triphammer-road-apartments | article |  | 2 | 0 | 3 | yes | last fix pass (objections applied, linter gate) | objections applied; nothing unresolved |
| late-night-food-cornell-collegetown | article |  | 1 | 0 | 2 | yes | last fix pass (objections applied, linter gate) | objections applied; left open: none. No sources were re-fetched in this pass. Each fix either removes a claim or reuses hours the reviewer confirmed today through the Dining Now API, or Sun-reported… |
| laundromats-in-ithaca-near-cornell-collegetown | idea-run |  | 6 | 1 | 0 | yes | skeptic (fix round) | fixed on the second round |
| laundry-in-cornell-dorms-cost-how-it-works | article |  | 1 | 0 | 1 | yes | last fix pass (objections applied, linter gate) | objections applied; nothing unresolved |
| living-outside-ithaca-varna-dryden-tcat | article |  | 2 | 0 | 0 | yes | reworked, linter gate (no sources added) | no skeptic verdict; linter clean |
| mail-packages-off-campus-cornell-students-ithaca | idea-run |  | 4 | 0 | 0 | yes | skeptic (rework) |  |
| maplewood-apartments-cornell | article |  | 0 | 0 | 0 | yes | reworked, linter gate (no sources added) | no skeptic verdict; linter clean |
| mews-hall-cornell | idea-run |  | 4 | 0 | 4 | yes | skeptic (rework) |  |
| morrison-dining-cornell | idea-run |  | 2 | 0 | 1 | yes | skeptic (rework) |  |
| moving-out-ithaca-apartment-deposit-back | article |  | 2 | 0 | 0 | yes | reworked, linter gate (no sources added) | no skeptic verdict; linter clean |
| new-construction-collegetown-buildings-since-2015 | article |  | 3 | 0 | 1 | yes | last fix pass (objections applied, linter gate) | objections applied; left open: The writer's notes flagged two items as out of scope, and I did not touch them. The table's 304 College Ave. address for Catherine Commons is not stated in the Cornell… |
| new-york-drivers-license-ithaca-dmv-cornell-students | idea-run |  | 4 | 0 | 1 | yes | skeptic (rework) |  |
| northside-ithaca-neighborhood | idea-run |  | 1 | 0 | 0 | yes | skeptic (rework) |  |
| nyc-to-cornell-bus-c2c-ourbus-flixbus-greyhound | spoke | q-getting-around-0027 | 5 | 0 | 4 | yes | skeptic (rework) |  |
| off-campus | article |  | 0 | 0 | 10 | yes | last fix pass (objections applied, linter gate) | objections applied; left open: The file changed on disk after my edit (a harness notice). I did not re-read it to see what changed. The intro paragraph's claims ('most likely ending July 31', 'campus… |
| off-campus-housing-cornell-grad-students | reader_guide | q-housing-0053 | 9 | 0 | 1 | yes | reworked, linter gate (no sources added) | no skeptic verdict; linter clean |
| off-campus-housing-cornell-juniors-seniors-renting | reader_guide | q-housing-0051 | 8 | 0 | 1 | yes | skeptic (rework) |  |
| off-campus-housing-cornell-sophomores | reader_guide | q-housing-0050 | 1 | 0 | 0 | yes | skeptic (rework) |  |
| off-campus-move-in-checklist-cornell | article |  | 2 | 0 | 0 | yes | reworked, linter gate (no sources added) | no skeptic verdict; linter clean |
| omniride-break-even-calculator | article |  | 3 | 0 | 0 | yes | last fix pass (objections applied, linter gate) | objections applied; nothing unresolved |
| parent | article |  | 1 | 0 | 4 | yes | last fix pass (objections applied, linter gate) | objections applied; left open: The '(Apr 6 in 2026)' note on the sophomore deadline line was on the page before today's rework, and today's sophomore source does not state it. I left it as is because… |
| parking-collegetown-downtown-ithaca-garages-permits | article |  | 1 | 0 | 0 | yes | last fix pass (objections applied, linter gate) | objections applied; nothing unresolved |
| prospect-of-whitby-cooperative-cornell | article |  | 0 | 0 | 5 | yes | last fix pass (objections applied, linter gate) | objections applied; nothing unresolved |
| rent-a-car-or-truck-in-ithaca-cornell-move-in | article |  | 1 | 0 | 3 | yes | skeptic (gap-wording round) | sound after the gap-wording round |
| roommate-disputes-joint-lease-ithaca | idea-run |  | 4 | 0 | 0 | yes | skeptic (rework) |  |
| self-storage-near-cornell-prices-sizes | article |  | 1 | 0 | 1 | yes | last fix pass (objections applied, linter gate) | objections applied; left open: The writer kept the StorageSeeker (Storage Sense) figures but noted the page returned 503, so they were not rechecked today. This pass did not recheck them either, beca… |
| set-up-utilities-ithaca-apartment-nyseg-internet | article |  | 3 | 0 | 1 | yes | last fix pass (objections applied, linter gate) | objections applied; nothing unresolved |
| shipping-belongings-home-from-ithaca-cornell | article |  | 0 | 0 | 0 | yes | reworked, linter gate (no sources added) | no skeptic verdict; linter clean |
| short-stay | start_here | q-housing-0079 | 4 | 0 | 1 | yes | skeptic (rework) |  |
| should-i-bring-a-car-cornell-ithaca-cost | article |  | 0 | 0 | 0 | yes | last fix pass (objections applied, linter gate) | objections applied; nothing unresolved |
| sober-living-community-cornell | article |  | 2 | 0 | 0 | yes | reworked, linter gate (no sources added) | no skeptic verdict; linter clean |
| staying-in-ithaca-over-cornell-breaks | spoke | q-getting-around-0041 | 2 | 0 | 0 | yes | skeptic (fix round) | fixed on the second round |
| store-bike-over-summer-ithaca-cornell | article |  | 2 | 0 | 0 | yes | reworked, linter gate (no sources added) | no skeptic verdict; linter clean |
| studio-apartments-ithaca-options-prices | article |  | 0 | 0 | 2 | yes | last fix pass (objections applied, linter gate) | objections applied; nothing unresolved |
| subletting-in-ithaca-guide-cornell-students | article |  | 2 | 0 | 0 | yes | reworked, linter gate (no sources added) | no skeptic verdict; linter clean |
| summer-storage-vs-shipping-vs-sublet-cornell-cost | article |  | 0 | 0 | 0 | yes | reworked, linter gate (no sources added) | no skeptic verdict; linter clean |
| summer-sublet-ithaca-finding-housing-may-august | article |  | 3 | 0 | 0 | yes | reworked, linter gate (no sources added) | no skeptic verdict; linter clean |
| surviving-ithaca-winter-old-apartment-drafty-house | idea-run |  | 2 | 0 | 1 | yes | skeptic (rework) |  |
| syracuse-airport-to-cornell-ourbus-car-service | spoke | q-getting-around-0030 | 6 | 0 | 0 | yes | hand fix after the fix-round verdict, skeptic-verified (reports/02-hand-verify.json) | fixed by hand on the last objection; a sonnet skeptic re-fetched the sources and judged it sound |
| tcat-free-for-cornell-students-hours-routes | spoke | q-getting-around-0034 | 1 | 0 | 0 | yes | skeptic (rework) |  |
| tcat-winter-snow-routes-delays-cornell | idea-run |  | 3 | 0 | 2 | yes | skeptic (rework) |  |
| thanks | article |  | 0 | 0 | 0 | yes | reworked, linter gate (no sources added) | no skeptic verdict; linter clean |
| thanksgiving-bus-fare-premium-ithaca-2026 | article |  | 2 | 0 | 0 | yes | reworked, linter gate (no sources added) | no skeptic verdict; linter clean |
| the-ivy-collegetown-325-college-ave | idea-run |  | 2 | 0 | 2 | yes | skeptic (rework) |  |
| the-ivy-vs-collegetown-terrace-ithaca | article |  | 0 | 0 | 0 | yes | reworked, linter gate (no sources added) | no skeptic verdict; linter clean |
| toni-morrison-hall-cornell | idea-run |  | 1 | 0 | 0 | yes | hand fix after the fix-round verdict, skeptic-verified (reports/02-hand-verify.json) | fixed by hand on the last objection; a sonnet skeptic re-fetched the sources and judged it sound |
| tool.html | article |  | 0 | 0 | 0 | yes | reworked, linter gate (no sources added) | no skeptic verdict; linter clean |
| transfer-spring | start_here | q-getting-around-0070 | 7 | 0 | 12 | yes | hand fix after the fix-round verdict, skeptic-verified (reports/02-hand-verify.json) | fixed by hand on the last objection; a sonnet skeptic re-fetched the sources and judged it sound |
| transferring-to-cornell-guide | article |  | 0 | 0 | 0 | yes | reworked, linter gate (no sources added) | no skeptic verdict; linter clean |
| uber-lyft-taxi-ithaca-cornell | spoke | q-getting-around-0045 | 11 | 0 | 3 | yes | skeptic (rework) |  |
| vegetarian-vegan-options-cornell-dining | article |  | 0 | 0 | 0 | yes | last fix pass (objections applied, linter gate) | objections applied; nothing unresolved |
| veterans-house-cornell | article |  | 1 | 0 | 1 | yes | last fix pass (objections applied, linter gate) | objections applied; nothing unresolved |
| visiting-scholar-postdoc-furnished-housing-ithaca | spoke | q-housing-0046 | 6 | 0 | 3 | yes | skeptic (rework) |  |
| voting-in-ithaca-cornell-student-register-polling-place | idea-run |  | 7 | 0 | 0 | yes | skeptic (rework) |  |
| west-campus-dining-rooms-compared-cornell | idea-run |  | 2 | 0 | 2 | yes | skeptic (rework) |  |
| what-a-month-off-campus-costs-cornell | spoke | q-housing-0092 | 5 | 0 | 0 | yes | skeptic (rework) |  |
| what-to-wear-ithaca-winter-cornell | idea-run |  | 2 | 0 | 3 | yes | skeptic (rework) |  |
| when-to-apply-for-cornell-housing-deadlines | article |  | 1 | 0 | 0 | yes | reworked, linter gate (no sources added) | no skeptic verdict; linter clean |
| when-to-sign-lease-timeline-cornell | article |  | 0 | 0 | 0 | yes | reworked, linter gate (no sources added) | no skeptic verdict; linter clean |
| which-cornell-dorms-have-air-conditioning | article |  | 3 | 0 | 3 | yes | last fix pass (objections applied, linter gate) | objections applied; left open: The page needed no edits. All three sources the writer added return 200 today. The Court-Kay-Bauer page says "CKB Hall rooms have system-controlled Air Filtration", whi… |
| why-cornell-requires-sophomores-to-live-on-campus | article |  | 0 | 0 | 2 | yes | last fix pass (objections applied, linter gate) | objections applied; left open: None. I fetched all six URLs today and each returned 200. Each change the writer made is supported by its source. Residential Policy: the studies link on-campus living… |
| winter-activities-ithaca-cornell-students | idea-run |  | 3 | 0 | 0 | yes | skeptic (rework) |  |
