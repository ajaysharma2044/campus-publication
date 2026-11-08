#!/usr/bin/env python
"""IndexNow: tell Bing, Yandex and the other IndexNow engines which pages are new or changed, right after a deploy.

    worker/.venv/bin/python scripts/v2/indexnow.py [--site build/site] [--crawlers config/crawlers.yml] [--dry-run] [--all]

Reads the sitemap the renderer wrote (build/site/sitemap.xml: one <loc> and <lastmod> per page) and compares it with the state file
(build/indexnow-state.json: the lastmod last submitted for each URL). Only URLs that are new or whose lastmod changed are sent, in one
POST to the endpoint in config/crawlers.yml (api.indexnow.org forwards to every participating engine), with the key from the key file
and keyLocation https://<host>/<key>.txt, which the renderer serves. Every URL and the response code go to reports/indexnow.log, one
line each; the state is updated only on a 200 or 202. A preview build has an empty sitemap, so nothing is submitted and the log says
so. --dry-run lists what would be sent; --all resubmits every sitemap URL (after a domain change). publish.sh runs this after each
successful deploy.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from urllib.parse import urlsplit

import httpx
import yaml

REPO = Path(__file__).resolve().parents[2]
BATCH = 10_000      # the protocol's limit per POST
TIMEOUT = 20.0


def load_crawlers(path: Path) -> dict:
    data = yaml.safe_load(path.read_text(encoding="utf-8")) if path.exists() else {}
    return dict((data if isinstance(data, dict) else {}).get("indexnow") or {})


def repo_path(p: str, default: str) -> Path:
    s = str(p or default)
    return Path(s) if Path(s).is_absolute() else REPO / s


def sitemap_urls(sitemap: Path) -> dict[str, str]:
    """{url: lastmod} from the renderer's sitemap (one <url> per line; no namespace parsing needed)."""
    if not sitemap.exists():
        return {}
    text = sitemap.read_text(encoding="utf-8")
    out = {}
    for loc, mod in re.findall(r"<url><loc>(.*?)</loc><lastmod>(.*?)</lastmod></url>", text):
        out[loc.replace("&amp;", "&")] = mod
    return out


def log_line(log: Path, text: str) -> None:
    log.parent.mkdir(parents=True, exist_ok=True)
    with log.open("a", encoding="utf-8") as fh:
        fh.write(f"{datetime.now().isoformat(timespec='seconds')} | {text}\n")


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--site", default=str(REPO / "build" / "site"), help="the rendered site (its sitemap.xml and <key>.txt)")
    ap.add_argument("--crawlers", default=str(REPO / "config" / "crawlers.yml"))
    ap.add_argument("--dry-run", action="store_true", help="print the URLs that would be submitted; send nothing, change nothing")
    ap.add_argument("--all", action="store_true", help="submit every sitemap URL, not only the new and changed ones")
    a = ap.parse_args(argv)
    cfg = load_crawlers(Path(a.crawlers))
    endpoint = str(cfg.get("endpoint") or "https://api.indexnow.org/indexnow")
    key_file, log, state_path = repo_path(cfg.get("key_file"), "config/indexnow.key"), repo_path(cfg.get("log"), "reports/indexnow.log"), repo_path(cfg.get("state"), "build/indexnow-state.json")
    site = Path(a.site)
    key = key_file.read_text(encoding="utf-8").strip() if key_file.exists() else ""
    if not key:
        print(f"no IndexNow key in {key_file}; nothing submitted", file=sys.stderr)
        log_line(log, f"skipped | no key file {key_file}")
        return 1
    urls = sitemap_urls(site / "sitemap.xml")
    if not urls:
        print(f"{site / 'sitemap.xml'} lists no URLs (a preview build, or no production domain); nothing submitted", file=sys.stderr)
        log_line(log, "skipped | sitemap empty (preview build or no site.domain)")
        return 0
    if not (site / f"{key}.txt").exists():
        print(f"{site / (key + '.txt')} is missing: the renderer did not write the key file; nothing submitted", file=sys.stderr)
        log_line(log, f"skipped | key file {key}.txt missing from {site}")
        return 1
    host = urlsplit(next(iter(urls))).netloc
    try:
        state = json.loads(state_path.read_text(encoding="utf-8")) if state_path.exists() else {}
    except ValueError:
        state = {}
    changed = sorted(u for u, mod in urls.items() if a.all or state.get(u) != mod)
    if not changed:
        print(f"nothing new or changed among {len(urls)} URLs; nothing submitted", file=sys.stderr)
        log_line(log, f"nothing new | {len(urls)} URLs unchanged")
        return 0
    if a.dry_run:
        print(f"would submit {len(changed)} of {len(urls)} URLs to {endpoint} for {host} (key {key[:6]}..., keyLocation https://{host}/{key}.txt):")
        for u in changed:
            print(f"  {u} ({urls[u]})")
        return 0
    rc = 0
    with httpx.Client(timeout=TIMEOUT, follow_redirects=False, headers={"Content-Type": "application/json; charset=utf-8", "User-Agent": "FootnoteDaily-IndexNow/1.0"}) as client:
        for i in range(0, len(changed), BATCH):
            batch = changed[i:i + BATCH]
            body = {"host": host, "key": key, "keyLocation": f"https://{host}/{key}.txt", "urlList": batch}
            try:
                r = client.post(endpoint, json=body)
                code = r.status_code
            except Exception as e:  # noqa: BLE001 - the deploy is done; a failed ping is logged and retried on the next publish
                code = f"error {type(e).__name__}"
            ok = code in (200, 202)
            for u in batch:
                log_line(log, f"{code} | {u} | lastmod {urls[u]}")
                if ok:
                    state[u] = urls[u]
            print(f"submitted {len(batch)} URL(s) to {endpoint}: {code}{'' if ok else ' (not recorded; they go again next publish)'}", file=sys.stderr)
            rc = rc or (0 if ok else 1)
    state_path.parent.mkdir(parents=True, exist_ok=True)
    state_path.write_text(json.dumps(state, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    return rc


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
