"""Phase 9c of docs/v5/prelaunch-spec.md: wave release, promotion, stop rule and kill switch. Nothing here deploys or changes robots.txt.

    worker/.venv/bin/python scripts/prelaunch/waves.py plan [--size 400]     # write config/waves.json: wave 1 = the top eligible pages by score and demand
    worker/.venv/bin/python scripts/prelaunch/waves.py status                 # waves, their sizes, which are promoted, the stop rule's verdict for the next wave
    worker/.venv/bin/python scripts/prelaunch/waves.py promote <n>            # set index: true on every page of wave n (refused when the stop rule fails), then rebuild
    worker/.venv/bin/python scripts/prelaunch/waves.py kill <section>         # set index: false on every page of a section (the kill switch), then rebuild

Eligibility comes from reports/09-eligibility.csv (scripts/prelaunch/score_pages.py). The stop rule reads config/wave-metrics.json, which Ajay
fills from Search Console per wave: {"1": {"indexed_pct": 55, "weeks": 4, "impressions_trend": "rising", "audit_error_rate_pct": 1.2, "manual_actions": 0}}.
The next wave is allowed only if the previous wave is at least 50 percent indexed after 3 weeks or more, impressions are flat or rising,
the latest weekly audit error rate is under 3 percent, and there are no manual actions. index: true pages render index, follow and enter
the sitemap; everything else stays noindex, follow (site/src/layouts/Base.astro, site/src/pages/sitemap.xml.ts).
"""
from __future__ import annotations

import csv
import json
import re
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
WAVES = REPO / "config" / "waves.json"
METRICS = REPO / "config" / "wave-metrics.json"
ELIG = REPO / "reports" / "09-eligibility.csv"
SECTION_FLOOR = {"transfer": 12}   # the transfer section always rides in wave 1 (spec 9c); other sections get their share by score


def hidden_topics() -> set[str]:
    """Topics marked hidden: true in site/site.config.ts (fewer than five quality articles; hidden from navigation and kept unindexed)."""
    cfg = (REPO / "site" / "site.config.ts").read_text(encoding="utf-8")
    return set(re.findall(r"\{ id: '([a-z-]+)', hidden: true", cfg))


def eligible() -> list[dict]:
    if not ELIG.exists():
        sys.exit("run scripts/prelaunch/score_pages.py first")
    with ELIG.open(encoding="utf-8") as f:
        rows = [r for r in csv.DictReader(f) if r["eligible"] == "True" and r.get("section") not in hidden_topics()]   # a hidden hub stays unindexed (spec 7b)
    for r in rows:
        r["score"] = int(r["score"])
    return rows


def set_index(file: Path, value: bool) -> bool:
    text = file.read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not m:
        return False
    fm = m.group(1)
    line = f"index: {'true' if value else 'false'}"
    if re.search(r"^index:\s*\S+", fm, re.M):
        fm2 = re.sub(r"^index:\s*\S+.*$", line, fm, count=1, flags=re.M)
    else:
        fm2 = fm + "\n" + line
    if fm2 == fm:
        return False
    file.write_text(f"---\n{fm2}\n---\n" + text[m.end():], encoding="utf-8")
    return True


def rebuild() -> None:
    print("rebuilding the site (LINT_CONTENT_WARN unset: the linter must pass)")
    subprocess.run(["npm", "run", "build"], cwd=REPO / "site", check=True)


def plan(size: int) -> None:
    rows = sorted(eligible(), key=lambda r: (-r["score"], r["url"]))
    wave1, rest = [], []
    per_section = defaultdict(list)
    for r in rows:
        per_section[r["section"]].append(r)
    # spread across sections: round-robin by score until the size is reached, the transfer floor first
    picked = set()
    for r in per_section.get("transfer", [])[: SECTION_FLOOR["transfer"]]:
        wave1.append(r); picked.add(r["url"])
    queues = {s: [r for r in rs if r["url"] not in picked] for s, rs in per_section.items()}
    while len(wave1) < size and any(queues.values()):
        for s in sorted(queues, key=lambda s: -len(queues[s])):
            if queues[s] and len(wave1) < size:
                r = queues[s].pop(0); wave1.append(r); picked.add(r["url"])
    rest = [r for r in rows if r["url"] not in picked]
    waves = {"1": [r["url"] for r in wave1]}
    n = 2
    for i in range(0, len(rest), size):
        waves[str(n)] = [r["url"] for r in rest[i: i + size]]; n += 1
    WAVES.parent.mkdir(parents=True, exist_ok=True)
    WAVES.write_text(json.dumps({"size": size, "waves": waves, "promoted": []}, indent=1), encoding="utf-8")
    print(f"wave 1: {len(wave1)} pages ({dict(Counter(r['section'] for r in wave1))}); {len(waves) - 1} later wave(s); written {WAVES.relative_to(REPO)}")


def stop_rule(prev: str) -> tuple[bool, str]:
    if not METRICS.exists():
        return False, f"config/wave-metrics.json is missing: enter the Search Console numbers for wave {prev} first"
    m = json.loads(METRICS.read_text(encoding="utf-8")).get(prev)
    if not m:
        return False, f"no metrics for wave {prev} in config/wave-metrics.json"
    reasons = []
    if float(m.get("weeks", 0)) < 3:
        reasons.append(f"only {m.get('weeks')} week(s) since wave {prev}, 3 to 4 required")
    if float(m.get("indexed_pct", 0)) < 50:
        reasons.append(f"wave {prev} is {m.get('indexed_pct')}% indexed, 50% required")
    if str(m.get("impressions_trend", "")).lower() not in ("flat", "rising"):
        reasons.append(f"impressions trend is {m.get('impressions_trend')!r}, flat or rising required")
    if float(m.get("audit_error_rate_pct", 100)) >= 3:
        reasons.append(f"weekly audit error rate {m.get('audit_error_rate_pct')}%, under 3% required")
    if int(m.get("manual_actions", 1)) != 0:
        reasons.append("manual actions present")
    return (not reasons), ("; ".join(reasons) or "stop rule satisfied")


def file_for(url: str) -> Path | None:
    parts = [p for p in url.split("/") if p]
    if parts[0] == "cornell" and len(parts) == 3:
        return REPO / "content" / "articles" / parts[1] / f"{parts[2]}.md"
    if parts[0] == "tools":
        return REPO / "content" / "tools" / parts[1] / "tool.md"
    if parts[0] == "datasets":
        return REPO / "content" / "datasets" / f"{parts[1]}.md"
    if parts[0] == "start":
        return REPO / "content" / "start" / f"{parts[1]}.md"
    return None


def main(argv: list[str]) -> int:
    if not argv:
        print(__doc__); return 2
    cmd = argv[0]
    if cmd == "plan":
        size = int(argv[argv.index("--size") + 1]) if "--size" in argv else 400
        plan(size); return 0
    cfg = json.loads(WAVES.read_text(encoding="utf-8")) if WAVES.exists() else None
    if cmd == "status":
        if not cfg:
            print("no config/waves.json yet (run plan)"); return 1
        for n, urls in cfg["waves"].items():
            print(f"wave {n}: {len(urls)} pages{' (promoted)' if n in cfg['promoted'] else ''}")
        nxt = str(len(cfg["promoted"]) + 1)
        if cfg["promoted"]:
            ok, why = stop_rule(cfg["promoted"][-1]); print(f"next wave {nxt}: {'allowed' if ok else 'blocked'}: {why}")
        else:
            print("next wave 1: allowed once Ajay approves the launch (LAUNCH_CHECKLIST.md)")
        return 0
    if cmd == "promote":
        n = argv[1]
        if not cfg or n not in cfg["waves"]:
            print("unknown wave"); return 1
        if cfg["promoted"] and n != str(len(cfg["promoted"]) + 1):
            print(f"waves are promoted in order; next is {len(cfg['promoted']) + 1}"); return 1
        if cfg["promoted"]:
            ok, why = stop_rule(cfg["promoted"][-1])
            if not ok:
                print(f"refused: {why}"); return 1
        changed = 0
        for url in cfg["waves"][n]:
            f = file_for(url)
            if f and f.exists() and set_index(f, True):
                changed += 1
        cfg["promoted"].append(n)
        WAVES.write_text(json.dumps(cfg, indent=1), encoding="utf-8")
        print(f"wave {n}: index: true on {changed} page(s)")
        rebuild(); return 0
    if cmd == "kill":
        section = argv[1]
        changed = 0
        for f in list((REPO / "content" / "articles" / section).glob("*.md")) + [p for p in (REPO / "content" / "tools").glob("*/tool.md")] + list((REPO / "content" / "datasets").glob("*.md")):
            text = f.read_text(encoding="utf-8")
            if f.parent.name == section or re.search(rf"^topic:\s*{re.escape(section)}\s*$", text, re.M):
                if set_index(f, False):
                    changed += 1
        print(f"kill switch: index: false on {changed} page(s) of {section}")
        rebuild(); return 0
    print(__doc__); return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
