"""Subscription-only bulk mode (owner decision 2026-11-07): the stages through parallel `claude -p` workers with a fake session runner:
extraction keeps only verbatim quotes, a usage limit pauses and resumes, STOP stops, articles get written, checked, verified and
published, and the practical-first ordering puts costs and deadlines ahead of the rest."""
from __future__ import annotations

import json
import re
from datetime import date, datetime, timedelta
from pathlib import Path

from campus_worker.bulk import batch_client as bc
from campus_worker.bulk import headless, plan as planmod, questions, rank, run
from tests.test_bulk import PAGE_TEXT, _seed, _seed_claims

PAIR_RE = re.compile(r"^- read (\S+) → write (\S+)$", re.M)


def _fake_runner(root: Path, *, limit_first: list | None = None):
    """Writes the output files a worker would write. Extraction: one verbatim money claim + one claim whose quote is not on the page.
    Writing / verifying: the batch fake responder over the packet text."""
    calls = {"n": 0}

    def runner(prompt: str, *, model: str, max_turns: int) -> headless.SessionResult:
        calls["n"] += 1
        if limit_first and limit_first.pop(0):
            return headless.SessionResult(1, "Claude AI usage limit reached. Your limit resets in 1 minute.", "", True, 0.1)
        for src, dst in PAIR_RE.findall(prompt):
            text = (root / src).read_text()
            out = root / dst
            if "/extract/" in dst:
                m = re.search(r"[^.]*\$6,872[^.]*\.", text)
                claims = [{"field": "rate.room.double", "value_type": "money", "value": 687200, "currency": "USD", "billing_period": "per_semester", "price_basis": "per_person", "academic_year": "2026-27",
                           "quote": m.group(0).strip() if m else "", "confidence": 0.9},
                          {"field": "fee.housing_application", "value_type": "money", "value": 0, "quote": "There is no fee to apply.", "confidence": 0.5}]
                out.write_text(json.dumps({"claims": claims, "entities": [{"name": "Barbara Fixture Hall", "entity_type": "residence_hall"}], "processes": []}))
            elif dst.endswith(".draft.json"):
                out.write_text(run._fake_responder(bc.BatchRequest("write:x", model, "", text, 10)))
            elif dst.endswith(".verdict.json"):
                out.write_text(run._fake_responder(bc.BatchRequest("verify:x", model, "", text, 10)))
        return headless.SessionResult(0, f"DONE {len(PAIR_RE.findall(prompt))} files", "", False, 0.2, 4, 0.05)

    runner.calls = calls
    return runner


def test_parse_reset_and_pause_resume(monkeypatch, tmp_path):
    monkeypatch.setattr(headless, "STOP_FILE", tmp_path / "STOP")   # the repo's own .run/STOP must not end the test early
    now = datetime(2026, 11, 7, 10, 0)
    assert headless.parse_reset("limit resets in 2 hours", now=now) == now + timedelta(hours=2)
    assert headless.parse_reset("Your limit resets at 3pm", now=now) == now.replace(hour=15, minute=0)
    assert headless.parse_reset("resets at 9:30am", now=now) == (now + timedelta(days=1)).replace(hour=9, minute=30)
    assert headless.parse_reset("nothing useful", now=now) is None
    clock = {"t": now}
    probes = {"n": 0}
    log = []

    def probe():
        probes["n"] += 1
        return probes["n"] >= 2   # first probe still limited, second clears

    p = headless.Pause(log=log.append, probe=probe, sleep=lambda s: clock.__setitem__("t", clock["t"] + timedelta(seconds=s)), now=lambda: clock["t"])
    p.trigger("usage limit reached, resets in 1 minute")
    assert p.until == now + timedelta(minutes=1) and p.pauses == 1
    p.wait_if_paused()
    assert p.until is None and probes["n"] == 2 and any("resuming" in l for l in log)


def test_extraction_through_fake_workers_keeps_verbatim_quotes_and_pauses_once(clean_conn, migrated_url, tmp_path, monkeypatch):
    inst, campus, topics, hall, sid, snap = _seed(clean_conn)
    monkeypatch.setattr(headless, "RUN_ROOT", tmp_path / "headless")
    monkeypatch.setattr(headless, "STOP_FILE", tmp_path / "STOP")
    monkeypatch.setattr(headless, "REPO_ROOT", tmp_path)
    runner = _fake_runner(tmp_path, limit_first=[True])
    clock = {"t": datetime(2026, 11, 7, 10, 0)}
    pause = headless.Pause(log=lambda m: None, probe=lambda: True, sleep=lambda s: clock.__setitem__("t", clock["t"] + timedelta(seconds=s)), now=lambda: clock["t"])
    out = headless.extract_stage(school="fixture-state", run_id="t-extract", workers=2, chunk_size=5, model="sonnet", pause=pause, log=lambda m: None, runner=runner, dsn=migrated_url)
    assert out["pending_at_start"] == 1 and out["counts"].get("pages") == 1 and out["counts"].get("claims") == 1 and out["counts"].get("dropped_no_quote") == 1
    assert pause.pauses == 1 and out["requeued"] == 1 and runner.calls["n"] == 2
    with clean_conn.cursor() as cur:
        cur.execute("SELECT field, value_number FROM claims WHERE institution_id=%s", (inst,))
        rows = cur.fetchall()
        cur.execute("SELECT extracted_at IS NOT NULL AS done, extraction_batch_id FROM fetch_snapshots WHERE id=%s", (snap,))
        done = cur.fetchone()
    assert [(r["field"], r["value_number"]) for r in rows] == [("rate.room.double", 687200)] and done["done"] and done["extraction_batch_id"].startswith("headless:t-extract:")
    assert (tmp_path / "headless" / "t-extract" / "progress.jsonl").exists()


def test_stop_file_stops_the_worker_loop(tmp_path, monkeypatch, migrated_url):
    monkeypatch.setattr(headless, "STOP_FILE", tmp_path / "STOP")
    (tmp_path / "STOP").write_text("")
    handled = []
    st = headless.run_chunks([[1], [2]], workers=2, handle=lambda c, conn: (handled.append(c) or (True, None)), pause=headless.Pause(log=lambda m: None, probe=lambda: True), log=lambda m: None, label="t", dsn=migrated_url)
    assert st["stopped"] and handled == []


def test_practical_first_ordering_puts_costs_and_deadlines_first():
    rows = [{"question": "Barbara Fixture Hall at Fixture State: rooms, cost and what to know", "page_type": "entity_guide", "topic_key": "housing"},
            {"question": "When is the housing application deadline at Fixture State?", "page_type": "question_guide", "topic_key": "housing"},
            {"question": "How do I change my major at Fixture State?", "page_type": "process_guide", "topic_key": "courses"},
            {"question": "Alumni reunion weekend dates", "page_type": "question_guide", "topic_key": "alumni_events"},
            {"question": "Do transfers have to live on campus?", "page_type": "question_guide", "topic_key": "housing", "audience": "transfer"}]
    ranks = [rank.practical_rank(r) for r in rows]
    assert ranks[1] == 0 and ranks[2] == 1 and ranks[4] == 1 and ranks[0] <= 1 and ranks[3] == 5


def test_articles_through_fake_workers_publish_and_report(clean_conn, migrated_url, tmp_path, monkeypatch):
    inst, campus, topics, hall, snap, ids = _seed_claims(clean_conn)
    questions.build(clean_conn, slug="fixture-state")
    rank.rank_all(clean_conn, institution_id=inst, official_domains=("example.edu",), today=date(2026, 11, 6))
    from campus_worker.render import site
    monkeypatch.setattr(site, "OUT_DEFAULT", tmp_path / "site")
    monkeypatch.setattr(headless, "RUN_ROOT", tmp_path / "headless")
    monkeypatch.setattr(headless, "STOP_FILE", tmp_path / "STOP")
    monkeypatch.setattr(headless, "REPO_ROOT", tmp_path)
    (tmp_path / "docs" / "digest").mkdir(parents=True)
    runner = _fake_runner(tmp_path)
    pause = headless.Pause(log=lambda m: None, probe=lambda: True)
    log = []
    rep = headless.articles_stage(school="fixture-state", run_id="t-art", workers=2, chunk_size=2, verify_chunk=3, model="sonnet", pause=pause, log=log.append, runner=runner, deploy_every=2, batch_limit=4, max_batches=1, deploy=False, dsn=migrated_url)
    assert rep["published"] >= 1 and rep["batches"] == 1 and rep["pages_per_hour"] > 0
    assert any(l.startswith("REPORT:") for l in log)
    with clean_conn.cursor() as cur:
        cur.execute("SELECT stage, count(*) AS n FROM bulk_pages WHERE run_id='t-art' GROUP BY stage")
        stages = {r["stage"]: r["n"] for r in cur.fetchall()}
        cur.execute("SELECT count(*) AS n FROM page_versions v JOIN pages p ON p.id=v.page_id WHERE p.institution_id=%s AND v.gate_status='passed' AND v.writer_model LIKE 'batch:headless:%%'", (inst,))
        n = cur.fetchone()["n"]
    assert stages.get("published", 0) >= 1 and n >= 1
    assert (tmp_path / "headless" / "t-art" / "progress.md").read_text().startswith("# Subscription-only run t-art")
    assert any("subscription-only run" in f.read_text() for f in (tmp_path / "docs" / "digest").glob("*.md"))


def test_steps_pass_stores_each_verbatim_step_as_a_quoted_claim_and_plans_the_how_to_page(clean_conn, migrated_url, tmp_path, monkeypatch):
    inst, campus, topics, hall, sid, snap = _seed(clean_conn)
    text = PAGE_TEXT + " How to apply: Step 1. Submit the housing application in the portal. Step 2. Pay the housing deposit. Step 3. 3.0 GPA minimum is required to stay."
    with clean_conn.cursor() as cur:
        cur.execute("UPDATE fetch_snapshots SET retained_text=%s, extracted_at=now() WHERE id=%s", (text, snap))
    clean_conn.commit()
    monkeypatch.setattr(headless, "RUN_ROOT", tmp_path / "headless")
    monkeypatch.setattr(headless, "STOP_FILE", tmp_path / "STOP")
    monkeypatch.setattr(headless, "REPO_ROOT", tmp_path)

    def runner(prompt: str, *, model: str, max_turns: int) -> headless.SessionResult:
        assert "STEP RULES" in prompt and "character for character" in prompt
        for src, dst in PAIR_RE.findall(prompt):
            (tmp_path / dst).write_text(json.dumps({"processes": [{"name": "apply for housing", "steps": ["1. Submit the housing application in the portal.", "Pay the housing deposit.", "3. 3.0 GPA minimum is required to stay.", "Move in on August 20."]},
                                                                  {"name": "cancel housing", "steps": ["Email the housing office."]}]}))
        return headless.SessionResult(0, "DONE 1", "", False, 0.1, 3, 0.02)

    pause = headless.Pause(log=lambda m: None, probe=lambda: True)
    out = headless.extract_stage(school="fixture-state", run_id="t-steps", workers=1, chunk_size=5, model="sonnet", pause=pause, log=lambda m: None, runner=runner, dsn=migrated_url, mode="steps")
    assert out["pending_at_start"] == 1 and out["counts"] == {"pages": 1, "processes": 1, "steps": 3, "dropped_no_quote": 2, "errors": 0}
    with clean_conn.cursor() as cur:
        cur.execute("SELECT c.field, c.value_text, cs.excerpt FROM claims c JOIN claim_sources cs ON cs.claim_id=c.id WHERE c.field LIKE 'process.apply_for_housing%%' AND c.superseded_by_id IS NULL ORDER BY c.field")
        rows = cur.fetchall()
        cur.execute("SELECT steps_extracted_at IS NOT NULL AS done, steps_batch_id FROM fetch_snapshots WHERE id=%s", (snap,))
        mark = cur.fetchone()
    assert [r["field"] for r in rows] == ["process.apply_for_housing", "process.apply_for_housing.step_01", "process.apply_for_housing.step_02", "process.apply_for_housing.step_03"]
    assert mark["done"] and mark["steps_batch_id"].startswith("headless:t-steps:")
    assert rows[1]["excerpt"] == rows[1]["value_text"] == "Submit the housing application in the portal." and rows[2]["value_text"] == "Pay the housing deposit."
    assert rows[3]["value_text"] == "3.0 GPA minimum is required to stay."   # the list marker goes, the decimal that opens the step stays
    assert rows[0]["excerpt"] == "Submit the housing application in the portal." and json.loads(rows[0]["value_text"])["steps"] == [r["value_text"] for r in rows[1:]]
    assert headless.extract_stage(school="fixture-state", run_id="t-steps", workers=1, chunk_size=5, model="sonnet", pause=pause, log=lambda m: None, runner=runner, dsn=migrated_url, mode="steps")["pending_at_start"] == 0
    # the question map plans the how-to page from the verbatim steps (a paraphrased step list alone plans none), with a title-sized query
    gen = questions.generate(clean_conn, institution_id=inst, school="Fixture State", town="Fixtown", year="2026-27")
    proc = [g for g in gen if g["page_type"] == "process_guide"]
    assert [g["primary_query"] for g in proc] == ["apply for housing Fixture State"] and proc[0]["facts"] == 3 and proc[0]["answer_key"] == "process:apply-for-housing"
    # a re-run of the page with a shorter list retires the stale tail: the procedure is one page's list, never a stitch of two
    with clean_conn.cursor() as cur:
        cur.execute("UPDATE fetch_snapshots SET steps_extracted_at=NULL WHERE id=%s", (snap,))
    clean_conn.commit()

    def shorter(prompt: str, *, model: str, max_turns: int) -> headless.SessionResult:
        for src, dst in PAIR_RE.findall(prompt):
            (tmp_path / dst).write_text(json.dumps({"processes": [{"name": "apply for housing", "steps": ["Submit the housing application in the portal.", "Pay the housing deposit."]}]}))
        return headless.SessionResult(0, "DONE 1", "", False, 0.1, 3, 0.02)

    headless.extract_stage(school="fixture-state", run_id="t-steps", workers=1, chunk_size=5, model="sonnet", pause=pause, log=lambda m: None, runner=shorter, dsn=migrated_url, mode="steps")
    with clean_conn.cursor() as cur:
        cur.execute("SELECT field, evidence_category FROM claims WHERE field LIKE 'process.apply_for_housing.step%%' ORDER BY field, created_at")
        states = [(r["field"][-7:], r["evidence_category"]) for r in cur.fetchall()]
    assert states == [("step_01", "verified_fact"), ("step_02", "verified_fact"), ("step_03", "stale")]
    gen = questions.generate(clean_conn, institution_id=inst, school="Fixture State", town="Fixtown", year="2026-27")
    assert [g["facts"] for g in gen if g["page_type"] == "process_guide"] == [2]
    assert questions.process_query("prepare to enter the United States as international faculty/staff", "Cornell") == "prepare to enter the United States Cornell"
    assert questions.process_query("complete Spring Housing Selection as a rising sophomore", "Cornell") == "complete Spring Housing Selection Cornell"
    assert questions.process_query("request an individual exemption from the residential requirement", "Cornell") == "request an individual exemption Cornell"
    assert questions.process_query("change my major", "Cornell") == "change my major Cornell"
    # the packet for that page opens with its own verbatim steps and carries no JSON procedure blob
    questions.build(clean_conn, slug="fixture-state")
    rank.rank_all(clean_conn, institution_id=inst, official_domains=("example.edu",), today=date(2026, 11, 6))
    planmod.plan_pages(clean_conn, institution_id=inst, limit=50, run_id="t-steps")
    with clean_conn.cursor() as cur:
        cur.execute("SELECT * FROM bulk_pages WHERE run_id='t-steps' AND plan->>'answer_key' = 'process:apply-for-housing'")
        page = cur.fetchone()
    assert page is not None
    gathered = planmod.gather(clean_conn, dict(page), institution_id=inst)
    fields = [f["field"] for f in gathered["facts"]]
    assert fields[:2] == ["process.apply_for_housing.step_01", "process.apply_for_housing.step_02"] and "process.apply_for_housing" not in fields
    assert all(not f["value"].startswith("{") for f in gathered["facts"]) and "process.apply_for_housing.step_03" not in fields


def test_steps_pass_marks_a_parse_failure_and_moves_on(clean_conn, migrated_url, tmp_path, monkeypatch):
    inst, campus, topics, hall, sid, snap = _seed(clean_conn)
    with clean_conn.cursor() as cur:
        cur.execute("UPDATE fetch_snapshots SET retained_text=%s, extracted_at=now() WHERE id=%s", (PAGE_TEXT + " Step 1. Apply online.", snap))
    clean_conn.commit()
    monkeypatch.setattr(headless, "RUN_ROOT", tmp_path / "headless")
    monkeypatch.setattr(headless, "STOP_FILE", tmp_path / "STOP")
    monkeypatch.setattr(headless, "REPO_ROOT", tmp_path)

    def garbled(prompt: str, *, model: str, max_turns: int) -> headless.SessionResult:
        for src, dst in PAIR_RE.findall(prompt):
            (tmp_path / dst).write_text("I could not find any procedures on this page, sorry.")
        return headless.SessionResult(0, "DONE 1", "", False, 0.1, 3, 0.02)

    out = headless.extract_stage(school="fixture-state", run_id="t-steps-err", workers=1, chunk_size=5, model="sonnet", pause=headless.Pause(log=lambda m: None, probe=lambda: True), log=lambda m: None, runner=garbled, dsn=migrated_url, mode="steps")
    assert out["counts"]["errors"] == 1 and out["counts"].get("steps", 0) == 0
    with clean_conn.cursor() as cur:
        cur.execute("SELECT steps_extracted_at IS NOT NULL AS done, steps_batch_id FROM fetch_snapshots WHERE id=%s", (snap,))
        mark = cur.fetchone()
        cur.execute("SELECT count(*) AS n FROM claims WHERE field LIKE 'process.%%' AND institution_id=%s", (inst,))
        n = cur.fetchone()["n"]
    assert mark["done"] and mark["steps_batch_id"].endswith(":error") and n == 0   # marked, recoverable by clearing the marker, nothing stored
