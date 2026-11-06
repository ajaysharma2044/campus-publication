"""Layered process graphs (continuous-local-run R47; AT47).

A process (e.g. changing majors / internal transfer) is a graph of nodes in four layers:
  L0 overview → L1 each real transition (college A → college B) → L2 a specific major or situation → L3 edge cases.
Every node carries rules (steps, prerequisites, GPA/course requirements, deadlines, forms, offices, exceptions) filled from
official pages and tied to claims with source URLs. A node whose rules are identical to its parent's inherits them and
stores nothing new. The page decision per node is computed by code:
  standalone  rules differ from the parent AND (an observed query targets it OR ≥ 2 independent questions)
  section     rules differ, no observed demand
  none        identical to the parent
The process navigator (tools/navigator.py) answers any from→to path from the graph without generating doorway pages.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from uuid import UUID

import psycopg

RULE_KEYS = ("steps", "prerequisites", "gpa_min", "course_requirements", "deadlines", "forms", "offices", "exceptions", "notes")


def canonical_rules(rules: dict) -> dict:
    out = {}
    for k in RULE_KEYS:
        v = rules.get(k)
        if v in (None, "", [], {}):
            continue
        out[k] = v
    return out


def rules_hash(rules: dict) -> str:
    return hashlib.sha256(json.dumps(canonical_rules(rules), sort_keys=True, default=str).encode()).hexdigest()


@dataclass
class NodeSpec:
    key: str
    label: str
    layer: int
    parent_key: str | None = None
    from_state: str | None = None
    to_state: str | None = None
    situation: str | None = None
    rules: dict = field(default_factory=dict)
    source_urls: list[str] = field(default_factory=list)
    claim_ids: list[UUID] = field(default_factory=list)


def ensure_graph(conn: psycopg.Connection, *, institution_id: UUID, key: str, name: str, topic_key: str | None = None, description: str | None = None, tool_path: str | None = None) -> UUID:
    with conn.cursor() as cur:
        tid = None
        if topic_key:
            cur.execute("SELECT id FROM topics WHERE key=%s", (topic_key,))
            r = cur.fetchone()
            tid = r["id"] if r else None
        cur.execute("""INSERT INTO process_graphs (institution_id, topic_id, key, name, description, tool_path) VALUES (%s,%s,%s,%s,%s,%s)
                       ON CONFLICT (institution_id, key) DO UPDATE SET name=EXCLUDED.name, description=COALESCE(EXCLUDED.description, process_graphs.description),
                         tool_path=COALESCE(EXCLUDED.tool_path, process_graphs.tool_path), topic_id=COALESCE(EXCLUDED.topic_id, process_graphs.topic_id) RETURNING id""",
                    (institution_id, tid, key, name, description, tool_path))
        gid = cur.fetchone()["id"]
    conn.commit()
    return gid


def upsert_node(conn: psycopg.Connection, graph_id: UUID, spec: NodeSpec) -> dict:
    """Store a node. If its canonical rules equal the parent's, it inherits (rules stored empty, inherits_parent=TRUE)."""
    with conn.cursor() as cur:
        parent = None
        if spec.parent_key:
            cur.execute("SELECT id, rules, rules_hash, layer FROM process_nodes WHERE graph_id=%s AND key=%s", (graph_id, spec.parent_key))
            parent = cur.fetchone()
            if not parent:
                raise LookupError(f"parent node {spec.parent_key} not found")
            if spec.layer <= parent["layer"]:
                raise ValueError("a child must be one layer below its parent")
        h = rules_hash(spec.rules)
        inherits = bool(parent) and h == parent["rules_hash"]
        stored_rules = {} if inherits else canonical_rules(spec.rules)
        cur.execute(
            """INSERT INTO process_nodes (graph_id, parent_id, layer, key, label, from_state, to_state, situation, rules, rules_hash, inherits_parent, source_urls)
               VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s::jsonb,%s,%s,%s)
               ON CONFLICT (graph_id, key) DO UPDATE SET parent_id=EXCLUDED.parent_id, layer=EXCLUDED.layer, label=EXCLUDED.label, from_state=EXCLUDED.from_state,
                 to_state=EXCLUDED.to_state, situation=EXCLUDED.situation, rules=EXCLUDED.rules, rules_hash=EXCLUDED.rules_hash, inherits_parent=EXCLUDED.inherits_parent,
                 source_urls=EXCLUDED.source_urls, updated_at=now() RETURNING id""",
            (graph_id, parent["id"] if parent else None, spec.layer, spec.key, spec.label, spec.from_state, spec.to_state, spec.situation, json.dumps(stored_rules), h, inherits, spec.source_urls),
        )
        nid = cur.fetchone()["id"]
        for cid in spec.claim_ids:
            cur.execute("INSERT INTO process_node_claims (node_id, claim_id) VALUES (%s,%s) ON CONFLICT DO NOTHING", (nid, cid))
    conn.commit()
    return {"node_id": str(nid), "inherits_parent": inherits, "rules_hash": h}


def effective_rules(conn: psycopg.Connection, node_id: UUID) -> dict:
    """Rules with inheritance resolved: a node that inherits returns its nearest ancestor's rules; otherwise its own
    merged over the parent's (child keys override)."""
    chain = []
    with conn.cursor() as cur:
        cur_id = node_id
        while cur_id:
            cur.execute("SELECT id, parent_id, rules, inherits_parent FROM process_nodes WHERE id=%s", (cur_id,))
            r = cur.fetchone()
            if not r:
                break
            chain.append(r)
            cur_id = r["parent_id"]
    merged: dict = {}
    for r in reversed(chain):  # root first
        if r["inherits_parent"]:
            continue
        merged.update(r["rules"] or {})
    return merged


def demand_for_node(conn: psycopg.Connection, graph_id: UUID, node_key: str, *, institution_id: UUID) -> dict:
    """Observed demand for a node: observed (non-hypothesis) questions whose cluster label or text mentions the node's
    label/states, counted as independent occurrences; plus query targets naming its page path."""
    with conn.cursor() as cur:
        cur.execute("SELECT label, from_state, to_state, situation, page_path FROM process_nodes WHERE graph_id=%s AND key=%s", (graph_id, node_key))
        n = cur.fetchone()
        terms = [t for t in (n["label"], n["from_state"], n["to_state"], n["situation"]) if t]
        cur.execute("""SELECT count(DISTINCT COALESCE(source_ref, id::text)) AS n FROM questions WHERE institution_id=%s AND NOT is_hypothesis AND
                       (%s::text IS NOT NULL AND lower(raw_text) LIKE '%%' || lower(%s) || '%%')""", (institution_id, n["label"], n["label"]))
        occ = cur.fetchone()["n"]
        targets = 0
        if n["page_path"]:
            cur.execute("SELECT count(*) AS n FROM query_targets WHERE page_path=%s", (n["page_path"],))
            targets = cur.fetchone()["n"]
    return {"independent_questions": int(occ), "query_targets": int(targets), "terms": terms}


def decide_pages(conn: psycopg.Connection, graph_id: UUID, *, institution_id: UUID, school_slug: str, topic_key: str, demand_lookup=None) -> list[dict]:
    """Compute the page decision for every node (R47). demand_lookup(node_key) -> {independent_questions, query_targets} may be injected (tests)."""
    with conn.cursor() as cur:
        cur.execute("SELECT id, key, label, layer, parent_id, rules_hash, inherits_parent FROM process_nodes WHERE graph_id=%s ORDER BY layer, key", (graph_id,))
        nodes = [dict(r) for r in cur.fetchall()]
    by_id = {n["id"]: n for n in nodes}
    out = []
    with conn.cursor() as cur:
        for n in nodes:
            parent = by_id.get(n["parent_id"]) if n["parent_id"] else None
            if parent and (n["inherits_parent"] or n["rules_hash"] == parent["rules_hash"]):
                dec, why, path = "none", "rules identical to the parent node; nothing new to say", None
            else:
                d = demand_lookup(n["key"]) if demand_lookup else demand_for_node(conn, graph_id, n["key"], institution_id=institution_id)
                if d["query_targets"] >= 1 or d["independent_questions"] >= 2:
                    dec, why = "standalone", f"rules differ from parent; observed demand (queries={d['query_targets']}, independent questions={d['independent_questions']})"
                    path = f"/schools/{school_slug}/{topic_key}/{n['key']}/"
                else:
                    dec, why, path = "section", "rules differ from parent but no observed demand yet; section on the parent page", None
            if n["layer"] == 0:
                dec, why, path = "standalone", "process overview page (L0)", f"/schools/{school_slug}/{topic_key}/{n['key']}/"
            cur.execute("UPDATE process_nodes SET page_decision=%s, decision_reason=%s, page_path=%s, updated_at=now() WHERE id=%s", (dec, why, path, n["id"]))
            out.append({"key": n["key"], "layer": n["layer"], "decision": dec, "reason": why, "page_path": path})
    conn.commit()
    return out


def graph_summary(conn: psycopg.Connection, graph_id: UUID) -> dict:
    with conn.cursor() as cur:
        cur.execute("""SELECT n.key, n.label, n.layer, n.from_state, n.to_state, n.situation, n.inherits_parent, n.page_decision, n.page_path, n.source_urls,
                              (SELECT count(*) FROM process_node_claims c WHERE c.node_id=n.id) AS claims FROM process_nodes n WHERE n.graph_id=%s ORDER BY n.layer, n.key""", (graph_id,))
        nodes = [dict(r) for r in cur.fetchall()]
    return {"nodes": nodes, "by_layer": {l: sum(1 for n in nodes if n["layer"] == l) for l in range(4)},
            "decisions": {d: sum(1 for n in nodes if n["page_decision"] == d) for d in ("standalone", "section", "none")}}
