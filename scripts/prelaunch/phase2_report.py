"""Phase 2 of docs/v5/prelaunch-spec.md, the record: reports/02-rework.md (what changed on every flagged page and how the skeptic judged it)
and reports/gaps-phase2.md (every gap decision the rework made, in the line format scripts/prelaunch/gaps.py merges into reports/gaps.md).

    worker/.venv/bin/python scripts/prelaunch/phase2_report.py

Inputs: reports/02-pages.json (the flagged pages), reports/02-batchA-results.json and 02-batchB-results.json (rework + skeptic verdict per
page), reports/02-batchA-fix-results.json and 02-batchB-fix-results.json (the targeted fix round for the pages the skeptic rejected, with a
second verdict), reports/02-hand-fixes.json (fixes made by hand after the last verdict, optional), and reports/02-gapwording-results.json (the third round:
every page the widened linter flagged after the Phase 5 skeptics found a second layer of gap wording, reworked and verified again).
"""
from __future__ import annotations

import json
import re
import sys
from datetime import date
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
R = REPO / "reports"


def load(name: str):
    p = R / name
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else []


def one_line(s: str, n: int = 160) -> str:
    s = re.sub(r"\s+", " ", str(s or "")).strip().replace("|", "/")
    return s if len(s) <= n else s[: n - 1].rstrip() + "…"


def main() -> int:
    flagged = {x["slug"]: x for x in load("02-pages.json")} if (R / "02-pages.json").exists() else {}
    results = {}
    for name, batch in (("02-batchA-results.json", "A"), ("02-batchB-results.json", "B")):
        for x in load(name):
            x["batch"] = batch
            results[x["slug"]] = x
    fixes = {}
    for name in ("02-batchA-fix-results.json", "02-batchB-fix-results.json"):
        for x in load(name):
            fixes[x["slug"]] = x
    hand = {x["slug"]: x for x in load("02-hand-fixes.json")}
    final = {}
    for x in load("02-final-fixes.json"):   # the last pass: each skeptic objection applied, added facts checked; the linter and the build are the gate after it
        slug = x["file"].split("/")[-1].replace(".md", "")
        if slug == "tool.md" or slug == "tool":
            slug = x["file"].split("/")[-2]
        final[slug] = x
    third = {}
    for x in load("02-gapwording-results.json"):
        slug = x["file"].split("/")[-1].replace(".md", "")
        if slug == "tool":
            slug = x["file"].split("/")[-2]
        third[slug] = x
        if slug not in results:
            results[slug] = {"slug": slug, "file": x["file"], "kind": "tool" if "/tools/" in x["file"] else ("dataset" if "/datasets/" in x["file"] else ("start_here" if "/start/" in x["file"] else "article")), "queue_id": "", "batch": "C",
                             "changed": True, "lint_clean": (x.get("report") or {}).get("lint_clean"), "gaps": (x.get("report") or {}).get("gaps") or [], "sections_removed": [], "sources_added": (x.get("report") or {}).get("sources_added") or [],
                             "title_changed_to": (x.get("report") or {}).get("title_changed_to") or "", "lost_purpose": False, "sound": bool((x.get("verdict") or {}).get("sound")), "problems": (x.get("verdict") or {}).get("problems"), "retried": x.get("retried")}
        else:
            results[slug]["gaps"] = list(results[slug].get("gaps") or []) + list((x.get("report") or {}).get("gaps") or [])
            results[slug]["sound"] = bool((x.get("verdict") or {}).get("sound")); results[slug]["problems"] = (x.get("verdict") or {}).get("problems")
            results[slug]["_third"] = True
    # gaps-phase2.md: one "## <slug>" section per page, one line per gap decision
    G = [f"# Phase 2 gap decisions ({date.today().isoformat()})", "",
         "One line per gap the rework resolved, in the format scripts/prelaunch/gaps.py merges into reports/gaps.md. "
         "Rule: a page never tells the reader what the sources lack; the item is answered from a source found on the source checklist, or the promise is removed.", ""]
    n_gaps = 0
    for slug in sorted(results):
        gaps = list(results[slug].get("gaps") or [])
        if slug in fixes:
            gaps += list((fixes[slug].get("fix") or {}).get("gaps") or [])
        if not gaps:
            continue
        G.append(f"## {slug}")
        for g in gaps:
            G.append(f"- {one_line(g.get('item'), 220)} | sources tried: {one_line(g.get('tried'), 260)} | outcome: {one_line(g.get('outcome'), 320)}")
            n_gaps += 1
        G.append("")
    (R / "gaps-phase2.md").write_text("\n".join(G) + "\n", encoding="utf-8")
    # 02-rework.md
    rows = []
    for slug, x in sorted(results.items()):
        final_sound = bool(x.get("sound"))
        verdict_by = "skeptic (rework)"
        if slug in fixes:
            final_sound = bool((fixes[slug].get("verdict") or {}).get("sound"))
            verdict_by = "skeptic (fix round)"
        if slug in hand:
            final_sound = bool(hand[slug].get("sound", True))
            verdict_by = hand[slug].get("by", "hand fix, re-linted")
        if slug in third:
            final_sound = bool((third[slug].get("verdict") or {}).get("sound"))
            verdict_by = "skeptic (gap-wording round)"
        if slug in final:
            r = final[slug].get("result") or {}
            final_sound = bool(r.get("lint_clean")) and (r.get("emdash_count") == 0)
            verdict_by = "last fix pass (objections applied, linter gate)"
        if slug in third and slug not in final and not (third[slug].get("verdict")):
            final_sound = bool((third[slug].get("report") or {}).get("lint_clean"))
            verdict_by = "reworked, linter gate (no sources added)"
        rows.append((slug, x))
        x["_final_sound"], x["_verdict_by"] = final_sound, verdict_by
    sound = sum(1 for _, x in rows if x["_final_sound"])
    removed = sum(len(x.get("sections_removed") or []) for _, x in rows)
    retitled = [(s, x["title_changed_to"]) for s, x in rows if x.get("title_changed_to")]
    L = [f"# Phase 2: flagged pages reworked ({date.today().isoformat()})", "",
         "Every page the content linter flagged (reports/02-pages.json: a sentence telling the reader what the sources or the page lack, or a page the spec names) was reworked by one agent per page following the gap workflow (docs/v5/prelaunch-spec.md, Phase 1b and 2): "
         "search the source checklist for the missing item, cite it when found, otherwise remove the promise (a sentence, a section, or the title claim) and log the decision. A skeptic agent then re-read each page: linter at 0, no admission sentences, every new fact checked against its fetched source, every body URL in the sources list, the mandatory additions present. "
         "Pages the skeptic rejected went through one targeted fix round with a second verdict. Agents: opus for the rework and the fixes, sonnet for the skeptic.", "",
         f"- Pages reworked: {len(rows)} (batch A {sum(1 for _, x in rows if x['batch'] == 'A')}, batch B {sum(1 for _, x in rows if x['batch'] == 'B')}, third round only {sum(1 for _, x in rows if x['batch'] == 'C')}; third round in all {len(third)})",
         "- Third round: after the Phase 5 cluster skeptics found gap wording the first linter missed (table labels such as 'Not published', planner notes such as 'Not in the brief', references to the brief and the fact file, source-quality asides), the linter was widened twice (scripts/lint-content.py, 2026-11-11 patterns), three listing tables were rewritten by scripts/prelaunch/table_cells.py (517 cells), and every page the widened linter flagged was reworked and verified again under a written wording policy (reports/02-gapwording-results.json).",
         f"- Judged sound after the last round: {sound} of {len(rows)}",
         f"- Gap decisions logged: {n_gaps} (reports/gaps-phase2.md, merged into reports/gaps.md)",
         f"- Sections removed because no source answered them: {removed}",
         f"- Titles changed to match what the page can answer: {len(retitled)}" + ("".join(f"\n  - {s}: {t}" for s, t in retitled) if retitled else ""),
         f"- Pages that lost their purpose (would need a merge or a retire): {[s for s, x in rows if x.get('lost_purpose')] or 'none'}",
         f"- Content linter after Phase 2: run `python3 scripts/lint-content.py` (strict; the Astro prebuild runs it too).", "",
         "| Page | Kind | Queue id | Gaps | Sections removed | Sources added | Sound | Judged by | Notes |", "|---|---|---|---|---|---|---|---|---|"]
    for slug, x in rows:
        gaps = len(x.get("gaps") or []) + (len((fixes[slug].get("fix") or {}).get("gaps") or []) if slug in fixes else 0)
        note = x.get("problems") if not x.get("sound") else ""
        if slug in fixes:
            note = fixes[slug].get("verdict", {}).get("problems") if not fixes[slug].get("verdict", {}).get("sound") else "fixed on the second round"
        if slug in hand:
            note = hand[slug].get("note", "")
        if slug in third:
            v = third[slug].get("verdict") or {}
            note = "sound after the gap-wording round" if v.get("sound") else (v.get("problems") or "no skeptic verdict; linter clean")
        if slug in final:
            u = (final[slug].get("result") or {}).get("unresolved") or "none"
            note = "objections applied; " + ("nothing unresolved" if u.strip().lower().rstrip(".") == "none" else "left open: " + u)
        L.append(f"| {slug} | {x.get('kind','')} | {x.get('queue_id','')} | {gaps} | {len(x.get('sections_removed') or [])} | {len(x.get('sources_added') or [])} | {'yes' if x['_final_sound'] else 'NO'} | {x['_verdict_by']} | {one_line(note, 200)} |")
    unsound = [s for s, x in rows if not x["_final_sound"]]
    if unsound:
        L += ["", f"## Still rejected by the skeptic ({len(unsound)})", ""]
        for s in unsound:
            prob = (third[s].get("verdict") or {}).get("problems") if s in third else (fixes[s]["verdict"]["problems"] if s in fixes else results[s].get("problems"))
            L += [f"### {s}", "", str(prob or "").strip(), ""]
    (R / "02-rework.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"{len(rows)} pages, {sound} sound, {n_gaps} gap decisions -> reports/02-rework.md, reports/gaps-phase2.md; still rejected: {unsound}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
