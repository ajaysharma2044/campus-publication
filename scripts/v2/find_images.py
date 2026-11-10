#!/usr/bin/env python
"""Image finder for EduExplained v2 (docs/v2/spec.md, "Images and visuals").

Search (Wikimedia Commons and Openverse need no key); write.sh runs it before each writer session with the row's primary query:
    worker/.venv/bin/python scripts/v2/find_images.py --query "Mews Hall Cornell" [--query "..."] --out content/images/candidates/q-housing-0001.json [--n 8]
                                                     [--school cornell-university] [--subject "Mews Hall"]
Store the photos an article's frontmatter lists; write.sh runs it right after the writer session, publish.sh before each lint:
    worker/.venv/bin/python scripts/v2/find_images.py --article content/articles/housing/mews-hall-guide.md [--out <candidates.json>]
    Each images entry names its candidate by credit_url (= the candidate's page_url). The file is downloaded to
    content/images/<slug>/<n>.webp (n from the entry's file name; under about 150 KB), logged in content/images/credits.yml, and the
    entry's file, credit_url, license and license_url are rewritten from the candidate (the API's license data). An owner photo
    content/images/inbox/<slug>-<n>.<ext> (or <slug>.<ext> for n = 1) takes the place of image n instead, credited from its ledger
    entry (source owner or permission) or, failing that, to the site. Running it again downloads and converts nothing twice.
Fetch candidates by index by hand, numbering on from the files already in the folder:
    worker/.venv/bin/python scripts/v2/find_images.py --out content/images/candidates/q-housing-0001.json --fetch mews-hall-guide --pick 0,2
Re-audit every published article's photos against the license and relevance rules (writes reports/photo-audit.md, changes nothing):
    worker/.venv/bin/python scripts/v2/find_images.py --audit [--audit-out reports/photo-audit.md]
Both store modes print a JSON list of the images placed to stdout; everything else goes to stderr ("not fetched" / "not used" lines
say why an entry was left alone).

Sources: Wikimedia Commons, then Openverse (Flickr and other open collections). Stock sites with their own licenses (Unsplash, Pexels)
are no longer searched: only CC0, public domain (PDM / "Public domain"), CC BY and CC BY-SA (any version) are accepted, and anything
else, including a missing or unclear license, NC and ND, is dropped. License fields are kept as the API returned them (a public-domain
Commons file has no license URL). Commons search needs every word to match, so a query that finds nothing is shortened from the end,
two words at least ("Mews Hall Cornell dorm review" -> "Mews Hall Cornell dorm" -> "Mews Hall Cornell"). A source that is down or rate
limited (Openverse anonymous: 20/min, 200/day) yields an empty list for that source, never a crash. Candidates are deduped by file_url.
Relevance (config/schools.yml): a photo is used only when its title or description names the article's school or town (namesakes in
`exclude` never pass) AND relates to the article's subject: the frontmatter `subject` (a string or list), else the title and primary
query. --query mode filters with --school and --subject (defaults: the config's default school; the queries themselves); --article mode
reads them from the frontmatter and refuses an entry that fails ("not used (off-topic: ...)" on stderr and a line in
build/runs/v2/photos.log), so a page gets no photo rather than an unrelated one. --audit re-checks every published article's photos
(license and relevance, Commons metadata fetched live) and writes reports/photo-audit.md.
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
from urllib.parse import unquote, urlsplit, urlunsplit

import httpx
import yaml
from PIL import Image, ImageOps

REPO = Path(__file__).resolve().parents[2]
# Wikimedia's User-Agent policy format: name/version (contact) library/version. Its edge returns 403 for any UA that contains
# "example.com", so the placeholder uses the reserved .example TLD. Replace the contact with the real editor address before launch.
USER_AGENT = f"FootnoteDaily-ImageFinder/1.0 (EduExplained image finder; editor@footnotedaily.example) httpx/{httpx.__version__}"
TIMEOUT = 10.0
MIN_WIDTH = 600            # smaller files are icons or thumbnails
MAX_WIDTH = 1600
MAX_BYTES = 150_000
MIMES = {"image/jpeg", "image/png", "image/webp"}
INBOX_SUFFIXES = {".jpg", ".jpeg", ".png", ".webp", ".tif", ".tiff", ".avif"}   # what Pillow opens here; HEIC is not among them
SOURCE_NAMES = {"wikimedia": "Wikimedia Commons"}
HOST_NAMES = {"flickr.com": "Flickr", "wikimedia.org": "Wikimedia Commons", "rawpixel.com": "Rawpixel", "europeana.eu": "Europeana"}
ACCEPT = re.compile(r"^(cc0|cc zero|pdm|pd|public domain|public domain mark|cc by|cc by sa)\b")   # commercial use allowed; never NC or ND
SCHOOLS_FILE = REPO / "config" / "schools.yml"
PHOTO_LOG = REPO / "build" / "runs" / "v2" / "photos.log"
STOPWORDS = frozenset(("a an and are as at be but by can do does for from how i if in into is it its my of on or should that the this to vs versus "
                       "what when where which who why will with without you your near best cheap cheapest worth cost costs guide students student "
                       "really actually get find need much many does").split())
OWNER_LICENSE = "All rights reserved"
FM_RE = re.compile(r"^﻿?---[ \t]*\n(.*?)\n---[ \t]*\n?(.*)$", re.S)
IMAGE_KEYS = ("file", "alt", "caption", "credit", "credit_url", "license", "license_url")


def accepted(license_name: str) -> bool:
    """CC0, public domain, CC BY or CC BY-SA (the licenses that allow commercial use); never NC or ND; never an empty or unknown license."""
    words = re.sub(r"[^a-z0-9]+", " ", (license_name or "").lower()).strip()
    if not words or "nc" in words.split() or "nd" in words.split():
        return False
    return bool(ACCEPT.match(words))


def clean(text: str) -> str:
    """Strip HTML (Commons returns Artist and descriptions as HTML) and collapse whitespace."""
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", str(text or "")))).strip()


# ------------------------------------------------------------------------------------------ relevance (config/schools.yml)
def words_of(text) -> list:
    return re.sub(r"[^a-z0-9]+", " ", str(text or "").lower()).split()


def phrase_in(phrase, text_words: list) -> bool:
    """The phrase's words appear in order in the text ("cornell university" in "cornell university west campus")."""
    pw = words_of(phrase)
    return bool(pw) and f" {' '.join(pw)} " in f" {' '.join(text_words)} "


def school_profile(slug=None):
    """The school an article names (or the config's default): name, the words that name it or its town, and the namesakes to refuse.
    None when config/schools.yml is missing or names no such school and no default."""
    data = yaml.safe_load(SCHOOLS_FILE.read_text(encoding="utf-8")) if SCHOOLS_FILE.exists() else None
    data = data if isinstance(data, dict) else {}
    schools = data.get("schools") or {}
    slug = str(slug or "").strip() or data.get("default")
    sc = schools.get(slug)
    if sc is None and data.get("default") in schools:
        if slug:
            print(f"school {slug!r} is not in {SCHOOLS_FILE.relative_to(REPO)}; using the default {data['default']!r}", file=sys.stderr)
        slug, sc = data["default"], schools[data["default"]]
    if not isinstance(sc, dict):
        return None
    place = [sc.get("name") or slug, *(sc.get("terms") or []), sc.get("town") or "", *(sc.get("town_terms") or [])]
    return {"slug": slug, "name": str(sc.get("name") or slug), "town": str(sc.get("town") or ""), "place_terms": [str(t) for t in place if t],
            "exclude": [str(t) for t in (sc.get("exclude") or []) if t]}


def subject_terms(subjects: list, school: dict) -> list:
    """The words of the subject phrases that carry meaning: no stopwords, nothing that only names the school or the town."""
    place_words = {w for t in school["place_terms"] for w in words_of(t)}
    out = []
    for s in subjects or []:
        for w in words_of(s):
            if len(w) >= 3 and w not in STOPWORDS and w not in place_words and w not in out:
                out.append(w)
    return out


def term_matches(term: str, text_words: list) -> bool:
    """Exact word, or the same first four letters for words of five or more ("housing" matches "houses", "transfer" matches "transfers")."""
    return any(w == term or (len(term) >= 5 and len(w) >= 5 and w[:4] == term[:4]) for w in text_words)


def irrelevant(c: dict, school: dict, subjects: list):
    """Why a candidate may not illustrate this article, or None when it may: its title or description must name the school or the town
    (never a namesake from `exclude`) and relate to the subject (a subject word, or a whole subject phrase, in the text)."""
    tw = words_of(f"{c.get('title') or ''} {c.get('description') or ''}")
    for ex in school["exclude"]:
        if phrase_in(ex, tw):
            return f"names {ex} (a namesake, not {school['name']})"
    if not any(phrase_in(t, tw) for t in school["place_terms"]):
        return f"names neither {school['name']} nor {school['town'] or 'its town'}"
    terms = subject_terms(subjects, school)
    if terms and not any(term_matches(t, tw) for t in terms) and not any(phrase_in(s, tw) for s in subjects):
        return "unrelated to the subject (" + ", ".join(terms[:6]) + ")"
    return None


def article_subjects(fm: dict) -> list:
    """The frontmatter `subject` (a string or list), else the title and primary query."""
    subj = fm.get("subject")
    if isinstance(subj, str) and subj.strip():
        return [subj.strip()]
    if isinstance(subj, list) and any(str(x).strip() for x in subj):
        return [str(x).strip() for x in subj if str(x).strip()]
    return [str(fm.get(k) or "").strip() for k in ("title", "primary_query") if str(fm.get(k) or "").strip()]


def log_photo(line: str) -> None:
    print(line, file=sys.stderr)
    try:
        PHOTO_LOG.parent.mkdir(parents=True, exist_ok=True)
        with PHOTO_LOG.open("a", encoding="utf-8") as fh:
            fh.write(f"{datetime.now().isoformat(timespec='seconds')} {line}\n")
    except OSError:
        pass


def strip_query(url: str) -> str:
    """Drop utm_* and other parameters so the same file dedupes across Commons and Openverse's Wikimedia mirror."""
    return urlunsplit(urlsplit(url or "")._replace(query="", fragment=""))


def same_url(a, b) -> bool:
    norm = lambda u: strip_query(str(u or "")).lower().replace("http://", "https://").rstrip("/")  # noqa: E731
    return bool(a) and bool(b) and norm(a) == norm(b)


def cand(source, title, page_url, file_url, thumb_url, author, license_name, license_url, width, height, description="") -> dict:
    return {"source": source, "title": clean(title)[:160], "page_url": page_url or "", "file_url": file_url or "",
            "thumb_url": thumb_url or "", "author": clean(author)[:120], "license": (license_name or "").strip(),
            "license_url": license_url or "", "width": int(width or 0), "height": int(height or 0), "description": clean(description)[:400]}


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
                        meta("Artist"), meta("LicenseShortName") or meta("License"), meta("LicenseUrl"), ii.get("width"), ii.get("height"),
                        meta("ImageDescription")))
    return out


def search_openverse(client: httpx.Client, q: str, n: int) -> list:
    r = client.get("https://api.openverse.org/v1/images/", params={"q": q, "license": "cc0,by,by-sa,pdm", "page_size": min(n, 20)})
    r.raise_for_status()
    out = []
    for x in r.json().get("results", []):
        slug, version = (x.get("license") or "").lower(), x.get("license_version") or ""   # e.g. "by-sa" and "4.0"
        name = {"cc0": "CC0", "pdm": "Public Domain Mark"}.get(slug, "CC " + slug.upper())
        out.append(cand("openverse", x.get("title"), x.get("foreign_landing_url"), x.get("url"), x.get("thumbnail"),
                        x.get("creator"), f"{name} {version}".strip(), x.get("license_url"), x.get("width"), x.get("height"),
                        " ".join(str(t.get("name") or "") for t in (x.get("tags") or []) if isinstance(t, dict))))
    return out


def search(queries: list, n: int, school=None, subjects=None) -> list:
    """Accepted-license candidates for the queries; with a school profile, only those relevant to it and the subjects (the queries when
    none are given)."""
    out, seen = [], set()
    subjects = list(subjects or queries)

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
                why = irrelevant(c, school, subjects) if school else None
                if why:
                    print(f"{name}: skipped {c['title'][:70]!r}: {why}", file=sys.stderr)
                    continue
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
        return str((cfg.get("site") or {}).get("name") or "EduExplained")
    except Exception:  # noqa: BLE001 - no config yet
        return "EduExplained"


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


def fetch(cands_path: Path, slug: str, picks: list, images_dir: Path, school=None, subjects=None) -> list:
    """Hand mode: candidates by index to <images-dir>/<slug>/<n>.webp, numbering on from the files already there. With a school
    profile (--school, or the config default) and --subject, a candidate that fails the relevance rule is not fetched."""
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
            why = irrelevant(c, school, subjects) if school and subjects else None
            if why:
                log_photo(f"{slug}: [{i}] {c.get('title', '')[:70]!r} not fetched (off-topic: {why})")
                continue
            name = f"{n + 1}.webp"
            try:
                save_webp(download(client, c["file_url"]), folder / name)
            except Exception as e:  # noqa: BLE001 - one bad file never stops the others
                print(f"[{i}] {c['file_url']}: {type(e).__name__}: {e}; not fetched", file=sys.stderr)
                continue
            n += 1
            entries.append(entry(slug, name, c["source"], c["page_url"], c["author"], c["license"], c["license_url"], found_at, credit(c)))
            placed.append({"file": name, "alt_suggestion": c["title"], "caption": c["title"], "credit": credit(c), "author": c["author"],
                           "credit_url": c["page_url"], "source_url": c["page_url"], "license": c["license"], "license_url": c["license_url"]})
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
    school, subjects = school_profile(fm.get("school")), article_subjects(fm)
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
                if not accepted(c["license"]):
                    print(f"images[{i}] {old}: license {c['license']!r} is not accepted; not used", file=sys.stderr)
                    continue
                why = irrelevant(c, school, subjects) if school else None
                if why:   # no photo rather than an off-topic one (owner rule); a file already stored stays in the folder, unreferenced
                    log_photo(f"{slug}: images[{i}] {c.get('title', '')[:70]!r} not used (off-topic: {why}; subject {' / '.join(subjects)[:80]!r})")
                    continue
                if not dest.exists():
                    try:
                        save_webp(download(client, c["file_url"]), dest)
                    except Exception as e:  # noqa: BLE001
                        print(f"images[{i}] {c['file_url']}: {type(e).__name__}: {e}; not fetched", file=sys.stderr)
                        continue
                    entries.append(entry(slug, name, c["source"], c["page_url"], c["author"], c["license"], c["license_url"], found_at, credit(c)))
                new = {"file": name, "credit": normalize_credit(im.get("credit"), im.get("license")) or credit(c), "author": c["author"],
                       "credit_url": c["page_url"], "source_url": c["page_url"], "license": c["license"], "license_url": c["license_url"]}
            im.update(new)
            if old and old != name:
                body = re.sub(r"\]\(\s*(?:/images/" + re.escape(slug) + "/)?" + re.escape(old) + r"\s*\)", f"]({name})", body)
            done.append({k: im.get(k, "") for k in IMAGE_KEYS + ("author", "source_url")})
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


# ------------------------------------------------------------------------------------------ audit of the live photos
def commons_meta(client: httpx.Client, page_url: str):
    """Title, description, author and license of a Commons file page, fetched live; None for any other page."""
    m = re.search(r"commons\.wikimedia\.org/wiki/(File:[^?#]+)", page_url or "")
    if not m:
        return None
    title = unquote(m.group(1)).replace("_", " ")
    try:
        r = client.get("https://commons.wikimedia.org/w/api.php", params={"action": "query", "format": "json", "titles": title, "prop": "imageinfo",
                                                                           "iiprop": "extmetadata", "iiextmetadatafilter": "LicenseShortName|License|Artist|LicenseUrl|ImageDescription"})
        r.raise_for_status()
        pages = r.json().get("query", {}).get("pages", {})
    except Exception as e:  # noqa: BLE001
        print(f"commons {title!r}: {type(e).__name__}: {e}", file=sys.stderr)
        return None
    for pg in pages.values():
        ii = (pg.get("imageinfo") or [{}])[0]
        em = ii.get("extmetadata") or {}
        meta = lambda k: (em.get(k) or {}).get("value") or ""  # noqa: E731
        if not ii:
            return None
        return {"title": re.sub(r"^File:|\.[^.]+$", "", pg.get("title", "")), "description": clean(meta("ImageDescription")), "author": clean(meta("Artist")),
                "license": (meta("LicenseShortName") or meta("License")).strip(), "license_url": meta("LicenseUrl")}
    return None


def audit(articles_dir: Path, queue_path: Path, images_dir: Path, out_path: Path) -> int:
    """Every published article's photos against the license and relevance rules; a Markdown report; returns the number of failing photos.
    Nothing is changed: a failing photo is removed by hand (or the article goes back through the image step)."""
    import csv
    with queue_path.open(newline="", encoding="utf-8-sig") as fh:
        published = {(r.get("id") or "").strip() for r in csv.DictReader(fh) if (r.get("status") or "").strip() == "published"}
    ledger, _ = load_ledger(images_dir / "credits.yml")
    rows, failing, checked = [], 0, 0
    with httpx.Client(timeout=TIMEOUT, follow_redirects=True, headers={"User-Agent": USER_AGENT}) as client:
        for path in sorted(articles_dir.glob("*/*.md")):
            m = FM_RE.match(path.read_text(encoding="utf-8"))
            fm = (yaml.safe_load(m.group(1)) or {}) if m else {}
            if str(fm.get("queue_id") or "") not in published:
                continue
            slug, school, subjects = path.stem, school_profile(fm.get("school")), article_subjects(fm)
            images = [im for im in (fm.get("images") or []) if isinstance(im, dict)]
            if not images:
                rows.append((slug, "", "none", "", "", "no photo", "the page has no photo"))
                continue
            cands_path = images_dir / "candidates" / f"{fm.get('queue_id')}.json"
            cands = json.loads(cands_path.read_text(encoding="utf-8")) if cands_path.exists() else []
            for i, im in enumerate(images):
                checked += 1
                url = str(im.get("source_url") or im.get("credit_url") or "")
                meta = commons_meta(client, url)
                c = next((c for c in cands if same_url(url, c.get("page_url"))), {})
                led = next((e for e in ledger if e.get("article_slug") == slug and e.get("file") == im.get("file")), {})
                title = (meta or {}).get("title") or c.get("title") or unquote(url.rsplit("/", 1)[-1]).replace("_", " ")
                desc = (meta or {}).get("description") or c.get("description") or ""
                lic = (meta or {}).get("license") or str(im.get("license") or led.get("license") or "")
                author = (meta or {}).get("author") or str(im.get("author") or led.get("author") or "")
                problems = []
                if not accepted(lic):
                    problems.append(f"license {lic or 'missing'!r} is not CC0, public domain, CC BY or CC BY-SA")
                why = irrelevant({"title": title, "description": desc}, school, subjects) if school else None
                if why:
                    problems.append(why)
                if not url:
                    problems.append("no source URL")
                if not author:
                    problems.append("no author")
                if not (im.get("license_url") or led.get("license_url")) and not re.match(r"^(public domain|pd|pdm|cc0)", re.sub(r"[^a-z0-9]+", " ", lic.lower()).strip()):
                    problems.append("no license URL")
                failing += bool(problems)
                rows.append((slug, str(im.get("file") or ""), "lead" if i == 0 else f"image {i + 1}", title[:90], lic, "FAIL" if problems else "pass", "; ".join(problems)))
    lines = [f"# Photo audit, {date.today().isoformat()}", "",
             "Every photo on a published page against the owner's rules (v3 catch-up part 2, step 3): license CC0, public domain, CC BY or CC BY-SA; the",
             "title or description names the article's school or town (config/schools.yml, namesakes excluded) and relates to the article's subject",
             "(the frontmatter `subject`, else the title and primary query); source URL, author, license and license URL stored. Commons metadata",
             "fetched live by scripts/v2/find_images.py --audit. Nothing was changed: a failing lead photo is removed or replaced by hand.", "",
             f"Checked {checked} photo(s) on {len({r[0] for r in rows})} published page(s): {failing} fail.", "",
             "| article | file | role | title | license | result | why |", "|---|---|---|---|---|---|---|"]
    lines += ["| " + " | ".join(str(x).replace("|", "/") for x in r) + " |" for r in rows]
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"audit: {checked} photos, {failing} failing -> {out_path}", file=sys.stderr)
    return failing


def main(argv: list) -> int:
    ap = argparse.ArgumentParser(description="Find openly licensed, relevant photos (Wikimedia Commons, Openverse) and store them as WebP.")
    ap.add_argument("--query", action="append", default=[], help="subject to search, e.g. 'Mews Hall Cornell' (repeatable)")
    ap.add_argument("--out", type=Path, help="candidates JSON: written by --query, read by --fetch and --article "
                                              "(--article defaults to <images-dir>/candidates/<queue_id>.json)")
    ap.add_argument("--n", type=int, default=8, help="results to ask each source for (default 8)")
    ap.add_argument("--article", type=Path, metavar="MD", help="article file: store the images its frontmatter lists")
    ap.add_argument("--fetch", metavar="SLUG", help="article slug: download --pick candidates to <images-dir>/<slug>/<n>.webp")
    ap.add_argument("--pick", default="", help="comma-separated candidate indexes for --fetch, e.g. 0,2")
    ap.add_argument("--images-dir", type=Path, default=REPO / "content" / "images", help="default content/images")
    ap.add_argument("--school", default="", help="school slug from config/schools.yml for the relevance rule (default: the config's default school)")
    ap.add_argument("--subject", action="append", default=[], help="the article's subject for the relevance rule (repeatable; default: the queries)")
    ap.add_argument("--audit", action="store_true", help="re-check every published article's photos (license, relevance, credit fields); changes nothing")
    ap.add_argument("--audit-out", type=Path, default=REPO / "reports" / "photo-audit.md")
    ap.add_argument("--articles-dir", type=Path, default=REPO / "content" / "articles")
    ap.add_argument("--queue", type=Path, default=REPO / "queue" / "queue.csv")
    args = ap.parse_args(argv)
    if args.audit:
        return 1 if audit(args.articles_dir, args.queue, args.images_dir, args.audit_out) else 0
    if not (args.query or args.article or args.fetch):
        ap.error("give --query to search, --article MD, --fetch SLUG --pick I,J to store photos, or --audit")
    if (args.query or args.fetch) and not args.out:
        ap.error("--query and --fetch need --out (the candidates JSON)")
    school = school_profile(args.school)
    if args.query:
        cands = search(args.query, args.n, school=school, subjects=args.subject or None)
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(cands, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"{len(cands)} candidates -> {args.out}", file=sys.stderr)
    if args.article:
        print(json.dumps(fetch_article(args.article, args.out, args.images_dir), indent=1, ensure_ascii=False))
    if args.fetch:
        picks = [int(p) for p in args.pick.split(",") if p.strip()]
        if not picks:
            ap.error("--fetch needs --pick with at least one candidate index")
        print(json.dumps(fetch(args.out, args.fetch, picks, args.images_dir, school=school, subjects=args.subject or None), indent=1, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
