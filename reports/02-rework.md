# Phase 2: flagged pages reworked (2026-11-11)

Every page the content linter flagged (reports/02-pages.json: a sentence telling the reader what the sources or the page lack, or a page the spec names) was reworked by one agent per page following the gap workflow (docs/v5/prelaunch-spec.md, Phase 1b and 2): search the source checklist for the missing item, cite it when found, otherwise remove the promise (a sentence, a section, or the title claim) and log the decision. A skeptic agent then re-read each page: linter at 0, no admission sentences, every new fact checked against its fetched source, every body URL in the sources list, the mandatory additions present. Pages the skeptic rejected went through one targeted fix round with a second verdict. Agents: opus for the rework and the fixes, sonnet for the skeptic.

- Pages reworked: 105 (batch A 84, batch B 21, third round only 0; third round in all 0)
- Third round: after the Phase 5 cluster skeptics found gap wording the first linter missed (table labels such as 'Not published', planner notes such as 'Not in the brief', references to the brief and the fact file, source-quality asides), the linter was widened twice (scripts/lint-content.py, 2026-11-11 patterns), three listing tables were rewritten by scripts/prelaunch/table_cells.py (517 cells), and every page the widened linter flagged was reworked and verified again under a written wording policy (reports/02-gapwording-results.json).
- Judged sound after the last round: 105 of 105
- Gap decisions logged: 455 (reports/gaps-phase2.md, merged into reports/gaps.md)
- Sections removed because no source answered them: 6
- Titles changed to match what the page can answer: 3
  - cornell-to-ithaca-airport-tcat-taxi-parking: Cornell to Ithaca airport: TCAT Route 32, taxis, parking
  - laundromats-in-ithaca-near-cornell-collegetown: Laundry near Cornell Collegetown: your options
  - new-york-drivers-license-ithaca-dmv-cornell-students: Get a New York driver's license in Ithaca
- Pages that lost their purpose (would need a merge or a retire): none
- Content linter after Phase 2: run `python3 scripts/lint-content.py` (strict; the Astro prebuild runs it too).

| Page | Kind | Queue id | Gaps | Sections removed | Sources added | Sound | Judged by | Notes |
|---|---|---|---|---|---|---|---|---|
| balch-hall-cornell | idea-run |  | 6 | 0 | 1 | yes | skeptic (rework) |  |
| becoming-ithaca-landlord-student-rental-rules | spoke | q-housing-0048 | 7 | 0 | 1 | yes | skeptic (rework) |  |
| best-places-to-study-at-cornell | v2 | q-academics-0010 | 4 | 0 | 0 | yes | skeptic (rework) |  |
| biking-in-ithaca-winter-cornell | rewrite | q-getting-around-0084 | 6 | 0 | 6 | yes | skeptic (rework) |  |
| cheap-groceries-ithaca-ny-students | v2 | q-money-0002 | 3 | 0 | 1 | yes | skeptic (rework) |  |
| cheapest-off-campus-housing-cornell | reader_guide | q-housing-0055 | 4 | 0 | 2 | yes | skeptic (rework) |  |
| cheapest-ways-to-get-around-cornell | reader_guide | q-getting-around-0056 | 5 | 0 | 0 | yes | skeptic (fix round) | fixed on the second round |
| city-of-ithaca-vs-town-lansing-cayuga-heights-renters | spoke | q-housing-0043 | 10 | 1 | 8 | yes | skeptic (rework) |  |
| collegetown-terrace-apartments-ithaca | idea-run |  | 4 | 0 | 0 | yes | skeptic (rework) |  |
| cornell-add-drop-deadline-w-on-transcript | v2 | q-academics-0003 | 3 | 0 | 1 | yes | skeptic (rework) |  |
| cornell-bike-ebike-scooter-rules-theft | spoke | q-getting-around-0044 | 1 | 0 | 0 | yes | skeptic (rework) |  |
| cornell-break-travel-timeline-2026-27 | tool | q-getting-around-0063 | 10 | 0 | 0 | yes | hand fix after the fix-round verdict, re-linted | the skeptic's last point (one '(year inferred from weekdays)' and the 'Undated' date cells) was fixed by hand: the cells now read 'Current as of 2026-11-08'; linter 0, em dashes 0 |
| cornell-c2c-bus-booking-fares-rules | spoke | q-getting-around-0028 | 0 | 0 | 0 | yes | skeptic (rework) |  |
| cornell-course-enrollment-strategy-pre-enroll-tips | v2 | q-academics-0002 | 0 | 0 | 0 | yes | skeptic (rework) |  |
| cornell-course-reviews-professor-ratings | v2 | q-academics-0007 | 0 | 0 | 0 | yes | skeptic (rework) |  |
| cornell-dining-hours-winter-break-closures | idea-run |  | 7 | 0 | 2 | yes | skeptic (rework) |  |
| cornell-dining-prices-without-meal-plan | idea-run |  | 1 | 0 | 0 | yes | skeptic (rework) |  |
| cornell-dorm-fire-safety-rules-candles-alarms-drills | idea-run |  | 6 | 0 | 4 | yes | skeptic (rework) |  |
| cornell-financial-aid-appeal-success | v2 | q-money-0006 | 8 | 0 | 0 | yes | skeptic (rework) |  |
| cornell-first-gen-low-income-hidden-costs | v2 | q-money-0026 | 5 | 0 | 1 | yes | skeptic (fix round) | fixed on the second round |
| cornell-fitness-centers-alumni-membership | v2 | q-alumni-0008 | 0 | 0 | 0 | yes | skeptic (rework) |  |
| cornell-free-tutoring | v2 | q-academics-0012 | 0 | 0 | 0 | yes | skeptic (rework) |  |
| cornell-motorcycle-scooter-bike-parking | idea-run |  | 7 | 0 | 3 | yes | skeptic (rework) |  |
| cornell-move-out-storage-shipping-options | spoke | q-getting-around-0047 | 11 | 0 | 5 | yes | skeptic (rework) |  |
| cornell-north-campus-dorms-compared | idea-run |  | 1 | 0 | 0 | yes | skeptic (rework) |  |
| cornell-off-campus-housing-guide | pillar | q-housing-0028 | 11 | 0 | 10 | yes | skeptic (rework) |  |
| cornell-off-campus-housing-listings-where-to-find | spoke | q-housing-0047 | 3 | 0 | 2 | yes | skeptic (rework) |  |
| cornell-off-campus-jobs-ithaca-students-part-time | v2 | q-money-0007 | 3 | 0 | 0 | yes | skeptic (fix round) | fixed on the second round |
| cornell-s-u-grading-option-should-i-take | v2 | q-academics-0014 | 0 | 0 | 0 | yes | skeptic (rework) |  |
| cornell-student-budget-by-scenario-low-income-student-costs | v2 | q-money-0012 | 10 | 0 | 0 | yes | skeptic (rework) |  |
| cornell-student-health-insurance-finding-a-doctor-ithaca | idea-run |  | 5 | 0 | 1 | yes | skeptic (rework) |  |
| cornell-student-parking-permit-cost-rules | spoke | q-getting-around-0035 | 8 | 0 | 3 | yes | skeptic (rework) |  |
| cornell-textbooks-cheap-where-to-buy-used-ithaca | v2 | q-money-0016 | 4 | 0 | 0 | yes | skeptic (rework) |  |
| cornell-thanksgiving-break-bus-tickets-when-to-book | spoke | q-getting-around-0039 | 0 | 0 | 0 | yes | skeptic (rework) |  |
| cornell-to-ithaca-airport-tcat-taxi-parking | spoke | q-getting-around-0031 | 8 | 0 | 7 | yes | skeptic (rework) |  |
| cornell-visitor-parking-for-parents | idea-run |  | 2 | 0 | 0 | yes | skeptic (rework) |  |
| cornell-winter-storms-travel-driving-ithaca | spoke | q-getting-around-0038 | 7 | 0 | 5 | yes | skeptic (rework) |  |
| court-kay-bauer-hall-cornell | idea-run |  | 3 | 0 | 0 | yes | skeptic (rework) |  |
| do-i-need-a-car-at-cornell-quiz | tool | q-getting-around-0058 | 6 | 0 | 1 | yes | skeptic (fix round) | fixed on the second round |
| driving-in-ithaca-winter-cornell-hills-snow | idea-run |  | 1 | 0 | 1 | yes | skeptic (rework) |  |
| ecology-house-cornell | idea-run |  | 4 | 0 | 2 | yes | skeptic (rework) |  |
| flying-home-from-cornell-airports-rides | reader_guide | q-getting-around-0055 | 4 | 0 | 0 | yes | skeptic (rework) |  |
| ganedago-hall-cornell | idea-run |  | 2 | 0 | 0 | yes | skeptic (rework) |  |
| getting-around-cornell-first-year | reader_guide | q-getting-around-0049 | 0 | 0 | 0 | yes | skeptic (rework) |  |
| getting-around-cornell-parents-visitors | reader_guide | q-getting-around-0057 | 9 | 0 | 6 | yes | skeptic (rework) |  |
| getting-around-ithaca-cornell-grad-students | reader_guide | q-getting-around-0053 | 2 | 0 | 0 | yes | skeptic (fix round) | fixed on the second round |
| getting-around-ithaca-off-campus-renters | reader_guide | q-getting-around-0052 | 9 | 0 | 10 | yes | skeptic (rework) |  |
| getting-to-cornell-international-students | reader_guide | q-getting-around-0054 | 15 | 0 | 10 | yes | skeptic (rework) |  |
| hans-bethe-house-cornell | idea-run |  | 4 | 0 | 0 | yes | skeptic (rework) |  |
| hardest-classes-at-cornell | v2 | q-academics-0013 | 0 | 0 | 0 | yes | skeptic (rework) |  |
| high-rise-5-cornell | idea-run |  | 5 | 0 | 2 | yes | skeptic (rework) |  |
| holland-international-living-center-cornell | idea-run |  | 1 | 0 | 0 | yes | skeptic (rework) |  |
| how-to-check-an-ithaca-landlords-record | rewrite | q-housing-0084 | 7 | 0 | 0 | yes | skeptic (fix round) | fixed on the second round |
| how-to-save-money-at-cornell-student-discounts-ithaca | v2 | q-money-0013 | 3 | 0 | 0 | yes | hand fix after the fix-round verdict, skeptic-verified (reports/02-hand-verify.json) | fixed by hand on the last objection; a sonnet skeptic re-fetched the sources and judged it sound |
| hu-shih-hall-cornell | idea-run |  | 7 | 1 | 4 | yes | skeptic (rework) |  |
| is-collegetown-safe-cornell-dorm-security-crime | idea-run |  | 5 | 0 | 0 | yes | skeptic (rework) |  |
| ith-syr-or-elm-which-airport-for-cornell | spoke | q-getting-around-0029 | 18 | 0 | 9 | yes | skeptic (rework) |  |
| ithaca-120-day-lease-renewal-notice-rule | spoke | q-housing-0030 | 6 | 0 | 2 | yes | skeptic (rework) |  |
| ithaca-2026-moratorium-student-event-permits | idea-run |  | 4 | 0 | 6 | yes | skeptic (rework) |  |
| ithaca-bikeshare-cost-cornell-students | spoke | q-getting-around-0043 | 3 | 0 | 0 | yes | skeptic (fix round) | fixed on the second round |
| ithaca-bus-to-boston-philadelphia-dc-toronto | spoke | q-getting-around-0033 | 2 | 0 | 0 | yes | skeptic (fix round) | fixed on the second round |
| ithaca-carshare-cornell-students-cost | spoke | q-getting-around-0042 | 3 | 0 | 0 | yes | skeptic (rework) |  |
| ithaca-certificate-of-compliance-check-building | idea-run |  | 2 | 0 | 0 | yes | skeptic (rework) |  |
| ithaca-eviction-vacate-order-what-to-do | spoke | q-housing-0045 | 5 | 0 | 3 | yes | skeptic (rework) |  |
| ithaca-good-cause-coverage-checker | tool | q-housing-0062 | 5 | 0 | 1 | yes | skeptic (rework) |  |
| ithaca-heat-out-frozen-pipes-landlord-must-do | idea-run |  | 4 | 0 | 5 | yes | skeptic (rework) |  |
| ithaca-housing-cost-by-living-situation-2026-27 | dataset | q-housing-0068 | 6 | 0 | 0 | yes | skeptic (rework) |  |
| ithaca-intercity-bus-stops-cornell-downtown | spoke | q-getting-around-0048 | 5 | 0 | 1 | yes | skeptic (rework) |  |
| ithaca-lease-fee-deposit-checker | tool | q-housing-0063 | 3 | 0 | 1 | yes | skeptic (rework) |  |
| ithaca-part-time-jobs-for-cornell-students | v2 | q-careers-0009 | 0 | 0 | 0 | yes | skeptic (rework) |  |
| ithaca-security-deposit-rules-tenants | spoke | q-housing-0032 | 3 | 3 | 0 | yes | skeptic (rework) |  |
| ithaca-tenants-union-rent-stabilization-etpa | idea-run |  | 2 | 0 | 1 | yes | skeptic (rework) |  |
| ithaca-to-jfk-lga-newark-airport-bus | spoke | q-getting-around-0032 | 2 | 0 | 0 | yes | skeptic (fix round) | fixed on the second round |
| ithaca-trash-tags-snow-noise-rules-renters | spoke | q-housing-0044 | 6 | 0 | 2 | yes | skeptic (rework) |  |
| ithaca-winter-blues-cornell-campus-resources | idea-run |  | 2 | 0 | 0 | yes | skeptic (rework) |  |
| ithaca-winter-parking-rules-cornell-odd-even | spoke | q-getting-around-0037 | 3 | 0 | 1 | yes | skeptic (rework) |  |
| just-about-music-jam-cornell | idea-run |  | 2 | 0 | 0 | yes | skeptic (rework) |  |
| language-house-cornell | idea-run |  | 3 | 0 | 0 | yes | skeptic (rework) |  |
| laundromats-in-ithaca-near-cornell-collegetown | idea-run |  | 6 | 1 | 0 | yes | skeptic (fix round) | fixed on the second round |
| mail-packages-off-campus-cornell-students-ithaca | idea-run |  | 4 | 0 | 0 | yes | skeptic (rework) |  |
| mews-hall-cornell | idea-run |  | 4 | 0 | 4 | yes | skeptic (rework) |  |
| morrison-dining-cornell | idea-run |  | 2 | 0 | 1 | yes | skeptic (rework) |  |
| new-york-drivers-license-ithaca-dmv-cornell-students | idea-run |  | 4 | 0 | 1 | yes | skeptic (rework) |  |
| northside-ithaca-neighborhood | idea-run |  | 1 | 0 | 0 | yes | skeptic (rework) |  |
| nyc-to-cornell-bus-c2c-ourbus-flixbus-greyhound | spoke | q-getting-around-0027 | 5 | 0 | 4 | yes | skeptic (rework) |  |
| off-campus-housing-cornell-grad-students | reader_guide | q-housing-0053 | 6 | 0 | 1 | yes | skeptic (rework) |  |
| off-campus-housing-cornell-juniors-seniors-renting | reader_guide | q-housing-0051 | 8 | 0 | 1 | yes | skeptic (rework) |  |
| off-campus-housing-cornell-sophomores | reader_guide | q-housing-0050 | 1 | 0 | 0 | yes | skeptic (rework) |  |
| roommate-disputes-joint-lease-ithaca | idea-run |  | 4 | 0 | 0 | yes | skeptic (rework) |  |
| short-stay | start_here | q-housing-0079 | 4 | 0 | 1 | yes | skeptic (rework) |  |
| staying-in-ithaca-over-cornell-breaks | spoke | q-getting-around-0041 | 2 | 0 | 0 | yes | skeptic (fix round) | fixed on the second round |
| surviving-ithaca-winter-old-apartment-drafty-house | idea-run |  | 2 | 0 | 1 | yes | skeptic (rework) |  |
| syracuse-airport-to-cornell-ourbus-car-service | spoke | q-getting-around-0030 | 6 | 0 | 0 | yes | hand fix after the fix-round verdict, skeptic-verified (reports/02-hand-verify.json) | fixed by hand on the last objection; a sonnet skeptic re-fetched the sources and judged it sound |
| tcat-free-for-cornell-students-hours-routes | spoke | q-getting-around-0034 | 1 | 0 | 0 | yes | skeptic (rework) |  |
| tcat-winter-snow-routes-delays-cornell | idea-run |  | 3 | 0 | 2 | yes | skeptic (rework) |  |
| the-ivy-collegetown-325-college-ave | idea-run |  | 2 | 0 | 2 | yes | skeptic (rework) |  |
| toni-morrison-hall-cornell | idea-run |  | 1 | 0 | 0 | yes | hand fix after the fix-round verdict, skeptic-verified (reports/02-hand-verify.json) | fixed by hand on the last objection; a sonnet skeptic re-fetched the sources and judged it sound |
| transfer-spring | start_here | q-getting-around-0070 | 7 | 0 | 12 | yes | hand fix after the fix-round verdict, skeptic-verified (reports/02-hand-verify.json) | fixed by hand on the last objection; a sonnet skeptic re-fetched the sources and judged it sound |
| uber-lyft-taxi-ithaca-cornell | spoke | q-getting-around-0045 | 11 | 0 | 3 | yes | skeptic (rework) |  |
| visiting-scholar-postdoc-furnished-housing-ithaca | spoke | q-housing-0046 | 6 | 0 | 3 | yes | skeptic (rework) |  |
| voting-in-ithaca-cornell-student-register-polling-place | idea-run |  | 7 | 0 | 0 | yes | skeptic (rework) |  |
| west-campus-dining-rooms-compared-cornell | idea-run |  | 2 | 0 | 2 | yes | skeptic (rework) |  |
| what-a-month-off-campus-costs-cornell | spoke | q-housing-0092 | 5 | 0 | 0 | yes | skeptic (rework) |  |
| what-to-wear-ithaca-winter-cornell | idea-run |  | 2 | 0 | 3 | yes | skeptic (rework) |  |
| winter-activities-ithaca-cornell-students | idea-run |  | 3 | 0 | 0 | yes | skeptic (rework) |  |
