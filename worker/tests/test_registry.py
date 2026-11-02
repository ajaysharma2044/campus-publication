from datetime import date
from pathlib import Path
import pytest
from campus_worker import registry
from campus_worker.config import FIXTURES_DIR
from campus_worker.types import CampusRecord

CSV = FIXTURES_DIR / "ipeds" / "hd_synthetic.csv"


def test_import_is_idempotent_and_release_dated(clean_conn):
    r1 = registry.import_ipeds_hd(clean_conn, CSV, release="SYNTHETIC_HD", release_date=date(2026, 1, 1), mark_fixture=True)
    assert r1.created == 5 and r1.systems == 1
    r2 = registry.import_ipeds_hd(clean_conn, CSV, release="SYNTHETIC_HD", release_date=date(2026, 1, 1), mark_fixture=True)
    assert r2.created == 0 and r2.updated == 5
    with clean_conn.cursor() as cur:
        cur.execute("SELECT source_release FROM institution_external_ids WHERE external_id='900003'")
        assert cur.fetchone()["source_release"] == "SYNTHETIC_HD"
        cur.execute("SELECT count(*) AS n FROM institutions WHERE identity_status='synthetic_fixture'")
        assert cur.fetchone()["n"] == 5


def test_same_name_schools_are_distinct_entities(clean_conn):
    registry.import_ipeds_hd(clean_conn, CSV, release="SYNTHETIC_HD", release_date=date(2026, 1, 1), mark_fixture=True)
    cands = registry.disambiguate(clean_conn, "Fixture State University")
    ids = {c["id"] for c in cands}
    assert len(ids) >= 2  # two campuses with the same name + the system office
    a = registry.find_by_external_id(clean_conn, "ipeds_unitid", "900001")
    b = registry.find_by_external_id(clean_conn, "ipeds_unitid", "900004")
    assert a["id"] != b["id"] and a["canonical_name"] == b["canonical_name"]


def test_system_is_not_a_campus(clean_conn):
    registry.import_ipeds_hd(clean_conn, CSV, release="SYNTHETIC_HD", release_date=date(2026, 1, 1), mark_fixture=True)
    system = registry.find_by_external_id(clean_conn, "ipeds_unitid", "900002")
    assert system["is_system"] is True
    with pytest.raises(ValueError):
        registry.ensure_campus(clean_conn, system["id"], CampusRecord(name="HQ", slug="hq"))
    registry.link_system_membership(clean_conn, "900001", "900002")
    with pytest.raises(ValueError):
        registry.link_system_membership(clean_conn, "900004", "900001")  # a campus cannot be a parent system


def test_rename_preserves_id_and_records_alias(clean_conn, tmp_path):
    registry.import_ipeds_hd(clean_conn, CSV, release="SYNTHETIC_HD", release_date=date(2026, 1, 1), mark_fixture=True)
    before = registry.find_by_external_id(clean_conn, "ipeds_unitid", "900005")["id"]
    renamed = tmp_path / "hd2.csv"
    renamed.write_text(CSV.read_text().replace("Lakeside College", "Lakeside University"))
    registry.import_ipeds_hd(clean_conn, renamed, release="SYNTHETIC_HD2", release_date=date(2027, 1, 1), mark_fixture=True)
    after = registry.find_by_external_id(clean_conn, "ipeds_unitid", "900005")
    assert after["id"] == before and after["canonical_name"] == "Lakeside University"
    with clean_conn.cursor() as cur:
        cur.execute("SELECT alias FROM institution_aliases WHERE institution_id=%s AND alias_type='former_name'", (before,))
        assert cur.fetchone()["alias"] == "Lakeside College"


def test_missing_columns_rejected(clean_conn, tmp_path):
    bad = tmp_path / "bad.csv"
    bad.write_text("UNITID,INSTNM\n1,X\n")
    with pytest.raises(ValueError, match="missing columns"):
        registry.import_ipeds_hd(clean_conn, bad, release="x", release_date=date(2026, 1, 1))


def test_school_configs_seed_and_topic_applicability(clean_conn):
    from campus_worker.seed import seed_all
    out = seed_all(clean_conn)
    assert len(out["schools"]) == 2
    cornell = registry.find_by_external_id(clean_conn, "ipeds_unitid", "190415")
    riverbend = registry.find_by_external_id(clean_conn, "ipeds_unitid", "900003")
    assert cornell["identity_status"] == "pending_verification"
    assert riverbend["identity_status"] == "synthetic_fixture"
    assert registry.topic_applicability(clean_conn, cornell["id"], "housing") == "applicable"
    assert registry.topic_applicability(clean_conn, riverbend["id"], "housing") == "not_applicable"
    assert registry.topic_applicability(clean_conn, riverbend["id"], "dining") == "unknown"
