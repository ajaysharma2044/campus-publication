# Opportunity map (specs/continuous-local-run.md R41, R22)

Generated 2026-11-06T20:13:15+00:00 from database state. Scores are deterministic (D from recorded demand evidence, AGI from observed results, G and E estimates from the authority gap and the source map); priority (SPEC §11) is recorded but not the advance rule for this lane. Sortable CSV: `build/opportunity-map.csv`.

Clusters: 1230 · sweet-spot: 2 · watch: 1161 · reject: 55 · navigational: 11 · undecided: 0 · entities: 178 · auto-created topics: 0 · complete: True

## Top sweet-spot clusters

| # | scope | topic | entity | best query variant | D | AGI | G | E | niche_score | format |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | cornell-university | housing |  | Do Cornell transfer students have to live on campus? | 2 | 5 | 5 | 4 | 80.00 |  |
| 2 | cornell-university | housing |  | Is Cornell's North Campus expansion being used to house transfers? | 2 | 4 | 5 | 4 | 72.00 |  |

## Coverage by topic

| topic | sweet-spot | watch | reject | navigational | undecided |
|---|---|---|---|---|---|
| accessibility | 0 | 0 | 2 | 0 | 0 |
| admissions | 0 | 4 | 0 | 0 | 0 |
| alumni_benefits | 0 | 2 | 2 | 0 | 0 |
| alumni_education | 0 | 2 | 0 | 0 | 0 |
| alumni_events | 0 | 0 | 2 | 2 | 0 |
| alumni_giving | 0 | 0 | 0 | 1 | 0 |
| alumni_records | 0 | 2 | 0 | 1 | 0 |
| alumni_visiting | 0 | 2 | 0 | 0 | 0 |
| careers | 0 | 1 | 2 | 0 | 0 |
| clubs_events | 0 | 1 | 2 | 0 | 0 |
| costs_aid | 0 | 3 | 2 | 0 | 0 |
| courses | 0 | 4 | 0 | 0 | 0 |
| dining | 0 | 227 | 2 | 1 | 0 |
| events_calendar | 0 | 3 | 1 | 0 | 0 |
| health_wellbeing | 0 | 1 | 1 | 1 | 0 |
| housing | 2 | 452 | 10 | 1 | 1 |
| jobs_grad | 0 | 2 | 0 | 0 | 0 |
| jobs_internships | 0 | 1 | 1 | 1 | 0 |
| jobs_outcomes | 0 | 0 | 2 | 0 | 0 |
| jobs_student | 0 | 0 | 2 | 1 | 0 |
| jobs_university | 0 | 1 | 2 | 0 | 0 |
| parents_billing | 0 | 0 | 2 | 1 | 0 |
| parents_calendar | 0 | 3 | 0 | 0 | 0 |
| parents_logistics | 0 | 1 | 2 | 0 | 0 |
| parents_prep | 0 | 2 | 1 | 0 | 0 |
| parents_visitors | 0 | 2 | 0 | 1 | 0 |
| programs | 0 | 4 | 1 | 0 | 0 |
| services | 0 | 124 | 0 | 0 | 0 |
| town_food | 0 | 3 | 0 | 0 | 0 |
| town_government | 0 | 163 | 0 | 0 | 0 |
| town_jobs | 0 | 4 | 1 | 0 | 0 |
| town_neighborhoods | 0 | 1 | 2 | 0 | 0 |
| town_offcampus_housing | 0 | 3 | 1 | 0 | 0 |
| town_outdoors | 0 | 32 | 2 | 0 | 0 |
| town_services | 0 | 1 | 2 | 0 | 0 |
| town_transit_intercity | 0 | 1 | 3 | 0 | 0 |
| town_transit_local | 0 | 103 | 0 | 0 | 0 |
| town_weather | 0 | 0 | 2 | 0 | 0 |
| transfer | 0 | 4 | 1 | 0 | 0 |
| transportation | 0 | 2 | 2 | 0 | 0 |

## Every cluster

| scope | topic | entity | best query | D | AGI | G | E | niche | decision | reason |
|---|---|---|---|---|---|---|---|---|---|---|
| cornell-university | housing |  | Do Cornell transfer students have to live on campus? | 2 | 5 | 5 | 4 | 80.00 | sweet_spot | D=2 AGI=5 G=5 E=4; weak/missing result present; niche_score=80 |
| cornell-university | housing |  | Is Cornell's North Campus expansion being used to house transfers? | 2 | 4 | 5 | 4 | 72.00 | sweet_spot | D=2 AGI=4 G=5 E=4; weak/missing result present; niche_score=72 |
| cornell-university | dining |  | Cornell dining hall hours | 2 | 4 | 5 | 4 | 72.00 | navigational | pure navigational query (official navigational result); rejected (R21) |
| cornell-university | housing |  | Is housing guaranteed for transfer students at Cornell? | 2 | 4 | 4 | 4 | 64.00 | done | D=2 AGI=4 G=4 E=4; weak/missing result present; niche_score=64 |
| cornell-university | housing |  | Cornell housing guaranteed | 1 | 4 | 5 | 4 | 36.00 | watch | below threshold on D: D=1 AGI=4 G=5 E=4 |
| cornell-university | housing |  | Cornell housing application deadline site:reddit.com/r/Cornell | 2 | 1 | 2 | 4 | 24.00 | watch | strong dedicated incumbent (AGI=1); head term logged as watch |
| cornell-university | housing |  | Does the guarantee for first-years extend to transfers? | 2 | 1 | 2 | 4 | 24.00 | watch | strong dedicated incumbent (AGI=1); head term logged as watch |
| cornell-university | programs |  | Cornell add a minor | 2 | 1 | 2 | 4 | 24.00 | watch | strong dedicated incumbent (AGI=1); head term logged as watch |
| cornell-university | programs |  | Cornell how to change major | 2 | 1 | 2 | 4 | 24.00 | watch | strong dedicated incumbent (AGI=1); head term logged as watch |
| ithaca-ny | town_jobs |  | Ithaca summer jobs | 2 | 1 | 2 | 4 | 24.00 | watch | strong dedicated incumbent (AGI=1); head term logged as watch |
| ithaca-ny | town_neighborhoods |  | collegetown vs downtown Ithaca | 2 | 1 | 2 | 4 | 24.00 | watch | strong dedicated incumbent (AGI=1); head term logged as watch |
| cornell-university | housing |  | Cornell off-campus housing | 1 | 2 | 3 | 4 | 20.00 | navigational | pure navigational query (official navigational result); rejected (R21) |
| cornell-university | alumni_visiting |  | Cornell alumni housing reunion | 1 | 2 | 2 | 4 | 16.00 | watch | below threshold on D, AGI, G: D=1 AGI=2 G=2 E=4 |
| ithaca-ny | town_transit_local |  | Ithaca bus pass students | 1 | 1 | 2 | 4 | 12.00 | watch | strong dedicated incumbent (AGI=1); head term logged as watch |
| cornell-university | housing |  | Can a transfer student cancel Cornell housing and live off campus? | 2 | 0 | 1 | 4 | 8.00 | watch | strong dedicated incumbent (AGI=0); head term logged as watch |
| ithaca-ny | town_government |  | Ithaca trash recycling schedule | 1 | 0 | 1 | 4 | 4.00 | watch | strong dedicated incumbent (AGI=0); head term logged as watch |
| cornell-university | alumni_events |  | Cornell alumni directory mentoring | 0 | 4 | 5 | 4 | 0.00 | navigational | pure navigational query (official navigational result); rejected (R21) |
| cornell-university | alumni_events |  | Cornell homecoming 2026 | 0 | 2 | 3 | 4 | 0.00 | navigational | pure navigational query (official navigational result); rejected (R21) |
| cornell-university | alumni_giving |  | Cornell how to give annual fund | 0 | 0 | 1 | 4 | 0.00 | navigational | pure navigational query (official navigational result); rejected (R21) |
| cornell-university | alumni_records |  | Cornell degree verification | 1 | 0 | 0 | 4 | 0.00 | navigational | pure navigational query (official navigational result); rejected (R21) |
| cornell-university | health_wellbeing |  | Cornell health services hours | 0 | 0 | 1 | 4 | 0.00 | navigational | pure navigational query (official navigational result); rejected (R21) |
| cornell-university | jobs_internships |  | Cornell career center appointment | 0 | 1 | 2 | 4 | 0.00 | navigational | pure navigational query (official navigational result); rejected (R21) |
| cornell-university | jobs_student |  | Cornell student jobs | 0 | 1 | 2 | 4 | 0.00 | navigational | pure navigational query (official navigational result); rejected (R21) |
| cornell-university | parents_billing |  | Cornell pay bill parent portal | 0 | 1 | 2 | 4 | 0.00 | navigational | pure navigational query (official navigational result); rejected (R21) |
| cornell-university | parents_visitors |  | Cornell campus tour booking | 0 | 1 | 2 | 4 | 0.00 | navigational | pure navigational query (official navigational result); rejected (R21) |
| cornell-university | accessibility |  | Cornell accessible housing | 0 | 5 | 5 | 4 | 0.00 | reject | below threshold on D: D=0 AGI=5 G=5 E=4 |
| cornell-university | accessibility |  | Cornell disability accommodations how to request | 0 | 5 | 5 | 4 | 0.00 | reject | below threshold on D: D=0 AGI=5 G=5 E=4 |
| cornell-university | alumni_benefits |  | Cornell alumni discounts | 0 | 4 | 5 | 4 | 0.00 | reject | below threshold on D: D=0 AGI=4 G=5 E=4 |
| cornell-university | alumni_benefits |  | Cornell alumni email | 0 | 5 | 5 | 4 | 0.00 | reject | below threshold on D: D=0 AGI=5 G=5 E=4 |
| cornell-university | alumni_events |  | Cornell alumni club near me | 0 | 5 | 5 | 4 | 0.00 | reject | below threshold on D: D=0 AGI=5 G=5 E=4 |
| cornell-university | alumni_events |  | Cornell reunion 2027 | 0 | 5 | 5 | 4 | 0.00 | reject | below threshold on D: D=0 AGI=5 G=5 E=4 |
| cornell-university | careers |  | Cornell career fair dates | 0 | 5 | 5 | 4 | 0.00 | reject | below threshold on D: D=0 AGI=5 G=5 E=4 |
| cornell-university | careers |  | Cornell internship timeline recruiting | 0 | 5 | 5 | 4 | 0.00 | reject | below threshold on D: D=0 AGI=5 G=5 E=4 |
| cornell-university | clubs_events |  | Cornell gym membership students | 0 | 2 | 3 | 4 | 0.00 | reject | below threshold on D, AGI: D=0 AGI=2 G=3 E=4 |
| cornell-university | clubs_events |  | Cornell how to join a club | 0 | 5 | 5 | 4 | 0.00 | reject | below threshold on D: D=0 AGI=5 G=5 E=4 |
| cornell-university | costs_aid |  | Cornell payment plan | 0 | 5 | 5 | 4 | 0.00 | reject | below threshold on D: D=0 AGI=5 G=5 E=4 |
| cornell-university | costs_aid |  | Cornell tuition 2026-27 | 0 | 5 | 5 | 4 | 0.00 | reject | below threshold on D: D=0 AGI=5 G=5 E=4 |
| cornell-university | dining |  | Cornell grocery near campus | 0 | 4 | 5 | 4 | 0.00 | reject | below threshold on D: D=0 AGI=4 G=5 E=4 |
| cornell-university | dining |  | Cornell meal plan required | 0 | 5 | 5 | 4 | 0.00 | reject | below threshold on D: D=0 AGI=5 G=5 E=4 |
| cornell-university | events_calendar |  | Cornell graduation date 2027 | 0 | 2 | 3 | 4 | 0.00 | reject | below threshold on D, AGI: D=0 AGI=2 G=3 E=4 |
| cornell-university | health_wellbeing |  | Cornell health insurance waiver deadline | 0 | 5 | 5 | 4 | 0.00 | reject | below threshold on D: D=0 AGI=5 G=5 E=4 |
| cornell-university | housing | 1 Forest Park Lane | 1 Forest Park Lane cost | 0 | 5 | 5 | 4 | 0.00 | reject | below threshold on D: D=0 AGI=5 G=5 E=4 |
| cornell-university | housing | 1 Forest Park Lane | 1 Forest Park Lane review | 0 | 5 | 5 | 4 | 0.00 | reject | below threshold on D: D=0 AGI=5 G=5 E=4 |
| cornell-university | housing | 104 Mary Ann Wood Drive | 104 Mary Ann Wood Drive cost | 0 | 5 | 5 | 4 | 0.00 | reject | below threshold on D: D=0 AGI=5 G=5 E=4 |
| cornell-university | housing | Barbara McClintock Hall | Barbara McClintock Hall review Cornell | 0 | 2 | 3 | 4 | 0.00 | reject | below threshold on D, AGI: D=0 AGI=2 G=3 E=4 |
| cornell-university | housing |  | Cornell housing cost per semester | 0 | 2 | 3 | 4 | 0.00 | reject | below threshold on D, AGI: D=0 AGI=2 G=3 E=4 |
| cornell-university | housing | Court-Kay-Bauer Hall | Court-Kay-Bauer Hall review Cornell | 0 | 2 | 3 | 4 | 0.00 | reject | below threshold on D, AGI: D=0 AGI=2 G=3 E=4 |
| cornell-university | housing | Equity & Engagement Community (EEC) | Equity & Engagement Community review Cornell | 0 | 4 | 4 | 4 | 0.00 | reject | below threshold on D: D=0 AGI=4 G=4 E=4 |
| cornell-university | housing | Equity & Engagement Community | Equity & Engagement Community review Cornell | 0 | 4 | 4 | 4 | 0.00 | reject | below threshold on D: D=0 AGI=4 G=4 E=4 |
| cornell-university | housing | Hu Shih Hall | Hu Shih Hall review Cornell | 0 | 2 | 3 | 4 | 0.00 | reject | below threshold on D, AGI: D=0 AGI=2 G=3 E=4 |
| cornell-university | housing | Jameson Hall | Jameson Hall review Cornell | 0 | 2 | 2 | 4 | 0.00 | reject | below threshold on D, AGI, G: D=0 AGI=2 G=2 E=4 |
| cornell-university | jobs_internships |  | Cornell co-op program | 0 | 5 | 5 | 4 | 0.00 | reject | below threshold on D: D=0 AGI=5 G=5 E=4 |
| cornell-university | jobs_outcomes |  | Cornell first destination report | 0 | 5 | 5 | 4 | 0.00 | reject | below threshold on D: D=0 AGI=5 G=5 E=4 |
| cornell-university | jobs_outcomes |  | Cornell graduate earnings by major | 0 | 5 | 5 | 4 | 0.00 | reject | below threshold on D: D=0 AGI=5 G=5 E=4 |
| cornell-university | jobs_student |  | Cornell student job pay rate | 0 | 5 | 5 | 4 | 0.00 | reject | below threshold on D: D=0 AGI=5 G=5 E=4 |
| cornell-university | jobs_student |  | Cornell work-study jobs how to apply | 0 | 5 | 5 | 4 | 0.00 | reject | below threshold on D: D=0 AGI=5 G=5 E=4 |
| cornell-university | jobs_university |  | Cornell how to apply for a job | 0 | 5 | 5 | 4 | 0.00 | reject | below threshold on D: D=0 AGI=5 G=5 E=4 |
| cornell-university | jobs_university |  | jobs at Cornell | 0 | 5 | 5 | 4 | 0.00 | reject | below threshold on D: D=0 AGI=5 G=5 E=4 |
| cornell-university | parents_billing |  | Cornell ferpa parent access | 0 | 5 | 5 | 4 | 0.00 | reject | below threshold on D: D=0 AGI=5 G=5 E=4 |
| cornell-university | parents_billing |  | Cornell payment plan | 0 | 5 | 5 | 4 | 0.00 | reject | below threshold on D: D=0 AGI=5 G=5 E=4 |
| cornell-university | parents_logistics |  | Cornell send package to student | 0 | 5 | 5 | 4 | 0.00 | reject | below threshold on D: D=0 AGI=5 G=5 E=4 |
| cornell-university | parents_logistics |  | visiting Cornell hotels parking | 0 | 5 | 5 | 4 | 0.00 | reject | below threshold on D: D=0 AGI=5 G=5 E=4 |
| cornell-university | parents_prep |  | Cornell key dates first year | 0 | 5 | 5 | 4 | 0.00 | reject | below threshold on D: D=0 AGI=5 G=5 E=4 |
| cornell-university | programs |  | Cornell advising appointment | 0 | 5 | 5 | 4 | 0.00 | reject | below threshold on D: D=0 AGI=5 G=5 E=4 |
| ithaca-ny | town_jobs |  | Ithaca jobs for students | 0 | 5 | 5 | 4 | 0.00 | reject | below threshold on D: D=0 AGI=5 G=5 E=4 |
| ithaca-ny | town_neighborhoods |  | Ithaca neighborhoods for students | 0 | 5 | 5 | 4 | 0.00 | reject | below threshold on D: D=0 AGI=5 G=5 E=4 |
| ithaca-ny | town_neighborhoods |  | best neighborhood Ithaca students | 0 | 5 | 5 | 4 | 0.00 | reject | below threshold on D: D=0 AGI=5 G=5 E=4 |
| ithaca-ny | town_offcampus_housing |  | Ithaca tenant rights | 0 | 5 | 5 | 4 | 0.00 | reject | below threshold on D: D=0 AGI=5 G=5 E=4 |
| ithaca-ny | town_outdoors |  | Ithaca hiking trails | 0 | 5 | 5 | 4 | 0.00 | reject | below threshold on D: D=0 AGI=5 G=5 E=4 |
| ithaca-ny | town_outdoors |  | Ithaca state parks | 0 | 5 | 5 | 4 | 0.00 | reject | below threshold on D: D=0 AGI=5 G=5 E=4 |
| ithaca-ny | town_services |  | Ithaca bank near campus | 0 | 2 | 3 | 4 | 0.00 | reject | below threshold on D, AGI: D=0 AGI=2 G=3 E=4 |
| ithaca-ny | town_services |  | Ithaca phone store | 0 | 5 | 5 | 4 | 0.00 | reject | below threshold on D: D=0 AGI=5 G=5 E=4 |
| ithaca-ny | town_transit_intercity |  | Ithaca to new york city bus | 0 | 2 | 2 | 4 | 0.00 | reject | below threshold on D, AGI, G: D=0 AGI=2 G=2 E=4 |
| ithaca-ny | town_transit_intercity |  | bus from Ithaca to nyc | 0 | 5 | 5 | 4 | 0.00 | reject | below threshold on D: D=0 AGI=5 G=5 E=4 |
| ithaca-ny | town_transit_intercity |  | car rental Ithaca | 0 | 2 | 3 | 4 | 0.00 | reject | below threshold on D, AGI: D=0 AGI=2 G=3 E=4 |
| ithaca-ny | town_weather |  | Ithaca snow how bad | 0 | 5 | 5 | 4 | 0.00 | reject | below threshold on D: D=0 AGI=5 G=5 E=4 |
| ithaca-ny | town_weather |  | Ithaca weather winter what to pack | 0 | 5 | 5 | 4 | 0.00 | reject | below threshold on D: D=0 AGI=5 G=5 E=4 |
| cornell-university | transfer |  | Cornell transfer requirements gpa | 0 | 5 | 5 | 4 | 0.00 | reject | below threshold on D: D=0 AGI=5 G=5 E=4 |
| cornell-university | transportation |  | Cornell parking permit cost | 0 | 5 | 5 | 4 | 0.00 | reject | below threshold on D: D=0 AGI=5 G=5 E=4 |
| cornell-university | transportation |  | Cornell winter campus travel | 0 | 4 | 5 | 4 | 0.00 | reject | below threshold on D: D=0 AGI=4 G=5 E=4 |
| cornell-university | admissions |  | Cornell acceptance rate | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | admissions |  | Cornell admissions requirements | 2 | 0 | 0 | 4 | 0.00 | watch | strong dedicated incumbent (AGI=0); head term logged as watch |
| cornell-university | admissions |  | Cornell early decision deadline | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | alumni_benefits |  | Cornell alumni career services | 0 | 0 | 1 | 4 | 0.00 | watch | strong dedicated incumbent (AGI=0); head term logged as watch |
| cornell-university | alumni_benefits |  | Cornell alumni library access | 0 | 1 | 2 | 4 | 0.00 | watch | strong dedicated incumbent (AGI=1); head term logged as watch |
| cornell-university | alumni_education |  | Cornell alumni audit courses | 0 | 1 | 2 | 4 | 0.00 | watch | strong dedicated incumbent (AGI=1); head term logged as watch |
| cornell-university | alumni_records |  | Cornell diploma replacement | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | alumni_visiting |  | Cornell alumni visiting campus parking | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | careers |  | Cornell first destination outcomes report | 0 | 1 | 2 | 4 | 0.00 | watch | strong dedicated incumbent (AGI=1); head term logged as watch |
| cornell-university | clubs_events |  | Cornell greek life rush dates | 0 | 1 | 2 | 4 | 0.00 | watch | strong dedicated incumbent (AGI=1); head term logged as watch |
| cornell-university | costs_aid |  | Cornell financial aid deadline | 0 | 1 | 2 | 4 | 0.00 | watch | strong dedicated incumbent (AGI=1); head term logged as watch |
| cornell-university | costs_aid |  | Cornell work-study how to apply | 0 | 0 | 1 | 4 | 0.00 | watch | strong dedicated incumbent (AGI=0); head term logged as watch |
| cornell-university | courses |  | Cornell add drop deadline | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | courses |  | Cornell course enrollment dates | 0 | 1 | 2 | 4 | 0.00 | watch | strong dedicated incumbent (AGI=1); head term logged as watch |
| cornell-university | courses |  | Cornell prerequisites override | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | dining | 104West | 104West cost | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | dining | 104West | 104West for parents | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | dining | 104West | 104West for transfer students | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | dining | 104West | 104West hours | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | dining | 104West | 104West parking | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | dining | 104West | 104West review | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | dining | 104West | 104West vs Becker House Dining Room | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | dining | Amit Bhatia Libe Café | Amit Bhatia Libe Café for parents | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | dining | Amit Bhatia Libe Café | Amit Bhatia Libe Café vs Atrium Café | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | dining | Atrium Café | Atrium Café cost | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | dining | Atrium Café | Atrium Café for parents | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | dining | Atrium Café | Atrium Café for transfer students | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | dining | Atrium Café | Atrium Café review | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | dining | Atrium Café | Atrium Café vs Big Red Barn | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | dining | Bear Necessities | Bear Necessities for parents | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | dining | Bear Necessities | Bear Necessities for transfer students | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | dining | Bear Necessities | Bear Necessities hours | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | dining | Bear Necessities | Bear Necessities vs Crossings Café | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | dining | Becker House Dining Room | Becker House Dining Room cost | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | dining | Becker House Dining Room | Becker House Dining Room for parents | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | dining | Becker House Dining Room | Becker House Dining Room hours | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | dining | Becker House Dining Room | Becker House Dining Room parking | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | dining | Becker House Dining Room | Becker House Dining Room review | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | dining | Becker House Dining Room | Becker House Dining Room vs Cook House Dining Room | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | dining | Big Red Barn | Big Red Barn cost | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | dining | Big Red Barn | Big Red Barn for parents | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | dining | Big Red Barn | Big Red Barn for transfer students | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | dining | Big Red Barn | Big Red Barn hours | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | dining | Big Red Barn | Big Red Barn review | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | dining | Bus Stop Bagels | Bus Stop Bagels cost | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | dining | Bus Stop Bagels | Bus Stop Bagels for parents | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | dining | Bus Stop Bagels | Bus Stop Bagels for transfer students | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | dining | Bus Stop Bagels | Bus Stop Bagels hours | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | dining | Bus Stop Bagels | Bus Stop Bagels parking | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | dining | Bus Stop Bagels | Bus Stop Bagels vs Café Jennie | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | dining | Café Jennie | Café Jennie cost | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | dining | Café Jennie | Café Jennie for parents | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | dining | Café Jennie | Café Jennie for transfer students | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | dining | Café Jennie | Café Jennie review | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | dining | Café Jennie | Café Jennie vs College of Veterinary Medicine Café | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | dining | College of Veterinary Medicine Café | College of Veterinary Medicine Café cost | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | dining | College of Veterinary Medicine Café | College of Veterinary Medicine Café for transfer students | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | dining | College of Veterinary Medicine Café | College of Veterinary Medicine Café hours | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | dining | College of Veterinary Medicine Café | College of Veterinary Medicine Café parking | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | dining | College of Veterinary Medicine Café | College of Veterinary Medicine Café vs Cornell Dairy Bar | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | dining | Cook House Dining Room | Cook House Dining Room for parents | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | dining | Cook House Dining Room | Cook House Dining Room for transfer students | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | dining | Cook House Dining Room | Cook House Dining Room review | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | dining | Cook House Dining Room | Cook House Dining Room vs Jansen’s Dining Room at Hans Bethe House | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | dining | Cornell Dairy Bar | Cornell Dairy Bar for parents | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | dining | Cornell Dairy Bar | Cornell Dairy Bar for transfer students | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | dining | Cornell Dairy Bar | Cornell Dairy Bar hours | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | dining | Cornell Dairy Bar | Cornell Dairy Bar parking | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | dining |  | Cornell meal plan cost | 0 | 0 | 1 | 4 | 0.00 | watch | strong dedicated incumbent (AGI=0); head term logged as watch |
| cornell-university | dining | Crossings Café | Crossings Café cost | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | dining | Crossings Café | Crossings Café for parents | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | dining | Crossings Café | Crossings Café for transfer students | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | dining | Crossings Café | Crossings Café vs McCormick's at Moakley House | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | dining | Goldie's | Goldie's for transfer students | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | dining | Goldie's | Goldie's parking | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | dining | Goldie's | Goldie's vs Green Dragon | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | dining | Green Dragon | Green Dragon cost | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | dining | Green Dragon | Green Dragon for parents | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | dining | Green Dragon | Green Dragon review | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | dining | Green Dragon | Green Dragon vs Mann Café | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | dining | Jansen's Market | Jansen's Market for parents | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | dining | Jansen's Market | Jansen's Market for transfer students | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | dining | Jansen's Market | Jansen's Market parking | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | dining | Jansen’s Dining Room at Hans Bethe House | Jansen’s Dining Room at Hans Bethe House cost | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | dining | Jansen’s Dining Room at Hans Bethe House | Jansen’s Dining Room at Hans Bethe House for parents | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | dining | Jansen’s Dining Room at Hans Bethe House | Jansen’s Dining Room at Hans Bethe House for transfer students | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | dining | Jansen’s Dining Room at Hans Bethe House | Jansen’s Dining Room at Hans Bethe House parking | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | dining | Jansen’s Dining Room at Hans Bethe House | Jansen’s Dining Room at Hans Bethe House review | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | dining | Keeton House Dining Room | Keeton House Dining Room cost | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | dining | Keeton House Dining Room | Keeton House Dining Room for parents | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | dining | Keeton House Dining Room | Keeton House Dining Room for transfer students | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | dining | Keeton House Dining Room | Keeton House Dining Room hours | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | dining | Keeton House Dining Room | Keeton House Dining Room parking | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | dining | Keeton House Dining Room | Keeton House Dining Room vs Rose House Dining Room | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | dining | Mann Café | Mann Café hours | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | dining | Mann Café | Mann Café parking | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | dining | Mann Café | Mann Café review | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | dining | Mann Café | Mann Café vs Martha's Café | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | dining | Martha's Café | Martha's Café cost | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | dining | Martha's Café | Martha's Café for parents | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | dining | Martha's Café | Martha's Café for transfer students | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | dining | Martha's Café | Martha's Café hours | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | dining | Martha's Café | Martha's Café vs Mattin's Café | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | dining | Mattin's Café | Mattin's Café for parents | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | dining | Mattin's Café | Mattin's Café for transfer students | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | dining | Mattin's Café | Mattin's Café parking | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | dining | McCormick's at Moakley House | McCormick's at Moakley House cost | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | dining | McCormick's at Moakley House | McCormick's at Moakley House for parents | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | dining | McCormick's at Moakley House | McCormick's at Moakley House for transfer students | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | dining | McCormick's at Moakley House | McCormick's at Moakley House hours | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | dining | McCormick's at Moakley House | McCormick's at Moakley House parking | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | dining | McCormick's at Moakley House | McCormick's at Moakley House review | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | dining | Morrison Dining | Morrison Dining cost | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | dining | Morrison Dining | Morrison Dining for transfer students | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | dining | Morrison Dining | Morrison Dining hours | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | dining | Morrison Dining | Morrison Dining parking | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | dining | Morrison Dining | Morrison Dining vs North Star Dining Room | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | dining | North Star Dining Room | North Star Dining Room for parents | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | dining | North Star Dining Room | North Star Dining Room hours | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | dining | North Star Dining Room | North Star Dining Room review | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | dining | North Star Dining Room | North Star Dining Room vs Risley Dining | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | dining | Novick's Café | Novick's Café cost | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | dining | Novick's Café | Novick's Café for parents | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | dining | Novick's Café | Novick's Café review | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | dining | Okenshields | Okenshields cost | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | dining | Okenshields | Okenshields for parents | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | dining | Okenshields | Okenshields for transfer students | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | dining | Okenshields | Okenshields parking | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | dining | Risley Dining | Risley Dining cost | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | dining | Risley Dining | Risley Dining for parents | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | dining | Rose House Dining Room | Rose House Dining Room cost | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | dining | Rose House Dining Room | Rose House Dining Room for parents | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | dining | Rose House Dining Room | Rose House Dining Room for transfer students | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | dining | Rose House Dining Room | Rose House Dining Room review | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | dining | Rusty's | Rusty's for parents | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | dining | Rusty's | Rusty's for transfer students | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | dining | Rusty's | Rusty's hours | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | dining | Rusty's | Rusty's parking | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | dining | Trillium | Trillium cost | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | dining | Trillium | Trillium for transfer students | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | dining | Trillium | Trillium parking | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | dining | Trillium | Trillium review | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | dining | 104West | how to get to 104West | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | dining | Amit Bhatia Libe Café | how to get to Amit Bhatia Libe Café | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | dining | Atrium Café | how to get to Atrium Café | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | dining | Bear Necessities | how to get to Bear Necessities | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | dining | Bus Stop Bagels | how to get to Bus Stop Bagels | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | dining | Café Jennie | how to get to Café Jennie | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | dining | College of Veterinary Medicine Café | how to get to College of Veterinary Medicine Café | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | dining | Cook House Dining Room | how to get to Cook House Dining Room | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | dining | Cornell Dairy Bar | how to get to Cornell Dairy Bar | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | dining | Crossings Café | how to get to Crossings Café | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | dining | Goldie's | how to get to Goldie's | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | dining | Jansen's Market | how to get to Jansen's Market | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | dining | Jansen’s Dining Room at Hans Bethe House | how to get to Jansen’s Dining Room at Hans Bethe House | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | dining | Keeton House Dining Room | how to get to Keeton House Dining Room | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | dining | Mann Café | how to get to Mann Café | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | dining | Martha's Café | how to get to Martha's Café | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | dining | Mattin's Café | how to get to Mattin's Café | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | dining | Morrison Dining | how to get to Morrison Dining | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | dining | North Star Dining Room | how to get to North Star Dining Room | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | dining | Novick's Café | how to get to Novick's Café | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | dining | Risley Dining | how to get to Risley Dining | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | dining | Rose House Dining Room | how to get to Rose House Dining Room | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | dining | Trillium | how to get to Trillium | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | health_wellbeing |  | Cornell counseling appointment how to | 0 | 0 | 1 | 4 | 0.00 | watch | strong dedicated incumbent (AGI=0); head term logged as watch |
| cornell-university | housing | 1 Forest Park Lane | 1 Forest Park Lane for grad students | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | 1 Forest Park Lane | 1 Forest Park Lane for international students | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | 1 Forest Park Lane | 1 Forest Park Lane for transfer students | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | 1 Forest Park Lane | 1 Forest Park Lane room size | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | 104 Mary Ann Wood Drive | 104 Mary Ann Wood Drive for grad students | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | 104 Mary Ann Wood Drive | 104 Mary Ann Wood Drive for international students | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | 104 Mary Ann Wood Drive | 104 Mary Ann Wood Drive for parents | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | 104 Mary Ann Wood Drive | 104 Mary Ann Wood Drive review | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | 104 Mary Ann Wood Drive | 104 Mary Ann Wood Drive room size | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | 112 Edgemoor | 112 Edgemoor cost | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | 112 Edgemoor | 112 Edgemoor for grad students | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | 112 Edgemoor | 112 Edgemoor for parents | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | 112 Edgemoor | 112 Edgemoor for transfer students | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | 112 Edgemoor | 112 Edgemoor parking | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | 112 Edgemoor | 112 Edgemoor review | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | 112 Edgemoor | 112 Edgemoor room size | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | 301 College Avenue | 301 College Avenue for grad students | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | 301 College Avenue | 301 College Avenue for parents | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | 301 College Avenue | 301 College Avenue for transfer students | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | 301 College Avenue | 301 College Avenue review | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | 301 College Avenue | 301 College Avenue room size | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Akwe:kon | Akwe:kon for grad students | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Akwe:kon | Akwe:kon parking | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Akwe:kon | Akwe:kon review Cornell | 0 | 1 | 2 | 4 | 0.00 | watch | strong dedicated incumbent (AGI=1); head term logged as watch |
| cornell-university | housing | Akwe:kon | Akwe:kon room size | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Alice Cook House | Alice Cook House for parents | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Alice Cook House | Alice Cook House for transfer students | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Alice Cook House | Alice Cook House parking | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Alice Cook House | Alice Cook House review Cornell | 0 | 1 | 2 | 4 | 0.00 | watch | strong dedicated incumbent (AGI=1); head term logged as watch |
| cornell-university | housing | Alice Cook House | Alice Cook House room size | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Alice Cook House | Alice Cook House vs Carl Becker House | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Balch Hall | Balch Hall cost | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Balch Hall | Balch Hall for parents | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Balch Hall | Balch Hall for transfer students | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Balch Hall | Balch Hall parking | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Balch Hall | Balch Hall review Cornell | 0 | 1 | 2 | 4 | 0.00 | watch | strong dedicated incumbent (AGI=1); head term logged as watch |
| cornell-university | housing | Barbara McClintock Hall | Barbara McClintock Hall cost | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Barbara McClintock Hall | Barbara McClintock Hall for grad students | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Barbara McClintock Hall | Barbara McClintock Hall for international students | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Barbara McClintock Hall | Barbara McClintock Hall for transfer students | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing |  | Can transfer students live on North Campus at Cornell? | 1 | 0 | 0 | 4 | 0.00 | watch | single observed occurrence; waits for a second independent occurrence before search observation |
| cornell-university | housing | Carl Becker House | Carl Becker House for grad students | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Carl Becker House | Carl Becker House for international students | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Carl Becker House | Carl Becker House for transfer students | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Carl Becker House | Carl Becker House review Cornell | 0 | 1 | 2 | 4 | 0.00 | watch | strong dedicated incumbent (AGI=1); head term logged as watch |
| cornell-university | housing | Carl Becker House | Carl Becker House vs Flora Rose House | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Cascadilla Hall | Cascadilla Hall cost | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Cascadilla Hall | Cascadilla Hall for international students | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Cascadilla Hall | Cascadilla Hall for parents | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Cascadilla Hall | Cascadilla Hall parking | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Cascadilla Hall | Cascadilla Hall review Cornell | 0 | 1 | 2 | 4 | 0.00 | watch | strong dedicated incumbent (AGI=1); head term logged as watch |
| cornell-university | housing | Cascadilla Hall | Cascadilla Hall room size | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Clara Dickson Hall | Clara Dickson Hall cost | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Clara Dickson Hall | Clara Dickson Hall for international students | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Clara Dickson Hall | Clara Dickson Hall for parents | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Clara Dickson Hall | Clara Dickson Hall for transfer students | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Clara Dickson Hall | Clara Dickson Hall parking | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Clara Dickson Hall | Clara Dickson Hall review Cornell | 0 | 1 | 2 | 4 | 0.00 | watch | strong dedicated incumbent (AGI=1); head term logged as watch |
| cornell-university | housing | Court-Kay-Bauer Hall | Court-Kay-Bauer Hall cost | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Court-Kay-Bauer Hall | Court-Kay-Bauer Hall for grad students | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Court-Kay-Bauer Hall | Court-Kay-Bauer Hall for international students | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Court-Kay-Bauer Hall | Court-Kay-Bauer Hall for parents | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Court-Kay-Bauer Hall | Court-Kay-Bauer Hall for transfer students | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Court-Kay-Bauer Hall | Court-Kay-Bauer Hall parking | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing |  | Did Cornell restore guaranteed housing for transfer students after Fall 2016? | 1 | 0 | 0 | 4 | 0.00 | watch | single observed occurrence; waits for a second independent occurrence before search observation |
| cornell-university | housing |  | Do I have to buy a meal plan as a transfer at Cornell? | 1 | 0 | 0 | 4 | 0.00 | watch | single observed occurrence; waits for a second independent occurrence before search observation |
| cornell-university | housing |  | Does Cornell guarantee housing for transfer students? | 1 | 0 | 0 | 4 | 0.00 | watch | single observed occurrence; waits for a second independent occurrence before search observation |
| cornell-university | housing | Ecology House | Ecology House cost | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Ecology House | Ecology House for grad students | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Ecology House | Ecology House for international students | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Ecology House | Ecology House parking | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Ecology House | Ecology House review Cornell | 0 | 1 | 2 | 4 | 0.00 | watch | strong dedicated incumbent (AGI=1); head term logged as watch |
| cornell-university | housing | Ecology House | Ecology House room size | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Ecology House | Ecology House vs Equity & Engagement Community | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Equity & Engagement Community (EEC) | Equity & Engagement Community (EEC) cost | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Equity & Engagement Community (EEC) | Equity & Engagement Community (EEC) for grad students | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Equity & Engagement Community (EEC) | Equity & Engagement Community (EEC) for international students | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Equity & Engagement Community (EEC) | Equity & Engagement Community (EEC) for parents | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Equity & Engagement Community (EEC) | Equity & Engagement Community (EEC) parking | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Equity & Engagement Community (EEC) | Equity & Engagement Community (EEC) room size | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Equity & Engagement Community (EEC) | Equity & Engagement Community (EEC) vs Holland International Living Center (HILC | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Equity & Engagement Community | Equity & Engagement Community cost | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Equity & Engagement Community | Equity & Engagement Community for international students | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Equity & Engagement Community | Equity & Engagement Community for transfer students | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Equity & Engagement Community | Equity & Engagement Community parking | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Equity & Engagement Community | Equity & Engagement Community vs Equity & Engagement Community (EEC) | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Flora Rose House | Flora Rose House cost | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Flora Rose House | Flora Rose House for parents | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Flora Rose House | Flora Rose House for transfer students | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Flora Rose House | Flora Rose House parking | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Flora Rose House | Flora Rose House review Cornell | 0 | 1 | 2 | 4 | 0.00 | watch | strong dedicated incumbent (AGI=1); head term logged as watch |
| cornell-university | housing | Hans Bethe House | Hans Bethe House cost | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Hans Bethe House | Hans Bethe House for grad students | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Hans Bethe House | Hans Bethe House for international students | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Hans Bethe House | Hans Bethe House for parents | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Hans Bethe House | Hans Bethe House for transfer students | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Hans Bethe House | Hans Bethe House review Cornell | 0 | 1 | 2 | 4 | 0.00 | watch | strong dedicated incumbent (AGI=1); head term logged as watch |
| cornell-university | housing | Hans Bethe House | Hans Bethe House room size | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | High Rise #5 | High Rise #5 cost | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | High Rise #5 | High Rise #5 for grad students | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | High Rise #5 | High Rise #5 for international students | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | High Rise #5 | High Rise #5 for parents | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | High Rise #5 | High Rise #5 for transfer students | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | High Rise #5 | High Rise #5 review Cornell | 0 | 1 | 2 | 4 | 0.00 | watch | strong dedicated incumbent (AGI=1); head term logged as watch |
| cornell-university | housing | High Rise #5 | High Rise #5 room size | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Holland International Living Center (HILC) | Holland International Living Center (HILC) cost | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Holland International Living Center (HILC) | Holland International Living Center (HILC) for grad students | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Holland International Living Center (HILC) | Holland International Living Center (HILC) for international students | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Holland International Living Center (HILC) | Holland International Living Center HILC review Cornell | 0 | 1 | 2 | 4 | 0.00 | watch | strong dedicated incumbent (AGI=1); head term logged as watch |
| cornell-university | housing | Holland International Living Center (HILC) | Holland International Living Center (HILC) room size | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Holland International Living Center (HILC) | Holland International Living Center (HILC) vs Just About Music (JAM) | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing |  | How do I apply for housing as a Cornell transfer student, and what is the deadli | 1 | 0 | 0 | 4 | 0.00 | watch | single observed occurrence; waits for a second independent occurrence before search observation |
| cornell-university | housing |  | How many transfer students get on-campus housing each year? | 1 | 0 | 0 | 4 | 0.00 | watch | single observed occurrence; waits for a second independent occurrence before search observation |
| cornell-university | housing | Hu Shih Hall | Hu Shih Hall cost | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Hu Shih Hall | Hu Shih Hall for grad students | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Hu Shih Hall | Hu Shih Hall parking | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Hu Shih Hall | Hu Shih Hall room size | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing |  | Is Schuyler House for transfer students? | 1 | 0 | 0 | 4 | 0.00 | watch | single observed occurrence; waits for a second independent occurrence before search observation |
| cornell-university | housing |  | Is housing guaranteed for first-year students at Cornell? | 1 | 0 | 0 | 4 | 0.00 | watch | single observed occurrence; waits for a second independent occurrence before search observation |
| cornell-university | housing | Jameson Hall | Jameson Hall for transfer students | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Jameson Hall | Jameson Hall parking | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Just About Music (JAM) | Just About Music (JAM) cost | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Just About Music (JAM) | Just About Music (JAM) for grad students | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Just About Music (JAM) | Just About Music (JAM) for transfer students | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Just About Music (JAM) | Just About Music (JAM) parking | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Just About Music (JAM) | Just About Music (JAM) review | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Just About Music (JAM) | Just About Music (JAM) room size | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Just About Music (JAM) | Just About Music (JAM) vs Language House | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Language House | Language House cost | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Language House | Language House for grad students | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Language House | Language House for international students | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Language House | Language House for parents | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Language House | Language House for transfer students | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Latino Living Center (LLC) | Latino Living Center (LLC) cost | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Latino Living Center (LLC) | Latino Living Center (LLC) for international students | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Latino Living Center (LLC) | Latino Living Center (LLC) parking | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Latino Living Center (LLC) | Latino Living Center (LLC) review | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Latino Living Center (LLC) | Latino Living Center (LLC) room size | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Latino Living Center (LLC) | Latino Living Center (LLC) vs Loving House | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Loving House | Loving House cost | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Loving House | Loving House for international students | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Loving House | Loving House for parents | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Loving House | Loving House for transfer students | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Loving House | Loving House parking | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Loving House | Loving House review | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Loving House | Loving House room size | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Low Rise #6 | Low Rise #6 cost | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Low Rise #6 | Low Rise #6 for international students | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Low Rise #6 | Low Rise #6 for parents | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Low Rise #6 | Low Rise #6 for transfer students | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Low Rise #6 | Low Rise #6 parking | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Low Rise #6 | Low Rise #6 review | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Low Rise #6 | Low Rise #6 room size | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Low Rise #7 | Low Rise #7 cost | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Low Rise #7 | Low Rise #7 for grad students | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Low Rise #7 | Low Rise #7 for international students | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Low Rise #7 | Low Rise #7 for parents | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Low Rise #7 | Low Rise #7 for transfer students | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Low Rise #7 | Low Rise #7 parking | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Low Rise #7 | Low Rise #7 review | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Mary Donlon Hall | Mary Donlon Hall for grad students | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Mary Donlon Hall | Mary Donlon Hall for transfer students | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Mary Donlon Hall | Mary Donlon Hall review | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Mary Donlon Hall | Mary Donlon Hall room size | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Mews Hall | Mews Hall cost | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Mews Hall | Mews Hall for international students | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Mews Hall | Mews Hall for parents | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Mews Hall | Mews Hall for transfer students | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Mews Hall | Mews Hall parking | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Mews Hall | Mews Hall room size | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Multicultural Living Learning Unit (McLLU) | Multicultural Living Learning Unit (McLLU) for international students | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Multicultural Living Learning Unit (McLLU) | Multicultural Living Learning Unit (McLLU) for parents | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Multicultural Living Learning Unit (McLLU) | Multicultural Living Learning Unit (McLLU) for transfer students | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Multicultural Living Learning Unit (McLLU) | Multicultural Living Learning Unit (McLLU) review | 0 | 1 | 2 | 4 | 0.00 | watch | strong dedicated incumbent (AGI=1); head term logged as watch |
| cornell-university | housing | Program House Mission and Expectations | Program House Mission and Expectations for grad students | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Program House Mission and Expectations | Program House Mission and Expectations for international students | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Program House Mission and Expectations | Program House Mission and Expectations for parents | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Program House Mission and Expectations | Program House Mission and Expectations review | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Program House Mission and Expectations | Program House Mission and Expectations vs Risley Residential College | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Risley Residential College | Risley Residential College cost | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Risley Residential College | Risley Residential College for grad students | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Risley Residential College | Risley Residential College for international students | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Risley Residential College | Risley Residential College for parents | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Risley Residential College | Risley Residential College for transfer students | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Risley Residential College | Risley Residential College parking | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Risley Residential College | Risley Residential College review | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Risley Residential College | Risley Residential College vs Sober Living Community | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Ruth Bader Ginsburg Hall | Ruth Bader Ginsburg Hall cost | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Ruth Bader Ginsburg Hall | Ruth Bader Ginsburg Hall for international students | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Ruth Bader Ginsburg Hall | Ruth Bader Ginsburg Hall for parents | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Ruth Bader Ginsburg Hall | Ruth Bader Ginsburg Hall parking | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Ruth Bader Ginsburg Hall | Ruth Bader Ginsburg Hall review | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Schuyler House | Schuyler House cost | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Schuyler House | Schuyler House for grad students | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Schuyler House | Schuyler House for international students | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Schuyler House | Schuyler House for parents | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Schuyler House | Schuyler House for transfer students | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Schuyler House | Schuyler House parking | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Schuyler House | Schuyler House review | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Schuyler House | Schuyler House room size | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Sheldon Court | Sheldon Court cost | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Sheldon Court | Sheldon Court for grad students | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Sheldon Court | Sheldon Court for international students | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Sheldon Court | Sheldon Court for parents | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Sheldon Court | Sheldon Court for transfer students | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Sheldon Court | Sheldon Court parking | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Sheldon Court | Sheldon Court review | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Sober Living Community | Sober Living Community cost | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Sober Living Community | Sober Living Community for international students | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Sober Living Community | Sober Living Community for transfer students | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Sober Living Community | Sober Living Community parking | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Sober Living Community | Sober Living Community review | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Sober Living Community | Sober Living Community room size | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Sober Living Community | Sober Living Community vs Ujamaa Residential College | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Toni Morrison Hall | Toni Morrison Hall cost | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Toni Morrison Hall | Toni Morrison Hall for international students | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Toni Morrison Hall | Toni Morrison Hall for parents | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Toni Morrison Hall | Toni Morrison Hall for transfer students | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Toni Morrison Hall | Toni Morrison Hall parking | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Toni Morrison Hall | Toni Morrison Hall review | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Toni Morrison Hall | Toni Morrison Hall room size | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Townhouse Apartments | Townhouse Apartments cost | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Townhouse Apartments | Townhouse Apartments for grad students | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Townhouse Apartments | Townhouse Apartments for international students | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Townhouse Apartments | Townhouse Apartments for transfer students | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Townhouse Apartments | Townhouse Apartments parking | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Townhouse Apartments | Townhouse Apartments review | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Townhouse Apartments | Townhouse Apartments room size | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Ujamaa Residential College | Ujamaa Residential College cost | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Ujamaa Residential College | Ujamaa Residential College for international students | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Ujamaa Residential College | Ujamaa Residential College for parents | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Ujamaa Residential College | Ujamaa Residential College for transfer students | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Ujamaa Residential College | Ujamaa Residential College parking | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Ujamaa Residential College | Ujamaa Residential College review | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Ujamaa Residential College | Ujamaa Residential College room size | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Ujamaa Residential College | Ujamaa Residential College vs Veterans House | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Veterans House | Veterans House cost | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Veterans House | Veterans House for grad students | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Veterans House | Veterans House for parents | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Veterans House | Veterans House parking | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Veterans House | Veterans House review | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing |  | What are the housing options for transfers at Cornell? | 1 | 0 | 0 | 4 | 0.00 | watch | single observed occurrence; waits for a second independent occurrence before search observation |
| cornell-university | housing |  | What are the off-campus housing options for Cornell transfer students? | 1 | 0 | 0 | 4 | 0.00 | watch | single observed occurrence; waits for a second independent occurrence before search observation |
| cornell-university | housing |  | What is Cornell's two-year residency requirement, and does it apply to transfers | 1 | 0 | 0 | 4 | 0.00 | watch | single observed occurrence; waits for a second independent occurrence before search observation |
| cornell-university | housing |  | What is the transfer housing application deadline? | 1 | 0 | 0 | 4 | 0.00 | watch | single observed occurrence; waits for a second independent occurrence before search observation |
| cornell-university | housing |  | When is the Cornell housing application due for transfers? | 1 | 0 | 0 | 4 | 0.00 | watch | single observed occurrence; waits for a second independent occurrence before search observation |
| cornell-university | housing |  | When will transfer students find out about housing at Cornell? | 1 | 0 | 0 | 4 | 0.00 | watch | single observed occurrence; waits for a second independent occurrence before search observation |
| cornell-university | housing |  | Where are transfer students placed (which residence halls)? | 1 | 0 | 0 | 4 | 0.00 | watch | single observed occurrence; waits for a second independent occurrence before search observation |
| cornell-university | housing |  | Where do Cornell transfer students live, West or North Campus? | 1 | 0 | 0 | 4 | 0.00 | watch | single observed occurrence; waits for a second independent occurrence before search observation |
| cornell-university | housing |  | Where do Cornell transfer students live? | 1 | 0 | 0 | 4 | 0.00 | watch | single observed occurrence; waits for a second independent occurrence before search observation |
| cornell-university | housing |  | Why were Cornell transfers put in converted lounges? | 1 | 0 | 0 | 4 | 0.00 | watch | single observed occurrence; waits for a second independent occurrence before search observation |
| cornell-university | housing | William Keeton House | William Keeton House cost | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | William Keeton House | William Keeton House for grad students | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | William Keeton House | William Keeton House for international students | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | William Keeton House | William Keeton House for parents | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | William Keeton House | William Keeton House for transfer students | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | William Keeton House | William Keeton House parking | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | William Keeton House | William Keeton House review | 0 | 1 | 2 | 4 | 0.00 | watch | strong dedicated incumbent (AGI=1); head term logged as watch |
| cornell-university | housing | William Keeton House | William Keeton House room size | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | 104 Mary Ann Wood Drive | how to get to 104 Mary Ann Wood Drive | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | 301 College Avenue | how to get to 301 College Avenue | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Balch Hall | how to get to Balch Hall | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Barbara McClintock Hall | how to get to Barbara McClintock Hall | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Carl Becker House | how to get to Carl Becker House | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Court-Kay-Bauer Hall | how to get to Court-Kay-Bauer Hall | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Ecology House | how to get to Ecology House | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Equity & Engagement Community | how to get to Equity & Engagement Community | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Equity & Engagement Community (EEC) | how to get to Equity & Engagement Community (EEC) | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Flora Rose House | how to get to Flora Rose House | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Hans Bethe House | how to get to Hans Bethe House | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Hu Shih Hall | how to get to Hu Shih Hall | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Jameson Hall | how to get to Jameson Hall | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Latino Living Center (LLC) | how to get to Latino Living Center (LLC) | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Loving House | how to get to Loving House | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Low Rise #6 | how to get to Low Rise #6 | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Mary Donlon Hall | how to get to Mary Donlon Hall | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Mews Hall | how to get to Mews Hall | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Multicultural Living Learning Unit (McLLU) | how to get to Multicultural Living Learning Unit (McLLU) | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Program House Mission and Expectations | how to get to Program House Mission and Expectations | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Risley Residential College | how to get to Risley Residential College | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Ruth Bader Ginsburg Hall | how to get to Ruth Bader Ginsburg Hall | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Schuyler House | how to get to Schuyler House | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Sheldon Court | how to get to Sheldon Court | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Toni Morrison Hall | how to get to Toni Morrison Hall | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Ujamaa Residential College | how to get to Ujamaa Residential College | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | program house mission | how to get to program house mission | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | 104 Mary Ann Wood Drive | is 104 Mary Ann Wood Drive good for transfers | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | 301 College Avenue | is 301 College Avenue good for transfers | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Alice Cook House | is Alice Cook House good for transfers | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Balch Hall | is Balch Hall good for transfers | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Barbara McClintock Hall | is Barbara McClintock Hall good for transfers | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Carl Becker House | is Carl Becker House good for transfers | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Cascadilla Hall | is Cascadilla Hall good for transfers | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Court-Kay-Bauer Hall | is Court-Kay-Bauer Hall good for transfers | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Equity & Engagement Community (EEC) | is Equity & Engagement Community (EEC) good for transfers | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Flora Rose House | is Flora Rose House good for transfers | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Hans Bethe House | is Hans Bethe House good for transfers | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | High Rise #5 | is High Rise #5 good for transfers | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Jameson Hall | is Jameson Hall good for transfers | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Just About Music (JAM) | is Just About Music (JAM) good for transfers | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Latino Living Center (LLC) | is Latino Living Center (LLC) good for transfers | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Loving House | is Loving House good for transfers | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Low Rise #6 | is Low Rise #6 good for transfers | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Low Rise #7 | is Low Rise #7 good for transfers | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Mews Hall | is Mews Hall good for transfers | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Multicultural Living Learning Unit (McLLU) | is Multicultural Living Learning Unit (McLLU) good for transfers | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Program House Mission and Expectations | is Program House Mission and Expectations good for transfers | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Risley Residential College | is Risley Residential College good for transfers | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Ruth Bader Ginsburg Hall | is Ruth Bader Ginsburg Hall good for transfers | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Schuyler House | is Schuyler House good for transfers | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Sheldon Court | is Sheldon Court good for transfers | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Sober Living Community | is Sober Living Community good for transfers | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Toni Morrison Hall | is Toni Morrison Hall good for transfers | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Townhouse Apartments | is Townhouse Apartments good for transfers | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Ujamaa Residential College | is Ujamaa Residential College good for transfers | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Veterans House | is Veterans House good for transfers | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | William Keeton House | is William Keeton House good for transfers | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | program house mission | is program house mission good for transfers | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | program house mission | program house mission for parents | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | program house mission | program house mission for transfer students | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | program house mission | program house mission parking | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | program house mission | program house mission review | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | program house mission | program house mission room size | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | jobs_grad |  | Cornell graduate assistantship stipend | 0 | 0 | 1 | 4 | 0.00 | watch | strong dedicated incumbent (AGI=0); head term logged as watch |
| cornell-university | jobs_grad |  | Cornell postdoc positions how to apply | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | jobs_internships |  | Cornell internship recruiting timeline | 0 | 0 | 1 | 4 | 0.00 | watch | strong dedicated incumbent (AGI=0); head term logged as watch |
| cornell-university | jobs_university |  | Cornell staff benefits overview | 0 | 1 | 2 | 4 | 0.00 | watch | strong dedicated incumbent (AGI=1); head term logged as watch |
| cornell-university | parents_calendar |  | Cornell family weekend 2026 | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | parents_calendar |  | Cornell move-in dates parents | 0 | 1 | 2 | 4 | 0.00 | watch | strong dedicated incumbent (AGI=1); head term logged as watch |
| cornell-university | parents_logistics |  | Cornell campus safety resources parents | 0 | 1 | 2 | 4 | 0.00 | watch | strong dedicated incumbent (AGI=1); head term logged as watch |
| cornell-university | parents_prep |  | Cornell health insurance waiver | 0 | 0 | 1 | 4 | 0.00 | watch | strong dedicated incumbent (AGI=0); head term logged as watch |
| cornell-university | parents_prep |  | Cornell what to bring to the dorm | 0 | 0 | 1 | 4 | 0.00 | watch | strong dedicated incumbent (AGI=0); head term logged as watch |
| cornell-university | parents_visitors |  | Cornell visitor parking | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | parents_visitors |  | hotels near Cornell | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | programs |  | Cornell double major rules | 0 | 1 | 2 | 4 | 0.00 | watch | strong dedicated incumbent (AGI=1); head term logged as watch |
| cornell-university | services | Alumni | Alumni for parents | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | services | Alumni | Alumni hours | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | services | Alumni | Alumni parking | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | services | Catherwood Library | Catherwood Library for parents | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | services | Catherwood Library | Catherwood Library for transfer students | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | services | Catherwood Library | Catherwood Library hours | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | services | Catherwood Library | Catherwood Library parking | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | services | Clark Physical Sciences Library | Clark Physical Sciences Library for parents | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | services | Clark Physical Sciences Library | Clark Physical Sciences Library for transfer students | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | services | Clark Physical Sciences Library | Clark Physical Sciences Library hours | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | services | Clark Physical Sciences Library | Clark Physical Sciences Library parking | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | services | Clarke Africana Library | Clarke Africana Library for parents | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | services | Cornell Tech Library Services | Cornell Tech Library Services for parents | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | services | Cornell Tech Library Services | Cornell Tech Library Services hours | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | services | Cornell Tech Library Services | Cornell Tech Library Services parking | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | services |  | Cornell mail and packages | 0 | 0 | 1 | 4 | 0.00 | watch | strong dedicated incumbent (AGI=0); head term logged as watch |
| cornell-university | services |  | Cornell printing on campus | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | services | Cox Library of Music and Dance | Cox Library of Music and Dance for parents | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | services | Cox Library of Music and Dance | Cox Library of Music and Dance for transfer students | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | services | Cox Library of Music and Dance | Cox Library of Music and Dance hours | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | services | Engineering Library | Engineering Library hours | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | services | Flower-Sprecher Veterinary Library | Flower-Sprecher Veterinary Library for parents | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | services | Flower-Sprecher Veterinary Library | Flower-Sprecher Veterinary Library hours | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | services | HELP | HELP for parents | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | services | HELP | HELP for transfer students | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | services | HELP | HELP parking | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | services | Kroch Asia Collections | Kroch Asia Collections for parents | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | services | Kroch Asia Collections | Kroch Asia Collections for transfer students | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | services | Kroch Asia Collections | Kroch Asia Collections hours | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | services | Law Library | Law Library for parents | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | services | Law Library | Law Library hours | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | services | Law Library | Law Library parking | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | services | Library Annex | Library Annex for parents | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | services | Library Annex | Library Annex for transfer students | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | services | Library Annex | Library Annex hours | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | services | MENU | MENU for parents | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | services | Management Library | Management Library for transfer students | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | services | Management Library | Management Library hours | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | services | Management Library | Management Library parking | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | services | Mann Library | Mann Library for parents | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | services | Mann Library | Mann Library for transfer students | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | services | Mann Library | Mann Library hours | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | services | Mann Library | Mann Library parking | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | services | Mathematics Library | Mathematics Library for transfer students | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | services | Mathematics Library | Mathematics Library hours | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | services | Mathematics Library | Mathematics Library parking | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | services | Medical Center Archives | Medical Center Archives for parents | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | services | Medical Center Archives | Medical Center Archives for transfer students | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | services | Medical Center Archives | Medical Center Archives hours | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | services | Medical Center Archives | Medical Center Archives parking | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | services | Mui Ho Fine Arts Library | Mui Ho Fine Arts Library for parents | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | services | Mui Ho Fine Arts Library | Mui Ho Fine Arts Library for transfer students | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | services | Nestlé Library | Nestlé Library for parents | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | services | Nestlé Library | Nestlé Library hours | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | services | Nestlé Library | Nestlé Library parking | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | services | Olin Library | Olin Library for transfer students | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | services | Olin Library | Olin Library hours | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | services | Olin Library | Olin Library parking | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | services | Rare and Manuscript Collections | Rare and Manuscript Collections for parents | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | services | Rare and Manuscript Collections | Rare and Manuscript Collections for transfer students | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | services | Rare and Manuscript Collections | Rare and Manuscript Collections parking | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | services | Uris Library | Uris Library for parents | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | services | Uris Library | Uris Library parking | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | services | Wood Library | Wood Library hours | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | services | Wood Library | Wood Library parking | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | services | Clark Physical Sciences Library | how to get to Clark Physical Sciences Library | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | services | Clarke Africana Library | how to get to Clarke Africana Library | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | services | Cornell Tech Library Services | how to get to Cornell Tech Library Services | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | services | Engineering Library | how to get to Engineering Library | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | services | Flower-Sprecher Veterinary Library | how to get to Flower-Sprecher Veterinary Library | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | services | Kroch Asia Collections | how to get to Kroch Asia Collections | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | services | Law Library | how to get to Law Library | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | services | Library Annex | how to get to Library Annex | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | services | Mann Library | how to get to Mann Library | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | services | Mathematics Library | how to get to Mathematics Library | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | services | Medical Center Archives | how to get to Medical Center Archives | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | services | Mui Ho Fine Arts Library | how to get to Mui Ho Fine Arts Library | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | services | Nestlé Library | how to get to Nestlé Library | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | services | Wood Library | how to get to Wood Library | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_food |  | Ithaca cheap eats | 0 | 1 | 1 | 4 | 0.00 | watch | strong dedicated incumbent (AGI=1); head term logged as watch |
| ithaca-ny | town_food |  | Ithaca grocery stores near campus | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_food |  | Ithaca late night food | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_government | Aging | Aging for parents | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_government | Aging | Aging for transfer students | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_government | Assessment | Assessment for parents | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_government | Assigned Counsel | Assigned Counsel for parents | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_government | Assigned Counsel | Assigned Counsel hours | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_government | Board of Elections | Board of Elections for parents | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_government | Board of Elections | Board of Elections for transfer students | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_government | Building Permit | Building Permit hours | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_government | City Budget | City Budget for parents | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_government | City Budget | City Budget hours | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_government | Communications & Public Information | Communications & Public Information for transfer students | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_government | Communications & Public Information | Communications & Public Information hours | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_government | County Administration | County Administration for parents | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_government | County Administration | County Administration for transfer students | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_government | County Administration | County Administration hours | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_government | County Attorney | County Attorney for transfer students | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_government | County Attorney | County Attorney hours | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_government | County Clerk | County Clerk for parents | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_government | County Clerk | County Clerk for transfer students | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_government | County Clerk | County Clerk hours | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_government | County Compliance Program | County Compliance Program for transfer students | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_government | County Compliance Program | County Compliance Program hours | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_government | County Legislature | County Legislature for transfer students | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_government | County Legislature | County Legislature hours | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_government | Disclaimer and Privacy Policy | Disclaimer and Privacy Policy for parents | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_government | Disclaimer and Privacy Policy | Disclaimer and Privacy Policy hours | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_government | District Attorney | District Attorney for parents | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_government | District Attorney | District Attorney for transfer students | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_government | District Attorney | District Attorney hours | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_government | Dog License | Dog License for parents | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_government | Dog License | Dog License for transfer students | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_government | Dog License | Dog License hours | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_government | Domestic Partnership | Domestic Partnership for parents | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_government | Domestic Partnership | Domestic Partnership hours | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_government | Emergency Response | Emergency Response for parents | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_government | Emergency Response | Emergency Response for transfer students | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_government | Emergency Response | Emergency Response hours | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_government | Facilities Department | Facilities Department for parents | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_government | Facilities Department | Facilities Department for transfer students | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_government | Facilities Department | Facilities Department hours | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_government | Finance Department | Finance Department for parents | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_government | Finance Department | Finance Department for transfer students | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_government | Freedom of Information Request | Freedom of Information Request for parents | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_government | Freedom of Information Request | Freedom of Information Request for transfer students | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_government | GIS Division | GIS Division for transfer students | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_government | GIS Division | GIS Division hours | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_government | General City Bills | General City Bills for parents | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_government | General City Bills | General City Bills for transfer students | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_government | General City Bills | General City Bills hours | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_government | Highway Department | Highway Department for parents | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_government | Historian Division | Historian Division for transfer students | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_government | Historian Division | Historian Division hours | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_government | Human Resources | Human Resources for parents | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_government | Human Resources | Human Resources for transfer students | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_government | Human Resources | Human Resources hours | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_government | Human Rights | Human Rights for parents | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_government | Information Technology Services | Information Technology Services for parents | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_government | Information Technology Services | Information Technology Services for transfer students | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_government | Information Technology Services | Information Technology Services hours | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_government |  | Ithaca noise ordinance | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_government | Ithaca-Tompkins County Transportation Council | Ithaca-Tompkins County Transportation Council for parents | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_government | Ithaca-Tompkins County Transportation Council | Ithaca-Tompkins County Transportation Council hours | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_government | Marriage License | Marriage License hours | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_government | Noise Ordinance Permit | Noise Ordinance Permit for parents | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_government | Noise Ordinance Permit | Noise Ordinance Permit hours | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_government | Occupancy Tax | Occupancy Tax for parents | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_government | Occupancy Tax | Occupancy Tax hours | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_government | Parking Permit | Parking Permit for parents | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_government | Parking Permit | Parking Permit for transfer students | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_government | Parking Permit | Parking Permit hours | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_government | Parking Permits | Parking Permits for parents | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_government | Parking Regulations | Parking Regulations for parents | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_government | Parking | Parking for parents | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_government | Parking | Parking hours | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_government | Parks and Recreation | Parks and Recreation for parents | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_government | Parks and Recreation | Parks and Recreation for transfer students | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_government | Parks and Recreation | Parks and Recreation hours | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_government | Planning and Sustainability | Planning and Sustainability for parents | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_government | Planning and Sustainability | Planning and Sustainability for transfer students | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_government | Probation and Community Justice | Probation and Community Justice for parents | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_government | Property Taxes | Property Taxes for parents | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_government | Property Taxes | Property Taxes for transfer students | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_government | Property Taxes | Property Taxes hours | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_government | Recycling & Materials Management | Recycling & Materials Management for parents | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_government | Recycling & Materials Management | Recycling & Materials Management for transfer students | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_government | Recycling & Materials Management | Recycling & Materials Management hours | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_government | SIREN Sign-up | SIREN Sign-up for transfer students | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_government | Sheriff's Office | Sheriff's Office for parents | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_government | Sheriff's Office | Sheriff's Office hours | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_government | Social Services | Social Services for parents | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_government | Social Services | Social Services for transfer students | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_government | Special Event Permit | Special Event Permit for transfer students | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_government | Special Event Permit | Special Event Permit hours | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_government | Street Cleaning | Street Cleaning for parents | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_government | Trash Collection & Tags | Trash Collection & Tags for parents | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_government | Trash Collection & Tags | Trash Collection & Tags for transfer students | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_government | Trash Collection & Tags | Trash Collection & Tags hours | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_government | Veterans Services | Veterans Services hours | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_government | Weights and Measures | Weights and Measures for parents | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_government | Weights and Measures | Weights and Measures for transfer students | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_government | Whole Health | Whole Health for parents | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_government | Whole Health | Whole Health for transfer students | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_government | Whole Health | Whole Health hours | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_government | Workforce Development | Workforce Development for parents | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_government | Workforce Development | Workforce Development for transfer students | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_government | Workforce Development | Workforce Development hours | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_government | Youth Services | Youth Services for parents | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_government | Youth Services | Youth Services hours | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_jobs |  | Ithaca jobs for grad students | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_jobs |  | Ithaca jobs for residents | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_offcampus_housing |  | Ithaca apartment lease student | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_offcampus_housing |  | Ithaca off-campus housing | 0 | 1 | 2 | 4 | 0.00 | watch | strong dedicated incumbent (AGI=1); head term logged as watch |
| ithaca-ny | town_offcampus_housing |  | Ithaca rent average | 0 | 0 | 0 | 4 | 0.00 | watch | strong dedicated incumbent (AGI=0); head term logged as watch |
| ithaca-ny | town_outdoors | Cass Park Ice Rink | Cass Park Ice Rink review | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_outdoors | Cass Park Ice Rink | Cass Park Ice Rink safety rules | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_outdoors | Cass Park Pool | Cass Park Pool for parents | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_outdoors | Cass Park Pool | Cass Park Pool for transfer students | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_outdoors | Cass Park Pool | Cass Park Pool parking | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_outdoors | Cass Park Pool | Cass Park Pool safety rules | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_outdoors | Cass Park | Cass Park for parents | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_outdoors | Cass Park | Cass Park for transfer students | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_outdoors | Cass Park | Cass Park safety rules | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_outdoors |  | Ithaca gorges safety | 0 | 1 | 2 | 4 | 0.00 | watch | strong dedicated incumbent (AGI=1); head term logged as watch |
| ithaca-ny | town_outdoors |  | Ithaca swimming gorges rules | 0 | 1 | 2 | 4 | 0.00 | watch | strong dedicated incumbent (AGI=1); head term logged as watch |
| ithaca-ny | town_outdoors | Stewart Park Carousel | Stewart Park Carousel for transfer students | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_outdoors | Stewart Park Carousel | Stewart Park Carousel safety rules | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_outdoors | Stewart Park | Stewart Park for parents | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_outdoors | Stewart Park | Stewart Park for transfer students | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_outdoors | Stewart Park | Stewart Park parking | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_outdoors | Cass Park | how to get to Cass Park | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_outdoors | Cass Park Ice Rink | how to get to Cass Park Ice Rink | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_outdoors | Stewart Park | how to get to Stewart Park | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_outdoors | Stewart Park Carousel | how to get to Stewart Park Carousel | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_services |  | Ithaca urgent care | 0 | 0 | 0 | 4 | 0.00 | watch | strong dedicated incumbent (AGI=0); head term logged as watch |
| ithaca-ny | town_transit_intercity |  | Ithaca airport to campus | 0 | 1 | 2 | 4 | 0.00 | watch | strong dedicated incumbent (AGI=1); head term logged as watch |
| ithaca-ny | town_transit_local |  | Ithaca bus fare TCAT | 0 | 1 | 2 | 4 | 0.00 | watch | strong dedicated incumbent (AGI=1); head term logged as watch |
| ithaca-ny | town_transit_local |  | Ithaca bus routes map | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_transit_local | Route 10: 10 | Route 10: 10 cost | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_transit_local | Route 10: 10 | Route 10: 10 for parents | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_transit_local | Route 10: 10 | Route 10: 10 schedule | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_transit_local | Route 115: 11S | Route 115: 11S cost | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_transit_local | Route 115: 11S | Route 115: 11S for parents | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_transit_local | Route 115: 11S | Route 115: 11S for transfer students | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_transit_local | Route 115: 11S | Route 115: 11S schedule | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_transit_local | Route 11: 11 | Route 11: 11 cost | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_transit_local | Route 11: 11 | Route 11: 11 for parents | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_transit_local | Route 11: 11 | Route 11: 11 for transfer students | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_transit_local | Route 13: 13 | Route 13: 13 for parents | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_transit_local | Route 145: 14S | Route 145: 14S cost | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_transit_local | Route 145: 14S | Route 145: 14S for parents | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_transit_local | Route 14: 14 | Route 14: 14 for parents | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_transit_local | Route 14: 14 | Route 14: 14 schedule | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_transit_local | Route 15: 15 | Route 15: 15 cost | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_transit_local | Route 15: 15 | Route 15: 15 for parents | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_transit_local | Route 17: 17 | Route 17: 17 for transfer students | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_transit_local | Route 17: 17 | Route 17: 17 schedule | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_transit_local | Route 20: 20 | Route 20: 20 cost | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_transit_local | Route 20: 20 | Route 20: 20 for parents | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_transit_local | Route 20: 20 | Route 20: 20 schedule | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_transit_local | Route 21: 21 | Route 21: 21 for parents | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_transit_local | Route 21: 21 | Route 21: 21 for transfer students | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_transit_local | Route 21: 21 | Route 21: 21 schedule | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_transit_local | Route 30: 30 | Route 30: 30 cost | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_transit_local | Route 30: 30 | Route 30: 30 for parents | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_transit_local | Route 30: 30 | Route 30: 30 for transfer students | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_transit_local | Route 30: 30 | Route 30: 30 schedule | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_transit_local | Route 31: 31 | Route 31: 31 cost | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_transit_local | Route 31: 31 | Route 31: 31 for parents | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_transit_local | Route 31: 31 | Route 31: 31 for transfer students | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_transit_local | Route 32: 32 | Route 32: 32 cost | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_transit_local | Route 32: 32 | Route 32: 32 for parents | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_transit_local | Route 36: 36 | Route 36: 36 cost | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_transit_local | Route 36: 36 | Route 36: 36 schedule | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_transit_local | Route 37: 37 | Route 37: 37 for parents | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_transit_local | Route 37: 37 | Route 37: 37 for transfer students | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_transit_local | Route 40: 40 | Route 40: 40 cost | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_transit_local | Route 40: 40 | Route 40: 40 for parents | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_transit_local | Route 43: 43 | Route 43: 43 for parents | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_transit_local | Route 43: 43 | Route 43: 43 for transfer students | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_transit_local | Route 51: 51 | Route 51: 51 cost | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_transit_local | Route 51: 51 | Route 51: 51 for parents | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_transit_local | Route 51: 51 | Route 51: 51 schedule | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_transit_local | Route 52: 52 | Route 52: 52 cost | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_transit_local | Route 52: 52 | Route 52: 52 for parents | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_transit_local | Route 65: 65 | Route 65: 65 cost | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_transit_local | Route 65: 65 | Route 65: 65 for transfer students | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_transit_local | Route 67: 67 | Route 67: 67 cost | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_transit_local | Route 67: 67 | Route 67: 67 for parents | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_transit_local | Route 67: 67 | Route 67: 67 for transfer students | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_transit_local | Route 67: 67 | Route 67: 67 schedule | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_transit_local | Route 81: 81 | Route 81: 81 cost | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_transit_local | Route 81: 81 | Route 81: 81 for parents | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_transit_local | Route 82: 82 | Route 82: 82 cost | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_transit_local | Route 82: 82 | Route 82: 82 for parents | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_transit_local | Route 82: 82 | Route 82: 82 schedule | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_transit_local | Route 90: 90 | Route 90: 90 for parents | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_transit_local | Route 90: 90 | Route 90: 90 for transfer students | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_transit_local | Route 90: 90 | Route 90: 90 schedule | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_transit_local | Route 92: 92 | Route 92: 92 schedule | 0 | 0 | 0 | 4 | 0.00 | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | transfer |  | Cornell internal transfer between colleges | 0 | 1 | 2 | 4 | 0.00 | watch | strong dedicated incumbent (AGI=1); head term logged as watch |
| cornell-university | transfer |  | Cornell transfer credit policy | 0 | 0 | 1 | 4 | 0.00 | watch | strong dedicated incumbent (AGI=0); head term logged as watch |
| cornell-university | transportation |  | Cornell bike registration | 0 | 1 | 2 | 4 | 0.00 | watch | strong dedicated incumbent (AGI=1); head term logged as watch |
| cornell-university | transportation |  | Cornell bus pass students | 0 | 0 | 1 | 4 | 0.00 | watch | strong dedicated incumbent (AGI=0); head term logged as watch |
| cornell-university | admissions |  | Cornell admissions deadline | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | alumni_education |  | Cornell continuing education certificates | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | alumni_records |  | Cornell transcript request alumni | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | costs_aid |  | Cornell cost of attendance | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | courses |  | Cornell grading policy s/u | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | dining | Amit Bhatia Libe Café | Amit Bhatia Libe Café cost | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | dining | Amit Bhatia Libe Café | Amit Bhatia Libe Café for transfer students | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | dining | Amit Bhatia Libe Café | Amit Bhatia Libe Café hours | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | dining | Amit Bhatia Libe Café | Amit Bhatia Libe Café parking | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | dining | Amit Bhatia Libe Café | Amit Bhatia Libe Café review | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | dining | Atrium Café | Atrium Café hours | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | dining | Atrium Café | Atrium Café parking | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | dining | Bear Necessities | Bear Necessities cost | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | dining | Bear Necessities | Bear Necessities parking | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | dining | Bear Necessities | Bear Necessities review | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | dining | Becker House Dining Room | Becker House Dining Room for transfer students | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | dining | Big Red Barn | Big Red Barn parking | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | dining | Big Red Barn | Big Red Barn vs Bus Stop Bagels | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | dining | Bus Stop Bagels | Bus Stop Bagels review | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | dining | Café Jennie | Café Jennie hours | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | dining | Café Jennie | Café Jennie parking | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | dining | College of Veterinary Medicine Café | College of Veterinary Medicine Café for parents | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | dining | College of Veterinary Medicine Café | College of Veterinary Medicine Café review | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | dining | Cook House Dining Room | Cook House Dining Room cost | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | dining | Cook House Dining Room | Cook House Dining Room hours | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | dining | Cook House Dining Room | Cook House Dining Room parking | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | dining | Cornell Dairy Bar | Cornell Dairy Bar cost | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | dining | Cornell Dairy Bar | Cornell Dairy Bar review | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | dining | Cornell Dairy Bar | Cornell Dairy Bar vs Goldie's | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | dining | Crossings Café | Crossings Café hours | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | dining | Crossings Café | Crossings Café parking | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | dining | Crossings Café | Crossings Café review | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | dining | Goldie's | Goldie's cost | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | dining | Goldie's | Goldie's for parents | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | dining | Goldie's | Goldie's hours | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | dining | Goldie's | Goldie's review | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | dining | Green Dragon | Green Dragon for transfer students | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | dining | Green Dragon | Green Dragon hours | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | dining | Green Dragon | Green Dragon parking | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | dining | Jansen's Market | Jansen's Market cost | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | dining | Jansen's Market | Jansen's Market hours | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | dining | Jansen's Market | Jansen's Market review | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | dining | Jansen’s Dining Room at Hans Bethe House | Jansen’s Dining Room at Hans Bethe House hours | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | dining | Jansen’s Dining Room at Hans Bethe House | Jansen’s Dining Room at Hans Bethe House vs Keeton House Dining Room | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | dining | Keeton House Dining Room | Keeton House Dining Room review | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | dining | Mann Café | Mann Café cost | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | dining | Mann Café | Mann Café for parents | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | dining | Mann Café | Mann Café for transfer students | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | dining | Martha's Café | Martha's Café parking | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | dining | Martha's Café | Martha's Café review | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | dining | Mattin's Café | Mattin's Café cost | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | dining | Mattin's Café | Mattin's Café hours | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | dining | Mattin's Café | Mattin's Café review | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | dining | Mattin's Café | Mattin's Café vs Rusty's | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | dining | McCormick's at Moakley House | McCormick's at Moakley House vs Novick's Café | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | dining | Morrison Dining | Morrison Dining for parents | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | dining | Morrison Dining | Morrison Dining review | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | dining | North Star Dining Room | North Star Dining Room cost | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | dining | North Star Dining Room | North Star Dining Room for transfer students | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | dining | North Star Dining Room | North Star Dining Room parking | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | dining | Novick's Café | Novick's Café for transfer students | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | dining | Novick's Café | Novick's Café hours | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | dining | Novick's Café | Novick's Café parking | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | dining | Okenshields | Okenshields hours | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | dining | Okenshields | Okenshields review | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | dining | Risley Dining | Risley Dining for transfer students | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | dining | Risley Dining | Risley Dining hours | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | dining | Risley Dining | Risley Dining parking | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | dining | Risley Dining | Risley Dining review | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | dining | Rose House Dining Room | Rose House Dining Room hours | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | dining | Rose House Dining Room | Rose House Dining Room parking | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | dining | Rusty's | Rusty's cost | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | dining | Rusty's | Rusty's review | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | dining | Rusty's | Rusty's vs Trillium | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | dining | Trillium | Trillium for parents | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | dining | Trillium | Trillium hours | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | dining | Becker House Dining Room | how to get to Becker House Dining Room | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | dining | Big Red Barn | how to get to Big Red Barn | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | dining | Green Dragon | how to get to Green Dragon | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | dining | McCormick's at Moakley House | how to get to McCormick's at Moakley House | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | dining | Okenshields | how to get to Okenshields | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | dining | Rusty's | how to get to Rusty's | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | events_calendar |  | Cornell academic calendar 2026-27 | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | events_calendar |  | Cornell move-in day 2026 | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | events_calendar |  | Cornell orientation dates | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | 1 Forest Park Lane | 1 Forest Park Lane for parents | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | 1 Forest Park Lane | 1 Forest Park Lane parking | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | 104 Mary Ann Wood Drive | 104 Mary Ann Wood Drive for transfer students | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | 104 Mary Ann Wood Drive | 104 Mary Ann Wood Drive parking | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | 112 Edgemoor | 112 Edgemoor for international students | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | 301 College Avenue | 301 College Avenue cost | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | 301 College Avenue | 301 College Avenue for international students | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | 301 College Avenue | 301 College Avenue parking | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Akwe:kon | Akwe:kon cost | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Akwe:kon | Akwe:kon for international students | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Akwe:kon | Akwe:kon for parents | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Akwe:kon | Akwe:kon for transfer students | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Akwe:kon | Akwe:kon vs Ecology House | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Alice Cook House | Alice Cook House cost | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Alice Cook House | Alice Cook House for grad students | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Alice Cook House | Alice Cook House for international students | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Balch Hall | Balch Hall for grad students | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Balch Hall | Balch Hall for international students | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Balch Hall | Balch Hall room size | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Barbara McClintock Hall | Barbara McClintock Hall for parents | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Barbara McClintock Hall | Barbara McClintock Hall parking | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Barbara McClintock Hall | Barbara McClintock Hall room size | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Carl Becker House | Carl Becker House cost | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Carl Becker House | Carl Becker House for parents | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Carl Becker House | Carl Becker House parking | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Carl Becker House | Carl Becker House room size | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Cascadilla Hall | Cascadilla Hall for grad students | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Cascadilla Hall | Cascadilla Hall for transfer students | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Clara Dickson Hall | Clara Dickson Hall for grad students | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Clara Dickson Hall | Clara Dickson Hall room size | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Court-Kay-Bauer Hall | Court-Kay-Bauer Hall room size | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Ecology House | Ecology House for parents | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Ecology House | Ecology House for transfer students | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Equity & Engagement Community (EEC) | Equity & Engagement Community (EEC) for transfer students | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Equity & Engagement Community | Equity & Engagement Community for grad students | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Equity & Engagement Community | Equity & Engagement Community for parents | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Equity & Engagement Community | Equity & Engagement Community room size | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Flora Rose House | Flora Rose House for grad students | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Flora Rose House | Flora Rose House for international students | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Flora Rose House | Flora Rose House room size | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Flora Rose House | Flora Rose House vs Hans Bethe House | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Hans Bethe House | Hans Bethe House parking | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Hans Bethe House | Hans Bethe House vs William Keeton House | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | High Rise #5 | High Rise #5 parking | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Holland International Living Center (HILC) | Holland International Living Center (HILC) for parents | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Holland International Living Center (HILC) | Holland International Living Center (HILC) for transfer students | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Holland International Living Center (HILC) | Holland International Living Center (HILC) parking | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Hu Shih Hall | Hu Shih Hall for international students | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Hu Shih Hall | Hu Shih Hall for parents | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Hu Shih Hall | Hu Shih Hall for transfer students | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Jameson Hall | Jameson Hall cost | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Jameson Hall | Jameson Hall for grad students | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Jameson Hall | Jameson Hall for international students | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Jameson Hall | Jameson Hall for parents | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Jameson Hall | Jameson Hall room size | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Just About Music (JAM) | Just About Music (JAM) for international students | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Just About Music (JAM) | Just About Music (JAM) for parents | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Language House | Language House parking | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Language House | Language House review | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Language House | Language House room size | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Language House | Language House vs Latino Living Center (LLC) | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Latino Living Center (LLC) | Latino Living Center (LLC) for grad students | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Latino Living Center (LLC) | Latino Living Center (LLC) for parents | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Latino Living Center (LLC) | Latino Living Center (LLC) for transfer students | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Loving House | Loving House for grad students | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Loving House | Loving House vs Multicultural Living Learning Unit (McLLU) | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Low Rise #6 | Low Rise #6 for grad students | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Low Rise #7 | Low Rise #7 room size | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Mary Donlon Hall | Mary Donlon Hall cost | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Mary Donlon Hall | Mary Donlon Hall for international students | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Mary Donlon Hall | Mary Donlon Hall for parents | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Mary Donlon Hall | Mary Donlon Hall parking | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Mews Hall | Mews Hall for grad students | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Mews Hall | Mews Hall review | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Multicultural Living Learning Unit (McLLU) | Multicultural Living Learning Unit (McLLU) cost | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Multicultural Living Learning Unit (McLLU) | Multicultural Living Learning Unit (McLLU) for grad students | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Multicultural Living Learning Unit (McLLU) | Multicultural Living Learning Unit (McLLU) parking | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Multicultural Living Learning Unit (McLLU) | Multicultural Living Learning Unit (McLLU) room size | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Multicultural Living Learning Unit (McLLU) | Multicultural Living Learning Unit (McLLU) vs program house mission | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Program House Mission and Expectations | Program House Mission and Expectations cost | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Program House Mission and Expectations | Program House Mission and Expectations for transfer students | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Program House Mission and Expectations | Program House Mission and Expectations parking | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Program House Mission and Expectations | Program House Mission and Expectations room size | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Risley Residential College | Risley Residential College room size | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Ruth Bader Ginsburg Hall | Ruth Bader Ginsburg Hall for grad students | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Ruth Bader Ginsburg Hall | Ruth Bader Ginsburg Hall for transfer students | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Ruth Bader Ginsburg Hall | Ruth Bader Ginsburg Hall room size | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Sheldon Court | Sheldon Court room size | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Sober Living Community | Sober Living Community for grad students | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Sober Living Community | Sober Living Community for parents | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Toni Morrison Hall | Toni Morrison Hall for grad students | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Townhouse Apartments | Townhouse Apartments for parents | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Ujamaa Residential College | Ujamaa Residential College for grad students | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Veterans House | Veterans House for international students | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Veterans House | Veterans House for transfer students | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Veterans House | Veterans House room size | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | 1 Forest Park Lane | how to get to 1 Forest Park Lane | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | 112 Edgemoor | how to get to 112 Edgemoor | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Akwe:kon | how to get to Akwe:kon | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Alice Cook House | how to get to Alice Cook House | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Cascadilla Hall | how to get to Cascadilla Hall | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Clara Dickson Hall | how to get to Clara Dickson Hall | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | High Rise #5 | how to get to High Rise #5 | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Holland International Living Center (HILC) | how to get to Holland International Living Center (HILC) | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Just About Music (JAM) | how to get to Just About Music (JAM) | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Language House | how to get to Language House | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Low Rise #7 | how to get to Low Rise #7 | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Sober Living Community | how to get to Sober Living Community | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Townhouse Apartments | how to get to Townhouse Apartments | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Veterans House | how to get to Veterans House | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | William Keeton House | how to get to William Keeton House | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | 1 Forest Park Lane | is 1 Forest Park Lane good for transfers | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | 112 Edgemoor | is 112 Edgemoor good for transfers | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Akwe:kon | is Akwe:kon good for transfers | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Clara Dickson Hall | is Clara Dickson Hall good for transfers | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Ecology House | is Ecology House good for transfers | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Equity & Engagement Community | is Equity & Engagement Community good for transfers | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Holland International Living Center (HILC) | is Holland International Living Center (HILC) good for transfers | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Hu Shih Hall | is Hu Shih Hall good for transfers | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Language House | is Language House good for transfers | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | Mary Donlon Hall | is Mary Donlon Hall good for transfers | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | program house mission | program house mission cost | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | program house mission | program house mission for grad students | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | program house mission | program house mission for international students | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | housing | program house mission | program house mission vs Program House Mission and Expectations | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | parents_calendar |  | Cornell parent orientation | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | programs |  | Cornell study abroad requirements | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | services | Alumni | Alumni for transfer students | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | services | Clarke Africana Library | Clarke Africana Library for transfer students | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | services | Clarke Africana Library | Clarke Africana Library hours | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | services | Clarke Africana Library | Clarke Africana Library parking | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | services | Cornell Tech Library Services | Cornell Tech Library Services for transfer students | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | services |  | Cornell library hours | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | services |  | Cornell student id replacement | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | services | Cox Library of Music and Dance | Cox Library of Music and Dance parking | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | services | Engineering Library | Engineering Library for parents | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | services | Engineering Library | Engineering Library for transfer students | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | services | Engineering Library | Engineering Library parking | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | services | Flower-Sprecher Veterinary Library | Flower-Sprecher Veterinary Library for transfer students | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | services | Flower-Sprecher Veterinary Library | Flower-Sprecher Veterinary Library parking | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | services | HELP | HELP hours | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | services | Kroch Asia Collections | Kroch Asia Collections parking | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | services | Law Library | Law Library for transfer students | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | services | Library Annex | Library Annex parking | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | services | MENU | MENU for transfer students | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | services | MENU | MENU hours | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | services | MENU | MENU parking | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | services | Management Library | Management Library for parents | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | services | Mathematics Library | Mathematics Library for parents | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | services | Mui Ho Fine Arts Library | Mui Ho Fine Arts Library hours | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | services | Mui Ho Fine Arts Library | Mui Ho Fine Arts Library parking | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | services | Nestlé Library | Nestlé Library for transfer students | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | services | Olin Library | Olin Library for parents | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | services | POPULAR LINKS | POPULAR LINKS for parents | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | services | POPULAR LINKS | POPULAR LINKS for transfer students | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | services | POPULAR LINKS | POPULAR LINKS hours | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | services | POPULAR LINKS | POPULAR LINKS parking | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | services | Rare and Manuscript Collections | Rare and Manuscript Collections hours | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | services | Uris Library | Uris Library for transfer students | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | services | Uris Library | Uris Library hours | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | services | Wood Library | Wood Library for parents | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | services | Wood Library | Wood Library for transfer students | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | services | Alumni | how to get to Alumni | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | services | Catherwood Library | how to get to Catherwood Library | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | services | Cox Library of Music and Dance | how to get to Cox Library of Music and Dance | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | services | HELP | how to get to HELP | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | services | MENU | how to get to MENU | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | services | Management Library | how to get to Management Library | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | services | Olin Library | how to get to Olin Library | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | services | POPULAR LINKS | how to get to POPULAR LINKS | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | services | Rare and Manuscript Collections | how to get to Rare and Manuscript Collections | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | services | Uris Library | how to get to Uris Library | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_government | Aging | Aging hours | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_government | Assessment | Assessment for transfer students | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_government | Assessment | Assessment hours | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_government | Assigned Counsel | Assigned Counsel for transfer students | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_government | Board of Elections | Board of Elections hours | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_government | Building Permit | Building Permit for parents | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_government | Building Permit | Building Permit for transfer students | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_government | City Budget | City Budget for transfer students | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_government | Communications & Public Information | Communications & Public Information for parents | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_government | County Attorney | County Attorney for parents | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_government | County Compliance Program | County Compliance Program for parents | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_government | County Legislature | County Legislature for parents | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_government | Disclaimer and Privacy Policy | Disclaimer and Privacy Policy for transfer students | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_government | Domestic Partnership | Domestic Partnership for transfer students | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_government | Finance Department | Finance Department hours | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_government | Freedom of Information Request | Freedom of Information Request hours | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_government | GIS Division | GIS Division for parents | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_government | Highway Department | Highway Department for transfer students | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_government | Highway Department | Highway Department hours | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_government | Historian Division | Historian Division for parents | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_government | Human Rights | Human Rights for transfer students | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_government | Human Rights | Human Rights hours | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_government |  | Ithaca parking permit residential | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_government |  | Ithaca voter registration | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_government | Ithaca-Tompkins County Transportation Council | Ithaca-Tompkins County Transportation Council for transfer students | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_government | Marriage License | Marriage License for parents | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_government | Marriage License | Marriage License for transfer students | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_government | Motor Vehicles | Motor Vehicles for parents | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_government | Motor Vehicles | Motor Vehicles for transfer students | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_government | Motor Vehicles | Motor Vehicles hours | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_government | Noise Ordinance Permit | Noise Ordinance Permit for transfer students | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_government | Occupancy Tax | Occupancy Tax for transfer students | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_government | Parking Permits | Parking Permits for transfer students | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_government | Parking Permits | Parking Permits hours | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_government | Parking Regulations | Parking Regulations for transfer students | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_government | Parking Regulations | Parking Regulations hours | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_government | Parking | Parking for transfer students | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_government | Planning and Sustainability | Planning and Sustainability hours | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_government | Probation and Community Justice | Probation and Community Justice for transfer students | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_government | Probation and Community Justice | Probation and Community Justice hours | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_government | SIREN Sign-up | SIREN Sign-up for parents | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_government | SIREN Sign-up | SIREN Sign-up hours | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_government | Sheriff's Office | Sheriff's Office for transfer students | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_government | Social Services | Social Services hours | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_government | Special Event Permit | Special Event Permit for parents | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_government | Street Cleaning | Street Cleaning for transfer students | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_government | Street Cleaning | Street Cleaning hours | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_government | Use of City Property | Use of City Property for parents | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_government | Use of City Property | Use of City Property for transfer students | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_government | Use of City Property | Use of City Property hours | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_government | Veterans Services | Veterans Services for parents | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_government | Veterans Services | Veterans Services for transfer students | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_government | Weights and Measures | Weights and Measures hours | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_government | Youth Services | Youth Services for transfer students | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_jobs |  | Ithaca part time jobs | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_outdoors | Cass Park Ice Rink | Cass Park Ice Rink for parents | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_outdoors | Cass Park Ice Rink | Cass Park Ice Rink for transfer students | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_outdoors | Cass Park Ice Rink | Cass Park Ice Rink parking | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_outdoors | Cass Park Pool | Cass Park Pool review | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_outdoors | Cass Park | Cass Park parking | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_outdoors | Cass Park | Cass Park review | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_outdoors | Stewart Park Carousel | Stewart Park Carousel for parents | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_outdoors | Stewart Park Carousel | Stewart Park Carousel parking | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_outdoors | Stewart Park Carousel | Stewart Park Carousel review | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_outdoors | Stewart Park | Stewart Park review | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_outdoors | Stewart Park | Stewart Park safety rules | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_outdoors | Cass Park Pool | how to get to Cass Park Pool | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_transit_local | Route 10: 10 | Route 10: 10 for transfer students | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_transit_local | Route 11: 11 | Route 11: 11 schedule | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_transit_local | Route 13: 13 | Route 13: 13 cost | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_transit_local | Route 13: 13 | Route 13: 13 for transfer students | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_transit_local | Route 13: 13 | Route 13: 13 schedule | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_transit_local | Route 145: 14S | Route 145: 14S for transfer students | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_transit_local | Route 145: 14S | Route 145: 14S schedule | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_transit_local | Route 14: 14 | Route 14: 14 cost | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_transit_local | Route 14: 14 | Route 14: 14 for transfer students | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_transit_local | Route 15: 15 | Route 15: 15 for transfer students | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_transit_local | Route 15: 15 | Route 15: 15 schedule | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_transit_local | Route 17: 17 | Route 17: 17 cost | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_transit_local | Route 17: 17 | Route 17: 17 for parents | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_transit_local | Route 20: 20 | Route 20: 20 for transfer students | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_transit_local | Route 21: 21 | Route 21: 21 cost | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_transit_local | Route 31: 31 | Route 31: 31 schedule | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_transit_local | Route 32: 32 | Route 32: 32 for transfer students | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_transit_local | Route 32: 32 | Route 32: 32 schedule | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_transit_local | Route 36: 36 | Route 36: 36 for parents | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_transit_local | Route 36: 36 | Route 36: 36 for transfer students | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_transit_local | Route 37: 37 | Route 37: 37 cost | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_transit_local | Route 37: 37 | Route 37: 37 schedule | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_transit_local | Route 40: 40 | Route 40: 40 for transfer students | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_transit_local | Route 40: 40 | Route 40: 40 schedule | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_transit_local | Route 43: 43 | Route 43: 43 cost | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_transit_local | Route 43: 43 | Route 43: 43 schedule | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_transit_local | Route 51: 51 | Route 51: 51 for transfer students | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_transit_local | Route 52: 52 | Route 52: 52 for transfer students | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_transit_local | Route 52: 52 | Route 52: 52 schedule | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_transit_local | Route 65: 65 | Route 65: 65 for parents | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_transit_local | Route 65: 65 | Route 65: 65 schedule | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_transit_local | Route 81: 81 | Route 81: 81 for transfer students | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_transit_local | Route 81: 81 | Route 81: 81 schedule | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_transit_local | Route 82: 82 | Route 82: 82 for transfer students | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_transit_local | Route 90: 90 | Route 90: 90 cost | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_transit_local | Route 92: 92 | Route 92: 92 cost | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_transit_local | Route 92: 92 | Route 92: 92 for parents | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| ithaca-ny | town_transit_local | Route 92: 92 | Route 92: 92 for transfer students | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | transfer |  | Cornell transfer acceptance rate | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
| cornell-university | transfer |  | Cornell transfer deadline | 0 | None | 0 | 4 | None | watch | deferred: beyond the sweep intel cap; the discovery lane observes it later (R41) |
