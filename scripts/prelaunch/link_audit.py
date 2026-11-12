"""External link audit over every page under content/: each distinct http(s) URL in bodies and frontmatter sources is fetched once
(HEAD, then GET when HEAD is refused), hosts in parallel and each host serially with a pause. Output: reports/09-links.md (dead links by
host and by page) and build/linkcheck/status.json (url -> status, final url). 401/403/429 count as blocked (the page exists but refuses
automated clients), 404/410 as dead, 5xx and timeouts as unreachable today.

    worker/.venv/bin/python scripts/prelaunch/link_audit.py [--workers 6] [--only host]
"""
from __future__ import annotations

import json
import re
import sys
import threading
import time
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from datetime import date
from pathlib import Path
from urllib.parse import urlsplit

import httpx

REPO = Path(__file__).resolve().parents[2]
UA = "Mozilla/5.0 (Macintosh) EduExplained link check (https://eduexplained.netlify.app)"
URL_RE = re.compile(r"https?://(?:[^\s()\"'<>\]]|\([^\s()\"'<>\]]*\))+")   # parens allowed when balanced (Commons file titles)


def main(argv: list[str]) -> int:
    workers = int(argv[argv.index("--workers") + 1]) if "--workers" in argv else 6
    only = argv[argv.index("--only") + 1] if "--only" in argv else None
    pages: dict[str, set[str]] = defaultdict(set)
    for p in sorted((REPO / "content").rglob("*")):
        if p.suffix not in (".md", ".html") or not p.is_file() or "/images/" in str(p):
            continue
        for u in URL_RE.findall(p.read_text(encoding="utf-8")):
            u = u.rstrip(".,;:")
            if "eduexplained" in u or "footnote-daily" in u or "localhost" in u:
                continue
            pages[u].add(str(p.relative_to(REPO)))
    by_host: dict[str, list[str]] = defaultdict(list)
    for u in pages:
        h = urlsplit(u).netloc.lower()
        if only and h != only:
            continue
        by_host[h].append(u)
    print(f"{len(pages)} distinct URLs on {len(by_host)} hosts")
    status: dict[str, dict] = {}
    lock = threading.Lock()

    def check_host(host: str) -> None:
        with httpx.Client(headers={"User-Agent": UA}, timeout=20, follow_redirects=True) as c:
            for u in sorted(by_host[host]):
                code, final = None, ""
                for method in ("HEAD", "GET"):
                    try:
                        r = c.request(method, u)
                        code, final = r.status_code, str(r.url)
                        if method == "HEAD" and code in (405, 403, 400, 501, 404):
                            continue   # some servers refuse HEAD or 404 it; confirm with GET
                        break
                    except Exception as e:  # noqa: BLE001
                        code, final = f"error: {type(e).__name__}", ""
                with lock:
                    status[u] = {"status": code, "final": final}
                time.sleep(0.3)

    with ThreadPoolExecutor(max_workers=workers) as ex:
        list(ex.map(check_host, sorted(by_host, key=lambda h: -len(by_host[h]))))
    (REPO / "build" / "linkcheck").mkdir(parents=True, exist_ok=True)
    (REPO / "build" / "linkcheck" / "status.json").write_text(json.dumps(status, indent=1), encoding="utf-8")

    def kind(s) -> str:
        if isinstance(s, str):
            return "unreachable"
        if s in (404, 410):
            return "dead"
        if s in (401, 403, 429):
            return "blocked"
        if s >= 500:
            return "unreachable"
        return "ok"
    kinds = defaultdict(list)
    for u, d in status.items():
        kinds[kind(d["status"])].append(u)
    L = [f"# External link audit ({date.today().isoformat()})", "",
         f"{len(status)} distinct external URLs on {len(by_host)} hosts, cited by {len({p for ps in pages.values() for p in ps})} pages. "
         f"ok {len(kinds['ok'])}, dead (404/410) {len(kinds['dead'])}, blocked (401/403/429, the page exists but refuses automated clients) {len(kinds['blocked'])}, unreachable today (5xx, timeouts) {len(kinds['unreachable'])}.", "",
         "## Dead links by host", ""]
    dead_by_host = defaultdict(list)
    for u in kinds["dead"]:
        dead_by_host[urlsplit(u).netloc.lower()].append(u)
    for h, us in sorted(dead_by_host.items(), key=lambda x: -len(x[1])):
        L.append(f"### {h} ({len(us)})")
        for u in sorted(us):
            L.append(f"- {u} (on {len(pages[u])} page(s): {', '.join(sorted(pages[u])[:3])}{'...' if len(pages[u]) > 3 else ''})")
        L.append("")
    L += ["## Unreachable today", ""] + [f"- {status[u]['status']}: {u} ({len(pages[u])} page(s))" for u in sorted(kinds["unreachable"])] + ["",
          "## Blocked (exists, refuses automated clients)", ""] + [f"- {status[u]['status']}: {u} ({len(pages[u])} page(s))" for u in sorted(kinds["blocked"])] + [""]
    out = REPO / "reports" / "09-links.md"
    out.write_text("\n".join(L), encoding="utf-8")
    print(f"ok {len(kinds['ok'])}, dead {len(kinds['dead'])}, blocked {len(kinds['blocked'])}, unreachable {len(kinds['unreachable'])} -> {out.relative_to(REPO)}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
