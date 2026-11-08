"""Topic taxonomy seed and renderer (continuous-local-run R33, R46; AT33, AT45).

The seed below is the single source of truth for the R33 school topics, town topics and the audience topic
sets (alumni, parents and families, jobs and careers). `seed(conn)` upserts them (idempotent);
`render_markdown()` writes docs/strategy/topic-taxonomy.md from the same data plus any auto-created
topics in the database (R46), so the document never drifts from the seed.

Audiences (owner extension of SPEC §03): prospective_first_year, prospective_transfer, undergrad, grad,
international, parent, alumni, faculty_staff (incl. job applicants), visitor, resident.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import psycopg

from .config import REPO_ROOT

AUDIENCES = ("prospective_first_year", "prospective_transfer", "undergrad", "grad", "international", "parent", "alumni", "faculty_staff", "visitor", "resident")
STUDENTS = ("prospective_first_year", "prospective_transfer", "undergrad", "grad", "international")


@dataclass(frozen=True)
class Topic:
    key: str
    label: str
    scope: str                 # school | town | both
    audiences: tuple[str, ...]
    freshness_risk: str        # low | medium | high
    source_families: tuple[str, ...]
    sort_order: int
    description: str = ""
    parent_key: str | None = None
    seed_queries: tuple[str, ...] = ()   # R19 topic patterns: "{school}" / "{town}" placeholders; stored as hypotheses, never demand


# ---- school topics (R33) — existing keys from migration 0001 are kept and enriched; missing ones are added.
SCHOOL = [
    Topic("admissions", "Admissions and applications", "school", ("prospective_first_year", "prospective_transfer", "international", "parent"), "high", ("admissions_office",), 10, "deadlines, requirements, decisions"),
    Topic("transfer", "Transfer pathways", "school", ("prospective_transfer",), "high", ("admissions_office", "registrar", "college_offices"), 20, "pathways, credit transfer, deadlines, internal transfer between colleges"),
    Topic("programs", "Academic programs", "school", STUDENTS, "medium", ("registrar", "college_offices", "department_pages"), 30, "majors, minors, requirements, advising, study abroad"),
    Topic("courses", "Course enrollment and prerequisites", "school", STUDENTS, "high", ("class_roster_api", "registrar", "department_pages"), 40, "specific courses, prerequisites, enrollment, grading"),
    Topic("costs_aid", "Costs and financial aid", "school", STUDENTS + ("parent",), "high", ("bursar", "financial_aid_office"), 50, "tuition, fees, aid, scholarships, work-study, cost of living"),
    Topic("housing", "Housing", "school", STUDENTS + ("parent",), "high", ("housing_office", "off_campus_living"), 60, "on-campus halls, program houses, off-campus and Collegetown"),
    Topic("dining", "Dining and food", "school", STUDENTS + ("parent", "visitor"), "medium", ("dining_office",), 70, "dining halls, meal plans, cafes, grocery"),
    Topic("transportation", "Getting around and parking", "school", STUDENTS + ("faculty_staff", "visitor", "parent"), "medium", ("transportation_office", "transit_agency"), 80, "buses, parking, bikes, walking routes, winter travel"),
    Topic("health_wellbeing", "Health and wellbeing services", "school", STUDENTS + ("parent",), "medium", ("health_services",), 85, "locations, hours, how to access; no medical advice"),
    Topic("careers", "Jobs, internships and career services", "school", STUDENTS + ("alumni",), "medium", ("career_center", "hr_pages", "college_scorecard"), 110, "student jobs, internships, recruiting, outcomes"),
    Topic("clubs_events", "Clubs, Greek life, sports and recreation", "school", STUDENTS, "medium", ("student_activities", "athletics", "recreation"), 90, "clubs, Greek life, sports, gyms"),
    Topic("events_calendar", "Events and calendar", "school", STUDENTS + ("parent", "alumni", "visitor"), "high", ("registrar_calendar", "events_office"), 95, "orientation, move-in, Slope Day, graduation"),
    Topic("services", "Campus services", "school", STUDENTS + ("faculty_staff",), "medium", ("it_knowledge_base", "library", "mail_services"), 100, "IDs, mail, printing, IT, libraries"),
    Topic("parents_visitors", "Parents and visitors", "school", ("parent", "visitor"), "medium", ("visitor_relations", "parent_programs"), 105, "visiting, hotels, parking, tours"),
    Topic("accessibility", "Accessibility", "school", STUDENTS + ("faculty_staff", "visitor"), "medium", ("disability_services",), 120),
]
# ---- town topics (R33)
TOWN = [
    Topic("town_transit_intercity", "Transit in and out of town", "town", STUDENTS + ("parent", "visitor", "resident"), "high", ("airport", "intercity_bus", "car_rental"), 200, "airport, buses to NYC and other cities, car rental"),
    Topic("town_transit_local", "Local transit", "town", STUDENTS + ("resident", "visitor"), "high", ("transit_agency",), 210, "routes, fares, passes, schedules"),
    Topic("town_neighborhoods", "Neighborhoods", "town", STUDENTS + ("resident",), "low", ("city_government", "visitor_bureau"), 220),
    Topic("town_offcampus_housing", "Off-campus housing and leases", "town", STUDENTS + ("resident", "parent"), "medium", ("city_government", "county_government", "off_campus_living", "ny_state"), 230, "leases, tenant rights from official sources"),
    Topic("town_food", "Restaurants and food by need", "town", STUDENTS + ("resident", "visitor"), "medium", ("official_business_pages", "visitor_bureau"), 240, "late night, cheap, groceries"),
    Topic("town_outdoors", "Outdoors: gorges, trails, parks", "town", STUDENTS + ("resident", "visitor"), "medium", ("ny_state_parks", "city_government", "county_government"), 250, "including safety rules"),
    Topic("town_weather", "Weather and what to pack", "town", STUDENTS + ("parent",), "low", ("national_weather_service",), 260),
    Topic("town_services", "Banking, phone, healthcare access", "town", STUDENTS + ("resident",), "medium", ("official_business_pages", "county_government", "health_services"), 270),
    Topic("town_jobs", "Jobs in town", "town", STUDENTS + ("resident",), "medium", ("county_government", "major_employers", "state_labor"), 280, "major employers and seasonal work"),
    Topic("town_government", "Local government services students need", "town", STUDENTS + ("resident",), "medium", ("city_government", "county_government", "board_of_elections"), 290, "parking permits, voter registration info, leases and tenant rights"),
]
# ---- audience topic sets (R33 extension)
AUDIENCE_SETS = [
    Topic("alumni_benefits", "Alumni benefits", "school", ("alumni",), "medium", ("alumni_affairs", "library", "career_center"), 300, "email, library and database access, career services, discounts", "careers"),
    Topic("alumni_records", "Transcripts, diploma replacement, degree verification", "school", ("alumni",), "low", ("registrar",), 305, None and "", "services"),
    Topic("alumni_events", "Reunions, homecoming, regional clubs, directory and mentoring", "school", ("alumni",), "high", ("alumni_affairs",), 310, "", "events_calendar"),
    Topic("alumni_education", "Continuing education and certificates", "school", ("alumni",), "medium", ("continuing_education",), 315, "", "programs"),
    Topic("alumni_giving", "Giving: how it works", "school", ("alumni",), "low", ("alumni_affairs",), 320, "official pages only", None),
    Topic("alumni_visiting", "Visiting campus as an alum", "school", ("alumni",), "medium", ("visitor_relations", "alumni_affairs"), 325, "alumni housing and parking at events", "parents_visitors"),
    Topic("parents_calendar", "Family weekend, move-in and move-out, parent orientation", "school", ("parent",), "high", ("parent_programs", "housing_office", "registrar_calendar"), 330, "", "events_calendar"),
    Topic("parents_billing", "Paying the bill, payment plans, parent portal, FERPA", "school", ("parent",), "high", ("bursar", "registrar"), 335, "what parents can and can't see", "costs_aid"),
    Topic("parents_logistics", "Mail and packages, visiting, safety resources", "school", ("parent",), "medium", ("mail_services", "visitor_relations", "campus_police"), 340, "", "parents_visitors"),
    Topic("parents_prep", "Key dates, what to buy for a dorm, health insurance waivers", "school", ("parent", "prospective_first_year"), "high", ("housing_office", "health_services", "registrar_calendar"), 345, "", "housing"),
    Topic("jobs_student", "Student jobs on campus and work-study", "school", STUDENTS, "medium", ("student_employment", "financial_aid_office"), 350, "how to apply, typical pay from official sources", "careers"),
    Topic("jobs_internships", "Internships, co-ops and recruiting timelines", "school", STUDENTS, "medium", ("career_center",), 355, "", "careers"),
    Topic("jobs_outcomes", "First-destination outcomes and earnings", "school", STUDENTS + ("parent",), "low", ("career_center", "college_scorecard"), 360, "official reports and the federal College Scorecard only, with year and sample stated", "careers"),
    Topic("jobs_university", "Working at the university", "school", ("faculty_staff",), "medium", ("hr_pages",), 365, "openings, application process, benefits overview from HR pages", "careers"),
    Topic("jobs_grad", "Grad assistantships and postdocs", "school", ("grad",), "medium", ("graduate_school", "hr_pages"), 370, "", "careers"),
]
ALL = SCHOOL + TOWN + AUDIENCE_SETS


def seed(conn: psycopg.Connection) -> dict:
    """Upsert the taxonomy. Existing rows keep their id; labels/metadata are refreshed. Auto-created topics are untouched."""
    created = updated = 0
    with conn.cursor() as cur:
        for t in ALL:
            cur.execute(
                """INSERT INTO topics (key, label, description, sort_order, scope, audiences, freshness_risk, source_families, parent_key)
                   VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
                   ON CONFLICT (key) DO UPDATE SET label=EXCLUDED.label, description=EXCLUDED.description, sort_order=EXCLUDED.sort_order,
                     scope=EXCLUDED.scope, audiences=EXCLUDED.audiences, freshness_risk=EXCLUDED.freshness_risk, source_families=EXCLUDED.source_families,
                     parent_key=EXCLUDED.parent_key
                   RETURNING (xmax = 0) AS inserted""",
                (t.key, t.label, t.description or None, t.sort_order, t.scope, list(t.audiences), t.freshness_risk, list(t.source_families), t.parent_key),
            )
            if cur.fetchone()["inserted"]:
                created += 1
            else:
                updated += 1
    conn.commit()
    return {"created": created, "updated": updated, "total_seeded": len(ALL)}


def load(conn: psycopg.Connection) -> list[dict]:
    with conn.cursor() as cur:
        cur.execute("SELECT key, label, description, scope, audiences, freshness_risk, source_families, auto_created, created_from, parent_key, sort_order FROM topics ORDER BY sort_order, key")
        return [dict(r) for r in cur.fetchall()]


def render_markdown(topics: list[dict]) -> str:
    def table(rows):
        out = ["| key | label | audiences | freshness risk | authoritative source families |", "|---|---|---|---|---|"]
        for t in rows:
            out.append(f"| `{t['key']}` | {t['label']}{(' — ' + t['description']) if t.get('description') else ''} | {', '.join(t['audiences'])} | {t['freshness_risk']} | {', '.join(t['source_families'])} |")
        return "\n".join(out)
    school = [t for t in topics if t["scope"] in ("school", "both") and not t["parent_key"] and not t["auto_created"]]
    town = [t for t in topics if t["scope"] == "town" and not t["auto_created"]]
    aud = [t for t in topics if t["parent_key"] or t["key"].startswith(("alumni_", "parents_", "jobs_"))]
    aud = [t for t in aud if not t["auto_created"]]
    auto = [t for t in topics if t["auto_created"]]
    parts = ["# Topic taxonomy (specs/continuous-local-run.md R33, R46)", "",
             "Generated from `worker/campus_worker/taxonomy.py` (the seed) plus auto-created topics in the database. The taxonomy is a seed, not a limit: "
             "when 3 or more independent questions cluster outside every topic, a new topic is created automatically and listed under *Auto-created* (R46).", "",
             "Audiences: " + ", ".join(AUDIENCES) + ".", "", "## School topics", "", table(school), "", "## Town topics", "", table(town), "",
             "## Audience topic sets (alumni, parents and families, jobs and careers)", "",
             "Every audience variant passes the audience-guide test (`briefs.audience_guide_justified`): a separate page exists only when the rules, steps or facts differ for that audience; otherwise it is a section on the shared page.", "",
             table(aud), "", "## Auto-created topics (R46)", ""]
    parts.append(table(auto) if auto else "_None yet._")
    parts.append("")
    return "\n".join(parts)


def write_doc(conn: psycopg.Connection, path: Path | None = None) -> Path:
    p = path or (REPO_ROOT / "docs" / "strategy" / "topic-taxonomy.md")
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(render_markdown(load(conn)))
    return p


REQUIRED_R33_KEYS = {t.key for t in ALL}


# Topic seed queries (R19, R33): applied per school/town by expand.expand_topics(). Placeholders: {school}, {town}.
TOPIC_SEED_QUERIES: dict[str, tuple[str, ...]] = {
    "admissions": ("{school} admissions deadline", "{school} early decision deadline", "{school} admissions requirements", "{school} acceptance rate"),
    "transfer": ("{school} transfer deadline", "{school} transfer credit policy", "{school} internal transfer between colleges", "{school} transfer acceptance rate", "{school} transfer requirements gpa"),
    "programs": ("{school} how to change major", "{school} double major rules", "{school} add a minor", "{school} study abroad requirements", "{school} advising appointment"),
    "courses": ("{school} course enrollment dates", "{school} add drop deadline", "{school} prerequisites override", "{school} grading policy s/u"),
    "costs_aid": ("{school} tuition 2026-27", "{school} cost of attendance", "{school} financial aid deadline", "{school} work-study how to apply", "{school} payment plan"),
    "housing": ("{school} housing application deadline", "{school} off-campus housing", "{school} housing guaranteed", "{school} housing cost per semester"),
    "dining": ("{school} meal plan cost", "{school} dining hall hours", "{school} meal plan required", "{school} grocery near campus"),
    "transportation": ("{school} parking permit cost", "{school} bus pass students", "{school} bike registration", "{school} winter campus travel"),
    "health_wellbeing": ("{school} health services hours", "{school} counseling appointment how to", "{school} health insurance waiver deadline"),
    "careers": ("{school} career fair dates", "{school} internship timeline recruiting", "{school} first destination outcomes report"),
    "clubs_events": ("{school} how to join a club", "{school} greek life rush dates", "{school} gym membership students"),
    "events_calendar": ("{school} academic calendar 2026-27", "{school} move-in day 2026", "{school} graduation date 2027", "{school} orientation dates"),
    "services": ("{school} student id replacement", "{school} mail and packages", "{school} printing on campus", "{school} library hours"),
    "parents_visitors": ("{school} visitor parking", "{school} campus tour booking", "hotels near {school}"),
    "accessibility": ("{school} disability accommodations how to request", "{school} accessible housing"),
    "alumni_benefits": ("{school} alumni email", "{school} alumni library access", "{school} alumni career services", "{school} alumni discounts"),
    "alumni_records": ("{school} transcript request alumni", "{school} diploma replacement", "{school} degree verification"),
    "alumni_events": ("{school} reunion 2027", "{school} homecoming 2026", "{school} alumni club near me", "{school} alumni directory mentoring"),
    "alumni_education": ("{school} continuing education certificates", "{school} alumni audit courses"),
    "alumni_giving": ("{school} how to give annual fund",),
    "alumni_visiting": ("{school} alumni visiting campus parking", "{school} alumni housing reunion"),
    "parents_calendar": ("{school} family weekend 2026", "{school} move-in dates parents", "{school} parent orientation"),
    "parents_billing": ("{school} pay bill parent portal", "{school} payment plan", "{school} ferpa parent access"),
    "parents_logistics": ("{school} send package to student", "{school} campus safety resources parents", "visiting {school} hotels parking"),
    "parents_prep": ("{school} what to bring to the dorm", "{school} health insurance waiver", "{school} key dates first year"),
    "jobs_student": ("{school} student jobs", "{school} work-study jobs how to apply", "{school} student job pay rate"),
    "jobs_internships": ("{school} internship recruiting timeline", "{school} career center appointment", "{school} co-op program"),
    "jobs_outcomes": ("{school} graduate earnings by major", "{school} first destination report"),
    "jobs_university": ("jobs at {school}", "{school} staff benefits overview", "{school} how to apply for a job"),
    "jobs_grad": ("{school} graduate assistantship stipend", "{school} postdoc positions how to apply"),
    "town_transit_intercity": ("{town} airport to campus", "bus from {town} to nyc", "{town} to new york city bus", "car rental {town}"),
    "town_transit_local": ("{town} bus fare", "{town} bus pass students", "{town} bus routes map"),
    "town_neighborhoods": ("{town} neighborhoods for students", "best neighborhood {town} students", "collegetown vs downtown {town}"),
    "town_offcampus_housing": ("{town} off-campus housing", "{town} apartment lease student", "{town} tenant rights", "{town} rent average"),
    "town_food": ("{town} late night food", "{town} cheap eats", "{town} grocery stores near campus"),
    "town_outdoors": ("{town} gorges safety", "{town} hiking trails", "{town} state parks", "{town} swimming gorges rules"),
    "town_weather": ("{town} weather winter what to pack", "{town} snow how bad"),
    "town_services": ("{town} bank near campus", "{town} urgent care", "{town} phone store"),
    "town_jobs": ("{town} jobs for students", "{town} part time jobs", "{town} summer jobs"),
    "town_government": ("{town} parking permit residential", "{town} voter registration", "{town} trash recycling schedule", "{town} noise ordinance"),
}
