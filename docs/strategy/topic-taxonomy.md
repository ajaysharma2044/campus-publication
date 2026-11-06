# Topic taxonomy (specs/continuous-local-run.md R33, R46)

Generated from `worker/campus_worker/taxonomy.py` (the seed) plus auto-created topics in the database. The taxonomy is a seed, not a limit: when 3 or more independent questions cluster outside every topic, a new topic is created automatically and listed under *Auto-created* (R46).

Audiences: prospective_first_year, prospective_transfer, undergrad, grad, international, parent, alumni, faculty_staff, visitor, resident.

## School topics

| key | label | audiences | freshness risk | authoritative source families |
|---|---|---|---|---|
| `admissions` | Admissions and applications — deadlines, requirements, decisions | prospective_first_year, prospective_transfer, international, parent | high | admissions_office |
| `transfer` | Transfer pathways — pathways, credit transfer, deadlines, internal transfer between colleges | prospective_transfer | high | admissions_office, registrar, college_offices |
| `programs` | Academic programs — majors, minors, requirements, advising, study abroad | prospective_first_year, prospective_transfer, undergrad, grad, international | medium | registrar, college_offices, department_pages |
| `courses` | Course enrollment and prerequisites — specific courses, prerequisites, enrollment, grading | prospective_first_year, prospective_transfer, undergrad, grad, international | high | class_roster_api, registrar, department_pages |
| `costs_aid` | Costs and financial aid — tuition, fees, aid, scholarships, work-study, cost of living | prospective_first_year, prospective_transfer, undergrad, grad, international, parent | high | bursar, financial_aid_office |
| `housing` | Housing — on-campus halls, program houses, off-campus and Collegetown | prospective_first_year, prospective_transfer, undergrad, grad, international, parent | high | housing_office, off_campus_living |
| `dining` | Dining and food — dining halls, meal plans, cafes, grocery | prospective_first_year, prospective_transfer, undergrad, grad, international, parent, visitor | medium | dining_office |
| `transportation` | Getting around and parking — buses, parking, bikes, walking routes, winter travel | prospective_first_year, prospective_transfer, undergrad, grad, international, faculty_staff, visitor, parent | medium | transportation_office, transit_agency |
| `health_wellbeing` | Health and wellbeing services — locations, hours, how to access; no medical advice | prospective_first_year, prospective_transfer, undergrad, grad, international, parent | medium | health_services |
| `clubs_events` | Clubs, Greek life, sports and recreation — clubs, Greek life, sports, gyms | prospective_first_year, prospective_transfer, undergrad, grad, international | medium | student_activities, athletics, recreation |
| `events_calendar` | Events and calendar — orientation, move-in, Slope Day, graduation | prospective_first_year, prospective_transfer, undergrad, grad, international, parent, alumni, visitor | high | registrar_calendar, events_office |
| `services` | Campus services — IDs, mail, printing, IT, libraries | prospective_first_year, prospective_transfer, undergrad, grad, international, faculty_staff | medium | it_knowledge_base, library, mail_services |
| `parents_visitors` | Parents and visitors — visiting, hotels, parking, tours | parent, visitor | medium | visitor_relations, parent_programs |
| `careers` | Jobs, internships and career services — student jobs, internships, recruiting, outcomes | prospective_first_year, prospective_transfer, undergrad, grad, international, alumni | medium | career_center, hr_pages, college_scorecard |
| `accessibility` | Accessibility | prospective_first_year, prospective_transfer, undergrad, grad, international, faculty_staff, visitor | medium | disability_services |
| `daily_life` | Arrival and daily life |  | medium |  |
| `alumni_giving` | Giving: how it works — official pages only | alumni | low | alumni_affairs |

## Town topics

| key | label | audiences | freshness risk | authoritative source families |
|---|---|---|---|---|
| `town_transit_intercity` | Transit in and out of town — airport, buses to NYC and other cities, car rental | prospective_first_year, prospective_transfer, undergrad, grad, international, parent, visitor, resident | high | airport, intercity_bus, car_rental |
| `town_transit_local` | Local transit — routes, fares, passes, schedules | prospective_first_year, prospective_transfer, undergrad, grad, international, resident, visitor | high | transit_agency |
| `town_neighborhoods` | Neighborhoods | prospective_first_year, prospective_transfer, undergrad, grad, international, resident | low | city_government, visitor_bureau |
| `town_offcampus_housing` | Off-campus housing and leases — leases, tenant rights from official sources | prospective_first_year, prospective_transfer, undergrad, grad, international, resident, parent | medium | city_government, county_government, off_campus_living, ny_state |
| `town_food` | Restaurants and food by need — late night, cheap, groceries | prospective_first_year, prospective_transfer, undergrad, grad, international, resident, visitor | medium | official_business_pages, visitor_bureau |
| `town_outdoors` | Outdoors: gorges, trails, parks — including safety rules | prospective_first_year, prospective_transfer, undergrad, grad, international, resident, visitor | medium | ny_state_parks, city_government, county_government |
| `town_weather` | Weather and what to pack | prospective_first_year, prospective_transfer, undergrad, grad, international, parent | low | national_weather_service |
| `town_services` | Banking, phone, healthcare access | prospective_first_year, prospective_transfer, undergrad, grad, international, resident | medium | official_business_pages, county_government, health_services |
| `town_jobs` | Jobs in town — major employers and seasonal work | prospective_first_year, prospective_transfer, undergrad, grad, international, resident | medium | county_government, major_employers, state_labor |
| `town_government` | Local government services students need — parking permits, voter registration info, leases and tenant rights | prospective_first_year, prospective_transfer, undergrad, grad, international, resident | medium | city_government, county_government, board_of_elections |

## Audience topic sets (alumni, parents and families, jobs and careers)

Every audience variant passes the audience-guide test (`briefs.audience_guide_justified`): a separate page exists only when the rules, steps or facts differ for that audience; otherwise it is a section on the shared page.

| key | label | audiences | freshness risk | authoritative source families |
|---|---|---|---|---|
| `parents_visitors` | Parents and visitors — visiting, hotels, parking, tours | parent, visitor | medium | visitor_relations, parent_programs |
| `alumni_benefits` | Alumni benefits — email, library and database access, career services, discounts | alumni | medium | alumni_affairs, library, career_center |
| `alumni_records` | Transcripts, diploma replacement, degree verification | alumni | low | registrar |
| `alumni_events` | Reunions, homecoming, regional clubs, directory and mentoring | alumni | high | alumni_affairs |
| `alumni_education` | Continuing education and certificates | alumni | medium | continuing_education |
| `alumni_giving` | Giving: how it works — official pages only | alumni | low | alumni_affairs |
| `alumni_visiting` | Visiting campus as an alum — alumni housing and parking at events | alumni | medium | visitor_relations, alumni_affairs |
| `parents_calendar` | Family weekend, move-in and move-out, parent orientation | parent | high | parent_programs, housing_office, registrar_calendar |
| `parents_billing` | Paying the bill, payment plans, parent portal, FERPA — what parents can and can't see | parent | high | bursar, registrar |
| `parents_logistics` | Mail and packages, visiting, safety resources | parent | medium | mail_services, visitor_relations, campus_police |
| `parents_prep` | Key dates, what to buy for a dorm, health insurance waivers | parent, prospective_first_year | high | housing_office, health_services, registrar_calendar |
| `jobs_student` | Student jobs on campus and work-study — how to apply, typical pay from official sources | prospective_first_year, prospective_transfer, undergrad, grad, international | medium | student_employment, financial_aid_office |
| `jobs_internships` | Internships, co-ops and recruiting timelines | prospective_first_year, prospective_transfer, undergrad, grad, international | medium | career_center |
| `jobs_outcomes` | First-destination outcomes and earnings — official reports and the federal College Scorecard only, with year and sample stated | prospective_first_year, prospective_transfer, undergrad, grad, international, parent | low | career_center, college_scorecard |
| `jobs_university` | Working at the university — openings, application process, benefits overview from HR pages | faculty_staff | medium | hr_pages |
| `jobs_grad` | Grad assistantships and postdocs | grad | medium | graduate_school, hr_pages |

## Auto-created topics (R46)

_None yet._
