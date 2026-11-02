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
    permissions.seed_defaults(conn)
    out = {"permissions": "seeded", "schools": []}
    for p in sorted((FIXTURES_DIR / "school_configs").glob("*.yaml")):
        out["schools"].append(seed_school(conn, p))
    return out
