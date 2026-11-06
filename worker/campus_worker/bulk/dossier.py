"""D3: assemble the school + town dossier from the database into docs/dossiers/<school>/ (JSON per section plus a readable summary.md).

The database stays the source of truth (entities, claims with their sources, conflicts, process claims); the files are a snapshot
for the owner and for the question map. Gaps are computed from what each entity type is expected to state and does not."""
from __future__ import annotations

import json
import time
from collections import Counter, defaultdict
from datetime import date, datetime, timezone
from pathlib import Path
from uuid import UUID

import psycopg

from ..config import REPO_ROOT
from .util import json_default, long_date, money_text

EXPECTED_FAMILIES = {
    "residence_hall": ("rate", "capacity", "amenity", "location", "eligibility"),
    "dining_location": ("hours", "location"),
    "library": ("hours", "location"),
    "bus_route": ("route",),
    "office": ("contact", "hours", "location"),
    "program": ("requirement", "deadline"),
    "major": ("requirement", "prerequisite"),
    "parking_lot": ("rate", "location"),
    "town_service": ("contact", "hours"),
    "park": ("location",),
}
INSTITUTION_EXPECTED = ("deadline.housing_application", "fee.housing_application", "policy.cancellation", "eligibility.residency_requirement", "deadline.financial_aid",
                        "fee.tuition", "deadline.add_drop", "process.change_major", "process.transfer_credit", "contact.housing_office")


def human_value(c: dict) -> str:
    vt = c.get("value_type")
    if vt == "money":
        return money_text(int(c["value_number"]) if c.get("value_number") is not None else None, c.get("billing_period"), c.get("price_basis"))
    if vt == "date":
        return long_date(c.get("value_date"))
    if vt == "boolean":
        return "yes" if c.get("value_bool") else "no"
    if c.get("value_number") is not None:
        n = c["value_number"]
        return f"{int(n):,}" if float(n).is_integer() else f"{n}"
    return (c.get("value_text") or "")[:400]


def load(conn: psycopg.Connection, *, institution_id: UUID) -> dict:
    with conn.cursor() as cur:
        cur.execute("SELECT id, canonical_name, slug, city, state_code, institution_type, control, identity_status FROM institutions WHERE id=%s", (institution_id,))
        inst = dict(cur.fetchone())
        cur.execute("SELECT source_domains, audiences, coverage_status, academic_calendar, timezone FROM school_configs WHERE institution_id=%s LIMIT 1", (institution_id,))
        cfg = dict(cur.fetchone() or {})
        cur.execute("SELECT id, name, slug, kind, state_code FROM places ORDER BY name")
        places = [dict(r) for r in cur.fetchall()]
        cur.execute("""SELECT e.id, e.name, e.slug, e.entity_type, t.key AS topic_key, e.attributes FROM entities e JOIN topics t ON t.id=e.topic_id
                       WHERE e.institution_id=%s AND e.status='active' ORDER BY e.entity_type, e.name""", (institution_id,))
        entities = [dict(r) for r in cur.fetchall()]
        cur.execute("""SELECT c.id, c.entity_id, c.field, c.value_type, c.value_text, c.value_number, c.value_bool, c.value_date, c.billing_period, c.price_basis, c.room_type,
                              c.audience_applicability, c.academic_year, c.is_critical, c.conflict_status, c.retrieved_at, t.key AS topic_key,
                              COALESCE(json_agg(json_build_object('url', COALESCE(s.final_url, r.canonical_url), 'fetched_at', s.fetched_at, 'excerpt', cs.excerpt, 'snapshot_id', s.id, 'title', r.title)
                                       ORDER BY s.fetched_at DESC) FILTER (WHERE s.id IS NOT NULL), '[]'::json) AS sources
                       FROM claims c JOIN topics t ON t.id=c.topic_id
                       LEFT JOIN claim_sources cs ON cs.claim_id=c.id LEFT JOIN fetch_snapshots s ON s.id=cs.snapshot_id LEFT JOIN source_registry r ON r.id=s.source_id
                       WHERE c.institution_id=%s AND c.superseded_by_id IS NULL AND c.evidence_category='verified_fact'
                       GROUP BY c.id, t.key ORDER BY c.field""", (institution_id,))
        claims = [dict(r) for r in cur.fetchall()]
        cur.execute("""SELECT g.key, g.name, g.description, t.key AS topic_key,
                              (SELECT json_agg(json_build_object('layer', n.layer, 'key', n.key, 'label', n.label, 'rules', n.rules, 'page_decision', n.page_decision) ORDER BY n.layer, n.key) FROM process_nodes n WHERE n.graph_id=g.id) AS nodes
                       FROM process_graphs g LEFT JOIN topics t ON t.id=g.topic_id WHERE g.institution_id=%s""", (institution_id,))
        graphs = [dict(r) for r in cur.fetchall()]
        cur.execute("""SELECT x.id, x.conflict_type, x.status, a.field AS field_a, b.field AS field_b, a.value_text AS a_text, b.value_text AS b_text, a.value_number AS a_num, b.value_number AS b_num,
                              a.academic_year AS a_year, b.academic_year AS b_year FROM conflicts x JOIN claims a ON a.id=x.claim_a_id JOIN claims b ON b.id=x.claim_b_id WHERE x.institution_id=%s AND x.status='open'""", (institution_id,))
        conflicts = [dict(r) for r in cur.fetchall()]
        cur.execute("""SELECT COALESCE(r.crawl_section, r.source_family, 'other') AS section, count(DISTINCT r.id) AS pages, max(s.fetched_at) AS last_fetched
                       FROM source_registry r JOIN fetch_snapshots s ON s.source_id=r.id WHERE s.outcome='ok' AND s.retained_text IS NOT NULL AND r.source_kind LIKE 'official%%'
                         AND (r.institution_id=%s OR r.place_id IS NOT NULL) GROUP BY 1 ORDER BY 2 DESC""", (institution_id,))
        crawl = [dict(r) for r in cur.fetchall()]
    return {"institution": inst, "config": cfg, "places": places, "entities": entities, "claims": claims, "graphs": graphs, "conflicts": conflicts, "crawl": crawl}


def assemble(data: dict, *, today: date | None = None) -> dict:
    today = today or datetime.now(timezone.utc).date()
    claims = data["claims"]
    for c in claims:
        c["value"] = human_value(c)
        c["family"] = c["field"].split(".", 1)[0]
    by_entity: dict = defaultdict(list)
    for c in claims:
        if c.get("entity_id"):
            by_entity[c["entity_id"]].append(c)
    entities = []
    for e in data["entities"]:
        ecs = by_entity.get(e["id"], [])
        fams = sorted({c["family"] for c in ecs})
        entities.append({**e, "claim_count": len(ecs), "families": fams,
                         "facts": [{"field": c["field"], "value": c["value"], "academic_year": c.get("academic_year"), "source": (c["sources"][0]["url"] if c["sources"] else None)} for c in ecs[:12]]})
    processes = [{"name": json.loads(c["value_text"]).get("name") if (c.get("value_text") or "").startswith("{") else c["field"], "field": c["field"],
                  "steps": (json.loads(c["value_text"]).get("steps") if (c.get("value_text") or "").startswith("{") else [c.get("value_text")]), "source": (c["sources"][0]["url"] if c["sources"] else None), "claim_id": str(c["id"])}
                 for c in claims if c["family"] == "process"]
    for g in data["graphs"]:
        processes.append({"name": g["name"], "field": f"graph.{g['key']}", "steps": [n["label"] for n in (g.get("nodes") or []) if n.get("layer", 0) <= 1], "source": None, "graph": True})
    deadlines = sorted([c for c in claims if c["family"] == "deadline" or c.get("value_date")], key=lambda c: (c.get("value_date") or date.max, c["field"]))
    costs = [c for c in claims if c["value_type"] == "money" or c["family"] in ("fee", "rate", "cost")]
    policies = [c for c in claims if c["family"] in ("policy", "eligibility", "requirement", "prerequisite", "agreement", "accessibility")]
    contacts = [c for c in claims if c["family"] in ("contact", "hours", "location", "address")]
    town_topics = {"town_services", "town_transit_local", "town_transit_intercity", "town_neighborhoods", "town_offcampus_housing", "town_food", "town_outdoors", "town_weather", "town_jobs", "town_government"}
    town = {"places": data["places"], "entities": [e for e in entities if e["entity_type"] in ("town_service", "park", "bus_route") or e["topic_key"] in town_topics],
            "claims": [c for c in claims if c["topic_key"] in town_topics]}
    gaps = []
    for e in entities:
        expected = EXPECTED_FAMILIES.get(e["entity_type"], ())
        missing = [f for f in expected if f not in e["families"]]
        if missing:
            gaps.append({"entity": e["name"], "entity_type": e["entity_type"], "missing": missing})
    fields_present = {c["field"] for c in claims}
    inst_gaps = [f for f in INSTITUTION_EXPECTED if not any(x == f or x.startswith(f + ".") for x in fields_present)]
    stats = {"entities": len(entities), "entities_with_facts": sum(1 for e in entities if e["claim_count"]), "claims": len(claims), "claims_with_quote": sum(1 for c in claims if any(s.get("excerpt") for s in c["sources"])),
             "processes": len(processes), "deadlines": len(deadlines), "costs": len(costs), "policies": len(policies), "contacts": len(contacts), "conflicts": len(data["conflicts"]),
             "entity_gaps": len(gaps), "institution_gaps": len(inst_gaps), "pages_crawled": sum(r["pages"] for r in data["crawl"]), "by_entity_type": dict(Counter(e["entity_type"] for e in entities))}
    return {"identity": {**data["institution"], "config": data["config"]}, "entities": entities, "claims": claims, "processes": processes, "deadlines": deadlines, "costs": costs,
            "policies": policies, "contacts": contacts, "town": town, "conflicts": data["conflicts"], "gaps": {"entities": gaps, "institution": inst_gaps}, "crawl": data["crawl"], "stats": stats, "built": today.isoformat()}


def summary_md(d: dict, *, question_stats: dict | None = None, minutes: float | None = None, cost_minor: int = 0) -> str:
    i, s = d["identity"], d["stats"]
    lines = [f"# {i['canonical_name']} dossier", f"Built {long_date(d['built'])} from {s['pages_crawled']} crawled official pages. Every fact below carries a verbatim quote from its page in the database.", ""]
    lines += ["## Numbers", f"- Entities: {s['entities']} ({', '.join(f'{v} {k.replace(chr(95), chr(32))}' for k, v in sorted(s['by_entity_type'].items(), key=lambda kv: -kv[1]))}); {s['entities_with_facts']} have at least one fact.",
              f"- Claims: {s['claims']} ({s['claims_with_quote']} with a quote); costs {s['costs']}, deadlines {s['deadlines']}, policies {s['policies']}, contacts {s['contacts']}, processes {s['processes']}.",
              f"- Open conflicts between official pages: {s['conflicts']}. Gaps: {s['entity_gaps']} entities missing an expected fact family; {s['institution_gaps']} institution-level facts not found.",
              f"- Pages crawled by section: " + ", ".join(f"{r['section']} {r['pages']}" for r in d["crawl"][:14]) + ".", ""]
    if question_stats:
        lines += ["## Question map", f"- {question_stats.get('total', 0)} deduped questions ({question_stats.get('generated', 0)} generated from the dossier, {question_stats.get('cluster', 0)} from observed search clusters, {question_stats.get('yaml', 0)} from data/questions).",
                  f"- Incumbent classes: " + ", ".join(f"{k} {v}" for k, v in sorted((question_stats.get('by_class') or {}).items(), key=lambda kv: -kv[1])) + ".", ""]
    lines += ["## Deadlines (dated)"]
    seen_dl: dict = {}
    for c in d["deadlines"]:
        if c.get("value_date"):
            key = (str(c["value_date"]), c["sources"][0]["url"] if c["sources"] else "")
            seen_dl.setdefault(key, []).append(c["field"].split(".", 1)[-1].replace("_", " ").replace(".", " "))
    for (day, url), names in list(seen_dl.items())[:25]:
        lines.append(f"- {long_date(day)}: {'; '.join(dict.fromkeys(names))} — {url or 'no source url'}")
    lines += ["", "## Costs (sample)"]
    for c in d["costs"][:25]:
        ent = next((e["name"] for e in d["entities"] if e["id"] == c.get("entity_id")), None)
        lines.append(f"- {c['field'].replace('_', ' ')}{' for ' + ent if ent else ''}: {c['value']}{' (' + c['academic_year'] + ')' if c.get('academic_year') else ''}")
    lines += ["", "## Processes"]
    for p in d["processes"][:20]:
        lines.append(f"- {p['name']}: {len(p.get('steps') or [])} steps" + (f" — {p['source']}" if p.get("source") else ""))
    lines += ["", "## Conflicts between official pages"]
    lines += [f"- {x['field_a']} vs {x['field_b']} ({x['conflict_type']}): {x.get('a_text') or x.get('a_num')} vs {x.get('b_text') or x.get('b_num')}" for x in d["conflicts"][:20]] or ["- none open"]
    lines += ["", "## Gaps (what the official sites do not say)"]
    lines += [f"- {g['entity']} ({g['entity_type'].replace('_', ' ')}): no {', '.join(g['missing'])} facts" for g in d["gaps"]["entities"][:25]]
    lines += [f"- Institution-level: no {f} claim" for f in d["gaps"]["institution"]]
    lines += ["", "## Cost and time", f"- Extraction cost recorded: ${cost_minor / 100:.2f}; dossier build {minutes if minutes is not None else '?'} minutes.", ""]
    return "\n".join(lines)


def build(conn: psycopg.Connection, *, slug: str, out_dir: Path | None = None, question_stats: dict | None = None, minutes: float | None = None, cost_minor: int = 0) -> dict:
    t0 = time.monotonic()
    with conn.cursor() as cur:
        cur.execute("SELECT id FROM institutions WHERE slug=%s", (slug,))
        inst = cur.fetchone()
    if not inst:
        raise LookupError(slug)
    d = assemble(load(conn, institution_id=inst["id"]))
    out = out_dir or (REPO_ROOT / "docs" / "dossiers" / slug)
    out.mkdir(parents=True, exist_ok=True)
    for key in ("identity", "entities", "claims", "processes", "deadlines", "costs", "policies", "contacts", "town", "conflicts", "gaps", "crawl", "stats"):
        (out / f"{key}.json").write_text(json.dumps(d[key], indent=1, default=json_default))
    (out / "summary.md").write_text(summary_md(d, question_stats=question_stats, minutes=minutes if minutes is not None else round((time.monotonic() - t0) / 60, 2), cost_minor=cost_minor))
    with conn.cursor() as cur:
        cur.execute("INSERT INTO dossier_runs (institution_id, path, stats, minutes, cost_minor) VALUES (%s, %s, %s::jsonb, %s, %s)",
                    (inst["id"], str(out.relative_to(REPO_ROOT)) if str(out).startswith(str(REPO_ROOT)) else str(out), json.dumps(d["stats"] | {"questions": question_stats or {}}, default=json_default), minutes, cost_minor))
    conn.commit()
    return d["stats"] | {"path": str(out)}
