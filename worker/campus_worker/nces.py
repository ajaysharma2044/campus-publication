"""NCES IPEDS identity verification (continuous-local-run R17/S6; AT15; SPEC §07).

Verifies a registry institution against the official HD release downloaded from nces.ed.gov: the UNITID must exist in
the release and the names must match; the release file's SHA-256 is stored with the external id and the institution's
identity_status becomes 'verified'. Never matches by name alone.

    python -m campus_worker.nces verify --zip <HD2024.zip> --unitid 190415
"""
from __future__ import annotations

import csv
import hashlib
import io
import json
import sys
import zipfile
from datetime import date, datetime, timezone
from pathlib import Path

import psycopg


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def read_hd_row(zip_path: Path, unitid: str) -> tuple[dict | None, str, int]:
    """Return (row, csv_name, row_count) for the UNITID from the HD csv inside the zip."""
    with zipfile.ZipFile(zip_path) as z:
        name = next(n for n in z.namelist() if n.lower().endswith(".csv"))
        raw = z.read(name)
    try:
        text = raw.decode("utf-8-sig")       # recent releases: UTF-8 with a byte-order mark
    except UnicodeDecodeError:
        text = raw.decode("cp1252", errors="replace").lstrip("\ufeff")  # older releases: Windows-1252
    reader = csv.DictReader(io.StringIO(text))
    reader.fieldnames = [f.strip().lstrip("\ufeff") for f in (reader.fieldnames or [])]
    found, n = None, 0
    for row in reader:
        n += 1
        if (row.get("UNITID") or "").strip() == unitid:
            found = row
    return found, name, n


def _norm(s: str) -> str:
    return " ".join((s or "").lower().replace("-", " ").split())


def verify(conn: psycopg.Connection, *, zip_path: Path, unitid: str, release: str) -> dict:
    sha = sha256_file(zip_path)
    row, csv_name, n = read_hd_row(zip_path, unitid)
    if not row:
        return {"verified": False, "reason": f"UNITID {unitid} not present in {csv_name} ({n} rows)", "sha256": sha}
    with conn.cursor() as cur:
        cur.execute("""SELECT i.id, i.canonical_name, i.city, i.state_code, i.identity_status FROM institutions i JOIN institution_external_ids e ON e.institution_id=i.id
                       WHERE e.system_name='ipeds_unitid' AND e.external_id=%s""", (unitid,))
        inst = cur.fetchone()
    if not inst:
        return {"verified": False, "reason": f"UNITID {unitid} not in the registry", "sha256": sha}
    name_ok = _norm(inst["canonical_name"]) == _norm(row.get("INSTNM", ""))
    city_ok = _norm(inst["city"] or "") == _norm(row.get("CITY", "")) and (inst["state_code"] or "").upper() == (row.get("STABBR") or "").upper()
    if not (name_ok and city_ok):
        return {"verified": False, "reason": "registry row does not match the NCES row", "registry": dict(inst), "nces": {k: row.get(k) for k in ("INSTNM", "CITY", "STABBR")}, "sha256": sha}
    note = json.dumps({"nces_release": release, "file": csv_name, "sha256": sha, "verified_at": datetime.now(timezone.utc).isoformat(), "rows": n})
    with conn.cursor() as cur:
        cur.execute("""UPDATE institution_external_ids SET source_release=%s, source_release_date=%s, retrieved_at=now() WHERE institution_id=%s AND system_name='ipeds_unitid' AND external_id=%s""",
                    (f"{release} (nces.ed.gov, sha256={sha[:16]}…)", date.today(), inst["id"], unitid))
        cur.execute("UPDATE institutions SET identity_status='verified', notes=COALESCE(notes,'') || %s, updated_at=now() WHERE id=%s", (" | NCES verification " + note, inst["id"]))
    conn.commit()
    return {"verified": True, "institution_id": str(inst["id"]), "canonical_name": inst["canonical_name"], "nces_name": row.get("INSTNM"), "sha256": sha, "release": release, "file": csv_name, "rows": n}


def main(argv: list[str]) -> int:
    from .config import get_settings
    from .db import connect
    if not argv or argv[0] != "verify":
        print(__doc__)
        return 2
    zip_path = Path(argv[argv.index("--zip") + 1])
    unitid = argv[argv.index("--unitid") + 1]
    release = argv[argv.index("--release") + 1] if "--release" in argv else zip_path.stem
    conn = connect(get_settings().database_url)
    try:
        print(json.dumps(verify(conn, zip_path=zip_path, unitid=unitid, release=release), indent=2, default=str))
        return 0
    finally:
        conn.close()


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
