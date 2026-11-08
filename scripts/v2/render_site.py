#!/usr/bin/env python
"""Render the Footnote Daily v2 static site (docs/v2/spec.md, step 4: lint and publish).

    worker/.venv/bin/python scripts/v2/render_site.py [--out build/site] [--production] [--all]
        [--articles-dir content/articles] [--pages-dir content/pages] [--images-dir content/images] [--reviews-dir content/reviews]
        [--queue queue/queue.csv] [--config config/monetization.yml]

Reads content/articles/<topic>/<slug>.md (frontmatter + Markdown, optional ```figure blocks), content/pages/*.md (about, privacy,
contact, editorial-policy, corrections) and config/monetization.yml, and writes:
    /  /<topic>/  /<topic>/<slug>/  /<page>/  404.html  robots.txt  sitemap.xml  ads.txt  /static/  /images/<slug>/<n>.webp
Only articles whose queue row (queue/queue.csv) is in status published are rendered: publish.sh sets that after the review passed
and the lint is clean, so a draft, an article waiting for review or one that failed the lint never reaches the site. --all renders
every article (a local preview); a review (content/reviews/<slug>.json) with verdict reject is skipped either way.
A non-production build carries noindex on every page, a disallow-all robots.txt, an empty sitemap and no third-party scripts or ad
containers. --production (or site.production: true in the config) turns them on. A summary goes to stdout and to
build/runs/v2/render-<timestamp>.log.
"""
from __future__ import annotations

import argparse
import csv
import html
import json
import re
import shutil
import sys
from datetime import date, datetime
from pathlib import Path
from urllib.parse import urlsplit

import markdown
import yaml
from jinja2 import Environment, FileSystemLoader, select_autoescape

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "worker"))
from campus_worker.render import figures  # noqa: E402  (worker/campus_worker/render/figures.py; stdlib only)

RENDER = REPO / "worker" / "campus_worker" / "render"
TEMPLATES = RENDER / "templates" / "v2"
STATIC = RENDER / "static"
STATIC_FILES = ("campus.css", "v2.css", "fonts")       # not the v1 tools scripts or the synthetic placeholder images

TOPICS = {  # fixed slugs (contract 1), in site order
    "housing": ("Housing", "Dorms, program houses, co-ops, Collegetown and downtown apartments, leases, landlords, roommates and moving."),
    "getting-around": ("Getting around", "Flights into ITH and SYR, buses to NYC and Boston, airport rides, TCAT, parking, biking and break travel."),
    "academics": ("Academics", "Courses and professors, requirements, registration strategy, add/drop, internal transfer and study spots."),
    "money": ("Money", "Real cost of living, meal plan math, cheap groceries, jobs, financial aid appeals and budgets by scenario."),
    "daily-life": ("Daily life", "Dining, food in Collegetown and downtown, gyms, health care, phones and banking, winter gear, safety and clubs."),
    "careers": ("Careers", "Internships, recruiting timelines, career fairs and the employers that hire from campus."),
    "parents": ("Parents", "Visiting, hotels, move-in weekend, graduation and what to send."),
    "alumni": ("Alumni", "Benefits, events and staying in Ithaca after graduation."),
}
TYPE_LABELS = {"how-to": "How-to", "decision": "Decision guide", "scenario": "Scenario guide", "comparison": "Comparison", "place": "Place guide",
               "checklist": "Checklist", "roundup": "Roundup"}
PAGE_ORDER = ("about", "editorial-policy", "corrections", "contact", "privacy")
FAQ_HEAD = re.compile(r"<h2[^>]*>\s*(?:FAQs?|Frequently asked questions|Common questions|Related questions)\s*</h2>", re.I)
FIGURE_FENCE = re.compile(r"^```figure[ \t]*\n(.*?)\n```[ \t]*$", re.S | re.M)
PARAGRAPH_END = re.compile(r"</p>\n(?=<(?:p|h[2-6]|ul|ol|div|figure|table|blockquote|pre|hr|section)\b)")   # top-level paragraphs only
DEFAULT_DISCLOSURE = "This guide contains affiliate links. If you buy through one we may earn a commission at no extra cost to you; it never changes what we recommend."
IMAGE_MAX_BYTES = 150_000
IMAGE_MAX_WIDTH = 1600
WARNINGS: list[str] = []


def warn(msg: str) -> None:
    WARNINGS.append(msg)
    print("warning:", msg, file=sys.stderr)


# ------------------------------------------------------------------------------------------------ small helpers
def to_date(v) -> date | None:
    if isinstance(v, datetime):
        return v.date()
    if isinstance(v, date):
        return v
    try:
        return date.fromisoformat(str(v).strip()[:10]) if v else None
    except ValueError:
        return None


def datefmt(d: date | None) -> str:
    return f"{d:%B} {d.day}, {d.year}" if d else ""


def frontmatter(text: str) -> tuple[dict, str]:
    """Split a leading YAML block from the Markdown body. No block: empty frontmatter."""
    m = re.match(r"^---[ \t]*\n(.*?)\n---[ \t]*\n?(.*)$", text.lstrip("﻿"), re.S)
    if not m:
        return {}, text
    try:
        fm = yaml.safe_load(m.group(1)) or {}
    except yaml.YAMLError as e:
        raise ValueError(f"bad frontmatter: {e}") from e
    return (fm if isinstance(fm, dict) else {}), m.group(2)


def clean_title(title, url: str) -> str:
    """A source title without the trailing ' | Site' or ' - Site' tail; the host and path when there is no title."""
    t = " ".join(str(title or "").split())
    if not t:
        u = urlsplit(url)
        return (u.netloc + u.path).rstrip("/") or url
    for sep in (" | ", " - ", " – ", " — "):
        if sep in t and len(t.split(sep)[0]) >= 20:
            t = t.split(sep)[0].strip()
    return t


def strip_tags(s: str) -> str:
    return html.unescape(" ".join(re.sub(r"<[^>]+>", "", s).split()))


def md_html(text: str) -> str:
    return markdown.markdown(text, extensions=["tables", "fenced_code", "sane_lists"], output_format="html5")


def load_config(path: Path) -> dict:
    """config/monetization.yml with every key present (contract 6); missing or empty file gives the all-off defaults."""
    cfg = {"site": {"name": "Footnote Daily", "domain": "", "production": False}, "analytics": {"ga4_measurement_id": "", "gsc_verification": ""},
           "consent": {"provider": "", "script_url": ""},
           "ads": {"provider": "none", "adsense_client": "", "script_url": "", "slots": {"in_content": "", "sidebar": "", "sticky_footer": ""}},
           "grow": {"enabled": False, "site_id": ""}, "affiliates": {"disclosure": "", "programs": []}}
    data = yaml.safe_load(path.read_text(encoding="utf-8")) if path.exists() else {}
    for k, v in (data or {}).items():
        if isinstance(v, dict) and isinstance(cfg.get(k), dict):
            for k2, v2 in v.items():
                if isinstance(v2, dict) and isinstance(cfg[k].get(k2), dict):
                    cfg[k][k2].update({a: b for a, b in v2.items() if b is not None})
                elif v2 is not None:
                    cfg[k][k2] = v2
        elif v is not None:
            cfg[k] = v
    return cfg


# ------------------------------------------------------------------------------------------------ monetization markup
def head_scripts(cfg: dict, production: bool, ads: bool = True) -> str:
    """Consent platform, GA4 and Grow, plus the ad network's loader when `ads` (articles, topic pages and the home; the policy pages
    and the 404 carry no ads), each only when configured, and none on a non-production build."""
    if not production:
        return ""
    out = []
    ga = str(cfg["analytics"].get("ga4_measurement_id") or "").strip()
    consent_url = str(cfg["consent"].get("script_url") or "").strip()
    if consent_url:
        out.append("<script>window.dataLayer=window.dataLayer||[];function gtag(){dataLayer.push(arguments);}"
                   "gtag('consent','default',{ad_storage:'denied',ad_user_data:'denied',ad_personalization:'denied',analytics_storage:'denied',wait_for_update:500});</script>")
        out.append(f'<script src="{html.escape(consent_url)}" async data-consent-provider="{html.escape(str(cfg["consent"].get("provider") or ""))}"></script>')
    if ga:
        out.append(f'<script async src="https://www.googletagmanager.com/gtag/js?id={html.escape(ga)}"></script>'
                   f"<script>window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments);}}gtag('js',new Date());gtag('config','{html.escape(ga)}');</script>")
    grow = cfg["grow"]
    if grow.get("enabled") and str(grow.get("site_id") or "").strip():
        sid = html.escape(str(grow["site_id"]).strip())
        out.append('<script data-grow-initializer="">!(function(){window.growMe||((window.growMe=function(e){window.growMe._.push(e);}),(window.growMe._=[]));'
                   'var e=document.createElement("script");(e.type="text/javascript"),(e.src="https://faves.grow.me/main.js"),(e.defer=!0),'
                   f'e.setAttribute("data-grow-faves-site-id","{sid}");var t=document.getElementsByTagName("script")[0];t.parentNode.insertBefore(e,t);}})();</script>')
    if not ads:
        pass
    elif ads_provider(cfg) == "adsense" and str(cfg["ads"].get("adsense_client") or "").strip():
        out.append(f'<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client={html.escape(cfg["ads"]["adsense_client"].strip())}" crossorigin="anonymous"></script>')
    elif ads_provider(cfg) and str(cfg["ads"].get("script_url") or "").strip():     # Mediavine and Raptive: one script, their own placements
        out.append(f'<script async src="{html.escape(str(cfg["ads"]["script_url"]).strip())}" data-ad-provider="{ads_provider(cfg)}"></script>')
    return "\n".join(out)


def ads_provider(cfg: dict) -> str:
    p = str(cfg["ads"].get("provider") or "none").strip().lower()
    return p if p in ("adsense", "mediavine", "raptive") else ""


def ad_slot(cfg: dict, name: str, production: bool) -> str:
    """The AdSense container for one slot (in_content, sidebar, sticky_footer), or '' when it is not configured (no empty boxes).
    Mediavine and Raptive place their own ads from their script, so they get no containers."""
    slot = str((cfg["ads"].get("slots") or {}).get(name) or "").strip()
    client = str(cfg["ads"].get("adsense_client") or "").strip()
    if ads_provider(cfg) != "adsense" or not production or not client or not slot:
        return ""
    attrs = f'class="adsbygoogle" data-ad-client="{html.escape(client)}" data-ad-slot="{html.escape(slot)}"'
    if name == "sticky_footer":   # a fixed 320x50 mobile banner: it always fits the 58px bar, so no ad is ever clipped
        unit = f'<ins {attrs} style="display:inline-block;width:320px;height:50px"></ins>'
    else:
        unit = f'<span class="ad-slot__label">Advertisement</span><ins {attrs} style="display:block" data-ad-format="auto" data-full-width-responsive="true"></ins>'
    return f'<div class="ad-slot ad-slot--{name}">{unit}<script>(adsbygoogle=window.adsbygoogle||[]).push({{}});</script></div>'


def ads_txt(cfg: dict) -> str:
    provider = ads_provider(cfg)
    client = str(cfg["ads"].get("adsense_client") or "").strip()
    if provider == "adsense" and client:
        return f"google.com, {client.removeprefix('ca-')}, DIRECT, f08c47fec0942fa0\n"
    if provider:
        return f"# ads.txt lines come from {provider}; paste them here when the network sends them.\n"
    return ""


def affiliate_domains(cfg: dict) -> list[str]:
    out = []
    for p in cfg["affiliates"].get("programs") or []:
        d = (p.get("domain") or p.get("url") or "") if isinstance(p, dict) else p
        d = str(d or "").strip().lower()
        d = re.sub(r"^https?://", "", d).split("/")[0]
        if d:
            out.append(d)
    return out


# ------------------------------------------------------------------------------------------------ article body
def figure_html(fig: dict) -> str:
    cap = f'<figcaption><b class="figure__title">{html.escape(fig["title"])}</b> {html.escape(fig.get("caption") or "")}</figcaption>'
    return f'<figure class="figure figure--{fig["kind"]}">{cap}{fig["svg"]}</figure>'


def figure_yaml(text: str) -> dict:
    """The YAML of a figure block. Labels often carry a colon ("Move-in (2025 dates: August 18 and 19)"), which strict YAML
    rejects, so on failure every `key: value` scalar is quoted and parsed again."""
    try:
        return yaml.safe_load(text)
    except yaml.YAMLError:
        quoted = re.sub(r'^([ \t]*(?:-[ \t]+)?\w+:[ \t]+)(?!["\'\[{])(.+?)[ \t]*$', lambda m: m.group(1) + '"' + m.group(2).replace("\\", "\\\\").replace('"', '\\"') + '"', text, flags=re.M)
        return yaml.safe_load(quoted)


def extract_figures(body: str, slug: str, today: date) -> tuple[str, dict[str, str]]:
    """Replace each ```figure fence with a token line; return the body and token -> figure HTML. A block that fails is dropped with a warning."""
    figs: dict[str, str] = {}

    def repl(m):
        n = len(figs)
        try:
            spec = figure_yaml(m.group(1))
            fig = figures.figure_from_block(spec, uid=f"fig-{slug}-{n + 1}", today=today)
        except Exception as e:  # noqa: BLE001 - bad YAML or a malformed block drops that figure, never the page
            warn(f"{slug}: figure block {n + 1} could not be drawn ({type(e).__name__}: {str(e).splitlines()[0]}); dropped")
            return ""
        if not fig:
            warn(f"{slug}: figure block {n + 1} has an unknown kind or no rows; dropped")
            return ""
        token = f"@@FIGURE{n}@@"
        figs[token] = figure_html(fig)
        return token

    return FIGURE_FENCE.sub(repl, body), figs


def photo_figure(img: dict, slug: str, lede: bool = False) -> str:
    """A credited photo: '<caption> Photo: <credit, linked to its page>, <license, linked>'. The credit may come as
    'Jane Doe / Wikimedia Commons' or already in the finder's full form 'Photo: Jane Doe / Wikimedia Commons, CC BY-SA 4.0'."""
    lic_text = " ".join(str(img.get("license") or "").split())
    credit = re.sub(r"^\s*photo:\s*", "", " ".join(str(img.get("credit") or "").split()), flags=re.I)
    if lic_text and credit.lower().endswith(", " + lic_text.lower()):
        credit = credit[: -len(lic_text) - 2].rstrip()
    credit = html.escape(credit)
    if credit and img.get("credit_url"):
        credit = f'<a href="{html.escape(img["credit_url"])}" rel="noopener">{credit}</a>'
    lic = html.escape(lic_text)
    if lic and img.get("license_url"):
        lic = f'<a href="{html.escape(img["license_url"])}" rel="license noopener">{lic}</a>'
    credit_line = ", ".join(x for x in (f"Photo: {credit}" if credit else "", lic) if x)
    caption = html.escape(img.get("caption") or "")
    size = f' width="{img["width"]}" height="{img["height"]}"' if img.get("width") else ""
    loading = ' fetchpriority="high"' if lede else ' loading="lazy" decoding="async"'
    return (f'<figure class="photo{" photo--lede" if lede else ""}"><img src="/images/{slug}/{html.escape(img["out"])}" alt="{html.escape(img.get("alt") or "")}"{size}{loading}>'
            f'<figcaption>{caption}{" " if caption and credit_line else ""}<span class="photo__credit">{credit_line}</span></figcaption></figure>')


def place_images(body_html: str, images: list[dict], slug: str) -> tuple[str, str]:
    """Body references (`![alt](1.webp)` on its own line) become credited figures in place; the first unreferenced image is the lede;
    the rest go before the second, third, ... h2. Returns (lede figure HTML, body HTML)."""
    used: set[int] = set()

    def swap(m):
        name = m.group(1).rsplit("/", 1)[-1]
        for i, im in enumerate(images):
            if name in (im["file"], im["out"]):
                used.add(i)
                return photo_figure(im, slug)
        return m.group(0)

    body_html = re.sub(r'<p><img[^>]*?src="([^"]+)"[^>]*></p>', swap, body_html)
    rest = [im for i, im in enumerate(images) if i not in used]
    lede = photo_figure(rest.pop(0), slug, lede=True) if rest else ""
    if rest:
        parts = re.split(r"(?=<h2\b)", body_html)
        out = parts[:2]
        for p in parts[2:]:
            out += [photo_figure(rest.pop(0), slug) if rest else "", p]
        body_html = "".join(out) + "".join(photo_figure(im, slug) for im in rest)
    return lede, body_html


def faq_section(body_html: str) -> tuple[str, list[tuple[str, str]]]:
    """Wrap an FAQ heading and its section in <section class="faq">; return the question/answer pairs (h3 + paragraphs, or a bold lead)."""
    m = FAQ_HEAD.search(body_html)
    if not m:
        return body_html, []
    end = body_html.find("<h2", m.end())
    end = len(body_html) if end < 0 else end
    sec = body_html[m.start():end]
    items = [(strip_tags(q), strip_tags(a)) for q, a in re.findall(r"<h3[^>]*>(.*?)</h3>\s*((?:<p>.*?</p>\s*)+)", sec, re.S)]
    if not items:
        items = [(strip_tags(q), strip_tags(a)) for q, a in re.findall(r"<p><strong>(.*?)</strong>\s*(.*?)</p>", sec, re.S)]
    return body_html[:m.start()] + '<section class="faq">' + sec.rstrip("\n") + "</section>\n" + body_html[end:], [(q, a) for q, a in items if q and a]


def insert_after_paragraph(body_html: str, n: int, snippet: str) -> str:
    """Put a snippet after the n-th top-level paragraph; a body with fewer paragraphs gets none."""
    if not snippet:
        return body_html
    for i, m in enumerate(PARAGRAPH_END.finditer(body_html), 1):
        if i == n:
            return body_html[:m.end()] + snippet + "\n" + body_html[m.end():]
    return body_html


def json_ld(a: dict, site: dict, faq: list[tuple[str, str]]) -> str:
    url = f"{site['base_url']}{a['path']}" if site.get("base_url") else a["path"]
    data = [{"@context": "https://schema.org", "@type": "Article", "headline": a["title"], "description": a["meta"], "dateModified": a["updated_iso"],
             "mainEntityOfPage": url, "publisher": {"@type": "Organization", "name": site["name"]},
             **({"image": [f"{site.get('base_url', '')}/images/{a['slug']}/{im['out']}" for im in a["images"]]} if a["images"] else {})}]
    if faq:
        data.append({"@context": "https://schema.org", "@type": "FAQPage",
                     "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": ans}} for q, ans in faq]})
    return json.dumps(data if len(data) > 1 else data[0], ensure_ascii=False).replace("</", "<\\/")


# ------------------------------------------------------------------------------------------------ images
def copy_image(src: Path, out_dir: Path, name: str) -> tuple[str, int, int] | None:
    """Copy an article image into the build as <name>.webp. A WebP already under 150 KB is copied as it is; anything else (a PNG, a
    phone JPEG, an oversized WebP) is turned the right way up, capped at 1600 px wide and saved as WebP, lowering the quality and
    then the size until it is under 150 KB. Returns (file name, width, height)."""
    from PIL import Image, ImageOps

    out_dir.mkdir(parents=True, exist_ok=True)
    dest = out_dir / f"{name}.webp"
    try:
        with Image.open(src) as im:
            if src.suffix.lower() == ".webp" and src.stat().st_size <= IMAGE_MAX_BYTES:
                shutil.copy2(src, dest)
                return dest.name, im.width, im.height
            im = ImageOps.exif_transpose(im)
            im = im.convert("RGBA" if im.mode in ("RGBA", "LA", "P") else "RGB")
            if im.width > IMAGE_MAX_WIDTH:
                im = im.resize((IMAGE_MAX_WIDTH, max(1, round(im.height * IMAGE_MAX_WIDTH / im.width))))
            quality = 82
            while True:
                im.save(dest, "WEBP", quality=quality)
                if dest.stat().st_size <= IMAGE_MAX_BYTES or (quality <= 50 and im.width <= 640):
                    break
                if quality > 50:
                    quality -= 8
                else:
                    im = im.resize((int(im.width * 0.85), int(im.height * 0.85)))
            return dest.name, im.width, im.height
    except OSError as e:
        warn(f"{src}: cannot read image ({e}); skipped")
        return None


def published_ids(queue_path: Path) -> set[str]:
    """Ids of the queue rows in status published (queue/queue.csv, contract 1)."""
    if not queue_path.is_file():
        return set()
    with queue_path.open(newline="", encoding="utf-8-sig") as fh:
        return {(r.get("id") or "").strip() for r in csv.DictReader(fh) if (r.get("status") or "").strip() == "published"}


# ------------------------------------------------------------------------------------------------ content loading
def article_images(fm: dict, slug: str, images_dir: Path, out: Path, path: Path) -> list[dict]:
    """The frontmatter images that exist under content/images/<slug>/, copied into the build. A file named 1.jpg in the frontmatter
    also finds the 1.webp the finder stored (same stem). Owner photos are not handled here: scripts/v2/find_images.py --article
    moves an inbox drop into the article folder and the frontmatter, so the renderer has one source of truth."""
    images = []
    for im in fm.get("images") if isinstance(fm.get("images"), list) else []:
        if not isinstance(im, dict) or not im.get("file"):
            continue
        name = Path(str(im["file"])).stem
        src = images_dir / slug / str(im["file"])
        if not src.is_file():
            src = next(iter(sorted((images_dir / slug).glob(f"{name}.*"))), src)
        if not src.is_file():
            warn(f"{path}: image {src} not found; skipped")
            continue
        copied = copy_image(src, out / "images" / slug, name)
        if copied:
            images.append({**{k: str(im.get(k) or "") for k in ("alt", "caption", "credit", "credit_url", "license", "license_url")},
                           "file": str(im["file"]), "out": copied[0], "width": copied[1], "height": copied[2]})
    return images


def load_articles(articles_dir: Path, reviews_dir: Path, images_dir: Path, out: Path, today: date, published: set[str] | None = None) -> list[dict]:
    """Every renderable article, newest first. With `published` (a set of queue ids) only articles whose queue_id is in it are kept."""
    arts, held = [], []
    for path in sorted(articles_dir.glob("*/*.md")):
        try:
            fm, body = frontmatter(path.read_text(encoding="utf-8"))
        except ValueError as e:
            warn(f"{path}: {e}; skipped")
            continue
        slug, topic, queue_id = path.stem, str(fm.get("topic") or path.parent.name), str(fm.get("queue_id") or "")
        if published is not None and queue_id not in published:
            held.append(f"{path.parent.name}/{slug} ({queue_id or 'no queue_id'})")
            continue
        missing = [k for k in ("title", "meta", "updated") if not fm.get(k)]
        if topic not in TOPICS:
            missing.append(f"topic {topic!r} is not one of {', '.join(TOPICS)}")
        updated = to_date(fm.get("updated"))
        if not updated and "updated" not in missing:
            missing.append("updated (YYYY-MM-DD)")
        if missing:
            warn(f"{path}: missing {', '.join(missing)}; skipped")
            continue
        review = reviews_dir / f"{slug}.json"
        if review.exists():
            try:
                if (json.loads(review.read_text(encoding="utf-8")) or {}).get("verdict") == "reject":
                    warn(f"{path}: review verdict is reject; skipped")
                    continue
            except ValueError:
                warn(f"{review}: unreadable review json; article rendered anyway")
        sources = [{"url": str(s.get("url") or ""), "title": clean_title(s.get("title"), str(s.get("url") or "")), "accessed": datefmt(to_date(s.get("accessed")))}
                   for s in (fm.get("sources") or []) if isinstance(s, dict) and s.get("url")]
        arts.append({"slug": slug, "topic": topic, "topic_label": TOPICS[topic][0], "topic_href": f"/{topic}/", "path": f"/{topic}/{slug}/",
                     "title": str(fm["title"]).strip(), "meta": str(fm["meta"]).strip(), "type_label": TYPE_LABELS.get(str(fm.get("type") or "").strip(), ""),
                     "updated": updated, "updated_iso": updated.isoformat(), "updated_text": datefmt(updated), "body": body, "sources": sources,
                     "images": article_images(fm, slug, images_dir, out, path),
                     "reading_time": max(1, round(len(re.findall(r"\w+", FIGURE_FENCE.sub("", body))) / 230)), "queue_id": queue_id})
    if held:
        warn(f"{len(held)} article(s) whose queue row is not published were left out (--all renders them): {', '.join(held)}")
    arts.sort(key=lambda a: (a["updated"], a["title"]), reverse=True)
    return arts


def load_pages(pages_dir: Path) -> list[dict]:
    pages = []
    for path in sorted(pages_dir.glob("*.md")):
        try:
            fm, body = frontmatter(path.read_text(encoding="utf-8"))
        except ValueError as e:
            warn(f"{path}: {e}; skipped")
            continue
        if not fm.get("title") or not fm.get("meta"):
            warn(f"{path}: pages need title and meta in the frontmatter; skipped")
            continue
        upd = to_date(fm.get("updated"))
        pages.append({"slug": path.stem, "path": f"/{path.stem}/", "title": str(fm["title"]).strip(), "meta": str(fm["meta"]).strip(), "body": body,
                      "updated": upd, "updated_iso": upd.isoformat() if upd else "", "updated_text": datefmt(upd)})
    pages.sort(key=lambda p: (PAGE_ORDER.index(p["slug"]) if p["slug"] in PAGE_ORDER else len(PAGE_ORDER), p["slug"]))
    return pages


# ------------------------------------------------------------------------------------------------ build
def related_for(a: dict, arts: list[dict]) -> list[dict]:
    same = [b for b in arts if b["topic"] == a["topic"] and b["slug"] != a["slug"]][:4]
    if len(same) < 2:
        same += [b for b in arts if b["slug"] != a["slug"] and b not in same][: 2 - len(same)]
    return same


def build(args) -> int:
    cfg = load_config(Path(args.config))
    production = bool(args.production or cfg["site"].get("production"))
    out = Path(args.out).resolve()
    if out in (Path("/"), REPO, Path.cwd()) or out == REPO.parent:
        print(f"refusing to build into {out}", file=sys.stderr)
        return 2
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)
    today = date.today()
    domain = str(cfg["site"].get("domain") or "").strip().rstrip("/")
    site = {"name": str(cfg["site"].get("name") or "Footnote Daily"), "base_url": f"https://{domain}" if domain else ""}
    if production and not domain:
        warn("production build without site.domain: canonical URLs and the sitemap need it")

    arts = load_articles(Path(args.articles_dir), Path(args.reviews_dir), Path(args.images_dir), out, today,
                         published=None if args.all else published_ids(Path(args.queue)))
    pages = load_pages(Path(args.pages_dir))
    by_topic = {t: [a for a in arts if a["topic"] == t] for t in TOPICS}
    nav = [{"label": TOPICS[t][0], "href": f"/{t}/"} for t in TOPICS if by_topic[t]]
    footer_links = [{"label": p["title"].replace("About " + site["name"], "About"), "href": p["path"]} for p in pages]
    ads = {"provider": ads_provider(cfg) if production else "", "in_content": ad_slot(cfg, "in_content", production),
           "sidebar": ad_slot(cfg, "sidebar", production), "sticky_footer": ad_slot(cfg, "sticky_footer", production)}
    domains = affiliate_domains(cfg)
    head = {"gsc": str(cfg["analytics"].get("gsc_verification") or "").strip() if production else "", "scripts": head_scripts(cfg, production)}
    base_ctx = {"site": site, "production": production, "nav": nav, "footer_links": footer_links, "ads": ads, "affiliates": bool(domains), "head": head}
    env = Environment(loader=FileSystemLoader(str(TEMPLATES)), autoescape=select_autoescape(["html"]), trim_blocks=True, lstrip_blocks=True)
    written: list[str] = []

    def emit(rel: str, tpl: str, **ctx) -> None:
        p = out / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(env.get_template(tpl).render({**base_ctx, **ctx}), encoding="utf-8")
        written.append(rel)

    # policy pages and the 404 carry no ad and no ad loader (AdSense: no ads on pages without content), only the analytics and consent scripts
    no_ads = {"ads": {**ads, "sticky_footer": ""}, "head": {**head, "scripts": head_scripts(cfg, production, ads=False)}}

    for a in arts:
        body, figs = extract_figures(a["body"], a["slug"], today)
        body_html = md_html(body)
        for token, fig in figs.items():
            body_html = body_html.replace(f"<p>{token}</p>", fig)
        body_html = re.sub(r"<table>", '<div class="table-wrap"><table>', body_html).replace("</table>", "</table></div>")
        lede, body_html = place_images(body_html, a["images"], a["slug"])
        body_html, faq = faq_section(body_html)
        body_html = insert_after_paragraph(body_html, 3, ads["in_content"])
        hrefs = [h.lower() for h in re.findall(r'href="([^"]+)"', body_html)]
        disclosure = (str(cfg["affiliates"].get("disclosure") or "").strip() or DEFAULT_DISCLOSURE) if any(d in h for d in domains for h in hrefs) else ""
        emit(f"{a['topic']}/{a['slug']}/index.html", "article.html", template="article", path=a["path"], meta=a["meta"], section=a["topic_href"],
             a={**a, "body_html": body_html, "lede_html": lede, "disclosure": disclosure, "related": related_for(a, arts), "json_ld": json_ld(a, site, faq)})

    for t, (label, blurb) in TOPICS.items():
        if by_topic[t]:
            emit(f"{t}/index.html", "topic.html", template="topic", path=f"/{t}/", meta=blurb, section=f"/{t}/", topic={"label": label, "blurb": blurb}, articles=by_topic[t])
    topics = [{"label": TOPICS[t][0], "blurb": TOPICS[t][1], "href": f"/{t}/", "count": len(by_topic[t])} for t in TOPICS if by_topic[t]]
    emit("index.html", "home.html", template="home", path="/", section="/", latest=arts[:12], topics=topics,
         meta="Research-first guides for students, parents and alumni of Cornell University and Ithaca: housing, getting around, classes, money, daily life and careers.")
    for p in pages:
        emit(f"{p['slug']}/index.html", "page.html", template="page", path=p["path"], meta=p["meta"], section="", **no_ads, p={**p, "body_html": md_html(p["body"])})
    emit("404.html", "not_found.html", template="not_found", path="", meta="", section="", **no_ads)   # no path: a 404 has no canonical

    # static assets, robots, sitemap, ads.txt
    (out / "static").mkdir()
    for name in STATIC_FILES:
        src = STATIC / name
        (shutil.copytree if src.is_dir() else shutil.copy2)(src, out / "static" / name)
    if production:
        robots = "User-agent: *\nAllow: /\n" + (f"\nSitemap: {site['base_url']}/sitemap.xml\n" if site["base_url"] else "")
        entries = [("/", today.isoformat())] + [(f"/{t}/", max(a["updated"] for a in by_topic[t]).isoformat()) for t in TOPICS if by_topic[t]]
        entries += [(a["path"], a["updated_iso"]) for a in arts] + [(p["path"], p["updated_iso"] or today.isoformat()) for p in pages]
    else:
        robots, entries = "User-agent: *\nDisallow: /\n", []
    urls = "".join(f"<url><loc>{html.escape(site['base_url'] + path)}</loc><lastmod>{mod}</lastmod></url>\n" for path, mod in entries)
    (out / "robots.txt").write_text(robots, encoding="utf-8")
    (out / "sitemap.xml").write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + urls + "</urlset>\n", encoding="utf-8")
    (out / "ads.txt").write_text(ads_txt(cfg), encoding="utf-8")

    summary = (f"rendered {len(arts)} articles, {len(topics)} topic pages, {len(pages)} pages to {out} "
               f"({'production' if production else 'noindex preview'}; ads {ads['provider'] or 'off'}; {len(WARNINGS)} warnings)")
    print(summary)
    log = REPO / "build" / "runs" / "v2"
    log.mkdir(parents=True, exist_ok=True)
    (log / f"render-{datetime.now():%Y%m%d-%H%M%S}.log").write_text("\n".join([summary, *written, *("warning: " + w for w in WARNINGS)]) + "\n", encoding="utf-8")
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default=str(REPO / "build" / "site"))
    ap.add_argument("--production", action="store_true", help="no noindex, crawlable robots.txt, full sitemap, third-party scripts and ad slots on")
    ap.add_argument("--all", action="store_true", help="render every article, not only those whose queue row is published (a local preview)")
    ap.add_argument("--articles-dir", default=str(REPO / "content" / "articles"))
    ap.add_argument("--pages-dir", default=str(REPO / "content" / "pages"))
    ap.add_argument("--images-dir", default=str(REPO / "content" / "images"))
    ap.add_argument("--reviews-dir", default=str(REPO / "content" / "reviews"))
    ap.add_argument("--queue", default=str(REPO / "queue" / "queue.csv"))
    ap.add_argument("--config", default=str(REPO / "config" / "monetization.yml"))
    return build(ap.parse_args(argv))


if __name__ == "__main__":
    sys.exit(main())
