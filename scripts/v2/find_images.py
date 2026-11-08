#!/usr/bin/env python
"""Image finder for Footnote Daily v2 (docs/v2/spec.md, "Images and visuals").

Search (Wikimedia Commons and Openverse need no key); write.sh runs it before each writer session with the row's primary query:
    worker/.venv/bin/python scripts/v2/find_images.py --query "Mews Hall Cornell" [--query "..."] --out content/images/candidates/q-housing-0001.json [--n 8]
Store the photos an article's frontmatter lists; write.sh runs it right after the writer session, publish.sh before each lint:
    worker/.venv/bin/python scripts/v2/find_images.py --article content/articles/housing/mews-hall-guide.md [--out <candidates.json>]
    Each images entry names its candidate by credit_url (= the candidate's page_url). The file is downloaded to
    content/images/<slug>/<n>.webp (n from the entry's file name; under about 150 KB), logged in content/images/credits.yml, and the
    entry's file, credit_url, license and license_url are rewritten from the candidate (the API's license data). An owner photo
    content/images/inbox/<slug>-<n>.<ext> (or <slug>.<ext> for n = 1) takes the place of image n instead, credited from its ledger
    entry (source owner or permission) or, failing that, to the site. Running it again downloads and converts nothing twice.
Fetch candidates by index by hand, numbering on from the files already in the folder:
    worker/.venv/bin/python scripts/v2/find_images.py --out content/images/candidates/q-housing-0001.json --fetch mews-hall-guide --pick 0,2
Both store modes print a JSON list of the images placed to stdout; everything else goes to stderr ("not fetched" / "not used" lines
say why an entry was left alone).

Order: Wikimedia Commons, Openverse (Flickr and other open collections), then Unsplash and Pexels for generic shots, which run only
when UNSPLASH_ACCESS_KEY / PEXELS_API_KEY are in the environment (the shell wrapper sources worker/.env; this script never reads it)
and the first two sources found fewer than --n candidates. Commons search needs every word to match, so a query that finds nothing
is shortened from the end, two words at least ("Mews Hall Cornell dorm review" -> "Mews Hall Cornell dorm" -> "Mews Hall Cornell").
Accepted licenses: CC0, Public Domain (PDM / "Public domain"), CC BY, CC BY-SA (any version), Unsplash License, Pexels License.
NC, ND (we always resize, so ND is never usable) and anything without a clear license are dropped. License fields are kept as
the API returned them (a public-domain Commons file has no license URL). A source that is down or rate limited (Openverse
anonymous: 20/min, 200/day) yields an empty list for that source, never a crash. Candidates are deduped by file_url.
credit is "Author / Source" ("Kenneth C. Zirkel / Wikimedia Commons"); render_site.py shows "Photo: <credit>, <license>" under the
photo with the credit linked to credit_url and the license to license_url, the form the spec asks for.
"""
import argparse
import fcntl
import html
import io
import itertools
import json
import os
import re
import sys
from datetime import date, datetime
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit

import httpx
import yaml
from PIL import Image, ImageOps

REPO = Path(__file__).resolve().parents[2]
# Wikimedia's User-Agent policy format: name/version (contact) library/version. Its edge returns 403 for any UA that contains
# "example.com", so the placeholder uses the reserved .example TLD. Replace the contact with the real editor address before launch.
USER_AGENT = f"FootnoteDaily-ImageFinder/1.0 (Footnote Daily image finder; editor@footnotedaily.example) httpx/{httpx.__version__}"
TIMEOUT = 10.0
MIN_WIDTH = 600            # smaller files are icons or thumbnails
MAX_WIDTH = 1600
MAX_BYTES = 150_000
MIMES = {"image/jpeg", "image/png", "image/webp"}
INBOX_SUFFIXES = {".jpg", ".jpeg", ".png", ".webp", ".tif", ".tiff", ".avif"}   # what Pillow opens here; HEIC is not among them
SOURCE_NAMES = {"wikimedia": "Wikimedia Commons", "unsplash": "Unsplash", "pexels": "Pexels"}
HOST_NAMES = {"flickr.com": "Flickr", "wikimedia.org": "Wikimedia Commons", "rawpixel.com": "Rawpixel", "europeana.eu": "Europeana"}
ACCEPT = re.compile(r"^(cc0|cc zero|pdm|pd|public domain|cc by|unsplash license|pexels license)\b")
OWNER_LICENSE = "All rights reserved"
FM_RE = re.compile(r"^﻿?---[ \t]*\n(.*?)\n---[ \t]*\n?(.*)$", re.S)
IMAGE_KEYS = ("file", "alt", "caption", "credit", "credit_url", "license", "license_url")


def accepted(license_name: str) -> bool:
    """CC0, public domain, CC BY, CC BY-SA, Unsplash or Pexels license; never NC or ND; never an empty or unknown license."""
    words = re.sub(r"[^a-z0-9]+", " ", (license_name or "").lower()).strip()
    if not words or "nc" in words.split() or "nd" in words.split():
        return False
    return bool(ACCEPT.match(words))


def clean(text: str) -> str:
    """Strip HTML (Commons returns Artist and descriptions as HTML) and collapse whitespace."""
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", text or ""))).strip()


def strip_query(url: str) -> str:
    """Drop utm_* and other parameters so the same file dedupes across Commons and Openverse's Wikimedia mirror."""
    return urlunsplit(urlsplit(url or "")._replace(query="", fragment=""))


def same_url(a, b) -> bool:
    norm = lambda u: strip_query(str(u or "")).lower().replace("http://", "https://").rstrip("/")  # noqa: E731
    return bool(a) and bool(b) and norm(a) == norm(b)


def cand(source, title, page_url, file_url, thumb_url, author, license_name, license_url, width, height) -> dict:
    return {"source": source, "title": clean(title)[:160], "page_url": page_url or "", "file_url": file_url or "",
            "thumb_url": thumb_url or "", "author": clean(author)[:120], "license": (license_name or "").strip(),
            "license_url": license_url or "", "width": int(width or 0), "height": int(height or 0)}


def search_commons(client: httpx.Client, q: str, n: int) -> list:
    params = {"action": "query", "format": "json", "generator": "search", "gsrsearch": f"{q} filetype:bitmap",
              "gsrnamespace": 6, "gsrlimit": n, "prop": "imageinfo", "iiprop": "url|size|mime|extmetadata",
              "iiextmetadatafilter": "LicenseShortName|License|Artist|LicenseUrl|ImageDescription", "iiurlwidth": 640}
    r = client.get("https://commons.wikimedia.org/w/api.php", params=params)
    r.raise_for_status()
    pages = r.json().get("query", {}).get("pages", {})
    out = []
    for p in sorted(pages.values(), key=lambda p: p.get("index", 0)):
        ii = (p.get("imageinfo") or [{}])[0]
        em = ii.get("extmetadata") or {}
        meta = lambda k: (em.get(k) or {}).get("value") or ""  # noqa: E731
        if ii.get("mime") not in MIMES:
            continue
        title = re.sub(r"^File:|\.[^.]+$", "", p.get("title", ""))
        out.append(cand("wikimedia", title, ii.get("descriptionurl"), strip_query(ii.get("url")), strip_query(ii.get("thumburl")),
                        meta("Artist"), meta("LicenseShortName") or meta("License"), meta("LicenseUrl"), ii.get("width"), ii.get("height")))
    return out


def search_openverse(client: httpx.Client, q: str, n: int) -> list:
    r = client.get("https://api.openverse.org/v1/images/", params={"q": q, "license": "cc0,by,by-sa,pdm", "page_size": min(n, 20)})
    r.raise_for_status()
    out = []
    for x in r.json().get("results", []):
        slug, version = (x.get("license") or "").lower(), x.get("license_version") or ""   # e.g. "by-sa" and "4.0"
        name = {"cc0": "CC0", "pdm": "Public Domain Mark"}.get(slug, "CC " + slug.upper())
        out.append(cand("openverse", x.get("title"), x.get("foreign_landing_url"), x.get("url"), x.get("thumbnail"),
                        x.get("creator"), f"{name} {version}".strip(), x.get("license_url"), x.get("width"), x.get("height")))
    return out


def search_unsplash(client: httpx.Client, q: str, n: int):
    key = os.environ.get("UNSPLASH_ACCESS_KEY")
    if not key:
        return None
    r = client.get("https://api.unsplash.com/search/photos", params={"query": q, "per_page": n},
                   headers={"Authorization": f"Client-ID {key}", "Accept-Version": "v1"})
    r.raise_for_status()
    out = []
    for x in r.json().get("results", []):
        page = x["links"]["html"] + "?utm_source=footnote_daily&utm_medium=referral"   # attribution links need utm per Unsplash API terms
        dl = x["links"]["download"]                                                      # the download link also records the download, as the API terms ask
        out.append(cand("unsplash", x.get("description") or x.get("alt_description"), page, dl + ("&" if "?" in dl else "?") + f"force=true&w={MAX_WIDTH}",
                        x["urls"]["small"], x["user"]["name"], "Unsplash License", "https://unsplash.com/license", x.get("width"), x.get("height")))
    return out


def search_pexels(client: httpx.Client, q: str, n: int):
    key = os.environ.get("PEXELS_API_KEY")
    if not key:
        return None
    r = client.get("https://api.pexels.com/v1/search", params={"query": q, "per_page": n}, headers={"Authorization": key})
    r.raise_for_status()
    return [cand("pexels", x.get("alt"), x.get("url"), x["src"]["large2x"], x["src"]["medium"], x.get("photographer"),
                 "Pexels License", "https://www.pexels.com/license/", x.get("width"), x.get("height")) for x in r.json().get("photos", [])]


def search(queries: list, n: int) -> list:
    out, seen = [], set()

    def run(name, fn, client, q):
        """One source for one query; returns how many accepted candidates it added (None: no key)."""
        try:
            found = fn(client, q, n)
        except Exception as e:  # noqa: BLE001 - API down, rate limited, odd JSON: this source gives nothing
            print(f"{name}: {type(e).__name__}: {e}", file=sys.stderr)
            found = []
        if found is None:
            print(f"{name}: skipped (no API key in the environment)", file=sys.stderr)
            return None
        kept = 0
        for c in found:
            if accepted(c["license"]) and c["width"] >= MIN_WIDTH and c["file_url"] and c["file_url"] not in seen:
                seen.add(c["file_url"])
                out.append(c)
                kept += 1
        print(f"{name}: kept {kept} of {len(found)} for {q!r}", file=sys.stderr)
        return kept

    with httpx.Client(timeout=TIMEOUT, follow_redirects=True, headers={"User-Agent": USER_AGENT}) as client:
        for q in queries:
            words = re.sub(r"[^\w\s'&-]", " ", q).split()
            for k in range(len(words), min(len(words), 2) - 1, -1):     # every word must match on Commons: shorten from the end
                short = " ".join(words[:k])
                if run("wikimedia", search_commons, client, short):
                    break
            run("openverse", search_openverse, client, short)
        for name, fn in (("unsplash", search_unsplash), ("pexels", search_pexels)):
            if len(out) >= n:
                break                                   # keyed stock sites only fill gaps
            run(name, fn, client, queries[0])
    return out


def download(client: httpx.Client, url: str, cap: int = 60_000_000) -> bytes:
    buf = bytearray()
    with client.stream("GET", url) as r:
        r.raise_for_status()
        for chunk in r.iter_bytes():
            buf += chunk
            if len(buf) > cap:
                raise ValueError(f"file larger than {cap // 1_000_000} MB")
    return bytes(buf)


def to_webp(data: bytes) -> tuple:
    """Downscale to MAX_WIDTH, then lower quality (and width again) until the WebP is under MAX_BYTES."""
    im = Image.open(io.BytesIO(data))
    if im.format == "JPEG":
        im.draft("RGB", (2 * MAX_WIDTH, 2 * MAX_WIDTH))     # cheap decode of huge originals; stays above the target size
    im = ImageOps.exif_transpose(im).convert("RGB")
    for width in (MAX_WIDTH, 1280, 1024, 800):
        w = min(width, im.width)
        small = im.resize((w, max(1, round(im.height * w / im.width))), Image.Resampling.LANCZOS) if w < im.width else im
        for quality in (85, 75, 65, 55, 45):
            buf = io.BytesIO()
            small.save(buf, "WEBP", quality=quality)
            if buf.tell() <= MAX_BYTES:
                return buf.getvalue(), small.width, small.height
    print(f"still {buf.tell() // 1024} KB at {small.width}px and quality 45; kept anyway", file=sys.stderr)
    return buf.getvalue(), small.width, small.height


def save_webp(data: bytes, dest: Path) -> None:
    webp, w, h = to_webp(data)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(webp)
    print(f"-> {dest} {w}x{h} {len(webp) // 1024} KB", file=sys.stderr)


def source_label(c: dict) -> str:
    """Wikimedia Commons, Unsplash, Pexels, or for Openverse the collection the photo lives in (Flickr, ...), from its page host."""
    if c["source"] in SOURCE_NAMES:
        return SOURCE_NAMES[c["source"]]
    host = urlsplit(c.get("page_url") or "").netloc.lower().removeprefix("www.")
    return next((v for k, v in HOST_NAMES.items() if host.endswith(k)), host or "Openverse")


def credit(c: dict) -> str:
    """"Author / Source"; the page adds "Photo: " before it and the license after it."""
    return f"{c['author']} / {source_label(c)}" if c.get("author") else source_label(c)


def normalize_credit(text, license_name) -> str:
    """A credit written as the whole caption line ("Photo: X / Y, CC BY-SA 4.0") back to "X / Y"."""
    cr = re.sub(r"^\s*photo:\s*", "", str(text or ""), flags=re.I).strip()
    lic = str(license_name or "").strip()
    if lic and cr.lower().endswith(", " + lic.lower()):
        cr = cr[: -len(lic) - 1].rstrip(", ")
    return cr


def site_name() -> str:
    try:
        cfg = yaml.safe_load((REPO / "config" / "monetization.yml").read_text(encoding="utf-8")) or {}
        return str((cfg.get("site") or {}).get("name") or "Footnote Daily")
    except Exception:  # noqa: BLE001 - no config yet
        return "Footnote Daily"


def entry(slug, name, source, page_url, author, license_name, license_url, found_at, credit_text) -> dict:
    return {"file": name, "article_slug": slug, "source": source, "page_url": page_url, "author": author, "license": license_name,
            "license_url": license_url, "found_at": found_at, "fetched_at": datetime.now().isoformat(timespec="seconds"), "credit": credit_text}


def load_ledger(path: Path) -> tuple:
    """The ledger list plus its leading comment block, which the rewrite keeps."""
    text = path.read_text(encoding="utf-8") if path.exists() else ""
    head = "".join(itertools.takewhile(lambda l: l.startswith("#") or not l.strip(), text.splitlines(keepends=True)))
    data = yaml.safe_load(text) or []
    if not isinstance(data, list):
        raise SystemExit(f"{path} is not a YAML list (contract 5); fix it before fetching")
    return data, head


def add_ledger(path: Path, entries: list) -> None:
    """Append entries (replacing an older entry for the same article file) under a lock: write.sh stores for 4 articles at once."""
    if not entries:
        return
    with path.open("a", encoding="utf-8") as lock:       # "a" creates an empty ledger if there is none; nothing is written through it
        fcntl.flock(lock, fcntl.LOCK_EX)
        ledger, head = load_ledger(path)
        gone = {(e["article_slug"], e["file"]) for e in entries}
        ledger = [e for e in ledger if (e.get("article_slug"), e.get("file")) not in gone] + entries
        path.write_text(head + yaml.safe_dump(ledger, sort_keys=False, allow_unicode=True), encoding="utf-8")


def fetch(cands_path: Path, slug: str, picks: list, images_dir: Path) -> list:
    """Hand mode: candidates by index to <images-dir>/<slug>/<n>.webp, numbering on from the files already there."""
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]*", slug):
        raise SystemExit(f"bad slug {slug!r}: lowercase letters, digits and hyphens only")
    cands = json.loads(cands_path.read_text(encoding="utf-8"))
    found_at = date.fromtimestamp(cands_path.stat().st_mtime).isoformat()
    load_ledger(images_dir / "credits.yml")                 # refuse a broken ledger before any download
    folder = images_dir / slug
    n = max([int(p.stem) for p in folder.glob("*.webp") if p.stem.isdigit()], default=0)
    placed, entries = [], []
    with httpx.Client(timeout=TIMEOUT, follow_redirects=True, headers={"User-Agent": USER_AGENT}) as client:
        for i in picks:
            if not 0 <= i < len(cands):
                print(f"[{i}] no such candidate (file has {len(cands)}); not fetched", file=sys.stderr)
                continue
            c = cands[i]
            if not accepted(c.get("license", "")):
                print(f"[{i}] license {c.get('license')!r} is not accepted; not fetched", file=sys.stderr)
                continue
            name = f"{n + 1}.webp"
            try:
                save_webp(download(client, c["file_url"]), folder / name)
            except Exception as e:  # noqa: BLE001 - one bad file never stops the others
                print(f"[{i}] {c['file_url']}: {type(e).__name__}: {e}; not fetched", file=sys.stderr)
                continue
            n += 1
            entries.append(entry(slug, name, c["source"], c["page_url"], c["author"], c["license"], c["license_url"], found_at, credit(c)))
            placed.append({"file": name, "alt_suggestion": c["title"], "caption": c["title"], "credit": credit(c),
                           "credit_url": c["page_url"], "license": c["license"], "license_url": c["license_url"]})
    add_ledger(images_dir / "credits.yml", entries)
    return placed


def inbox_file(images_dir: Path, slug: str, n: int):
    """content/images/inbox/<slug>-<n>.<ext>, or <slug>.<ext> for image 1; None when there is none."""
    stems = {f"{slug}-{n}"} | ({slug} if n == 1 else set())
    hits = [p for p in sorted((images_dir / "inbox").glob("*")) if p.is_file() and p.stem in stems and p.suffix.lower() in INBOX_SUFFIXES]
    return hits[0] if hits else None


def fetch_article(path: Path, cands_path, images_dir: Path) -> list:
    """Store the images an article's frontmatter lists and point the frontmatter (and body references) at the stored files.
    The frontmatter is rewritten only when something changed, so a second run is a no-op."""
    text = path.read_text(encoding="utf-8")
    m = FM_RE.match(text)
    if not m:
        raise SystemExit(f"{path}: no YAML frontmatter")
    fm, body = yaml.safe_load(m.group(1)) or {}, m.group(2)
    images = fm.get("images") or []
    if not isinstance(images, list):
        raise SystemExit(f"{path}: images is not a list")
    slug = path.stem
    cands_path = cands_path or images_dir / "candidates" / f"{fm.get('queue_id')}.json"
    cands = json.loads(cands_path.read_text(encoding="utf-8")) if cands_path.exists() else []
    found_at = date.fromtimestamp(cands_path.stat().st_mtime).isoformat() if cands_path.exists() else date.today().isoformat()
    ledger, _ = load_ledger(images_dir / "credits.yml")
    site, folder = site_name(), images_dir / slug
    done, entries, positions = [], [], set()
    with httpx.Client(timeout=TIMEOUT, follow_redirects=True, headers={"User-Agent": USER_AGENT}) as client:
        for i, im in enumerate(images):
            if not isinstance(im, dict):
                continue
            old = str(im.get("file") or "")
            num = re.fullmatch(r"(\d+)\.\w+", old)
            n = int(num.group(1)) if num else i + 1
            positions.add(n)
            name, dest = f"{n}.webp", folder / f"{n}.webp"
            own = inbox_file(images_dir, slug, n)
            led = next((e for e in ledger if e.get("article_slug") == slug and e.get("file") == name and e.get("source") in ("owner", "permission")), None)
            if own or (led and dest.exists()):                 # an owner photo, new or already in place
                if own and not (led and dest.exists()):
                    try:
                        save_webp(own.read_bytes(), dest)
                    except Exception as e:  # noqa: BLE001
                        print(f"images[{i}] inbox/{own.name}: {type(e).__name__}: {e}; not used", file=sys.stderr)
                        continue
                    if not led:
                        led = entry(slug, name, "owner", "", site, OWNER_LICENSE, "", date.fromtimestamp(own.stat().st_mtime).isoformat(), site)
                        entries.append(led)
                new = {"file": name, "credit": led.get("credit") or site, "credit_url": led.get("page_url") or "",
                       "license": led.get("license") or OWNER_LICENSE, "license_url": led.get("license_url") or ""}
            else:
                c = next((c for c in cands if same_url(im.get("credit_url"), c["page_url"]) or same_url(im.get("credit_url"), c["file_url"])), None)
                if c is None:
                    print(f"images[{i}] {old}: credit_url {im.get('credit_url')!r} is not a candidate's page_url in {cands_path}; not fetched", file=sys.stderr)
                    continue
                if not dest.exists():
                    if not accepted(c["license"]):
                        print(f"images[{i}] {old}: license {c['license']!r} is not accepted; not fetched", file=sys.stderr)
                        continue
                    try:
                        save_webp(download(client, c["file_url"]), dest)
                    except Exception as e:  # noqa: BLE001
                        print(f"images[{i}] {c['file_url']}: {type(e).__name__}: {e}; not fetched", file=sys.stderr)
                        continue
                    entries.append(entry(slug, name, c["source"], c["page_url"], c["author"], c["license"], c["license_url"], found_at, credit(c)))
                new = {"file": name, "credit": normalize_credit(im.get("credit"), im.get("license")) or credit(c),
                       "credit_url": c["page_url"], "license": c["license"], "license_url": c["license_url"]}
            im.update(new)
            if old and old != name:
                body = re.sub(r"\]\(\s*(?:/images/" + re.escape(slug) + "/)?" + re.escape(old) + r"\s*\)", f"]({name})", body)
            done.append({k: im.get(k, "") for k in IMAGE_KEYS})
    for p in sorted((images_dir / "inbox").glob(f"{slug}*")):
        k = re.fullmatch(re.escape(slug) + r"(?:-(\d+))?", p.stem)
        if k and p.suffix.lower() in INBOX_SUFFIXES and int(k.group(1) or 1) not in positions:
            print(f"inbox/{p.name}: the article lists no image {int(k.group(1) or 1)}; add an images entry with alt and caption first; not used", file=sys.stderr)
    add_ledger(images_dir / "credits.yml", entries)
    new_text = "---\n" + yaml.safe_dump(fm, sort_keys=False, allow_unicode=True, width=4096) + "---\n" + body
    if done and new_text != text:
        path.write_text(new_text, encoding="utf-8")
        print(f"{path}: images frontmatter updated", file=sys.stderr)
    return done


def main(argv: list) -> int:
    ap = argparse.ArgumentParser(description="Find openly licensed photos (Commons, Openverse, Unsplash, Pexels) and store them as WebP.")
    ap.add_argument("--query", action="append", default=[], help="subject to search, e.g. 'Mews Hall Cornell' (repeatable)")
    ap.add_argument("--out", type=Path, help="candidates JSON: written by --query, read by --fetch and --article "
                                              "(--article defaults to <images-dir>/candidates/<queue_id>.json)")
    ap.add_argument("--n", type=int, default=8, help="results to ask each source for (default 8)")
    ap.add_argument("--article", type=Path, metavar="MD", help="article file: store the images its frontmatter lists")
    ap.add_argument("--fetch", metavar="SLUG", help="article slug: download --pick candidates to <images-dir>/<slug>/<n>.webp")
    ap.add_argument("--pick", default="", help="comma-separated candidate indexes for --fetch, e.g. 0,2")
    ap.add_argument("--images-dir", type=Path, default=REPO / "content" / "images", help="default content/images")
    args = ap.parse_args(argv)
    if not (args.query or args.article or args.fetch):
        ap.error("give --query to search, --article MD or --fetch SLUG --pick I,J to store photos")
    if (args.query or args.fetch) and not args.out:
        ap.error("--query and --fetch need --out (the candidates JSON)")
    if args.query:
        cands = search(args.query, args.n)
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(cands, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"{len(cands)} candidates -> {args.out}", file=sys.stderr)
    if args.article:
        print(json.dumps(fetch_article(args.article, args.out, args.images_dir), indent=1, ensure_ascii=False))
    if args.fetch:
        picks = [int(p) for p in args.pick.split(",") if p.strip()]
        if not picks:
            ap.error("--fetch needs --pick with at least one candidate index")
        print(json.dumps(fetch(args.out, args.fetch, picks, args.images_dir), indent=1, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
