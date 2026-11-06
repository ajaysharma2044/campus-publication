"""Photo slots for rendered pages (SPEC §04: imagery with credits, rights recorded).

A published page gets a photograph only when content/images/credits.yml lists one for its path under `pages:` with a
file, alt text, a credit and a license (the rights record). No entry means no image: a real page never shows the
preview's synthetic placeholders. The <img> carries data-rights="<license>" plus the file's pixel width and height,
which the SEO gate's image check requires.
"""
from __future__ import annotations

import shutil
import struct
from pathlib import Path

import yaml

from ..config import REPO_ROOT

PHOTOS_DIR = REPO_ROOT / "content" / "images"
CREDITS_FILE = PHOTOS_DIR / "credits.yml"
PHOTOS_URL = "img/photos/"          # under the page's static prefix
REQUIRED = ("file", "alt", "credit", "license")
FALLBACK_SIZE = (1600, 1000)        # the lede box is 16:10 (campus.css .lede-figure img); used only when the header cannot be read


def load_credits(path: Path | None = None) -> dict:
    f = path or CREDITS_FILE
    if not f.exists():
        return {}
    data = yaml.safe_load(f.read_text()) or {}
    return data if isinstance(data, dict) else {}


def _norm(path: str) -> str:
    p = "/" + str(path or "").strip().strip("/")
    return p if p.endswith("/") else p + "/"


def page_entry(page_path: str, credits: dict | None = None) -> dict | None:
    """The credits.yml `pages:` entry for a page path (trailing slash optional)."""
    pages = (credits if credits is not None else load_credits()).get("pages") or {}
    if not isinstance(pages, dict):
        return None
    entry = pages.get(page_path)
    if entry is None:
        want = _norm(page_path)
        entry = next((e for k, e in pages.items() if _norm(k) == want), None)
    return entry if isinstance(entry, dict) else None


def page_photo(page_path: str, *, credits: dict | None = None, photos_dir: Path | None = None, static_prefix: str = "/static/") -> dict | None:
    """The image record for a page, or None: needs file, alt, credit and license, and the file present in content/images/."""
    entry = page_entry(page_path, credits)
    if not entry or not all(str(entry.get(k) or "").strip() for k in REQUIRED):
        return None
    name = str(entry["file"]).strip()
    if Path(name).name != name:          # a bare file name inside content/images/, never a path
        return None
    src = (photos_dir or PHOTOS_DIR) / name
    if not src.is_file():
        return None
    w, h = image_size(src) or FALLBACK_SIZE
    return {"src": f"{static_prefix}{PHOTOS_URL}{name}", "file": name, "alt": str(entry["alt"]).strip(), "credit": str(entry["credit"]).strip(),
            "caption": str(entry.get("caption") or "").strip() or None, "rights": str(entry["license"]).strip(),
            "source_url": str(entry.get("source_url") or "").strip() or None, "width": w, "height": h}


def copy_photo(image: dict, out_root: Path, *, photos_dir: Path | None = None) -> Path | None:
    """Copy a page's photo into the build's static dir (<out_root>/static/img/photos/<file>)."""
    name = str(image.get("file") or "")
    src = (photos_dir or PHOTOS_DIR) / name
    if not name or Path(name).name != name or not src.is_file():
        return None
    dest = out_root / "static" / "img" / "photos" / name
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dest)
    return dest


_SOF = {0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7, 0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF}


def image_size(path: Path) -> tuple[int, int] | None:
    """Pixel (width, height) from a PNG or JPEG header; None for anything else. Pure Python: no PIL in the render path."""
    try:
        data = path.read_bytes()
    except OSError:
        return None
    if data[:8] == b"\x89PNG\r\n\x1a\n" and len(data) >= 24:
        w, h = struct.unpack(">II", data[16:24])
        return w, h
    if data[:2] == b"\xff\xd8":
        i = 2
        while i + 9 < len(data):
            if data[i] != 0xFF:
                i += 1
                continue
            marker = data[i + 1]
            if marker == 0xFF:
                i += 1
                continue
            if marker in (0xD8, 0x01) or 0xD0 <= marker <= 0xD7:   # standalone markers carry no length
                i += 2
                continue
            if marker in _SOF:
                h, w = struct.unpack(">HH", data[i + 5:i + 9])
                return w, h
            i += 2 + struct.unpack(">H", data[i + 2:i + 4])[0]
    return None
