#!/usr/bin/env python
"""v3 image step (docs/v3/spec.md "Publish requirements", pictures): give an article its lead photo or record that none exists.

    worker/.venv/bin/python scripts/v3/images.py content/articles/<dir>/<slug>.md [--images-dir content/images] [--intel-dir intel]

Order of searches (each through scripts/v2/find_images.py --query, whose relevance rule needs a Cornell or Ithaca name plus the subject):
the frontmatter `subject`, the plan row's `image:` hint, place names in the title, the topic's image_scenes (scripts/v3/topics.yml),
then a campus scene. The first relevant candidate becomes images[0]; find_images.py --article stores it and writes the credit. When
nothing is found the frontmatter gets `lead_photo: none-found <date>` and the page may publish on figures, tables and tools alone.
Code only, no session; safe to rerun (a stored lead photo is left alone)."""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from datetime import date
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[2]
FINDER = REPO / "scripts" / "v2" / "find_images.py"
PLACES = ["Collegetown", "Fall Creek", "West Campus", "North Campus", "South Campus", "Ithaca Commons", "TCAT", "Campus-to-Campus", "Syracuse",
          "Ithaca Tompkins", "Cayuga Heights", "Cascadilla", "Ho Plaza", "Arts Quad", "Olin Library", "Teagle", "Schoellkopf", "Statler", "Day Hall"]


def split(text: str) -> tuple[dict, str]:
    parts = text.split("---", 2)
    return yaml.safe_load(parts[1]) or {}, parts[2]


def dump(fm: dict, body: str) -> str:
    return "---\n" + yaml.safe_dump(fm, sort_keys=False, allow_unicode=True, width=10000) + "---" + body


def plan_hint(intel: Path, slug: str) -> str:
    for plan in intel.glob("*/plan.md"):
        for line in plan.read_text(encoding="utf-8").splitlines():
            if f"| {slug} |" in line or f"|{slug}|" in line:
                m = re.search(r"image\s*:\s*([^|;]+)", line, re.I)
                if m:
                    return m.group(1).strip()
    return ""


def topic_scenes(topic_dir: str) -> list[str]:
    for t in yaml.safe_load((REPO / "scripts/v3/topics.yml").read_text()):
        if t.get("dir") == topic_dir:
            return list(t.get("image_scenes") or [])
    return []


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(prog="images.py", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("article")
    ap.add_argument("--images-dir", default=str(REPO / "content/images"))
    ap.add_argument("--intel-dir", default=str(REPO / "intel"))
    a = ap.parse_args(argv)
    art = Path(a.article).resolve()
    images_dir = Path(a.images_dir)
    fm, body = split(art.read_text(encoding="utf-8"))
    slug, topic_dir = art.stem, art.parent.name
    stored = lambda: any((images_dir / slug).glob("*.webp")) if (images_dir / slug).exists() else False
    if (fm.get("images") or []) and stored():
        print(f"{slug}: lead photo already stored"); return 0
    subjects = fm.get("subject") or []
    subjects = [subjects] if isinstance(subjects, str) else list(subjects)
    title = str(fm.get("title") or slug)
    queries = subjects + ([plan_hint(Path(a.intel_dir), slug)] if plan_hint(Path(a.intel_dir), slug) else []) \
        + [p for p in PLACES if p.lower() in title.lower()] + topic_scenes(topic_dir) + ["Cornell University campus Ithaca"]
    seen, cand_path = set(), REPO / "content/images/candidates" / f"{slug}.json"
    cand_path.parent.mkdir(parents=True, exist_ok=True)
    for q in [x for x in queries if x and not (x in seen or seen.add(x))]:
        r = subprocess.run([sys.executable, str(FINDER), "--query", q, "--subject", q, "--out", str(cand_path), "--n", "8", "--images-dir", str(images_dir)],
                           cwd=REPO, capture_output=True, text=True, timeout=300)
        try:
            cands = json.load(open(cand_path))
        except Exception:
            cands = []
        if not cands:
            print(f"{slug}: no relevant licensed photo for {q!r}"); continue
        c = cands[0]
        ctitle = re.sub(r"\.(jpe?g|png|webp|tiff?)$", "", str(c.get("title") or q), flags=re.I).replace("File:", "").strip()
        fm["images"] = [{"file": "1.webp", "alt": ctitle[:140], "caption": ctitle[:120], "credit": f"{(c.get('author') or 'Unknown author')[:60]} / {str(c.get('source') or 'Wikimedia').title()}",
                         "credit_url": c.get("page_url") or "", "license": c.get("license") or "", "license_url": c.get("license_url") or ""}]
        fm["subject"] = subjects or [q]
        fm.pop("lead_photo", None)
        art.write_text(dump(fm, body), encoding="utf-8")
        subprocess.run([sys.executable, str(FINDER), "--article", str(art), "--out", str(cand_path), "--images-dir", str(images_dir)], cwd=REPO, capture_output=True, text=True, timeout=600)
        fm, body = split(art.read_text(encoding="utf-8"))
        if (fm.get("images") or []) and stored():
            print(f"{slug}: lead photo stored from {q!r}: {ctitle[:70]} ({c.get('license')})"); return 0
        fm["images"] = []
    fm["images"] = []
    fm["lead_photo"] = f"none-found {date.today().isoformat()}"
    art.write_text(dump(fm, body), encoding="utf-8")
    print(f"{slug}: no licensed photo for the subject, its scenes or the campus; marked lead_photo none-found (figures and tools carry the page)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
