"""Live preview server for the static site.

    worker/.venv/bin/python scripts/preview_server.py [--port 8765]

Serves build/preview and re-renders it (python -m campus_worker.render.preview)
whenever a file under worker/campus_worker/render/ changes, so template and CSS
edits show up on the next reload.
"""
from __future__ import annotations

import argparse
import http.server
import os
import subprocess
import sys
import threading
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WORKER = ROOT / "worker"
RENDER_DIR = WORKER / "campus_worker" / "render"
OUT = ROOT / "build" / "preview"

_lock = threading.Lock()
_last_stamp: float | None = None


def _stamp() -> float:
    latest = 0.0
    for p in RENDER_DIR.rglob("*"):
        if p.is_file() and "__pycache__" not in p.parts:
            latest = max(latest, p.stat().st_mtime)
    return latest


def render_if_stale() -> None:
    global _last_stamp
    with _lock:
        stamp = _stamp()
        if stamp == _last_stamp and OUT.exists():
            return
        proc = subprocess.run([sys.executable, "-m", "campus_worker.render.preview"], cwd=WORKER,
                              capture_output=True, text=True)
        if proc.returncode != 0:
            print("render FAILED:\n" + proc.stdout + proc.stderr, file=sys.stderr, flush=True)
            return
        _last_stamp = stamp
        print("re-rendered:", proc.stdout.strip(), flush=True)


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=str(OUT), **kw)

    def do_GET(self):
        render_if_stale()
        # /path -> /path/index.html or /path.html fallback
        path = self.path.split("?", 1)[0]
        target = OUT / path.lstrip("/")
        if not target.exists() and (OUT / (path.lstrip("/") + ".html")).exists():
            self.path = path + ".html"
        elif target.is_dir() and not path.endswith("/"):
            self.send_response(301); self.send_header("Location", path + "/"); self.end_headers(); return
        super().do_GET()

    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def log_message(self, fmt, *args):
        sys.stdout.write("%s %s\n" % (self.address_string(), fmt % args)); sys.stdout.flush()


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=8765)
    args = ap.parse_args()
    render_if_stale()
    srv = http.server.ThreadingHTTPServer(("127.0.0.1", args.port), Handler)
    print(f"preview at http://127.0.0.1:{args.port}/ (watching {RENDER_DIR})", flush=True)
    srv.serve_forever()


if __name__ == "__main__":
    main()
