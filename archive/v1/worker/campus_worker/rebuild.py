"""Rebuild database state from committed files (specs/continuous-local-run.md R31, AT28).

Safe to run twice: every step is an upsert or is guarded by an existence check, and the
session-2 report (docs/research/cornell-transfer-housing-run.json) is never overwritten.
Replayed rows get new UUIDs; docs/research/rebuild-id-map.json records them.

    python -m campus_worker.rebuild            # full rebuild against DATABASE_URL
    python -m campus_worker.rebuild --verify   # print the AT28 counts only
"""
from __future__ import annotations

import hashlib
import json
import sys
from datetime import date, datetime, timezone
from pathlib import Path

from . import db as dbmod
from .config import REPO_ROOT, get_settings
from .registry import disambiguate, import_ipeds_hd
from .seed import seed_all

IPEDS_DIR = REPO_ROOT / "data" / "ipeds"
IPEDS_FILE = IPEDS_DIR / "HD2024_mirror_cshirky_a812f69.csv"
IPEDS_RELEASE = "HD2024_mirror_cshirky_a812f69"
IPEDS_RELEASE_DATE = date(2026, 9, 27)  # commit date of the mirror (data/ipeds/README.md)
EXPECTED_IPEDS_ROWS = 6072
TRANSFER_HOUSING_PATH = "/schools/cornell-university/housing/transfer-housing/"
ID_MAP = REPO_ROOT / "docs" / "research" / "rebuild-id-map.json"


def verify_checksum() -> str:
    sums = (IPEDS_DIR / "SHA256SUMS").read_text().split()
    expected = sums[0]
    h = hashlib.sha256()
    with IPEDS_FILE.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    actual = h.hexdigest()
    if actual != expected:
        raise SystemExit(f"IPEDS checksum mismatch: expected {expected} got {actual}; refusing to import")
    return actual


def counts(conn) -> dict:
    with conn.cursor() as cur:
        cur.execute("SELECT count(*) AS n FROM institutions")
        inst = cur.fetchone()["n"]
        cur.execute("SELECT count(*) AS n FROM institutions WHERE identity_status='pending_verification'")
        pending = cur.fetchone()["n"]
        cur.execute("""SELECT count(*) AS n FROM questions q JOIN institution_external_ids e ON e.institution_id=q.institution_id
                       WHERE e.system_name='ipeds_unitid' AND e.external_id='190415'""")
        questions = cur.fetchone()["n"]
        cur.execute("""SELECT count(*) AS n, count(*) FILTER (WHERE evidence_category='estimate') AS est FROM claims c
                       JOIN institution_external_ids e ON e.institution_id=c.institution_id WHERE e.system_name='ipeds_unitid' AND e.external_id='190415'""")
        r = cur.fetchone()
        claims, est = r["n"], r["est"]
        cur.execute("SELECT count(*) AS n FROM page_versions v JOIN pages p ON p.id=v.page_id WHERE p.path=%s AND p.status='held'", (TRANSFER_HOUSING_PATH,))
        held_versions = cur.fetchone()["n"]
        cur.execute("SELECT max(version) AS v FROM schema_migrations")
        mig = cur.fetchone()["v"]
    return {"institutions": inst, "pending_verification": pending, "cornell_disambiguation": len(disambiguate(conn, "cornell")),
            "cornell_questions": questions, "cornell_claims": claims, "cornell_claims_estimate": est,
            "transfer_housing_held_versions": held_versions, "migration": mig}


def rebuild(conn) -> dict:
    out = {"replayed_at": datetime.now(timezone.utc).isoformat(), "steps": []}
    applied = dbmod.migrate(conn)
    out["steps"].append({"migrate": applied})
    out["steps"].append({"seed": seed_all(conn)})
    sha = verify_checksum()
    with conn.cursor() as cur:
        # any release label counts: the fixture seed re-labels Cornell's row, so the registry is "populated" when ≥ 6,072 UNITIDs exist
        cur.execute("SELECT count(*) AS n FROM institution_external_ids WHERE system_name='ipeds_unitid'")
        already = cur.fetchone()["n"]
    if already >= EXPECTED_IPEDS_ROWS:
        out["steps"].append({"ipeds_import": {"sha256": sha, "skipped": f"release {IPEDS_RELEASE} already imported ({already} rows); nothing to change"}})
    else:
        res = import_ipeds_hd(conn, IPEDS_FILE, release=IPEDS_RELEASE, release_date=IPEDS_RELEASE_DATE)
        out["steps"].append({"ipeds_import": {"sha256": sha, "created": res.created, "updated": res.updated, "systems": res.systems, "skipped": len(res.skipped)}})
    # Session-2 replay, guarded: only when the held transfer-housing page has no version yet.
    with conn.cursor() as cur:
        cur.execute("SELECT count(*) AS n FROM page_versions v JOIN pages p ON p.id=v.page_id WHERE p.path=%s", (TRANSFER_HOUSING_PATH,))
        have = cur.fetchone()["n"]
    if have:
        out["steps"].append({"session2_replay": "skipped: page version already present"})
    else:
        from . import session_run
        report = session_run.run_cornell_transfer_housing(render=False, report_path=ID_MAP)
        out["steps"].append({"session2_replay": {"claims": report["claims"], "discovery": {k: report["discovery"][k] for k in ("stored", "clusters_created")},
                                                 "page_id": report["draft"]["page_id"], "version_id": report["draft"]["version_id"], "gate": report["draft"]["gate"]["status"]}})
        idmap = json.loads(ID_MAP.read_text())
        idmap["note"] = ("Replay of the 2026-11-04 session-2 run from committed files (R31). Rows carry new UUIDs; evidence stays 'estimate'; "
                         "the original report docs/research/cornell-transfer-housing-run.json is unchanged.")
        ID_MAP.write_text(json.dumps(idmap, indent=2, default=str))
    out["counts"] = counts(conn)
    return out


def main(argv: list[str]) -> int:
    settings = get_settings()
    conn = dbmod.connect(settings.database_url)
    try:
        if argv and argv[0] == "--verify":
            print(json.dumps(counts(conn), indent=2))
            return 0
        print(json.dumps(rebuild(conn), indent=2, default=str))
        return 0
    finally:
        conn.close()


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
