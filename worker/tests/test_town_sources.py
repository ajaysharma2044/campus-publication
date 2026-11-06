"""GTFS collector and onboarding rules (continuous-local-run R34; AT34 support)."""
import io
import zipfile

from campus_worker import onboard_rules
from campus_worker.collectors import gtfs
from campus_worker.seed import seed_all


def _zip(files: dict[str, str]) -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        for n, c in files.items():
            z.writestr(n, c)
    return buf.getvalue()


def test_gtfs_routes_parse_and_store_place_scoped(clean_conn):
    seed_all(clean_conn)
    with clean_conn.cursor() as cur:
        cur.execute("SELECT id FROM places WHERE slug='ithaca-ny'")
        place_id = cur.fetchone()["id"]
    z = _zip({"agency.txt": "agency_id,agency_name,agency_url,agency_timezone\n1,Fixture Transit,https://transit.example.invalid,America/New_York\n",
              "routes.txt": "route_id,agency_id,route_short_name,route_long_name,route_type,route_color\n10,1,10,Commons - Campus (FIXTURE),3,FF0000\n30,1,30,Commons - Airport (FIXTURE),3,00FF00\n"})
    routes = gtfs.parse_routes(z)
    assert [r["slug"] for r in routes] == ["route-10", "route-30"] and routes[1]["attributes"]["agency"] == "Fixture Transit"
    res = gtfs.store_routes(clean_conn, routes, place_id=place_id, source_url="https://transit.example.invalid/gtfs.zip", source_id=None)
    assert res["created"] == 2 and res["found"] == 2
    res2 = gtfs.store_routes(clean_conn, routes[:1], place_id=place_id, source_url="https://transit.example.invalid/gtfs.zip", source_id=None)
    assert res2["updated"] == 1 and res2["deactivated"] == 1
    with clean_conn.cursor() as cur:
        cur.execute("SELECT name, institution_id, place_id, status FROM entities WHERE entity_type='bus_route' ORDER BY slug")
        rows = cur.fetchall()
    assert rows[0]["name"] == "Route 10: Commons - Campus (FIXTURE)" and all(r["institution_id"] is None and r["place_id"] == place_id for r in rows)
    assert [r["status"] for r in rows] == ["active", "inactive"]


def test_onboarding_rules_are_well_formed():
    keys = [r.key for r in onboard_rules.CORNELL_RULES + onboard_rules.ITHACA_RULES]
    assert len(keys) == len(set(keys))
    for r in onboard_rules.CORNELL_RULES:
        assert r.source_url.startswith("https://") and "cornell.edu" in r.source_url and r.topic_key in ("housing", "dining", "services")
    for r in onboard_rules.ITHACA_RULES:
        assert r.topic_key.startswith("town_") and r.entity_type in ("park", "town_service")
    assert onboard_rules.TCAT_GTFS_URL.startswith("https://realtimetcatbus.availtec.com/")
