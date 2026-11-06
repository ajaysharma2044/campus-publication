"""Cheapest-first funnel (continuous-local-run R25; AT23).

Stages, cheapest first: harvest/expand (deterministic) → search-intel on 2 variants → AGI + thresholds → only then
primary-source research, planning, writing, editing, verification, SEO. A cluster that fails a threshold stops
immediately and the refusal is written to the dispatch log with its reason, so "expensive stages never ran" can be
asserted from that log.
"""
from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass
from pathlib import Path
from uuid import UUID

import psycopg

from . import sweetspot
from .agents.dispatch import DISPATCH_LOG_DEFAULT

EXPENSIVE = ("researcher", "planner", "writer", "editor", "verifier", "seo", "tool-engineer", "search-strategist")
STAGE_ORDER = ("harvest", "expand", "search_intel", "agi_threshold", "research", "plan", "write", "edit", "beat_review", "verify", "seo", "publish", "recheck")


@dataclass
class Gate:
    ok: bool
    stage: str
    reason: str
    score: sweetspot.ClusterScore | None = None


def qualify(conn: psycopg.Connection, cluster_id: UUID, *, intel: dict | None = None) -> Gate:
    """Run the AGI/threshold stage. ok=True only for sweet-spot clusters (or ones already in production)."""
    with conn.cursor() as cur:
        cur.execute("SELECT queue_state FROM intent_clusters WHERE id=%s", (cluster_id,))
        st = cur.fetchone()["queue_state"]
    if st in ("in_production", "done"):
        return Gate(True, "agi_threshold", f"cluster already {st}")
    cs = sweetspot.score_cluster(conn, cluster_id, intel=intel)
    if cs.decision == "needs_intel":
        return Gate(False, "search_intel", cs.reason, cs)
    if cs.decision != "sweet_spot":
        return Gate(False, "agi_threshold", f"{cs.decision}: {cs.reason}", cs)
    return Gate(True, "agi_threshold", cs.reason, cs)


def refuse(agent: str, *, cluster_id: UUID | str, stage: str, reason: str, log_path: Path | None = None) -> dict:
    """Record that an expensive dispatch was NOT made and why (the funnel stopped the cluster)."""
    entry = {"ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "agent": agent, "status": "refused_by_funnel", "stage": stage, "reason": reason,
             "cluster_id": str(cluster_id), "run_id": os.environ.get("CAMPUS_RUN_ID"), "task_id": f"funnel:{str(cluster_id)[:8]}"}
    p = log_path or DISPATCH_LOG_DEFAULT
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry) + "\n")
    return entry


def guard(conn: psycopg.Connection, cluster_id: UUID, agent: str, *, log_path: Path | None = None) -> Gate:
    """Call before dispatching an expensive agent for a cluster. Returns Gate(ok=False) and logs the refusal if the cluster is unqualified."""
    if agent not in EXPENSIVE:
        return Gate(True, "cheap", "not an expensive stage")
    g = qualify(conn, cluster_id)
    if not g.ok:
        refuse(agent, cluster_id=cluster_id, stage=g.stage, reason=g.reason, log_path=log_path)
    return g


def dispatched_agents(log_path: Path | None = None, *, cluster_id: UUID | str | None = None) -> dict[str, list[str]]:
    """{status: [agent, ...]} from the dispatch log, optionally filtered by cluster (task ids carry the cluster prefix)."""
    p = log_path or DISPATCH_LOG_DEFAULT
    out: dict[str, list[str]] = {}
    if not p.exists():
        return out
    key = str(cluster_id)[:8] if cluster_id else None
    for line in p.read_text().splitlines():
        if not line.strip():
            continue
        e = json.loads(line)
        if key and key not in (e.get("task_id") or "") and key not in (e.get("cluster_id") or ""):
            continue
        out.setdefault(e.get("status", "?"), []).append(e.get("agent"))
    return out
