"""Official source map and harvest rules for the pilot scope: Cornell University + Ithaca / Tompkins County
(continuous-local-run R18, R34; AT19, AT34). Deterministic; registered idempotently.

    python -m campus_worker.onboard_rules register     register every source + rule (hosted DB)
    python -m campus_worker.onboard_rules list

Every URL below was checked on 2026-11-06: HTTP 200 and robots.txt allows our agent. tcatbus.com, flyithaca.com and parks.ny.gov
disallow Claude agents: they stay search_observation (recorded), and TCAT routes come from the agency's published GTFS feed instead.
"""
from __future__ import annotations

import json
import sys
from dataclasses import dataclass, field

from .harvest import HarvestRule

CORNELL_UNITID = "190415"
SCL = "https://scl.cornell.edu"

# ---- Cornell (school scope) -----------------------------------------------------------------------------------------
CORNELL_RULES: list[HarvestRule] = [
    HarvestRule("cornell_halls_first_year", f"{SCL}/residential-life/housing/campus-housing/first-year-undergraduates/residence-halls", "residence_hall", "housing",
                link_prefix="/residential-life/housing/campus-housing/first-year-undergraduates/residence-halls/", group_from_heading=False,
                attributes={"area": "North Campus", "population": "first-year"}, publisher="Cornell Student & Campus Life"),
    HarvestRule("cornell_halls_upper_level", f"{SCL}/residential-life/housing/campus-housing/upper-level-undergraduates/residence-halls", "residence_hall", "housing",
                link_prefix="/residential-life/housing/campus-housing/upper-level-undergraduates/residence-halls/", attributes={"population": "upper-level"}, publisher="Cornell Student & Campus Life"),
    HarvestRule("cornell_west_campus_houses", f"{SCL}/residential-life/housing/campus-housing/upper-level-undergraduates/west-campus-house-system", "residence_hall", "housing",
                link_prefix="/residential-life/housing/campus-housing/upper-level-undergraduates/west-campus-house-system/", attributes={"area": "West Campus", "population": "upper-level", "group": "West Campus House System"},
                publisher="Cornell Student & Campus Life"),
    HarvestRule("cornell_program_houses_first_year", f"{SCL}/residential-life/housing/campus-housing/first-year-undergraduates/program-houses", "residence_hall", "housing",
                link_prefix="/residential-life/housing/campus-housing/first-year-undergraduates/program-houses/", attributes={"kind": "program_house", "group": "Program Houses"}, publisher="Cornell Student & Campus Life"),
    HarvestRule("cornell_program_houses_upper_level", f"{SCL}/residential-life/housing/campus-housing/upper-level-undergraduates/program-houses", "residence_hall", "housing",
                link_prefix="/residential-life/housing/campus-housing/upper-level-undergraduates/program-houses/", attributes={"kind": "program_house", "group": "Program Houses"}, publisher="Cornell Student & Campus Life"),
    # Dining pages list eateries as text items "<name> – in <building>" / "<name> – a café in <building>" (no per-eatery links)
    HarvestRule("cornell_dining_rooms", f"{SCL}/residential-life/dining/eateries-menus/dining-rooms", "dining_location", "dining",
                item_selector="li", heading_regex=r"dining rooms:", name_split_regex=r"\s*[–-]\s*(in|on|at)\s+", detail_from_split="located_in",
                group_from_heading=True, attributes={"kind": "dining_room"}, publisher="Cornell Dining"),
    HarvestRule("cornell_cafes", f"{SCL}/residential-life/dining/eateries-menus/cafes-food-courts-coffeehouses", "dining_location", "dining",
                item_selector="li", heading_regex=r"locations:", name_split_regex=r"\s*[–-]\s+", detail_from_split="description",
                group_from_heading=True, attributes={"kind": "cafe"}, publisher="Cornell Dining"),
    HarvestRule("cornell_convenience_stores", f"{SCL}/residential-life/dining/eateries-menus/convenience-stores", "dining_location", "dining",
                item_selector="li", heading_regex=r"(locations|stores):", name_split_regex=r"\s*[–-]\s+", detail_from_split="description",
                group_from_heading=True, attributes={"kind": "convenience_store"}, publisher="Cornell Dining"),
    HarvestRule("cornell_libraries", "https://www.library.cornell.edu/libraries/", "library", "services", item_selector="h2", exclude_regex=r"^(Libraries|Search|Hours|Contact)$",
                attributes={"kind": "library"}, publisher="Cornell University Library"),
]

# ---- Ithaca / Tompkins County (town scope) -------------------------------------------------------------------------
ITHACA_PLACE_SLUG = "ithaca-ny"
ITHACA_RULES: list[HarvestRule] = [
    # parks.ny.gov disallows Claude agents in robots.txt (recorded) → search observation only; no state-park harvest rule.
    HarvestRule("city_of_ithaca_services", "https://www.cityofithacany.gov/", "town_service", "town_government", link_regex=r"^https://www\.cityofithacany\.gov/\d+/[A-Za-z0-9-]+$",
                exclude_regex=r"^(Government|Initiatives|Services|How Do I|Read on|View All|city updates|Visitors|Visitors to the City|Information for Residents|New Residents|Learn About|Contact|Join|Meeting|See-Click-Fix|SeeClickFix|My Car|Updates|Commitment|Maps|Plans)",
                attributes={"kind": "city_service"}, publisher="City of Ithaca"),
    HarvestRule("city_of_ithaca_parks", "https://www.cityofithacany.gov/229/IYB-Recreation-Division", "park", "town_outdoors", link_regex=r"^https://www\.cityofithacany\.gov/\d+/[A-Za-z0-9-]+$",
                include_regex=r"\b(Park|Pool|Rink|Carousel|Trail|Golf|Beach|Garden)\b", attributes={"kind": "city_park"}, publisher="City of Ithaca"),
    HarvestRule("tompkins_county_departments", "https://www.tompkinscountyny.gov/departments", "town_service", "town_government",
                link_regex=r"/All-Departments/[^/?#]+/?$", exclude_regex=r"^(All Departments|Departments)$", attributes={"kind": "county_department"}, publisher="Tompkins County"),
]
TCAT_GTFS_URL = "https://realtimetcatbus.availtec.com/InfoPoint/GTFS-Zip.ashx"

EXTRA_PERMISSIONS = [
    # domain_pattern, publisher, connector, access_mode, state, retention, rpm, notes, attribution
    ("realtimetcatbus.availtec.com", "TCAT (GTFS feed host)", "feed", "feed", "allowed_with_limits", "full_text", 1, "Published GTFS feed; routes.txt only (R34).", None),
    ("*.library.cornell.edu", "Cornell University Library", "official_html", "fetch_permitted", "allowed_with_limits", "excerpts_only", 4, "library directory", None),
    ("*.cityofithacany.gov", "City of Ithaca (current domain)", "official_html", "fetch_permitted", "allowed_with_limits", "excerpts_only", 4, "cityofithaca.org redirects here", None),
]


def register_all(conn, *, cornell_only: bool = False) -> dict:
    from .collectors.html import register_source
    from .harvest import register_rule
    from .permissions import record_terms_check
    from .registry import find_by_external_id

    out = {"cornell": [], "ithaca": [], "permissions": []}
    with conn.cursor() as cur:
        for dp, pub, conn_name, mode, state, ret, rpm, notes, attrib in EXTRA_PERMISSIONS:
            cur.execute("""INSERT INTO source_permissions (domain_pattern, publisher, connector, access_mode, permission_state, retention_policy, rate_limit_per_minute, notes, reviewed_at, attribution_required)
                           VALUES (%s,%s,%s,%s,%s,%s,%s,%s,now(),%s) ON CONFLICT (domain_pattern) DO NOTHING""", (dp, pub, conn_name, mode, state, ret, rpm, notes, attrib))
            out["permissions"].append(dp)
    conn.commit()
    # recorded robots decisions (checked 2026-11-06): the agency site and the airport disallow AI agents → search observation only
    for dp, note in (("*.tcatbus.com", "robots.txt disallows ClaudeBot/AI crawlers and the site returns 403 to automated agents; routes via the GTFS feed instead"),
                     ("*.flyithaca.com", "robots.txt disallows anthropic-ai/ClaudeBot; search-result observation only"),
                     ("parks.ny.gov", "robots.txt disallows anthropic-ai/ClaudeBot/Claude-Web and query-string listings; search-result observation only")):
        try:
            record_terms_check(conn, dp, access_mode="search_observation", robots_allows=False, note=note, terms_reference="robots.txt")
        except LookupError:
            pass
    inst = find_by_external_id(conn, "ipeds_unitid", CORNELL_UNITID)
    if not inst:
        raise LookupError("Cornell is not in the registry; run scripts/rebuild_from_repo.sh first")
    with conn.cursor() as cur:
        cur.execute("SELECT id FROM campuses WHERE institution_id=%s AND is_main LIMIT 1", (inst["id"],))
        campus = (cur.fetchone() or {}).get("id")
    for r in CORNELL_RULES:
        out["cornell"].append({"rule": r.key, "harvest_source_id": str(register_rule(conn, r, institution_id=inst["id"], campus_id=campus))})
    if cornell_only:
        return out
    with conn.cursor() as cur:
        cur.execute("SELECT id FROM places WHERE slug=%s", (ITHACA_PLACE_SLUG,))
        p = cur.fetchone()
    if not p:
        raise LookupError("place ithaca-ny missing; run the seed")
    for r in ITHACA_RULES:
        out["ithaca"].append({"rule": r.key, "harvest_source_id": str(register_rule(conn, r, institution_id=None, place_id=p["id"]))})
    # prune rules that are no longer part of the pilot source map (e.g. a host that turned out to disallow agents)
    keep = [r.key for r in CORNELL_RULES + ITHACA_RULES] + ["tcat_gtfs"]
    with conn.cursor() as cur:
        cur.execute("DELETE FROM harvest_sources WHERE NOT (rule_key = ANY(%s)) RETURNING rule_key", (keep,))
        out["pruned"] = [r["rule_key"] for r in cur.fetchall()]
    conn.commit()
    sid = register_source(conn, canonical_url=TCAT_GTFS_URL, institution_id=None, campus_id=None, source_kind="feed", publisher="TCAT (Tompkins Consolidated Area Transit)",
                          reliability="official", source_family="harvest:tcat_gtfs", place_id=p["id"], refresh_interval_hours=24 * 30)
    with conn.cursor() as cur:
        cur.execute("""INSERT INTO harvest_sources (source_id, rule_key, entity_type, topic_key, rule) VALUES (%s,'tcat_gtfs','bus_route','town_transit_local',%s::jsonb)
                       ON CONFLICT (source_id, rule_key) DO NOTHING""", (sid, json.dumps({"kind": "gtfs", "key": "tcat_gtfs", "source_url": TCAT_GTFS_URL, "entity_type": "bus_route", "topic_key": "town_transit_local"})))
    conn.commit()
    out["ithaca"].append({"rule": "tcat_gtfs", "source_id": str(sid)})
    return out


def main(argv: list[str]) -> int:
    from .config import get_settings
    from .db import connect
    if argv and argv[0] == "list":
        print(json.dumps({"cornell": [r.key for r in CORNELL_RULES], "ithaca": [r.key for r in ITHACA_RULES] + ["tcat_gtfs"]}, indent=2))
        return 0
    conn = connect(get_settings().database_url)
    try:
        print(json.dumps(register_all(conn), indent=2))
        return 0
    finally:
        conn.close()


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
