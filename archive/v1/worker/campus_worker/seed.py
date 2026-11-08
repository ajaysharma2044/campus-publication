"""Seed permissions and school configurations from labeled fixture files."""
from __future__ import annotations

from pathlib import Path

import psycopg
import yaml

from . import permissions
from .config import FIXTURES_DIR
from .registry import ensure_campus, upsert_institution, upsert_school_config
from .types import CampusRecord, InstitutionRecord, SchoolConfigRecord


def load_school_config_file(path: Path) -> dict:
    with path.open() as fh:
        return yaml.safe_load(fh)


def seed_school(conn: psycopg.Connection, path: Path) -> dict:
    doc = load_school_config_file(path)
    inst = InstitutionRecord(**doc["institution"])
    inst_id, created = upsert_institution(conn, inst, source_release="fixture:" + path.name, source_release_date=None)
    campus = CampusRecord(**doc["campus"])
    campus_id = ensure_campus(conn, inst_id, campus)
    cfg = SchoolConfigRecord(**doc["config"])
    cfg_id = upsert_school_config(conn, inst_id, campus_id, cfg)
    return {"institution_id": str(inst_id), "campus_id": str(campus_id), "school_config_id": str(cfg_id),
            "created": created, "identity_status": inst.identity_status, "file": path.name}


def seed_all(conn: psycopg.Connection) -> dict:
    from . import taxonomy
    permissions.seed_defaults(conn)
    out = {"permissions": "seeded", "topics": taxonomy.seed(conn), "places": seed_places(conn), "schools": []}
    for p in sorted((FIXTURES_DIR / "school_configs").glob("*.yaml")):
        out["schools"].append(seed_school(conn, p))
    return out


PLACES = [
    # slug, name, kind, state, parent_slug, attributes — Ithaca and Tompkins County, NY (continuous-local-run R34)
    ("tompkins-county-ny", "Tompkins County", "county", "NY", None, {"fips": "36109"}),
    ("ithaca-ny", "Ithaca", "city", "NY", "tompkins-county-ny", {"county": "Tompkins", "transit_agency": "TCAT", "airport": "ITH"}),
]


def seed_places(conn: psycopg.Connection) -> dict:
    import json as _json
    created = 0
    with conn.cursor() as cur:
        for slug, name, kind, state, parent, attrs in PLACES:
            parent_id = None
            if parent:
                cur.execute("SELECT id FROM places WHERE slug=%s", (parent,))
                r = cur.fetchone()
                parent_id = r["id"] if r else None
            cur.execute(
                """INSERT INTO places (name, slug, kind, state_code, parent_place_id, attributes) VALUES (%s,%s,%s,%s,%s,%s::jsonb)
                   ON CONFLICT (slug) DO UPDATE SET name=EXCLUDED.name, kind=EXCLUDED.kind, parent_place_id=EXCLUDED.parent_place_id, attributes=EXCLUDED.attributes
                   RETURNING (xmax = 0) AS inserted""",
                (name, slug, kind, state, parent_id, _json.dumps(attrs)),
            )
            created += 1 if cur.fetchone()["inserted"] else 0
        # Cornell's town
        cur.execute("""UPDATE institutions i SET place_id = p.id FROM places p, institution_external_ids e
                       WHERE p.slug='ithaca-ny' AND e.institution_id=i.id AND e.system_name='ipeds_unitid' AND e.external_id='190415' AND i.place_id IS NULL""")
    conn.commit()
    return {"created": created, "total": len(PLACES)}
