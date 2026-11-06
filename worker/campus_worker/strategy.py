"""Search strategy persistence (continuous-local-run R14, R23, R45 cannibalization; AT13).

The search-strategist agent returns search_strategy.json. This module:
- validates the cluster map: one page per query group, no two pages targeting the same query (query_targets PK),
- stores the strategy (strategies table) and its query targets,
- writes the readable docs/strategy/<school>/<topic>.md with every R14 section,
- records capture formats on clusters (R23) and exposes the win plan for the planner's brief (R14).
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from uuid import UUID

import psycopg

from .config import REPO_ROOT
from .search_cache import query_norm

SECTIONS = ("Cluster map", "Win plan per page", "Hub and internal-link plan", "Trust signals", "Refresh cadence", "Win criteria")


class CannibalizationError(ValueError):
    pass


def check_cluster_map(doc: dict, *, existing_targets: dict[str, str] | None = None) -> list[str]:
    """Defects in the cluster map: a query assigned to two pages (inside the doc or against already-published targets)."""
    errs = []
    seen: dict[str, str] = {}
    for row in doc.get("cluster_map") or []:
        for q in row.get("queries") or []:
            qn = query_norm(q)
            if qn in seen and seen[qn] != row["page_path"]:
                errs.append(f"query '{q}' targeted by two pages: {seen[qn]} and {row['page_path']}")
            seen[qn] = row["page_path"]
            if existing_targets and qn in existing_targets and existing_targets[qn] != row["page_path"]:
                errs.append(f"query '{q}' already targeted by published page {existing_targets[qn]}")
    paths = [r["page_path"] for r in doc.get("cluster_map") or []]
    plan_paths = {w["page_path"] for w in doc.get("win_plans") or []}
    for p in paths:
        if p not in plan_paths and (doc.get("cluster_map") and next(r for r in doc["cluster_map"] if r["page_path"] == p).get("format") != "section"):
            errs.append(f"page {p} has no win plan")
    return errs


def existing_targets(conn: psycopg.Connection) -> dict[str, str]:
    with conn.cursor() as cur:
        cur.execute("SELECT query_norm, page_path FROM query_targets")
        return {r["query_norm"]: r["page_path"] for r in cur.fetchall()}


def store(conn: psycopg.Connection, doc: dict, *, institution_id: UUID | None, place_id: UUID | None, topic_key: str, md_root: Path | None = None) -> dict:
    errs = check_cluster_map(doc, existing_targets=_targets_for_other_strategies(conn, institution_id, place_id, topic_key))
    if errs:
        raise CannibalizationError("; ".join(errs))
    with conn.cursor() as cur:
        cur.execute("SELECT id FROM topics WHERE key=%s", (topic_key,))
        topic = cur.fetchone()
        topic_id = topic["id"] if topic else None
        cur.execute("SELECT COALESCE(max(version),0)+1 AS v FROM strategies WHERE institution_id IS NOT DISTINCT FROM %s AND place_id IS NOT DISTINCT FROM %s AND topic_id IS NOT DISTINCT FROM %s",
                    (institution_id, place_id, topic_id))
        version = cur.fetchone()["v"]
        cur.execute("INSERT INTO strategies (institution_id, place_id, topic_id, version, doc) VALUES (%s,%s,%s,%s,%s::jsonb) RETURNING id", (institution_id, place_id, topic_id, version, json.dumps(doc)))
        sid = cur.fetchone()["id"]
        # replace this scope/topic's query targets with the new map (older versions of the same strategy are superseded)
        cur.execute("""DELETE FROM query_targets WHERE strategy_id IN (SELECT id FROM strategies WHERE institution_id IS NOT DISTINCT FROM %s AND place_id IS NOT DISTINCT FROM %s AND topic_id IS NOT DISTINCT FROM %s AND id<>%s)""",
                    (institution_id, place_id, topic_id, sid))
        for row in doc.get("cluster_map") or []:
            for i, q in enumerate(row.get("queries") or []):
                cur.execute("""INSERT INTO query_targets (query_norm, page_path, query_group, strategy_id, is_primary) VALUES (%s,%s,%s,%s,%s)
                               ON CONFLICT (query_norm) DO UPDATE SET page_path=EXCLUDED.page_path, query_group=EXCLUDED.query_group, strategy_id=EXCLUDED.strategy_id, is_primary=EXCLUDED.is_primary""",
                            (query_norm(q), row["page_path"], row["query_group"], sid, i == 0))
            if row.get("cluster_id"):
                try:
                    cur.execute("UPDATE intent_clusters SET capture_format=%s, updated_at=now() WHERE id=%s", (row.get("format"), UUID(str(row["cluster_id"]))))
                except (ValueError, psycopg.Error):
                    pass
    conn.commit()
    md = write_markdown(doc, scope_slug=(doc.get("scope") or {}).get("school_slug") or (doc.get("scope") or {}).get("town_slug") or "scope", topic_key=topic_key, root=md_root, version=version)
    with conn.cursor() as cur:
        cur.execute("UPDATE strategies SET md_path=%s WHERE id=%s", (str(md.relative_to(REPO_ROOT)) if md.is_relative_to(REPO_ROOT) else str(md), sid))
    conn.commit()
    return {"strategy_id": str(sid), "version": version, "md_path": str(md), "targets": sum(len(r.get("queries") or []) for r in doc.get("cluster_map") or [])}


def _targets_for_other_strategies(conn, institution_id, place_id, topic_key) -> dict[str, str]:
    with conn.cursor() as cur:
        cur.execute("""SELECT q.query_norm, q.page_path FROM query_targets q JOIN strategies s ON s.id=q.strategy_id LEFT JOIN topics t ON t.id=s.topic_id
                       WHERE NOT (s.institution_id IS NOT DISTINCT FROM %s AND s.place_id IS NOT DISTINCT FROM %s AND t.key IS NOT DISTINCT FROM %s)""", (institution_id, place_id, topic_key))
        return {r["query_norm"]: r["page_path"] for r in cur.fetchall()}


def write_markdown(doc: dict, *, scope_slug: str, topic_key: str, root: Path | None = None, version: int = 1) -> Path:
    root = root or (REPO_ROOT / "docs" / "strategy")
    p = root / scope_slug / f"{topic_key}.md"
    p.parent.mkdir(parents=True, exist_ok=True)
    L = [f"# Search strategy: {scope_slug} · {topic_key} (v{version})", "",
         f"Generated {datetime.now(timezone.utc).isoformat(timespec='seconds')} from the search-strategist contract (specs/continuous-local-run.md R14, R23). Observations are labeled "
         "'observed via search tool'; nothing here is a measured rank or volume.", ""]
    L += ["## Cluster map", "", "One page or tool per query group; no two pages target the same query.", "", "| query group | queries | page | format |", "|---|---|---|---|"]
    for r in doc.get("cluster_map") or []:
        L.append(f"| {r['query_group']} | {'; '.join(r.get('queries') or [])} | `{r['page_path']}` | {r['format']} |")
    L += ["", "## Win plan per page", ""]
    for w in doc.get("win_plans") or []:
        L += [f"### `{w['page_path']}`", "", f"- **Contribution that beats current results:** {w['contribution']}", f"- **Target title (≤60):** {w['target_title']}", f"- **H1:** {w['h1']}",
              f"- **Answer-first intro:** {w['answer_first_intro']}", f"- **Snippet formats:** {', '.join(w.get('snippet_formats') or [])}"]
        if w.get("secondary_questions"):
            L.append("- **Secondary questions (H2/H3):** " + "; ".join(w["secondary_questions"]))
        L.append("- **FAQ block:** " + ("; ".join(w["faq_real_questions"]) if w.get("faq_real_questions") else "none (no real observed questions)"))
        for b in w.get("beats") or []:
            L.append(f"- beats {b['url']}: {b['how']}")
        L.append("")
    L += ["## Hub and internal-link plan", "", "| from | to | anchor text |", "|---|---|---|"]
    for l in doc.get("internal_links") or []:
        L.append(f"| `{l['from']}` | `{l['to']}` | {l['anchor_text']} |")
    ts = doc.get("trust_signals") or {}
    L += ["", "## Trust signals", "", f"- sources section: {ts.get('sources_section')}", f"- methods page: {ts.get('methods_link')}", f"- visible updated date: {ts.get('updated_date')}", f"- corrections: {ts.get('corrections_link')}", ""]
    L += ["## Refresh cadence", "", "| page | every (days) | reason |", "|---|---|---|"]
    for r in doc.get("refresh_cadence") or []:
        L.append(f"| `{r['page_path']}` | {r['cadence_days']} | {r['reason']} |")
    L += ["", "## Win criteria", "", "| page | queries to re-check | after (days) | success |", "|---|---|---|---|"]
    for r in doc.get("win_criteria") or []:
        L.append(f"| `{r['page_path']}` | {'; '.join(r.get('queries') or [])} | {r['check_after_days']} | {r.get('success', '')} |")
    L.append("")
    p.write_text("\n".join(L))
    return p


def win_plan_for(conn: psycopg.Connection, page_path: str) -> dict | None:
    """The latest win plan for a page path (the planner carries it into the brief, R14)."""
    with conn.cursor() as cur:
        cur.execute("SELECT doc FROM strategies ORDER BY created_at DESC")
        for r in cur.fetchall():
            for w in (r["doc"].get("win_plans") or []):
                if w.get("page_path") == page_path:
                    return w
    return None


def primary_query_conflict(conn: psycopg.Connection, page_path: str, primary_query: str) -> str | None:
    """R45 cannibalization: the primary query must not be targeted by any other page."""
    with conn.cursor() as cur:
        cur.execute("SELECT page_path FROM query_targets WHERE query_norm=%s", (query_norm(primary_query),))
        r = cur.fetchone()
    if r and r["page_path"] != page_path:
        return r["page_path"]
    return None
