"""Experiment registry (SPEC §21, §23): one coherent factor per experiment, logged hypothesis,
allocation, primary metric, guardrails, minimum observation, stopping rule, outcome, rollback."""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from uuid import UUID

import psycopg

REQUIRED_GUARDRAIL_KEYS = {"metric", "max_regression_pct"}


@dataclass
class ExperimentSpec:
    key: str
    area: str
    hypothesis: str
    allocation: dict[str, int]
    primary_metric: str
    guardrails: list[dict]
    minimum_observation: str
    stopping_rule: str
    rollback_note: str

    def validate(self) -> list[str]:
        errs = []
        if sum(self.allocation.values()) != 100 or "control" not in self.allocation:
            errs.append("allocation must include 'control' and sum to 100")
        if not self.guardrails:
            errs.append("at least one guardrail (e.g. task completion, CLS, complaints) is required")
        for g in self.guardrails:
            if not REQUIRED_GUARDRAIL_KEYS <= set(g):
                errs.append(f"guardrail missing {REQUIRED_GUARDRAIL_KEYS - set(g)}")
        if len(self.hypothesis) < 20:
            errs.append("hypothesis too short to be falsifiable")
        if not self.stopping_rule or not self.minimum_observation:
            errs.append("stopping rule and minimum observation are required")
        return errs


def create(conn: psycopg.Connection, spec: ExperimentSpec) -> UUID:
    errs = spec.validate()
    if errs:
        raise ValueError("; ".join(errs))
    with conn.cursor() as cur:
        cur.execute("SELECT count(*) AS n FROM experiments WHERE area=%s AND status='running'", (spec.area,))
        if cur.fetchone()["n"]:
            raise ValueError(f"an experiment is already running in area {spec.area}; one factor at a time")
        cur.execute(
            """INSERT INTO experiments (key, area, hypothesis, allocation, primary_metric, guardrails, minimum_observation, stopping_rule, rollback_note)
               VALUES (%s,%s,%s,%s::jsonb,%s,%s::jsonb,%s,%s,%s) RETURNING id""",
            (spec.key, spec.area, spec.hypothesis, json.dumps(spec.allocation), spec.primary_metric, json.dumps(spec.guardrails),
             spec.minimum_observation, spec.stopping_rule, spec.rollback_note),
        )
        eid = cur.fetchone()["id"]
    conn.commit()
    return eid


def start(conn: psycopg.Connection, key: str) -> None:
    with conn.cursor() as cur:
        cur.execute("UPDATE experiments SET status='running', started_at=now() WHERE key=%s AND status='planned'", (key,))
    conn.commit()


def assign(key: str, allocation: dict[str, int], session_token: str) -> str:
    """Deterministic, stateless assignment from a short-lived session token (no user identity)."""
    bucket = int(hashlib.sha256(f"{key}|{session_token}".encode()).hexdigest()[:8], 16) % 100
    acc = 0
    for variant, pct in allocation.items():
        acc += pct
        if bucket < acc:
            return variant
    return "control"


def conclude(conn: psycopg.Connection, key: str, *, outcome: str, status: str = "concluded") -> None:
    if status not in ("concluded", "stopped", "rolled_back"):
        raise ValueError("status must be concluded|stopped|rolled_back")
    if outcome.strip().lower() in ("", "win", "success"):
        raise ValueError("outcome must state the measured result, including 'inconclusive' when it is")
    with conn.cursor() as cur:
        cur.execute("UPDATE experiments SET status=%s, outcome=%s, ended_at=now() WHERE key=%s", (status, outcome, key))
    conn.commit()
