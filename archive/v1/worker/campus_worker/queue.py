"""Persistent job queue (SPEC §25).

States: queued, leased, succeeded, retry_wait, held, dead_letter, cancelled.
- enqueue() is idempotent on idempotency_key.
- lease() is atomic (SELECT ... FOR UPDATE SKIP LOCKED) and honours dependencies, not_before,
  and delegation depth.
- reclaim_expired_leases() returns lost jobs to queued/retry_wait; complete() on a lost lease is
  refused and recorded as lost_lease so the caller can reconcile (SPEC §25).
- fail() applies exponential backoff with jitter up to max_attempts, then dead_letter.
- hold() requires a machine-readable reason and a retry condition.
"""
from __future__ import annotations

import json
import random
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from uuid import UUID

import psycopg

from .types import JobRecord

BASE_BACKOFF_SECONDS = 60
MAX_BACKOFF_SECONDS = 3600


class LeaseLost(Exception):
    """Raised when a worker tries to finish a job whose lease it no longer owns."""


@dataclass
class LeasedJob:
    id: UUID
    job_type: str
    payload: dict
    attempt: int
    lease_owner: str
    institution_id: UUID | None
    model_role: str | None
    is_paid: bool
    estimated_cost_minor: int | None
    delegation_depth: int


def _now() -> datetime:
    return datetime.now(timezone.utc)


def enqueue(conn: psycopg.Connection, job: JobRecord, *, max_delegation_depth: int = 1) -> tuple[UUID, bool]:
    """Insert a job unless its idempotency key exists. Returns (id, created)."""
    if job.delegation_depth > max_delegation_depth:
        raise ValueError(f"delegation depth {job.delegation_depth} exceeds limit {max_delegation_depth}")
    with conn.cursor() as cur:
        cur.execute(
            """INSERT INTO jobs (job_type, institution_id, campus_id, idempotency_key, payload, priority,
               depends_on, is_paid, estimated_cost_minor, model_role, max_attempts, parent_job_id, delegation_depth)
               VALUES (%s,%s,%s,%s,%s::jsonb,%s,%s,%s,%s,%s,%s,%s,%s)
               ON CONFLICT (idempotency_key) DO NOTHING RETURNING id""",
            (job.job_type, job.institution_id, job.campus_id, job.idempotency_key, json.dumps(job.payload),
             job.priority, job.depends_on, job.is_paid, job.estimated_cost_minor, job.model_role,
             job.max_attempts, job.parent_job_id, job.delegation_depth),
        )
        r = cur.fetchone()
        if r:
            conn.commit()
            return r["id"], True
        cur.execute("SELECT id FROM jobs WHERE idempotency_key=%s", (job.idempotency_key,))
        existing = cur.fetchone()["id"]
    conn.commit()
    return existing, False


def lease(conn: psycopg.Connection, owner: str, *, lease_seconds: int = 300, job_types: list[str] | None = None) -> LeasedJob | None:
    """Atomically lease the highest-priority eligible job. Dependencies must all be succeeded."""
    with conn.cursor() as cur:
        cur.execute(
            """SELECT j.id FROM jobs j
               WHERE j.state IN ('queued','retry_wait') AND j.not_before <= now()
                 AND (%(types)s::text[] IS NULL OR j.job_type = ANY(%(types)s::text[]))
                 AND NOT EXISTS (
                   SELECT 1 FROM unnest(j.depends_on) d(id)
                   LEFT JOIN jobs dj ON dj.id = d.id
                   WHERE dj.id IS NULL OR dj.state <> 'succeeded')
               ORDER BY j.priority DESC, j.created_at
               FOR UPDATE SKIP LOCKED LIMIT 1""",
            {"types": job_types},
        )
        r = cur.fetchone()
        if not r:
            conn.commit()
            return None
        cur.execute(
            """UPDATE jobs SET state='leased', lease_owner=%s, lease_expires_at=now() + make_interval(secs => %s),
               attempts = attempts + 1, updated_at=now()
               WHERE id=%s RETURNING id, job_type, payload, attempts, lease_owner, institution_id, model_role,
                                    is_paid, estimated_cost_minor, delegation_depth""",
            (owner, lease_seconds, r["id"]),
        )
        j = cur.fetchone()
    conn.commit()
    return LeasedJob(j["id"], j["job_type"], j["payload"], j["attempts"], j["lease_owner"], j["institution_id"],
                     j["model_role"], j["is_paid"], j["estimated_cost_minor"], j["delegation_depth"])


def _assert_lease(cur, job_id: UUID, owner: str) -> dict:
    cur.execute("SELECT state, lease_owner, lease_expires_at, attempts, max_attempts FROM jobs WHERE id=%s FOR UPDATE", (job_id,))
    j = cur.fetchone()
    if j is None:
        raise LookupError("job not found")
    if j["state"] != "leased" or j["lease_owner"] != owner:
        raise LeaseLost(f"job {job_id} is {j['state']} owned by {j['lease_owner']}, not {owner}")
    return j


def complete(conn: psycopg.Connection, job_id: UUID, owner: str) -> None:
    with conn.cursor() as cur:
        try:
            _assert_lease(cur, job_id, owner)
        except LeaseLost:
            conn.rollback()
            _record_lost_lease(conn, job_id, owner, "complete")
            raise
        cur.execute("UPDATE jobs SET state='succeeded', lease_owner=NULL, lease_expires_at=NULL, updated_at=now() WHERE id=%s", (job_id,))
    conn.commit()


def fail(conn: psycopg.Connection, job_id: UUID, owner: str, error: str, *, retryable: bool = True, retry_after_seconds: int | None = None) -> str:
    """Record a failure. Returns the new state ('retry_wait' or 'dead_letter')."""
    with conn.cursor() as cur:
        try:
            j = _assert_lease(cur, job_id, owner)
        except LeaseLost:
            conn.rollback()
            _record_lost_lease(conn, job_id, owner, "fail")
            raise
        if not retryable or j["attempts"] >= j["max_attempts"]:
            cur.execute(
                "UPDATE jobs SET state='dead_letter', lease_owner=NULL, lease_expires_at=NULL, last_error=%s, hold_owner='owner', updated_at=now() WHERE id=%s",
                (error[:2000], job_id),
            )
            state = "dead_letter"
        else:
            if retry_after_seconds is None:  # exponential backoff with jitter; provider retry-after wins
                base = min(MAX_BACKOFF_SECONDS, BASE_BACKOFF_SECONDS * (2 ** (j["attempts"] - 1)))
                retry_after_seconds = int(base * random.uniform(0.8, 1.2))
            cur.execute(
                """UPDATE jobs SET state='retry_wait', lease_owner=NULL, lease_expires_at=NULL, last_error=%s,
                   not_before = now() + make_interval(secs => %s), updated_at=now() WHERE id=%s""",
                (error[:2000], retry_after_seconds, job_id),
            )
            state = "retry_wait"
    conn.commit()
    return state


def hold(conn: psycopg.Connection, job_id: UUID, owner: str, reason: str, retry_condition: str, *, hold_owner: str = "system") -> None:
    if not reason or not retry_condition:
        raise ValueError("hold requires a machine-readable reason and a retry condition")
    with conn.cursor() as cur:
        try:
            _assert_lease(cur, job_id, owner)
        except LeaseLost:
            conn.rollback()
            _record_lost_lease(conn, job_id, owner, "hold")
            raise
        cur.execute(
            """UPDATE jobs SET state='held', lease_owner=NULL, lease_expires_at=NULL, hold_reason=%s,
               hold_retry_condition=%s, hold_owner=%s, updated_at=now() WHERE id=%s""",
            (reason, retry_condition, hold_owner, job_id),
        )
    conn.commit()


def hold_unleased(conn: psycopg.Connection, job_id: UUID, reason: str, retry_condition: str, *, hold_owner: str = "system") -> None:
    """Hold a job before it is ever leased (e.g. unpriced paid work at dispatch time)."""
    with conn.cursor() as cur:
        cur.execute(
            """UPDATE jobs SET state='held', hold_reason=%s, hold_retry_condition=%s, hold_owner=%s, updated_at=now()
               WHERE id=%s AND state IN ('queued','retry_wait')""",
            (reason, retry_condition, hold_owner, job_id),
        )
    conn.commit()


def release_hold(conn: psycopg.Connection, job_id: UUID) -> None:
    with conn.cursor() as cur:
        cur.execute("UPDATE jobs SET state='queued', hold_reason=NULL, hold_retry_condition=NULL, not_before=now(), updated_at=now() WHERE id=%s AND state='held'", (job_id,))
    conn.commit()


def reclaim_expired_leases(conn: psycopg.Connection) -> list[UUID]:
    """Return expired leases to the queue (as retry_wait so the attempt counts)."""
    with conn.cursor() as cur:
        cur.execute(
            """UPDATE jobs SET state = CASE WHEN attempts >= max_attempts THEN 'dead_letter' ELSE 'retry_wait' END,
               lease_owner=NULL, lease_expires_at=NULL, last_error=COALESCE(last_error,'') || ' [lease expired]',
               not_before=now(), updated_at=now()
               WHERE state='leased' AND lease_expires_at < now() RETURNING id"""
        )
        ids = [r["id"] for r in cur.fetchall()]
    conn.commit()
    return ids


def _record_lost_lease(conn: psycopg.Connection, job_id: UUID, owner: str, action: str) -> None:
    with conn.cursor() as cur:
        cur.execute(
            """INSERT INTO exceptions (severity, category, job_id, message, detail)
               VALUES ('warning','runtime',%s,'lost lease on completion; outputs not applied', %s::jsonb)""",
            (job_id, json.dumps({"owner": owner, "action": action})),
        )
    conn.commit()


def counts(conn: psycopg.Connection) -> dict[str, int]:
    with conn.cursor() as cur:
        cur.execute("SELECT state, count(*) AS n FROM jobs GROUP BY state")
        return {r["state"]: r["n"] for r in cur.fetchall()}


def held_and_dead(conn: psycopg.Connection) -> list[dict]:
    with conn.cursor() as cur:
        cur.execute(
            """SELECT id, job_type, state, hold_reason, hold_retry_condition, hold_owner, last_error,
                      now() - updated_at AS age FROM jobs WHERE state IN ('held','dead_letter') ORDER BY updated_at"""
        )
        return cur.fetchall()
