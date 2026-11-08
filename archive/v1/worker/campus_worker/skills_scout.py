"""Skill scout bookkeeping (continuous-local-run R12, R30; AT11, AT27): turn skill_eval.json outputs into
docs/ops/skill-evaluations.md and refresh docs/ops/skill-coverage.md. The guard hook reads skill-evaluations.md to
decide what may be vendored under .claude/skills/ — only rows marked `adopted` with a 40-hex SHA.

    python -m campus_worker.skills_scout merge build/runs/skill-scout-live-1.json [more.json ...]
"""
from __future__ import annotations

import json
import re
import sys
from datetime import date
from pathlib import Path

from .config import REPO_ROOT

EVAL_DOC = REPO_ROOT / "docs" / "ops" / "skill-evaluations.md"
COVERAGE_DOC = REPO_ROOT / "docs" / "ops" / "skill-coverage.md"
R30 = ["long-tail keyword and query research", "SERP and competitor gap analysis", "topical authority and cluster mapping", "content briefs", "editorial writing",
       "substantive editing", "on-page SEO (titles, meta, headings)", "structured data / schema", "internal linking", "content refresh and decay detection",
       "technical SEO audit", "snippet and answer formatting", "local and campus navigation content"]


def merge_outputs(outputs: list[dict]) -> dict:
    cands: dict[str, dict] = {}
    reviews: dict[str, dict] = {}
    benches: list[dict] = []
    adoptions: dict[str, dict] = {}
    rejections: dict[str, dict] = {}
    gaps: set[str] = set()
    uncertainties: list[str] = []
    for o in outputs:
        out = (o.get("doc") or {}).get("output") or o.get("output") or {}
        for c in out.get("candidates") or []:
            prev = cands.get(c["name"], {})
            merged = dict(prev)
            for k, v in c.items():
                if v not in (None, "", "unknown") or k not in merged:
                    merged[k] = v
            cands[c["name"]] = merged
        for r in out.get("source_reviews") or []:
            reviews[r["name"]] = r
        benches += out.get("benchmarks") or []
        for a in out.get("adoptions") or []:
            adoptions[a["name"]] = a
        for r in out.get("rejections") or []:
            rejections[r["name"]] = r
        gaps |= set(out.get("coverage_gaps") or [])
        uncertainties += (o.get("doc") or {}).get("uncertainties") or []
    return {"candidates": list(cands.values()), "reviews": reviews, "benchmarks": benches, "adoptions": adoptions, "rejections": rejections, "gaps": sorted(gaps), "uncertainties": uncertainties}


def render_evaluations(m: dict, *, runs: list[str], today: date | None = None) -> str:
    today = today or date.today()
    L = ["# Skill evaluations (specs/continuous-local-run.md R12, R30; AT11, AT27)", "",
         "This file is the authority for what may live under `.claude/skills/`. The guard hook (`.claude/hooks/guard.sh`) blocks any write into `.claude/skills/<name>/` unless `<name>` appears below with status `adopted` and a 40-hex commit SHA, or as the in-repo baseline. Rollback for any adopted skill: delete its folder and revert the adopting commit.",
         "", f"last scout run: {today.isoformat()} · runs: {', '.join(runs)}", "", "## Installed", "",
         "| name | status | source | sha | license | eval (baseline → candidate) | installed |", "|---|---|---|---|---|---|---|",
         "| `national-college-publishing` | baseline (in-repo) | `skills/national-college-publishing/` (symlink) | in-repo | repo | baseline | 2026-11-06 |"]
    for a in m["adoptions"].values():
        L.append(f"| `{a['name']}` | adopted | {a.get('url')} | {a.get('sha')} | {a.get('license')} | see benchmarks | {today.isoformat()} |")
    L += ["", "## Candidates (R12: top 10 with url, author, license, last commit, stars, what it does, hooks/scripts)", "",
          "| name | kind | url | author | license | last commit | stars | what it does | hooks | scripts | capabilities |", "|---|---|---|---|---|---|---|---|---|---|---|"]
    for c in m["candidates"]:
        L.append(f"| `{c['name']}` | {c.get('kind')} | {c.get('url')} | {c.get('author')} | {c.get('license')} | {c.get('last_commit')} | {c.get('stars')} | {(c.get('what_it_does') or '')[:140]} | {c.get('ships_hooks')} | {c.get('ships_scripts')} | {', '.join(c.get('capabilities') or [])} |")
    L += ["", "## Source reviews (top 5: full source read; reject on undisclosed network calls, out-of-scope writes, unclear license, paid account)", "",
          "| name | decision | network calls disclosed | writes in scope | license clear | paid required | reasons | files read |", "|---|---|---|---|---|---|---|---|"]
    for r in m["reviews"].values():
        L.append(f"| `{r['name']}` | **{r['decision']}** | {r.get('network_calls_disclosed')} | {r.get('writes_in_scope')} | {r.get('license_clear')} | {r.get('paid_required')} | {'; '.join(r.get('reasons') or [])[:300]} | {', '.join(r.get('files_read') or [])[:160]} |")
    L += ["", "## Benchmarks (docs/ops/skill-eval-set.md; baseline = in-repo references)", "",
          "| name | task | baseline | candidate | errors | turns | seconds | hard-rule regression | notes |", "|---|---|---|---|---|---|---|---|---|"]
    if m["benchmarks"]:
        for b in m["benchmarks"]:
            L.append(f"| `{b['name']}` | {b.get('task')} | {b.get('baseline_score')} | {b.get('candidate_score')} | {b.get('errors')} | {b.get('turns')} | {b.get('seconds')} | {b.get('hard_rule_regression')} | {(b.get('notes') or '')[:200]} |")
    else:
        L.append("| — | no benchmark rows recorded yet | | | | | | | |")
    L += ["", "## Rejected", "", "| name | reason |", "|---|---|"]
    for r in m["rejections"].values():
        L.append(f"| `{r['name']}` | {r.get('reason')} |")
    if not m["rejections"]:
        L.append("| — | none |")
    L += ["", "## Coverage gaps reported by the scout (become scout jobs, R30)", ""] + [f"- {g}" for g in m["gaps"]] + ([] if m["gaps"] else ["- none"])
    L += ["", "## Scout uncertainties (verbatim)", ""] + [f"- {u}" for u in m["uncertainties"]] + ([] if m["uncertainties"] else ["- none"])
    L.append("")
    return "\n".join(L)


TASK_CAPABILITIES = {  # eval-set task number → the R30 capabilities that task measures (docs/ops/skill-eval-set.md)
    "1": ("content briefs",), "2": ("content briefs", "local and campus navigation content"), "3": ("content briefs",),
    "4": ("substantive editing",), "5": ("on-page SEO (titles, meta, headings)", "snippet and answer formatting", "editorial writing"),
    "6": ("SERP and competitor gap analysis",),
}


def render_coverage(m: dict) -> str:
    """Refresh docs/ops/skill-coverage.md: a capability is covered by an adopted skill when a benchmark beat baseline; otherwise the
    in-repo reference stays, with the baseline score of the eval task(s) that measure that capability ("—" when no task does)."""
    by_cap: dict[str, list[dict]] = {}
    for b in m["benchmarks"]:
        task_no = str(b.get("task") or "").split("-")[0]
        for cap in TASK_CAPABILITIES.get(task_no, ()):
            by_cap.setdefault(cap, []).append(b)
    covering = {}
    for a in m["adoptions"].values():
        for cap in (next((c.get("capabilities") for c in m["candidates"] if c["name"] == a["name"]), None) or []):
            covering[cap] = a
    text = COVERAGE_DOC.read_text()
    out = []
    for line in text.splitlines():
        if line.startswith("| ") and not line.startswith("| capability") and "|" in line[2:]:
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            cap = cells[0]
            rows = [b for b in by_cap.get(cap, []) if b.get("baseline_score") is not None and b.get("turns")]
            if cap in covering:
                a = covering[cap]
                cells[1] = f"adopted `{a['name']}`"; cells[2] = a.get("sha", "")[:12]; cells[3] = "beat baseline"; cells[4] = "adopted"
            else:
                if rows:
                    cells[3] = "; ".join(sorted({f"{b['baseline_score']} (task {str(b.get('task')).split('-')[0]})" for b in rows}))
                    tried = sorted({f"`{b['name']}` {b.get('candidate_score')} vs {b['baseline_score']} on task {str(b.get('task')).split('-')[0]}" for b in rows})
                    cells[4] = "baseline kept; " + ", ".join(tried)
                else:
                    cells[3] = "— (no eval task measures it yet)"
                    cells[4] = "baseline; no benchmark"
                if cap in m["gaps"] or any(cap in g for g in m["gaps"]):
                    cells[4] = "**gap**: scout job open" + (f"; {cells[4]}" if rows else "")
            line = "| " + " | ".join(cells) + " |"
        out.append(line)
    return "\n".join(out) + "\n"


def main(argv: list[str]) -> int:
    if not argv or argv[0] != "merge":
        print(__doc__)
        return 2
    files = [Path(p) for p in argv[1:]]
    outputs = [json.loads(p.read_text()) for p in files]
    m = merge_outputs(outputs)
    EVAL_DOC.write_text(render_evaluations(m, runs=[p.name for p in files]))
    COVERAGE_DOC.write_text(render_coverage(m))
    print(json.dumps({"candidates": len(m["candidates"]), "reviews": len(m["reviews"]), "benchmarks": len(m["benchmarks"]), "adoptions": list(m["adoptions"]), "rejections": list(m["rejections"]), "gaps": m["gaps"]}, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
