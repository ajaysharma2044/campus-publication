"""Institution registry: IPEDS-style import, identity rules, lookups.

The importer is header-driven and release-dated. It accepts the IPEDS HD (institutional
characteristics) file layout by column name (UNITID, INSTNM, CITY, STABBR, CONTROL, SECTOR,
ICLEVEL, WEBADDR, IALIAS, F1SYSTYP, F1SYSNAM) and never infers an institution from a name
match alone. A row is either a campus-bearing institution or a system record; systems are
created as institutions with is_system = TRUE and never get campuses.

Live IPEDS downloads are not possible from this environment (nces.ed.gov blocked). The import
therefore runs on owner-supplied files or on the labeled synthetic fixture.
"""
from __future__ import annotations

import csv
import re
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from uuid import UUID

import psycopg

from .types import InstitutionRecord, CampusRecord, SchoolConfigRecord

# IPEDS code books (HD file). Kept explicit so a new release can be diffed.
IPEDS_CONTROL = {"1": "public", "2": "private_nonprofit", "3": "private_forprofit", "-3": "unknown"}
# SECTOR: 1 public 4yr+, 2 private np 4yr+, 3 private fp 4yr+, 4 public 2yr, 5 private np 2yr,
# 6 private fp 2yr, 7 public <2yr, 8 private np <2yr, 9 private fp <2yr, 0 administrative unit
IPEDS_SECTOR_TYPE = {
    "0": "system",
    "1": "university",
    "2": "university",
    "3": "college",
    "4": "community_college",
    "5": "college",
    "6": "college",
    "7": "technical_college",
    "8": "technical_college",
    "9": "technical_college",
}


def slugify(name: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    return re.sub(r"-{2,}", "-", s) or "institution"


@dataclass
class ImportResult:
    created: int = 0
    updated: int = 0
    systems: int = 0
    skipped: list[str] = None

    def __post_init__(self):
        self.skipped = self.skipped or []


def row_to_record(row: dict, release: str) -> InstitutionRecord | None:
    """Translate one IPEDS HD row into an InstitutionRecord. Returns None if unusable."""
    unitid = (row.get("UNITID") or "").strip()
    name = (row.get("INSTNM") or "").strip()
    if not unitid or not name:
        return None
    sector = (row.get("SECTOR") or "").strip()
    itype = IPEDS_SECTOR_TYPE.get(sector, "other")
    is_system = itype == "system"
    web = (row.get("WEBADDR") or "").strip().lower()
    web = re.sub(r"^https?://", "", web).split("/")[0] or None
    aliases = [a.strip() for a in re.split(r"[|;]", row.get("IALIAS") or "") if a.strip()]
    return InstitutionRecord(
        canonical_name=name,
        slug=f"{slugify(name)}-{unitid}",  # unitid suffix guarantees uniqueness across same-name schools
        institution_type=itype,
        control=IPEDS_CONTROL.get((row.get("CONTROL") or "").strip(), "unknown"),
        is_system=is_system,
        state_code=(row.get("STABBR") or "").strip() or None,
        city=(row.get("CITY") or "").strip() or None,
        primary_domain=web,
        identity_status="pending_verification",
        external_ids={"ipeds_unitid": unitid},
        aliases=aliases,
    )


def upsert_institution(
    conn: psycopg.Connection,
    rec: InstitutionRecord,
    *,
    source_release: str | None,
    source_release_date: date | None,
) -> tuple[UUID, bool]:
    """Insert or update by external id (never by name). Returns (id, created)."""
    with conn.cursor() as cur:
        inst_id = None
        for system_name, ext in rec.external_ids.items():
            cur.execute(
                "SELECT institution_id FROM institution_external_ids WHERE system_name=%s AND external_id=%s",
                (system_name, ext),
            )
            r = cur.fetchone()
            if r:
                inst_id = r["institution_id"]
                break
        created = inst_id is None
        if created:
            cur.execute(
                """INSERT INTO institutions (canonical_name, slug, institution_type, control, is_system,
                   country_code, state_code, city, primary_domain, identity_status)
                   VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) RETURNING id""",
                (
                    rec.canonical_name, rec.slug, rec.institution_type, rec.control, rec.is_system,
                    rec.country_code, rec.state_code, rec.city, rec.primary_domain, rec.identity_status,
                ),
            )
            inst_id = cur.fetchone()["id"]
        else:
            # Preserve history: a renamed institution keeps its id; old name becomes an alias.
            cur.execute("SELECT canonical_name FROM institutions WHERE id=%s", (inst_id,))
            old = cur.fetchone()["canonical_name"]
            if old != rec.canonical_name:
                cur.execute(
                    """INSERT INTO institution_aliases (institution_id, alias, alias_type, valid_to)
                       VALUES (%s,%s,'former_name',CURRENT_DATE) ON CONFLICT DO NOTHING""",
                    (inst_id, old),
                )
            cur.execute(
                """UPDATE institutions SET canonical_name=%s, institution_type=%s, control=%s, is_system=%s,
                   state_code=%s, city=%s, primary_domain=COALESCE(%s, primary_domain), updated_at=now()
                   WHERE id=%s""",
                (rec.canonical_name, rec.institution_type, rec.control, rec.is_system,
                 rec.state_code, rec.city, rec.primary_domain, inst_id),
            )
        for system_name, ext in rec.external_ids.items():
            cur.execute(
                """INSERT INTO institution_external_ids (institution_id, system_name, external_id,
                   source_release, source_release_date, retrieved_at)
                   VALUES (%s,%s,%s,%s,%s,now())
                   ON CONFLICT (system_name, external_id) DO UPDATE
                   SET source_release=EXCLUDED.source_release, source_release_date=EXCLUDED.source_release_date,
                       retrieved_at=now()""",
                (inst_id, system_name, ext, source_release, source_release_date),
            )
        for alias in rec.aliases:
            cur.execute(
                """INSERT INTO institution_aliases (institution_id, alias, alias_type)
                   VALUES (%s,%s,'abbreviation') ON CONFLICT DO NOTHING""",
                (inst_id, alias),
            )
        if rec.primary_domain:
            cur.execute(
                """INSERT INTO institution_aliases (institution_id, alias, alias_type)
                   VALUES (%s,%s,'domain') ON CONFLICT DO NOTHING""",
                (inst_id, rec.primary_domain),
            )
        return inst_id, created


def import_ipeds_hd(
    conn: psycopg.Connection,
    path: Path,
    *,
    release: str,
    release_date: date,
    mark_fixture: bool = False,
) -> ImportResult:
    """Import an IPEDS HD-layout CSV. `release` names the exact file (e.g. 'HD2024'); it is
    stored with every external id so coverage limitations can be stated truthfully."""
    res = ImportResult()
    with path.open(newline="", encoding="utf-8-sig") as fh:
        reader = csv.DictReader(fh)
        required = {"UNITID", "INSTNM", "SECTOR", "CONTROL", "STABBR", "CITY"}
        missing = required - set(reader.fieldnames or [])
        if missing:
            raise ValueError(f"IPEDS file missing columns: {sorted(missing)}")
        for row in reader:
            rec = row_to_record(row, release)
            if rec is None:
                res.skipped.append(row.get("UNITID") or "?")
                continue
            if mark_fixture:
                rec = rec.model_copy(update={"identity_status": "synthetic_fixture"})
            _, created = upsert_institution(conn, rec, source_release=release, source_release_date=release_date)
            if rec.is_system:
                res.systems += 1
            if created:
                res.created += 1
            else:
                res.updated += 1
    conn.commit()
    return res


def link_system_membership(conn: psycopg.Connection, member_unitid: str, system_unitid: str) -> None:
    """Attach a campus-bearing institution to a system record. Both must already exist."""
    with conn.cursor() as cur:
        cur.execute("SELECT institution_id FROM institution_external_ids WHERE system_name='ipeds_unitid' AND external_id=%s", (member_unitid,))
        m = cur.fetchone()
        cur.execute("SELECT i.id, i.is_system FROM institution_external_ids e JOIN institutions i ON i.id=e.institution_id WHERE e.system_name='ipeds_unitid' AND e.external_id=%s", (system_unitid,))
        s = cur.fetchone()
        if not m or not s:
            raise LookupError("member or system not found")
        if not s["is_system"]:
            raise ValueError("target is not a system record; a campus cannot be a parent system")
        cur.execute("UPDATE institutions SET parent_system_id=%s WHERE id=%s", (s["id"], m["institution_id"]))
    conn.commit()


def ensure_campus(conn: psycopg.Connection, institution_id: UUID, campus: CampusRecord) -> UUID:
    with conn.cursor() as cur:
        cur.execute("SELECT is_system FROM institutions WHERE id=%s", (institution_id,))
        r = cur.fetchone()
        if r is None:
            raise LookupError("institution not found")
        if r["is_system"]:
            raise ValueError("a university system is not a campus and cannot own campuses")
        cur.execute(
            """INSERT INTO campuses (institution_id, name, slug, is_main, city, state_code, timezone, status)
               VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
               ON CONFLICT (institution_id, slug) DO UPDATE SET name=EXCLUDED.name, is_main=EXCLUDED.is_main
               RETURNING id""",
            (institution_id, campus.name, campus.slug, campus.is_main, campus.city, campus.state_code,
             campus.timezone, campus.status),
        )
        cid = cur.fetchone()["id"]
    conn.commit()
    return cid


def upsert_school_config(
    conn: psycopg.Connection, institution_id: UUID, campus_id: UUID | None, cfg: SchoolConfigRecord
) -> UUID:
    import json

    with conn.cursor() as cur:
        cur.execute(
            """INSERT INTO school_configs (institution_id, campus_id, locale, timezone, academic_calendar,
               source_domains, permitted_connectors, audiences, coverage_status, is_underserved, refresh_policy)
               VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s::jsonb)
               ON CONFLICT (institution_id, campus_id) DO UPDATE SET
                 locale=EXCLUDED.locale, timezone=EXCLUDED.timezone, academic_calendar=EXCLUDED.academic_calendar,
                 source_domains=EXCLUDED.source_domains, permitted_connectors=EXCLUDED.permitted_connectors,
                 audiences=EXCLUDED.audiences, coverage_status=EXCLUDED.coverage_status,
                 is_underserved=EXCLUDED.is_underserved, refresh_policy=EXCLUDED.refresh_policy, updated_at=now()
               RETURNING id""",
            (institution_id, campus_id, cfg.locale, cfg.timezone, cfg.academic_calendar, cfg.source_domains,
             cfg.permitted_connectors, cfg.audiences, cfg.coverage_status, cfg.is_underserved,
             json.dumps(cfg.refresh_policy)),
        )
        cfg_id = cur.fetchone()["id"]
        cur.execute("SELECT id, key FROM topics")
        topic_ids = {r["key"]: r["id"] for r in cur.fetchall()}
        for key, tid in topic_ids.items():
            state = cfg.topic_applicability.get(key, "unknown")
            cur.execute(
                """INSERT INTO school_topic_applicability (school_config_id, topic_id, applicability, rationale)
                   VALUES (%s,%s,%s,%s)
                   ON CONFLICT (school_config_id, topic_id) DO UPDATE SET applicability=EXCLUDED.applicability,
                   rationale=EXCLUDED.rationale""",
                (cfg_id, tid, state, cfg.topic_rationale.get(key)),
            )
    conn.commit()
    return cfg_id


def find_by_external_id(conn: psycopg.Connection, system_name: str, external_id: str) -> dict | None:
    with conn.cursor() as cur:
        cur.execute(
            """SELECT i.* FROM institutions i JOIN institution_external_ids e ON e.institution_id=i.id
               WHERE e.system_name=%s AND e.external_id=%s""",
            (system_name, external_id),
        )
        return cur.fetchone()


def disambiguate(conn: psycopg.Connection, text: str) -> list[dict]:
    """Return candidate institutions for a free-text name. Never auto-selects: callers must
    resolve ambiguity explicitly (SPEC §07: a similarly named school is not the same entity)."""
    with conn.cursor() as cur:
        cur.execute(
            """SELECT DISTINCT i.id, i.canonical_name, i.city, i.state_code, i.institution_type, i.is_system
               FROM institutions i LEFT JOIN institution_aliases a ON a.institution_id=i.id
               WHERE lower(i.canonical_name) LIKE %s OR lower(a.alias) LIKE %s
               ORDER BY i.canonical_name LIMIT 25""",
            (f"%{text.lower()}%", f"%{text.lower()}%"),
        )
        return cur.fetchall()


def topic_applicability(conn: psycopg.Connection, institution_id: UUID, topic_key: str) -> str:
    with conn.cursor() as cur:
        cur.execute(
            """SELECT sta.applicability FROM school_topic_applicability sta
               JOIN school_configs sc ON sc.id=sta.school_config_id
               JOIN topics t ON t.id=sta.topic_id
               WHERE sc.institution_id=%s AND t.key=%s LIMIT 1""",
            (institution_id, topic_key),
        )
        r = cur.fetchone()
        return r["applicability"] if r else "unknown"
