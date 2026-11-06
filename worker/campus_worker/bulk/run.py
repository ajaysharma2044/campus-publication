"""Bulk-mode orchestration and CLI (specs/bulk-mode.md): dossier (crawl → extract → assemble → questions → rank) and the article run
(plan → gather → write → check → verify → publish), chunked batches, resume from the database, a daily spend cap, and a report.

    python -m campus_worker.bulk crawl     --school cornell-university [--dry-run] [--hosts a,b] [--sections housing,dining]
    python -m campus_worker.bulk extract   --school cornell-university [--limit 400] [--dry-run | --fake]
    python -m campus_worker.bulk dossier   --school cornell-university          # assemble docs/dossiers/<school>/ + question map + ranking
    python -m campus_worker.bulk plan      --school cornell-university --limit 20 [--json]
    python -m campus_worker.bulk run       --school cornell-university --limit 20 [--dry-run | --fake] [--resume] [--chunk 500] [--deploy]
    python -m campus_worker.bulk status    --school cornell-university
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from uuid import UUID

import psycopg

from ..config import REPO_ROOT, get_settings
from ..db import connect
from . import check as checkmod
from . import crawl as crawlmod
from . import dossier as dossiermod
from . import extract as extractmod
from . import plan as planmod
from . import questions as questionsmod
from . import rank as rankmod
from . import verify as verifymod
from . import write as writemod
from .batch_client import AnthropicBatchClient, BatchRequest, FakeBatchClient, estimate_minor, usage_minor
from .util import json_default

RUNS_DIR = REPO_ROOT / "build" / "runs" / "bulk"
DEFAULT_CAP_USD = 25.0


class SpendCapExceeded(Exception):
    pass


def daily_cap_minor() -> int:
    return int(float(os.environ.get("CAMPUS_API_DAILY_CAP_USD") or DEFAULT_CAP_USD) * 100)


def spent_today_minor(conn: psycopg.Connection) -> int:
    with conn.cursor() as cur:
        cur.execute("SELECT COALESCE(SUM(COALESCE(actual_cost_minor, est_cost_minor)), 0) AS n FROM bulk_batches WHERE submitted_at >= date_trunc('day', now()) AND status <> 'failed'")
        return int(cur.fetchone()["n"])


def _school(conn: psycopg.Connection, slug: str) -> dict:
    with conn.cursor() as cur:
        cur.execute("SELECT id, canonical_name, slug FROM institutions WHERE slug=%s", (slug,))
        row = cur.fetchone()
        if not row:
            raise SystemExit(f"unknown school slug {slug}")
        cur.execute("SELECT id FROM places")
        places = [r["id"] for r in cur.fetchall()]
    return dict(row) | {"place_ids": places}


def _client(settings, args):
    if getattr(args, "fake", False):
        return FakeBatchClient(_fake_responder)
    if getattr(args, "dry_run", False):
        return None
    if settings.anthropic_api_key_present:
        return AnthropicBatchClient()
    return None


def _fake_responder(req: BatchRequest) -> str:
    """Deterministic replies for tests: extraction returns nothing, writing echoes the first facts, verifying supports them."""
    if req.custom_id.startswith("extract:"):
        return json.dumps({"claims": [], "entities": [], "processes": []})
    if req.custom_id.startswith("verify:"):
        ids = [line.split()[1] for line in req.user.splitlines() if line.startswith("CLAIM ")]
        return json.dumps({"verdicts": [{"claim_id": i, "verdict": "supported", "note": "fake"} for i in ids]})
    facts = []
    for line in req.user.splitlines():
        if line.startswith("- id="):
            parts = dict(kv.split("=", 1) for kv in [p.strip() for p in line[2:].split(" | ")] if "=" in kv)
            facts.append(parts)
    quotes = {}
    cur = None
    for line in req.user.splitlines():
        if line.startswith("- id="):
            cur = line[2:].split(" | ")[0].split("=", 1)[1]
        elif line.strip().startswith("quote:") and cur:
            quotes[cur] = line.strip()[len("quote:"):].strip().strip('"')
    question = next((l.split(":", 1)[1].strip() for l in req.user.splitlines() if l.startswith("QUESTION:")), "the question")
    primary = next((l.split(":", 1)[1].strip() for l in req.user.splitlines() if l.startswith("PRIMARY QUERY:")), question)
    hubs = next((l.split(":", 1)[1].strip() for l in req.user.splitlines() if l.startswith("HUBS:")), "").split(", ")
    f0 = facts[0] if facts else {"id": "", "value": "", "field": ""}
    answer = f"{question.rstrip('?')}: {f0['value']}." if f0["value"] else f"{question} Short answer from the official page."
    return json.dumps({"title": (question if len(question) <= 60 else primary)[:60], "meta": (f"{question} {f0['value']}. Facts from the official pages, checked and dated. " * 3)[:150], "h1": question, "answer": answer,
                       "sections": [{"heading": "What the official page says", "body_md": f"The listed value is {f0['value']}. See the [housing guides]({hubs[0] if hubs else '/'}) and the [school page]({hubs[1] if len(hubs) > 1 else '/'})."}],
                       "table": {"caption": "Facts", "rows": [{"label": f["field"], "value": f["value"], "claim_id": f["id"]} for f in facts[:5]]} if facts else None, "steps": None,
                       "next_steps": [{"text": "Read the official page.", "target": facts[0].get("source", "https://example.edu").split(" (")[0] if facts else "https://example.edu"}],
                       "not_confirmed": [], "claims": [{"claim_id": f["id"], "quote": quotes.get(f["id"], ""), "used_for": f"The listed value is {f['value']}."} for f in facts[:5]], "internal_links": hubs})


def _submit(conn, client, *, kind: str, requests: list[BatchRequest], run_id: str, log) -> str:
    est = estimate_minor(requests)
    cap = daily_cap_minor()
    spent = spent_today_minor(conn)
    if spent + est > cap:
        raise SpendCapExceeded(f"{kind} batch of {len(requests)} would cost about ${est / 100:.2f}; ${spent / 100:.2f} already spent today, cap ${cap / 100:.2f}")
    bid = client.submit(requests)
    with conn.cursor() as cur:
        cur.execute("INSERT INTO bulk_batches (id, kind, run_id, status, request_count, est_cost_minor, custom_ids) VALUES (%s, %s, %s, 'in_progress', %s, %s, %s::jsonb) ON CONFLICT (id) DO NOTHING",
                    (bid, kind, run_id, len(requests), est, json.dumps([r.custom_id for r in requests])))
    conn.commit()
    log(f"{kind}: submitted batch {bid} with {len(requests)} requests (estimate ${est / 100:.2f}; spent today ${spent / 100:.2f} of ${cap / 100:.2f})")
    return bid


def _collect(conn, client, bid: str, *, log) -> list:
    client.wait(bid, log=log)
    results = list(client.results(bid))
    actual = 0
    usage = {"input_tokens": 0, "output_tokens": 0, "cache_read_input_tokens": 0, "cache_creation_input_tokens": 0}
    for r in results:
        if r.ok and r.usage and r.model:
            try:
                actual += usage_minor(r.model, r.usage)
            except KeyError:
                pass
            for k in usage:
                usage[k] += int(r.usage.get(k) or 0)
    with conn.cursor() as cur:
        cur.execute("UPDATE bulk_batches SET status='ended', ended_at=now(), actual_cost_minor=%s, usage=%s::jsonb, results_processed=TRUE WHERE id=%s", (actual, json.dumps(usage), bid))
    conn.commit()
    log(f"batch {bid}: {sum(1 for r in results if r.ok)} ok, {sum(1 for r in results if not r.ok)} errored, actual ${actual / 100:.2f}")
    return results


# ----------------------------------------------------------------------------------------------------------- commands
def cmd_crawl(args, settings, conn=None) -> int:
    conn = conn or connect(settings.database_url)
    out = crawlmod.run_crawl(conn, dsn=settings.database_url, slug=args.school, dry_run=args.dry_run, concurrency=args.concurrency, hosts=args.hosts.split(",") if args.hosts else None,
                             sections=args.sections.split(",") if args.sections else None, max_pages_per_host=args.max_pages, run_id=args.run_id)
    print(json.dumps({k: v for k, v in out.items() if k != "hosts"} | {"hosts": [{k: h.get(k) for k in ("host", "selected", "fetched", "unchanged", "failed", "reason", "error")} for h in out["hosts"]]}, indent=1, default=json_default))
    return 0


def cmd_extract(args, settings, conn=None) -> int:
    conn = conn or connect(settings.database_url)
    school = _school(conn, args.school)
    cfg = crawlmod.load_config(args.school)
    topic_by_section = extractmod.section_topic(conn, cfg)
    model = settings.model_routing.extraction_model
    snaps = extractmod.pending_snapshots(conn, institution_id=school["id"], place_ids=school["place_ids"], limit=args.limit, only_crawled=not args.all_sources)
    reqs = extractmod.build_requests(snaps, model=model, topic_by_section=topic_by_section)
    est = estimate_minor(reqs)
    print(f"extract: {len(reqs)} pages pending ({extractmod.unextracted_count(conn, institution_id=school['id'], place_ids=school['place_ids'])} in total), estimate ${est / 100:.2f} with {model}, daily cap ${daily_cap_minor() / 100:.2f}, spent today ${spent_today_minor(conn) / 100:.2f}")
    client = _client(settings, args)
    if client is None or not reqs:
        print("dry run: no API call" if client is None else "nothing to extract")
        return 0
    log = lambda m: print(time.strftime("%H:%M:%S"), m, flush=True)
    totals = {}
    for i in range(0, len(reqs), args.chunk):
        chunk = reqs[i:i + args.chunk]
        bid = _submit(conn, client, kind="extract", requests=chunk, run_id=args.run_id, log=log)
        results = _collect(conn, client, bid, log=log)
        stats = extractmod.process_results(conn, results, model=model, topic_by_section=topic_by_section, batch_id=bid, default_institution_id=school["id"])
        for k, v in stats.items():
            if isinstance(v, int):
                totals[k] = totals.get(k, 0) + v
        log(f"extract chunk {i // args.chunk + 1}: {json.dumps({k: v for k, v in stats.items() if k != 'store_errors'})}")
    print(json.dumps(totals, indent=1))
    return 0


def cmd_dossier(args, settings, conn=None) -> int:
    conn = conn or connect(settings.database_url)
    school = _school(conn, args.school)
    t0 = time.monotonic()
    qstats = questionsmod.build(conn, slug=args.school)
    rstats = rankmod.rank_all(conn, institution_id=school["id"])
    qstats["by_class"] = rstats["by_class"]
    with conn.cursor() as cur:
        cur.execute("SELECT COALESCE(SUM(COALESCE(actual_cost_minor, est_cost_minor)), 0) AS n FROM bulk_batches WHERE kind='extract'")
        cost = int(cur.fetchone()["n"])
    stats = dossiermod.build(conn, slug=args.school, question_stats=qstats, minutes=round((time.monotonic() - t0) / 60, 2), cost_minor=cost)
    print(json.dumps({"dossier": stats, "questions": qstats, "ranking": rstats}, indent=1, default=json_default))
    return 0


def cmd_plan(args, settings, conn=None) -> int:
    conn = conn or connect(settings.database_url)
    school = _school(conn, args.school)
    out = planmod.plan_pages(conn, institution_id=school["id"], limit=args.limit, run_id=args.run_id, include_existing=args.include_existing)
    if args.json:
        print(json.dumps(out["planned"], indent=1))
    else:
        print(json.dumps({"planned": len(out["planned"]), "skipped": len(out["skipped"]), "first": out["planned"][:10], "skipped_sample": out["skipped"][:5]}, indent=1))
    return 0


def _pages(conn, *, run_id: str, stages: tuple[str, ...], limit: int | None = None) -> list[dict]:
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM bulk_pages WHERE run_id=%s AND stage = ANY(%s) ORDER BY (plan->>'order_rank')::int NULLS LAST, created_at" + (f" LIMIT {int(limit)}" if limit else ""), (run_id, list(stages)))
        return [dict(r) for r in cur.fetchall()]


def _set(conn, page_id, **cols) -> None:
    sets = ", ".join(f"{k}=%s" + ("::jsonb" if isinstance(v, (dict, list)) else "") for k, v in cols.items())
    vals = [json.dumps(v, default=json_default) if isinstance(v, (dict, list)) else v for v in cols.values()]
    with conn.cursor() as cur:
        cur.execute(f"UPDATE bulk_pages SET {sets}, updated_at=now() WHERE id=%s", vals + [page_id])
    conn.commit()


def cmd_run(args, settings, conn=None) -> int:
    conn = conn or connect(settings.database_url)
    school = _school(conn, args.school)
    run_id = args.run_id
    log = lambda m: print(time.strftime("%H:%M:%S"), m, flush=True)
    t0 = time.monotonic()
    report = {"run_id": run_id, "school": args.school, "started": datetime.now(timezone.utc).isoformat(), "mode": "fake" if args.fake else ("dry-run" if args.dry_run else "api"), "published": [], "skipped": [], "failed": [], "batches": []}
    rp = RUNS_DIR / f"{run_id}.json"
    RUNS_DIR.mkdir(parents=True, exist_ok=True)

    def save():
        report["minutes"] = round((time.monotonic() - t0) / 60, 1)
        with conn.cursor() as cur:
            cur.execute("SELECT COALESCE(SUM(COALESCE(actual_cost_minor, est_cost_minor)), 0) AS n, count(*) AS b FROM bulk_batches WHERE run_id=%s", (run_id,))
            row = cur.fetchone()
        report["cost_minor"] = int(row["n"])
        report["cost_per_published_page_minor"] = round(report["cost_minor"] / len(report["published"]), 1) if report["published"] else None
        rp.write_text(json.dumps(report, indent=1, default=json_default))

    try:
        # 1-2. plan + gather (resume: reuse what the run already has)
        if not args.resume or not _pages(conn, run_id=run_id, stages=("planned", "gathered", "written", "checked", "verified", "published")):
            out = planmod.plan_pages(conn, institution_id=school["id"], limit=args.limit, run_id=run_id, include_existing=args.include_existing)
            report["planned"] = len(out["planned"])
            report["skipped"] += [{"path": s["path"], "reason": s["reason"], "stage": "plan"} for s in out["skipped"]]
            log(f"plan: {len(out['planned'])} pages planned, {len(out['skipped'])} skipped")
        for p in _pages(conn, run_id=run_id, stages=("planned",)):
            g = planmod.gather(conn, p, institution_id=school["id"])
            if g["fact_count"] == 0:
                report["skipped"].append({"path": p["path"], "reason": "no verified fact with a quote in scope", "stage": "gather"})
        gathered = _pages(conn, run_id=run_id, stages=("gathered",))
        log(f"gather: {len(gathered)} pages have facts")
        today = datetime.now(timezone.utc).date()
        wmodel, vmodel = settings.model_routing.writing_model, settings.model_routing.verification_model
        write_reqs = [writemod.build_request(p, model=wmodel, school_name=school["canonical_name"], today=today) for p in gathered]
        verify_est = sum(len(p["gathered"]["facts"]) for p in gathered) * 60
        est = estimate_minor(write_reqs) + (estimate_minor([BatchRequest("v", vmodel, verifymod.VERIFY_SYSTEM, " " * verify_est, verifymod.MAX_OUTPUT_TOKENS)]) * len(gathered) if gathered else 0)
        report["estimate_minor"] = est
        log(f"estimate: write+verify for {len(gathered)} pages about ${est / 100:.2f} ({wmodel} / {vmodel}); daily cap ${daily_cap_minor() / 100:.2f}, spent today ${spent_today_minor(conn) / 100:.2f}")
        client = _client(settings, args)
        if client is None:
            report["outcome"] = "dry_run" if (args.dry_run or not settings.anthropic_api_key_present) else "no_client"
            if not settings.anthropic_api_key_present and not args.dry_run:
                report["blocked_on"] = "ANTHROPIC_API_KEY in worker/.env (owner action, specs/bulk-mode.md §7)"
            save()
            print(json.dumps({k: report[k] for k in ("run_id", "mode", "outcome", "planned", "estimate_minor", "minutes") if k in report} | {"gathered": len(gathered), "blocked_on": report.get("blocked_on")}, indent=1))
            return 0
        # 3. write (chunked batches)
        for i in range(0, len(gathered), args.chunk):
            chunk = gathered[i:i + args.chunk]
            bid = _submit(conn, client, kind="write", requests=[writemod.build_request(p, model=wmodel, school_name=school["canonical_name"], today=today) for p in chunk], run_id=run_id, log=log)
            report["batches"].append(bid)
            for p in chunk:
                _set(conn, p["id"], write_batch_id=bid)
            by_id = {f"write:{p['id']}": p for p in chunk}
            for r in _collect(conn, client, bid, log=log):
                p = by_id.get(r.custom_id)
                if not p:
                    continue
                draft, err = writemod.parse_draft(r.text) if r.ok else (None, r.error)
                cost = usage_minor(r.model, r.usage) if (r.ok and r.model and r.usage) else 0
                if draft is None:
                    _set(conn, p["id"], stage="failed", skip_reason=f"write: {err}", cost_minor=cost)
                    report["failed"].append({"path": p["path"], "reason": f"write: {err}"})
                else:
                    _set(conn, p["id"], stage="written", draft=draft, cost_minor=cost)
            save()
        # 4. check (code)
        with conn.cursor() as cur:
            cur.execute("SELECT v.body_markdown FROM pages p JOIN page_versions v ON v.id=p.current_version_id WHERE p.institution_id=%s AND v.gate_status='passed'", (school["id"],))
            existing = [r["body_markdown"] for r in cur.fetchall()]
        for p in _pages(conn, run_id=run_id, stages=("written",)):
            snaps = list({f["snapshot_id"] for f in p["gathered"]["facts"]})
            with conn.cursor() as cur:
                cur.execute("SELECT id::text AS id, retained_text FROM fetch_snapshots WHERE id = ANY(%s::uuid[])", (snaps,))
                texts = {r["id"]: r["retained_text"] or "" for r in cur.fetchall()}
            draft, rep = checkmod.check_draft(p["draft"], p["gathered"], question=p["plan"].get("primary_query") or p["plan"]["question"], hubs=p["gathered"].get("hubs") or [], existing_bodies=existing, source_texts=texts)
            if rep["status"] == "ok":
                _set(conn, p["id"], stage="checked", draft=draft, checks=rep)
            else:
                _set(conn, p["id"], stage="skipped", draft=draft, checks=rep, skip_reason="check: " + "; ".join(rep["reasons"]))
                report["skipped"].append({"path": p["path"], "reason": "; ".join(rep["reasons"]), "stage": "check"})
        checked = _pages(conn, run_id=run_id, stages=("checked",))
        log(f"check: {len(checked)} pages pass the code checks")
        save()
        # 5. verify (batched) + publish
        for i in range(0, len(checked), args.chunk):
            chunk = checked[i:i + args.chunk]
            bid = _submit(conn, client, kind="verify", requests=[verifymod.build_request(p, model=vmodel) for p in chunk], run_id=run_id, log=log)
            report["batches"].append(bid)
            by_id = {f"verify:{p['id']}": p for p in chunk}
            for r in _collect(conn, client, bid, log=log):
                p = by_id.get(r.custom_id)
                if not p:
                    continue
                draft, rep = verifymod.apply_verdicts(p["draft"], r.text if r.ok else None)
                cost = usage_minor(r.model, r.usage) if (r.ok and r.model and r.usage) else 0
                survives = bool(draft.get("claims")) and checkmod._words(draft.get("answer") or "") >= 8
                _set(conn, p["id"], stage="verified" if survives else "skipped", draft=draft, verdicts=rep, cost_minor=p["cost_minor"] + cost, skip_reason=None if survives else "verify: no supported claim left in the answer")
                if not survives:
                    report["skipped"].append({"path": p["path"], "reason": "verification removed the answer's claims", "stage": "verify"})
            save()
        for p in _pages(conn, run_id=run_id, stages=("verified",)):
            try:
                out = verifymod.publish(conn, p, institution_id=school["id"], settings=settings, model=wmodel, run_id=run_id)
                report["published"].append(out | {"cost_minor": p["cost_minor"]})
            except Exception as e:  # noqa: BLE001 — one page's publish failure is recorded, the run continues
                conn.rollback()
                _set(conn, p["id"], stage="failed", skip_reason=f"publish: {type(e).__name__}: {str(e)[:200]}")
                report["failed"].append({"path": p["path"], "reason": f"publish: {type(e).__name__}: {str(e)[:200]}"})
            save()
        if report["published"]:
            from ..render import site
            site.render_shell(conn, out_root=site.OUT_DEFAULT, environment="staging", publication_name=settings.publication_name)
            if args.deploy:
                r = subprocess.run(["bash", str(REPO_ROOT / "scripts" / "deploy_netlify.sh")], capture_output=True, text=True, timeout=600)
                report["deploy"] = {"exit": r.returncode, "tail": (r.stdout + r.stderr)[-600:]}
        report["outcome"] = "completed"
    except SpendCapExceeded as e:
        report["outcome"] = f"stopped: {e}"
        log(str(e))
    finally:
        save()
    print(json.dumps({k: report.get(k) for k in ("run_id", "mode", "outcome", "planned", "minutes", "cost_minor", "cost_per_published_page_minor", "deploy")} | {"published": len(report["published"]), "skipped": len(report["skipped"]), "failed": len(report["failed"]),
                      "skip_reasons": _reasons(report["skipped"]), "report": str(rp)}, indent=1, default=json_default))
    return 0


def _reasons(items: list[dict]) -> dict:
    out: dict = {}
    for it in items:
        key = it.get("reason", "")[:60]
        out[key] = out.get(key, 0) + 1
    return out


def cmd_status(args, settings, conn=None) -> int:
    conn = conn or connect(settings.database_url)
    school = _school(conn, args.school)
    with conn.cursor() as cur:
        cur.execute("SELECT stage, count(*) AS n FROM bulk_pages GROUP BY stage ORDER BY stage")
        stages = {r["stage"]: r["n"] for r in cur.fetchall()}
        cur.execute("SELECT incumbent_class, count(*) AS n FROM bulk_questions WHERE institution_id=%s GROUP BY 1", (school["id"],))
        classes = {r["incumbent_class"] or "unranked": r["n"] for r in cur.fetchall()}
        cur.execute("SELECT count(*) AS n FROM bulk_questions WHERE institution_id=%s", (school["id"],))
        nq = cur.fetchone()["n"]
        cur.execute("SELECT kind, status, count(*) AS n, COALESCE(SUM(COALESCE(actual_cost_minor, est_cost_minor)),0) AS cost FROM bulk_batches GROUP BY 1,2 ORDER BY 1,2")
        batches = [dict(r) for r in cur.fetchall()]
    print(json.dumps({"school": args.school, "crawled_pages": crawlmod.crawled_page_count(conn), "unextracted_pages": extractmod.unextracted_count(conn, institution_id=school["id"], place_ids=school["place_ids"]),
                      "questions": nq, "incumbent_classes": classes, "bulk_pages_by_stage": stages, "batches": batches, "spent_today_minor": spent_today_minor(conn), "daily_cap_minor": daily_cap_minor(),
                      "api_key_present": settings.anthropic_api_key_present}, indent=1, default=json_default))
    return 0


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(prog="campus_worker.bulk", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--school", required=True)
    common.add_argument("--run-id", default=os.environ.get("CAMPUS_RUN_ID") or f"bulk-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}")
    c = sub.add_parser("crawl", parents=[common]); c.add_argument("--dry-run", action="store_true"); c.add_argument("--hosts"); c.add_argument("--sections"); c.add_argument("--concurrency", type=int, default=20); c.add_argument("--max-pages", type=int)
    e = sub.add_parser("extract", parents=[common]); e.add_argument("--limit", type=int, default=2000); e.add_argument("--chunk", type=int, default=500); e.add_argument("--dry-run", action="store_true"); e.add_argument("--fake", action="store_true"); e.add_argument("--all-sources", action="store_true")
    sub.add_parser("dossier", parents=[common])
    p = sub.add_parser("plan", parents=[common]); p.add_argument("--limit", type=int, default=20); p.add_argument("--json", action="store_true"); p.add_argument("--include-existing", action="store_true")
    r = sub.add_parser("run", parents=[common]); r.add_argument("--limit", type=int, default=20); r.add_argument("--chunk", type=int, default=500); r.add_argument("--dry-run", action="store_true"); r.add_argument("--fake", action="store_true")
    r.add_argument("--resume", action="store_true"); r.add_argument("--deploy", action="store_true"); r.add_argument("--include-existing", action="store_true")
    sub.add_parser("status", parents=[common])
    args = ap.parse_args(argv)
    settings = get_settings()
    return {"crawl": cmd_crawl, "extract": cmd_extract, "dossier": cmd_dossier, "plan": cmd_plan, "run": cmd_run, "status": cmd_status}[args.cmd](args, settings)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
