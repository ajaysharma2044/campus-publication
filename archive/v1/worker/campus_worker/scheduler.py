"""Bounded scheduler tick (SPEC §25, §26, §35).

run_once(conn, settings) does, in order:
  1. take a DB advisory lock (no overlapping ticks) — exit 'locked' if another tick holds it;
  2. reclaim expired leases;
  3. apply budget state: if paused, do not dispatch paid jobs (held jobs stay distinct from failed);
  4. hold unpriced paid jobs before dispatch;
  5. lease and run up to `max_jobs` eligible jobs through the handler registry, honouring
     max_concurrent_model_tasks (sequential here; concurrency is bounded, not parallelised);
  6. write a heartbeat with a status in {executing, waiting, usage_paused, blocked, failed}
     and return a result with an exit code (0 executing/completed, 10 waiting, 20 usage_paused,
     30 blocked, 1 failed).

Handlers are deterministic functions (job payload → dict). Model-backed handlers require a
connected provider; otherwise they hold with provider_auth. The handler registry is the only
place job types are mapped to code, so a model proposal can never schedule arbitrary work.
"""
from __future__ import annotations

import json
import traceback
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Callable
from uuid import UUID

import psycopg

from . import budget as budgetmod
from . import queue as q
from .adapters.base import ProviderError
from .adapters.model import HoldJob
from .config import Settings

EXIT = {"executing": 0, "completed": 0, "waiting": 10, "usage_paused": 20, "blocked": 30, "failed": 1, "locked": 11}
LOCK_KEY = "campus_scheduler_tick"


@dataclass
class TickResult:
    status: str
    ran: list[dict] = field(default_factory=list)
    reclaimed: list[str] = field(default_factory=list)
    held_unpriced: list[str] = field(default_factory=list)
    budget: dict = field(default_factory=dict)
    note: str = ""

    @property
    def exit_code(self) -> int:
        return EXIT[self.status]

    def as_dict(self) -> dict:
        return {"status": self.status, "exit_code": self.exit_code, "ran": self.ran, "reclaimed": self.reclaimed,
                "held_unpriced": self.held_unpriced, "budget": self.budget, "note": self.note}


Handler = Callable[[psycopg.Connection, Settings, q.LeasedJob], dict]
_HANDLERS: dict[str, Handler] = {}
PAID_JOB_TYPES = {"extract_claims_model", "plan_brief", "write_draft", "edit_draft", "verify_draft", "score_opportunity_model", "seo_review"}


def handler(job_type: str):
    def deco(fn: Handler):
        _HANDLERS[job_type] = fn
        return fn
    return deco


def registered_job_types() -> list[str]:
    return sorted(_HANDLERS)


# ---------------------------------------------------------------- built-in deterministic handlers
@handler("noop")
def _noop(conn, settings, job):
    return {"ok": True, "payload": job.payload}


@handler("fail_once_then_succeed")
def _flaky(conn, settings, job):
    """Test fixture: fails on the first attempt with a retryable error, succeeds afterwards."""
    if job.attempt == 1:
        raise ProviderError("simulated outage", retryable=True, kind="outage")
    return {"ok": True, "attempt": job.attempt}


@handler("revalidate_page")
def _revalidate_page(conn, settings, job):
    """Deterministic revalidation: re-check that the page's current version claims are not
    blocking; if they are, mark the page held and record an exception for editorial follow-up."""
    from .claims import blocking_claims

    page_id = UUID(job.payload["page_id"])
    with conn.cursor() as cur:
        cur.execute("SELECT current_version_id FROM pages WHERE id=%s", (page_id,))
        r = cur.fetchone()
        if not r or not r["current_version_id"]:
            return {"page_id": str(page_id), "result": "no_current_version"}
        cur.execute("SELECT claim_id FROM page_claims WHERE page_version_id=%s", (r["current_version_id"],))
        ids = [x["claim_id"] for x in cur.fetchall()]
    blocked = blocking_claims(conn, ids)
    with conn.cursor() as cur:
        if blocked:
            cur.execute("UPDATE pages SET status='held', revalidation_required=TRUE, revalidation_reason=%s WHERE id=%s", ("blocking claims: " + ",".join(str(b["id"]) for b in blocked), page_id))
            cur.execute("INSERT INTO exceptions (severity, category, job_id, message, detail) VALUES ('warning','gate',%s,'page held after source change: critical claims stale/conflicted',%s::jsonb)",
                        (job.id, json.dumps({"page_id": str(page_id), "claims": [str(b["id"]) for b in blocked]})))
        else:
            cur.execute("UPDATE pages SET revalidation_required=FALSE, revalidation_reason=NULL WHERE id=%s", (page_id,))
    conn.commit()
    return {"page_id": str(page_id), "blocking": len(blocked), "result": "held" if blocked else "clear"}


@handler("collect_source")
def _collect_source(conn, settings, job):
    from .collectors.html import collect_html_source
    from .fetcher import SafeFetcher

    fetcher = SafeFetcher(conn)
    return collect_html_source(conn, fetcher, UUID(job.payload["source_id"]))


def _model_handler_factory(role_fn_name: str):
    def _h(conn, settings, job):
        from .adapters.model import default_provider
        prov = default_provider()
        if not prov.capability().connected:
            raise HoldJob("provider_auth", "ANTHROPIC_API_KEY (API-billed) configured for the worker")
        raise HoldJob("not_implemented_dispatch", f"model job '{role_fn_name}' needs the orchestrator wiring for a connected provider (see roles/runners.py)")
    return _h


for _jt in ("plan_brief", "write_draft", "edit_draft", "verify_draft"):
    _HANDLERS[_jt] = _model_handler_factory(_jt)


# ---------------------------------------------------------------- tick
def heartbeat(conn: psycopg.Connection, component: str, status: str, detail: dict | None = None, *, success: bool) -> None:
    with conn.cursor() as cur:
        cur.execute(
            """INSERT INTO heartbeats (component, last_started_at, last_success_at, last_status, detail)
               VALUES (%s, now(), CASE WHEN %s THEN now() ELSE NULL END, %s, %s::jsonb)
               ON CONFLICT (component) DO UPDATE SET last_started_at=now(),
                 last_success_at = CASE WHEN %s THEN now() ELSE heartbeats.last_success_at END, last_status=EXCLUDED.last_status, detail=EXCLUDED.detail""",
            (component, success, status, json.dumps(detail or {}), success),
        )
    conn.commit()


def run_once(conn: psycopg.Connection, settings: Settings, *, max_jobs: int = 10, worker_id: str = "worker-1", job_types: list[str] | None = None) -> dict:
    res = TickResult("executing")
    with conn.cursor() as cur:
        cur.execute("SELECT pg_try_advisory_lock(hashtext(%s)) AS got", (LOCK_KEY,))
        if not cur.fetchone()["got"]:
            conn.commit()
            res.status, res.note = "locked", "another tick holds the scheduler lock"
            return res.as_dict()
    conn.commit()
    try:
        res.reclaimed = [str(i) for i in q.reclaim_expired_leases(conn)]
        bstat = budgetmod.status(conn, settings.budget, execution_mode=getattr(settings, "execution_mode", "api"))
        res.budget = bstat
        # hold unpriced paid jobs before they are ever leased
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM jobs WHERE state IN ('queued','retry_wait') AND is_paid AND estimated_cost_minor IS NULL")
            for r in cur.fetchall():
                q.hold_unleased(conn, r["id"], "unpriced", "estimated_cost_minor set from a priced model/provider")
                res.held_unpriced.append(str(r["id"]))
        model_tasks = 0
        for _ in range(max_jobs):
            with conn.cursor() as cur:
                cur.execute("SELECT DISTINCT job_type FROM jobs WHERE state IN ('queued','retry_wait') AND not_before <= now()")
                eligible_types = [r["job_type"] for r in cur.fetchall()]
            conn.commit()
            if job_types:
                eligible_types = [t for t in eligible_types if t in job_types]
            if bstat["paused"]:
                eligible_types = [t for t in eligible_types if t not in PAID_JOB_TYPES]
            if model_tasks >= settings.quotas.max_concurrent_model_tasks:
                eligible_types = [t for t in eligible_types if t not in PAID_JOB_TYPES]
            if not eligible_types:
                break
            job = q.lease(conn, worker_id, job_types=eligible_types)
            if job is None:
                break
            entry = {"job_id": str(job.id), "job_type": job.job_type, "attempt": job.attempt}
            fn = _HANDLERS.get(job.job_type)
            if fn is None:
                q.fail(conn, job.id, worker_id, f"no handler registered for job_type {job.job_type}", retryable=False)
                entry["result"] = "dead_letter:unknown_job_type"
                res.ran.append(entry)
                continue
            if job.job_type in PAID_JOB_TYPES:
                model_tasks += 1
            with conn.cursor() as cur:
                cur.execute("INSERT INTO runs (job_id, attempt, role, worker_id) VALUES (%s,%s,%s,%s) RETURNING id", (job.id, job.attempt, job.job_type, worker_id))
                run_id = cur.fetchone()["id"]
            conn.commit()
            try:
                out = fn(conn, settings, job)
                q.complete(conn, job.id, worker_id)
                _finish_run(conn, run_id, "succeeded", out)
                entry["result"] = "succeeded"
            except HoldJob as e:
                q.hold(conn, job.id, worker_id, e.reason, e.retry_condition)
                _finish_run(conn, run_id, "held", {"reason": e.reason})
                entry["result"] = f"held:{e.reason}"
            except budgetmod.BudgetExceeded as e:
                q.hold(conn, job.id, worker_id, "budget_paused", "daily or monthly cap headroom restored")
                _finish_run(conn, run_id, "held", {"reason": "budget_paused", "detail": str(e)})
                entry["result"] = "held:budget_paused"
            except ProviderError as e:
                state = q.fail(conn, job.id, worker_id, str(e), retryable=e.retryable, retry_after_seconds=e.retry_after_seconds)
                _finish_run(conn, run_id, "failed", {"error": str(e), "kind": e.kind})
                entry["result"] = state
            except q.LeaseLost:
                _finish_run(conn, run_id, "lost_lease", {})
                entry["result"] = "lost_lease"
            except Exception as e:  # noqa: BLE001 — recorded, never silently swallowed
                state = q.fail(conn, job.id, worker_id, f"{type(e).__name__}: {e}", retryable=True)
                _finish_run(conn, run_id, "failed", {"error": str(e), "trace": traceback.format_exc()[-1500:]})
                entry["result"] = state
            res.ran.append(entry)
        if not res.ran:
            if bstat["paused"]:
                res.status = "usage_paused"
            else:
                with conn.cursor() as cur:
                    cur.execute("SELECT count(*) AS n FROM jobs WHERE state='held' AND hold_reason LIKE 'provider_%'")
                    blocked = cur.fetchone()["n"]
                res.status = "blocked" if blocked else "waiting"
        else:
            res.status = "completed"
        heartbeat(conn, "scheduler", res.status, res.as_dict(), success=True)
    except Exception as e:  # noqa: BLE001
        res.status, res.note = "failed", f"{type(e).__name__}: {e}"
        heartbeat(conn, "scheduler", "failed", {"error": res.note}, success=False)
    finally:
        with conn.cursor() as cur:
            cur.execute("SELECT pg_advisory_unlock(hashtext(%s))", (LOCK_KEY,))
        conn.commit()
    return res.as_dict()


def _finish_run(conn, run_id, status, output):
    with conn.cursor() as cur:
        cur.execute("UPDATE runs SET finished_at=now(), status=%s, output_ref=%s WHERE id=%s", (status, json.dumps(output, default=str)[:4000], run_id))
    conn.commit()


# ---------------------------------------------------------------- daily / weekly plans (deterministic enqueueing)
def plan_daily(conn: psycopg.Connection, settings: Settings) -> dict:
    """Enqueue bounded daily work: refresh due sources (fair across schools with an exploration
    share for underserved institutions)."""
    from .types import JobRecord

    share = settings.quotas.exploration_share_pct
    with conn.cursor() as cur:
        cur.execute(
            """SELECT r.id, r.institution_id, COALESCE(sc.is_underserved, FALSE) AS underserved FROM source_registry r
               LEFT JOIN school_configs sc ON sc.institution_id=r.institution_id
               WHERE r.health IN ('healthy','unknown','degraded') AND (r.next_refresh_at IS NULL OR r.next_refresh_at <= now()) ORDER BY r.next_refresh_at NULLS FIRST""")
        due = cur.fetchall()
    cap = 20
    underserved = [d for d in due if d["underserved"]][: max(1, cap * share // 100)]
    rest = [d for d in due if not d["underserved"]][: cap - len(underserved)]
    enq = 0
    for d in underserved + rest:
        _, created = q.enqueue(conn, JobRecord(job_type="collect_source", idempotency_key=f"collect:{d['id']}:{datetime.now(timezone.utc).date()}",
                                              institution_id=d["institution_id"], payload={"source_id": str(d["id"])}, priority=60 if d["underserved"] else 50))
        enq += int(created)
    return {"due_sources": len(due), "enqueued": enq, "exploration_share_pct": share}
