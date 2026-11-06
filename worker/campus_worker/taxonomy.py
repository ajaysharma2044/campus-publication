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
