#!/usr/bin/env python
"""Render the Footnote Daily static site (docs/v2/spec.md step 4: lint and publish; docs/v3/spec.md contracts 3, 4 and 6).

    worker/.venv/bin/python scripts/v2/render_site.py [--out build/site] [--production] [--all]
        [--articles-dir content/articles] [--pages-dir content/pages] [--images-dir content/images] [--reviews-dir content/reviews]
        [--tools-dir content/tools] [--datasets-dir content/datasets] [--start-dir content/start]
        [--queue queue/queue.csv] [--config config/monetization.yml]
    worker/.venv/bin/python scripts/v2/render_site.py --to-read [reports/to-read.md]     # regenerate Ajay's reading list (see to_read)

Reads content/articles/<topic>/<slug>.md (frontmatter + Markdown with the fenced blocks below), content/tools/<slug>/{tool.md,tool.html},
content/datasets/<slug>.{md,csv}, content/start/<reader>.md, content/pages/*.md and config/monetization.yml, and writes:
    /  /<topic>/  /<topic>/<slug>/  /tools/  /tools/<slug>/  /datasets/  /datasets/<slug>/ (+ <slug>.csv)  /start/<reader>/  /<page>/
    404.html  robots.txt  sitemap.xml  ads.txt  /static/  /images/<slug>/<n>.webp
Fenced blocks in an article body (scripts/v2/lint.py's split_fences reads them the same way; fences do not nest):
    ```figure  (YAML: kind cost_table | timeline | steps, title, rows)  -> an inline SVG drawn from the block's own text (v2)
    ```glance  4 to 6 bullets                                           -> the "At a glance" box
    ```reader "If you're <reader>"  ...                                 -> a titled reader block: <details open>, collapsed on phones by a few lines of script
    ```tool <slug>```  (one line)                                        -> the tool's HTML fragment embedded in place, with a link to /tools/<slug>/
    any other fence stays a code block.
An article with a frontmatter `kind` (v3) also gets images[0] as the lead photo under the title, a table of contents when it is the
pillar, breadcrumbs topic > pillar > page when `pillar` is set, and the in-content ad slot before its first section instead of after the
third paragraph. Every article, tool, dataset and start page ends with the "Did this answer your question? Yes / No, I still need..."
box: a Netlify form named `answered` (data-netlify, honeypot, free text only) posting to /thanks/ (content/pages/thanks.md, noindex).
Only articles whose queue row (queue/queue.csv) is in status published are rendered: publish.sh sets that after the checks pass and
the lint is clean, so a draft or an article waiting for its check never reaches the site. --all renders every article (a local
preview); a review (content/reviews/<slug>.json) with verdict reject is skipped either way. A tool or dataset renders when its
frontmatter is complete; one that carries a `queue_id` renders only when that row is published (or with --all). Start pages render
when they have a title and meta. Topics: the eight v2 dirs plus every dir in scripts/v3/topics.yml, in that file's order.
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
sys.path.insert(0, str(Path(__file__).resolve().parent))
from campus_worker.render import figures  # noqa: E402  (worker/campus_worker/render/figures.py; stdlib only)
import lint  # noqa: E402  (scripts/v2/lint.py: split_fences, word_count, SECTION_DIRS; one reading of an article for the checks and the site)

RENDER = REPO / "worker" / "campus_worker" / "render"
TEMPLATES = RENDER / "templates" / "v2"
STATIC = RENDER / "static"
STATIC_FILES = ("campus.css", "v2.css", "fonts")       # not the v1 tools scripts or the synthetic placeholder images

TOPIC_INFO = {  # label and blurb per article dir; the order comes from scripts/v3/topics.yml (load_topics)
    "housing": ("Housing", "Dorms, program houses, co-ops, Collegetown and downtown apartments, leases, landlords, roommates and moving."),
    "getting-around": ("Getting around", "Flights into ITH and SYR, buses to NYC and Boston, airport rides, TCAT, parking, biking and break travel."),
    "academics": ("Academics", "Courses and professors, requirements, registration strategy, add/drop, internal transfer and study spots."),
    "money": ("Money", "Real cost of living, meal plan math, cheap groceries, jobs, financial aid appeals and budgets by scenario."),
    "daily-life": ("Daily life", "Dining, food in Collegetown and downtown, gyms, health care, phones and banking, winter gear, safety and clubs."),
    "careers": ("Careers", "Internships, recruiting timelines, career fairs and the employers that hire from campus."),
    "parents": ("Parents", "Visiting, hotels, move-in weekend, graduation and what to send."),
    "alumni": ("Alumni", "Benefits, events and staying in Ithaca after graduation."),
    "dining": ("Dining", "Dining halls, meal plans and Big Red Bucks, late-night options, dietary needs, Collegetown and downtown restaurants, groceries and cooking in an apartment."),
    "transfer": ("Transfer", "Applying as a transfer, credit evaluation, housing and the residential requirement, orientation, aid, spring versus fall entry and guaranteed transfer pathways."),
    "health": ("Health", "Cornell Health services and costs, the student health plan and waivers, pharmacies, mental health services, urgent care and hospitals in Ithaca, immunizations and accessibility."),
}
TYPE_LABELS = {"how-to": "How-to", "decision": "Decision guide", "scenario": "Scenario guide", "comparison": "Comparison", "place": "Place guide",
               "checklist": "Checklist", "roundup": "Roundup"}
KIND_LABELS = {"pillar": "Complete guide", "spoke": "Guide", "reader_guide": "Reader guide", "rewrite": "Guide"}
PAGE_ORDER = ("about", "editorial-policy", "corrections", "contact", "privacy")
HIDDEN_PAGES = ("thanks",)    # rendered, but not in the footer or the sitemap, and noindex: the form's landing page
FAQ_HEAD = re.compile(r"<h2[^>]*>\s*(?:FAQs?|Frequently asked questions|Common questions|Related questions)\s*</h2>", re.I)
PARAGRAPH_END = re.compile(r"</p>\n(?=<(?:p|h[2-6]|ul|ol|div|figure|table|blockquote|pre|hr|section|aside|details|nav)\b)")   # top-level paragraphs only
DEFAULT_DISCLOSURE = "This guide contains affiliate links. If you buy through one we may earn a commission at no extra cost to you; it never changes what we recommend."
IMAGE_MAX_BYTES = 150_000
IMAGE_MAX_WIDTH = 1600
FRAGMENT_FLAGS = ("<script src", "fetch(", "xmlhttprequest", "localstorage", "sessionstorage", "indexeddb", "<link ", "<iframe", "sendbeacon", "document.cookie")
TO_READ_ENTRY = re.compile(r"^- (\d{4}-\d{2}-\d{2}) \| (.*?) \| (/\S+/) \| (.*?) \| (\S+)\s*$")
WARNINGS: list[str] = []


def warn(msg: str) -> None:
    WARNINGS.append(msg)
    print("warning:", msg, file=sys.stderr)


# ------------------------------------------------------------------------------------------------ topics
def load_topics() -> dict[str, tuple[str, str]]:
    """dir -> (label, blurb). The order is scripts/v3/topics.yml's (the owner's: housing first), then any v2 dir the file lacks. A dir
    without a TOPIC_INFO entry takes its label from the dir name and its blurb from the yml scope."""
    order, scopes = [], {}
    yml = REPO / "scripts" / "v3" / "topics.yml"
    if yml.is_file():
        try:
            for t in yaml.safe_load(yml.read_text(encoding="utf-8")) or []:
                if isinstance(t, dict) and t.get("dir"):
                    d = str(t["dir"]).strip()
                    order.append(d)
                    scopes[d] = " ".join(str(t.get("scope") or "").split())
        except yaml.YAMLError as e:
            warn(f"{yml}: {str(e).splitlines()[0]}; v2 topics only")
    for d in TOPIC_INFO:
        if d not in order:
            order.append(d)
    out = {}
    for d in order:
        if d in TOPIC_INFO:
            out[d] = TOPIC_INFO[d]
            continue
        scope = scopes.get(d, "")
        blurb = (scope[:1].upper() + scope[1:]).rstrip(".") if scope else ""
        if len(blurb) > 180:
            blurb = blurb[:180].rsplit(",", 1)[0].rstrip(" ,;")
        out[d] = (d.replace("-", " ").capitalize(), blurb + "." if blurb else "")
    return out


TOPICS = load_topics()


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


def sources_list(fm: dict) -> list[dict]:
    return [{"url": str(s.get("url") or ""), "title": clean_title(s.get("title"), str(s.get("url") or "")), "accessed": datefmt(to_date(s.get("accessed")))}
            for s in (fm.get("sources") or []) if isinstance(s, dict) and s.get("url")]


def strip_tags(s: str) -> str:
    return html.unescape(" ".join(re.sub(r"<[^>]+>", "", s).split()))


def md_html(text: str, ids: bool = False) -> str:
    """Markdown to HTML; `ids` adds an id to every heading (the toc extension), which the pillar table of contents and in-page links use."""
    ext = ["tables", "fenced_code", "sane_lists"] + (["toc"] if ids else [])
    return markdown.markdown(text, extensions=ext, output_format="html5")


def wrap_tables(body_html: str) -> str:
    return re.sub(r"<table>", '<div class="table-wrap"><table>', body_html).replace("</table>", "</table></div>")


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


def load_crawlers(path: Path) -> dict:
    """config/crawlers.yml: allow and disallow lists of user agents and the IndexNow settings; empty lists when the file is missing."""
    data = yaml.safe_load(path.read_text(encoding="utf-8")) if path.exists() else {}
    data = data if isinstance(data, dict) else {}
    return {"allow": [str(x) for x in (data.get("allow") or [])], "disallow": [str(x) for x in (data.get("disallow") or [])],
            "indexnow": dict(data.get("indexnow") or {})}


def robots_txt(crawlers: dict, base_url: str) -> str:
    """The production robots.txt: each allowed agent with Allow: /, each disallowed agent with Disallow: /, every other agent allowed,
    then the sitemap URL (needs site.domain). A preview build never calls this; it stays Disallow: / for everyone."""
    out = ["# Footnote Daily crawler policy; the lists live in config/crawlers.yml"]
    for ua in crawlers["allow"]:
        out += ["", f"User-agent: {ua}", "Allow: /"]
    for ua in crawlers["disallow"]:
        out += ["", f"User-agent: {ua}", "Disallow: /"]
    out += ["", "User-agent: *", "Allow: /"]
    if base_url:
        out += ["", f"Sitemap: {base_url}/sitemap.xml"]
    return "\n".join(out) + "\n"


def indexnow_key(crawlers: dict) -> str:
    """The IndexNow key (32 hex characters) from the key file named in config/crawlers.yml, or '' when there is none."""
    kf = str(crawlers["indexnow"].get("key_file") or "")
    if not kf:
        return ""
    path = Path(kf) if Path(kf).is_absolute() else REPO / kf
    key = path.read_text(encoding="utf-8").strip() if path.exists() else ""
    if key and not re.fullmatch(r"[A-Za-z0-9-]{8,128}", key):
        warn(f"{kf}: not a valid IndexNow key (8 to 128 letters, digits or hyphens); skipped")
        return ""
    return key


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


# ------------------------------------------------------------------------------------------------ article body blocks
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


def figure_block_html(content: str, slug: str, n: int, today: date) -> str:
    """One ```figure block as an inline SVG figure; a block that fails is dropped with a warning, never the page."""
    try:
        fig = figures.figure_from_block(figure_yaml(content), uid=f"fig-{slug}-{n}", today=today)
    except Exception as e:  # noqa: BLE001 - bad YAML or a malformed block drops that figure
        warn(f"{slug}: figure block {n} could not be drawn ({type(e).__name__}: {str(e).splitlines()[0]}); dropped")
        return ""
    if not fig:
        warn(f"{slug}: figure block {n} has an unknown kind or no rows; dropped")
        return ""
    return figure_html(fig)


def glance_html(content: str) -> str:
    """The "At a glance" box: the glance fence's bullets (Markdown, links allowed)."""
    return f'<aside class="glance" aria-labelledby="glance-h"><p class="glance__title" id="glance-h">At a glance</p>{md_html(content)}</aside>'


def reader_html(title: str, content: str) -> str:
    """One "If you're ..." block: a <details> open by default (so the text is there without script), collapsed on phones by the
    article template's script so a hurried reader sees the titles and taps theirs."""
    title = title.strip().strip("\"'").strip() or "If you're in this situation"
    return (f'<details class="reader" open><summary class="reader__title"><span>{html.escape(title)}</span></summary>'
            f'<div class="reader__body">{md_html(content)}</div></details>')


def tool_embed_html(t: dict) -> str:
    """A tool embedded in an article: the fragment under a one-line head with the date of its numbers and a link to its page."""
    s = html.escape(t["slug"])
    return (f'<section class="tool-embed" id="tool-{s}" aria-labelledby="tool-{s}-h"><p class="tool-embed__head"><b id="tool-{s}-h">{html.escape(t["title"])}</b> '
            f'<span class="meta">Numbers as of {html.escape(t["as_of_text"])}. <a href="{t["path"]}">How this tool works</a></span></p>{t["fragment"]}</section>')


def body_to_html(body: str, slug: str, today: date, tools: dict[str, dict]) -> tuple[str, list[str]]:
    """The Markdown body with the fenced blocks replaced (figure, glance, reader, tool; any other fence stays a code block), then
    rendered, with ids on the headings. Returns (html, embedded tool slugs)."""
    tokens: dict[str, str] = {}
    parts: list[str] = []
    embedded: list[str] = []
    n_fig = 0

    def token(block: str) -> str:
        t = f"@@BLOCK{len(tokens)}@@"
        tokens[t] = block
        return f"\n\n{t}\n\n"

    for seg in lint.split_fences(body):
        if seg[0] == "text":
            parts.append(seg[1])
            continue
        _, lang, info, content = seg
        if lang == "figure":
            n_fig += 1
            fig = figure_block_html(content, slug, n_fig, today)
            parts.append(token(fig) if fig else "\n")
        elif lang == "glance":
            parts.append(token(glance_html(content)))
        elif lang == "reader":
            parts.append(token(reader_html(info, content)))
        elif lang == "tool":
            t = tools.get(info)
            if not t:
                warn(f"{slug}: tool {info!r} is not in the tools dir (or its row is not published); embed dropped")
                parts.append("\n")
            else:
                embedded.append(info)
                parts.append(token(tool_embed_html(t)))
        else:
            parts.append(f"\n```{lang}{(' ' + info) if info else ''}\n{content}\n```\n")
    out = md_html("".join(parts), ids=True)
    for t, block in tokens.items():
        out = out.replace(f"<p>{t}</p>", block)
    return out, embedded


def toc_html(body_html: str) -> str:
    """A pillar's table of contents: every h2 of the body (three or more), linked to its id."""
    heads = re.findall(r'<h2 id="([^"]+)"[^>]*>(.*?)</h2>', body_html, re.S)
    if len(heads) < 3:
        return ""
    items = "".join(f'<li><a href="#{html.escape(i)}">{html.escape(strip_tags(t))}</a></li>' for i, t in heads)
    return f'<nav class="toc" aria-labelledby="toc-h"><p class="toc__title" id="toc-h">In this guide</p><ol>{items}</ol></nav>'


def insert_before_first_h2(body_html: str, snippet: str) -> str:
    if not snippet:
        return body_html
    i = body_html.find("<h2")
    return body_html + "\n" + snippet if i < 0 else body_html[:i] + snippet + "\n" + body_html[i:]


def photo_figure(img: dict, slug: str, lede: bool = False) -> str:
    """A credited photo: '<caption> Photo: <credit, linked to its page>, <license, linked>'. The credit may come as
    'Jane Doe / Wikimedia Commons' or already in the finder's full form 'Photo: Jane Doe / Wikimedia Commons, CC BY-SA 4.0'."""
    lic_text = " ".join(str(img.get("license") or "").split())
    credit = re.sub(r"^\s*photo:\s*", "", " ".join(str(img.get("credit") or "").split()), flags=re.I)
    if lic_text and credit.lower().endswith(", " + lic_text.lower()):
        credit = credit[: -len(lic_text) - 2].rstrip()
    if not credit and img.get("author"):   # stored fields (author, source URL): the credit line is built from them when no credit text was written
        host = urlsplit(str(img.get("source_url") or img.get("credit_url") or "")).netloc.lower().removeprefix("www.")
        credit = f"{img['author']} / {'Wikimedia Commons' if host.endswith('wikimedia.org') else host}" if host else str(img["author"])
    credit = html.escape(credit)
    source_url = str(img.get("source_url") or img.get("credit_url") or "")
    if credit and source_url:
        credit = f'<a href="{html.escape(source_url)}" rel="noopener">{credit}</a>'
    lic = html.escape(lic_text)
    if lic and img.get("license_url"):
        lic = f'<a href="{html.escape(img["license_url"])}" rel="license noopener">{lic}</a>'
    credit_line = ", ".join(x for x in (f"Photo: {credit}" if credit else "", lic) if x)
    caption = html.escape(img.get("caption") or "")
    size = f' width="{img["width"]}" height="{img["height"]}"' if img.get("width") else ""
    loading = ' fetchpriority="high"' if lede else ' loading="lazy" decoding="async"'
    return (f'<figure class="photo{" photo--lede" if lede else ""}"><img src="/images/{slug}/{html.escape(img["out"])}" alt="{html.escape(img.get("alt") or "")}"{size}{loading}>'
            f'<figcaption>{caption}{" " if caption and credit_line else ""}<span class="photo__credit">{credit_line}</span></figcaption></figure>')


def place_images(body_html: str, images: list[dict], slug: str, lead_first: bool = False) -> tuple[str, str]:
    """Body references (`![alt](1.webp)` on its own line) become credited figures in place; the first unreferenced image is the lede;
    the rest go before the second, third, ... h2. With lead_first (v3), images[0] is the lead photo whatever the body says (contract 3)
    and a body reference to it is dropped. Returns (lede figure HTML, body HTML)."""
    used: set[int] = set()
    lead = 0 if lead_first and images else None

    def swap(m):
        name = m.group(1).rsplit("/", 1)[-1]
        for i, im in enumerate(images):
            if name in (im["file"], im["out"]):
                if i == lead:
                    return ""
                used.add(i)
                return photo_figure(im, slug)
        return m.group(0)

    body_html = re.sub(r'<p><img[^>]*?src="([^"]+)"[^>]*></p>', swap, body_html)
    if lead is not None:
        used.add(lead)
    rest = [im for i, im in enumerate(images) if i not in used]
    lede = photo_figure(images[lead], slug, lede=True) if lead is not None else (photo_figure(rest.pop(0), slug, lede=True) if rest else "")
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


def json_ld(a: dict, site: dict, faq: list[tuple[str, str]], crumbs: list[dict] | None = None) -> str:
    base = site.get("base_url") or ""
    url = f"{base}{a['path']}"
    data = [{"@context": "https://schema.org", "@type": "Article", "headline": a["title"], "description": a["meta"], "dateModified": a["updated_iso"],
             "mainEntityOfPage": url, "publisher": {"@type": "Organization", "name": site["name"]},
             **({"image": [f"{base}/images/{a['slug']}/{im['out']}" for im in a["images"]]} if a["images"] else {})}]
    if faq:
        data.append({"@context": "https://schema.org", "@type": "FAQPage",
                     "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": ans}} for q, ans in faq]})
    if crumbs:
        data.append({"@context": "https://schema.org", "@type": "BreadcrumbList",
                     "itemListElement": [{"@type": "ListItem", "position": i, "name": c["label"], **({"item": f"{base}{c['href']}"} if c.get("href") else {})}
                                         for i, c in enumerate(crumbs, 1)]})
    return json.dumps(data if len(data) > 1 else data[0], ensure_ascii=False).replace("</", "<\\/")


def dataset_json_ld(d: dict, site: dict) -> str:
    base = site.get("base_url") or ""
    data = {"@context": "https://schema.org", "@type": "Dataset", "name": d["title"], "description": d["meta"], "url": f"{base}{d['path']}",
            "dateModified": d["updated_iso"], "creator": {"@type": "Organization", "name": site["name"]}, "license": "https://creativecommons.org/licenses/by/4.0/"}
    if d.get("as_of_iso"):
        data["temporalCoverage"] = d["as_of_iso"]
    if d.get("csv_href"):
        data["distribution"] = [{"@type": "DataDownload", "encodingFormat": "text/csv", "contentUrl": f"{base}{d['csv_href']}"}]
    return json.dumps(data, ensure_ascii=False).replace("</", "<\\/")


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


def unlink_missing(body_html: str, live_paths: set[str]) -> str:
    """An internal link whose target is not on the site (an article still in its checks or rejected, a tool, dataset or start page
    not rendered) becomes plain text: no dead links."""
    def repl(m):
        href = m.group(1).split("#")[0].split("?")[0]
        href = href if href.endswith("/") else href + "/"
        parts = href.strip("/").split("/")
        if len(parts) == 2 and (parts[0] in TOPICS or parts[0] in lint.SECTION_DIRS) and href not in live_paths:
            return m.group(2)
        return m.group(0)
    return re.sub(r'<a href="(/[^"]+)"[^>]*>(.*?)</a>', repl, body_html, flags=re.S)


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
            images.append({**{k: str(im.get(k) or "") for k in ("alt", "caption", "credit", "credit_url", "license", "license_url", "author", "source_url")},
                           "file": str(im["file"]), "out": copied[0], "width": copied[1], "height": copied[2]})
    return images


def dated(fm: dict, key: str = "updated") -> tuple[date | None, str, str]:
    d = to_date(fm.get(key))
    return d, (d.isoformat() if d else ""), datefmt(d)


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
        kind = str(fm.get("kind") or "").strip()
        if kind and kind not in KIND_LABELS:
            warn(f"{path}: kind {kind!r} is not one of {', '.join(KIND_LABELS)}; rendered as a guide")
        arts.append({"slug": slug, "topic": topic, "topic_label": TOPICS[topic][0], "topic_href": f"/{topic}/", "path": f"/{topic}/{slug}/",
                     "title": str(fm["title"]).strip(), "meta": str(fm["meta"]).strip(), "type_label": TYPE_LABELS.get(str(fm.get("type") or "").strip(), ""),
                     "kind": kind, "kind_label": KIND_LABELS.get(kind, "Guide" if kind else ""), "pillar": str(fm.get("pillar") or "").strip(),
                     "readers": [str(r) for r in fm.get("readers") or [] if r] if isinstance(fm.get("readers"), list) else [],
                     "updated": updated, "updated_iso": updated.isoformat(), "updated_text": datefmt(updated), "body": body, "sources": sources_list(fm),
                     "images": article_images(fm, slug, images_dir, out, path),
                     "reading_time": max(1, round(lint.word_count(lint.split_fences(body)) / 230)), "queue_id": queue_id})
    if held:
        warn(f"{len(held)} article(s) whose queue row is not published were left out (--all renders them): {', '.join(held)}")
    arts.sort(key=lambda a: (a["updated"], a["title"]), reverse=True)
    return arts


def load_tools(tools_dir: Path, published: set[str] | None = None) -> dict[str, dict]:
    """content/tools/<slug>/tool.md (title, meta, topic, updated, numbers_as_of, sources, brief; optional queue_id) plus tool.html, the
    self-contained fragment. A fragment that reaches for the network or storage, lacks data-as-of or carries an <h1> gets a warning."""
    tools: dict[str, dict] = {}
    if not tools_dir.is_dir():
        return tools
    for d in sorted(p for p in tools_dir.iterdir() if p.is_dir()):
        md, frag = d / "tool.md", d / "tool.html"
        if not (md.is_file() and frag.is_file()):
            warn(f"{d}: a tool needs tool.md and tool.html; skipped")
            continue
        try:
            fm, body = frontmatter(md.read_text(encoding="utf-8"))
        except ValueError as e:
            warn(f"{md}: {e}; skipped")
            continue
        missing = [k for k in ("title", "meta", "topic", "updated", "numbers_as_of") if not fm.get(k)]
        topic = str(fm.get("topic") or "").strip()
        if topic and topic not in TOPICS:
            missing.append(f"topic {topic!r} is not one of {', '.join(TOPICS)}")
        if missing:
            warn(f"{md}: missing {', '.join(missing)}; skipped")
            continue
        qid = str(fm.get("queue_id") or "").strip()
        if published is not None and qid and qid not in published:
            warn(f"{md}: queue row {qid} is not published; skipped (--all renders it)")
            continue
        fragment = frag.read_text(encoding="utf-8")
        low = fragment.lower()
        flags = [f for f in FRAGMENT_FLAGS if f in low]
        if flags:
            warn(f"{frag}: fragment contains {', '.join(flags)}; tools are plain JavaScript with no network and no storage (contract 4)")
        if "data-as-of" not in low:
            warn(f"{frag}: no data-as-of attribute on its constants (contract 4)")
        if re.search(r"<h1\b", low):
            warn(f"{frag}: an <h1> inside the fragment; the page already has one")
        updated, updated_iso, updated_text = dated(fm)
        as_of, as_of_iso, as_of_text = dated(fm, "numbers_as_of")
        tools[d.name] = {"slug": d.name, "path": f"/tools/{d.name}/", "title": str(fm["title"]).strip(), "meta": str(fm["meta"]).strip(), "topic": topic,
                         "topic_label": TOPICS[topic][0], "topic_href": f"/{topic}/", "updated": updated or as_of or date.today(), "updated_iso": updated_iso or as_of_iso,
                         "updated_text": updated_text or as_of_text, "as_of": as_of, "as_of_iso": as_of_iso, "as_of_text": as_of_text or str(fm["numbers_as_of"]),
                         "sources": sources_list(fm), "brief": str(fm.get("brief") or ""), "body": body, "fragment": fragment, "used_in": [], "queue_id": qid}
    return tools


def load_datasets(datasets_dir: Path, out: Path, published: set[str] | None = None) -> list[dict]:
    """content/datasets/<slug>.md (title, meta, topic, updated, as_of, sample_size, method, sources; optional queue_id) with the table in
    the body, plus the CSV sibling copied to /datasets/<slug>/<slug>.csv for the download link."""
    items: list[dict] = []
    if not datasets_dir.is_dir():
        return items
    for md in sorted(datasets_dir.glob("*.md")):
        try:
            fm, body = frontmatter(md.read_text(encoding="utf-8"))
        except ValueError as e:
            warn(f"{md}: {e}; skipped")
            continue
        missing = [k for k in ("title", "meta", "topic", "updated", "as_of") if not fm.get(k)]
        topic = str(fm.get("topic") or "").strip()
        if topic and topic not in TOPICS:
            missing.append(f"topic {topic!r} is not one of {', '.join(TOPICS)}")
        if missing:
            warn(f"{md}: missing {', '.join(missing)}; skipped")
            continue
        qid = str(fm.get("queue_id") or "").strip()
        if published is not None and qid and qid not in published:
            warn(f"{md}: queue row {qid} is not published; skipped (--all renders it)")
            continue
        for k in ("sample_size", "method", "sources"):
            if not fm.get(k):
                warn(f"{md}: no {k} in the frontmatter (contract 4)")
        csv_src, csv_href, rows = md.with_suffix(".csv"), "", 0
        if csv_src.is_file():
            dest = out / "datasets" / md.stem / f"{md.stem}.csv"
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(csv_src, dest)
            csv_href = f"/datasets/{md.stem}/{md.stem}.csv"
            with csv_src.open(newline="", encoding="utf-8-sig") as fh:
                rows = max(0, sum(1 for _ in csv.reader(fh)) - 1)
        else:
            warn(f"{md}: no CSV sibling {csv_src.name}; the page has no download link")
        updated, updated_iso, updated_text = dated(fm)
        as_of, as_of_iso, as_of_text = dated(fm, "as_of")
        items.append({"slug": md.stem, "path": f"/datasets/{md.stem}/", "title": str(fm["title"]).strip(), "meta": str(fm["meta"]).strip(), "topic": topic,
                      "topic_label": TOPICS[topic][0], "topic_href": f"/{topic}/", "updated": updated or as_of or date.today(), "updated_iso": updated_iso or as_of_iso,
                      "updated_text": updated_text or as_of_text, "as_of_iso": as_of_iso, "as_of_text": as_of_text or str(fm["as_of"]),
                      "sample_size": str(fm.get("sample_size") or "").strip(), "method": " ".join(str(fm.get("method") or "").split()),
                      "sources": sources_list(fm), "body": body, "csv_href": csv_href, "csv_rows": rows, "queue_id": qid})
    items.sort(key=lambda d: (d["updated"], d["title"]), reverse=True)
    return items


def load_start(start_dir: Path) -> list[dict]:
    """content/start/<reader>.md: title, meta, optional updated and topics (the topic pages that link it); the body lists the guides in order."""
    items: list[dict] = []
    if not start_dir.is_dir():
        return items
    for md in sorted(start_dir.glob("*.md")):
        try:
            fm, body = frontmatter(md.read_text(encoding="utf-8"))
        except ValueError as e:
            warn(f"{md}: {e}; skipped")
            continue
        if not fm.get("title") or not fm.get("meta"):
            warn(f"{md}: a start page needs title and meta; skipped")
            continue
        topics = [str(t).strip() for t in (fm.get("topics") or []) if str(t).strip()] if isinstance(fm.get("topics"), list) else []
        for t in [t for t in topics if t not in TOPICS]:
            warn(f"{md}: topic {t!r} is not a topic dir; ignored")
        updated, updated_iso, updated_text = dated(fm)
        items.append({"slug": md.stem, "path": f"/start/{md.stem}/", "title": str(fm["title"]).strip(), "meta": str(fm["meta"]).strip(),
                      "topics": [t for t in topics if t in TOPICS], "updated": updated, "updated_iso": updated_iso, "updated_text": updated_text, "body": body})
    return items


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
                      "updated": upd, "updated_iso": upd.isoformat() if upd else "", "updated_text": datefmt(upd),
                      "noindex": bool(fm.get("noindex")) or path.stem in HIDDEN_PAGES, "hidden": bool(fm.get("hidden")) or path.stem in HIDDEN_PAGES,
                      "eyebrow": str(fm.get("eyebrow") or "").strip()})
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
    crawlers = load_crawlers(Path(args.crawlers))
    if production and not domain:
        warn("production build without site.domain: canonical URLs and the sitemap need it")

    pub = None if args.all else published_ids(Path(args.queue))
    arts = load_articles(Path(args.articles_dir), Path(args.reviews_dir), Path(args.images_dir), out, today, published=pub)
    tools = load_tools(Path(args.tools_dir), pub)
    datasets = load_datasets(Path(args.datasets_dir), out, pub)
    starts = load_start(Path(args.start_dir))
    pages = load_pages(Path(args.pages_dir))
    by_topic = {t: [a for a in arts if a["topic"] == t] for t in TOPICS}
    nav = [{"label": TOPICS[t][0], "href": f"/{t}/"} for t in TOPICS if by_topic[t]]
    footer_links = [{"label": p["title"].replace("About " + site["name"], "About"), "href": p["path"]} for p in pages if not p["hidden"]]
    ads = {"provider": ads_provider(cfg) if production else "", "in_content": ad_slot(cfg, "in_content", production),
           "sidebar": ad_slot(cfg, "sidebar", production), "sticky_footer": ad_slot(cfg, "sticky_footer", production)}
    domains = affiliate_domains(cfg)
    head = {"gsc": str(cfg["analytics"].get("gsc_verification") or "").strip() if production else "", "scripts": head_scripts(cfg, production)}
    base_ctx = {"site": site, "production": production, "nav": nav, "footer_links": footer_links, "ads": ads, "affiliates": bool(domains), "head": head, "noindex": False}
    env = Environment(loader=FileSystemLoader(str(TEMPLATES)), autoescape=select_autoescape(["html"]), trim_blocks=True, lstrip_blocks=True)
    written: list[str] = []

    def emit(rel: str, tpl: str, **ctx) -> None:
        p = out / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(env.get_template(tpl).render({**base_ctx, **ctx}), encoding="utf-8")
        written.append(rel)

    # policy pages and the 404 carry no ad and no ad loader (AdSense: no ads on pages without content), only the analytics and consent scripts
    no_ads = {"ads": {**ads, "sticky_footer": ""}, "head": {**head, "scripts": head_scripts(cfg, production, ads=False)}}

    live_paths = {x["path"] for x in arts} | {t["path"] for t in tools.values()} | {d["path"] for d in datasets} | {s["path"] for s in starts}
    for a in arts:
        body_html, embedded = body_to_html(a["body"], a["slug"], today, tools)
        for s in embedded:
            if a not in tools[s]["used_in"]:
                tools[s]["used_in"].append(a)
        body_html = wrap_tables(unlink_missing(body_html, live_paths))
        lede, body_html = place_images(body_html, a["images"], a["slug"], lead_first=bool(a["kind"]))
        if a["kind"] == "pillar":
            body_html = insert_before_first_h2(body_html, toc_html(body_html))
        body_html, faq = faq_section(body_html)
        body_html = insert_before_first_h2(body_html, ads["in_content"]) if a["kind"] else insert_after_paragraph(body_html, 3, ads["in_content"])
        hrefs = [h.lower() for h in re.findall(r'href="([^"]+)"', body_html)]
        disclosure = (str(cfg["affiliates"].get("disclosure") or "").strip() or DEFAULT_DISCLOSURE) if any(d in h for d in domains for h in hrefs) else ""
        crumbs: list[dict] = []
        if a["pillar"]:   # topic > pillar > this page; the pillar crumb only when the pillar is on the site
            crumbs.append({"label": a["topic_label"], "href": a["topic_href"]})
            pil = next((p for p in arts if p["path"] == a["pillar"]), None)
            if pil:
                crumbs.append({"label": pil["title"], "href": pil["path"]})
            crumbs.append({"label": a["title"], "href": ""})
        emit(f"{a['topic']}/{a['slug']}/index.html", "article.html", template="article", path=a["path"], meta=a["meta"], section=a["topic_href"],
             a={**a, "body_html": body_html, "lede_html": lede, "disclosure": disclosure, "related": related_for(a, arts), "crumbs": crumbs,
                "has_readers": 'class="reader"' in body_html, "json_ld": json_ld(a, site, faq, crumbs)})

    for t in tools.values():
        t_body = wrap_tables(unlink_missing(md_html(t["body"], ids=True), live_paths))
        emit(f"tools/{t['slug']}/index.html", "tool.html", template="tool", path=t["path"], meta=t["meta"], section=t["topic_href"], t={**t, "body_html": t_body})
    if tools:
        emit("tools/index.html", "list.html", template="list", path="/tools/", section="/tools/",
             meta=f"Calculators, quizzes and checklists from {site['name']}, built from the numbers in our topic briefs, each dated.",
             page={"eyebrow": "Tools", "title": "Tools", "deck": "Calculators, quizzes and checklists built from the numbers in our topic briefs. Each one shows the date its numbers are from; nothing you type is stored or sent anywhere.",
                   "items": sorted(tools.values(), key=lambda x: (x["updated"], x["title"]), reverse=True), "label": "Tool"})
    for d in datasets:
        d_body = wrap_tables(unlink_missing(md_html(d["body"], ids=True), live_paths))
        emit(f"datasets/{d['slug']}/index.html", "dataset.html", template="dataset", path=d["path"], meta=d["meta"], section=d["topic_href"],
             d={**d, "body_html": d_body, "json_ld": dataset_json_ld(d, site)})
    if datasets:
        emit("datasets/index.html", "list.html", template="list", path="/datasets/", section="/datasets/",
             meta=f"Original datasets from {site['name']}: tables we built ourselves from dated samples and official prices, each with its method, sample size and a CSV download.",
             page={"eyebrow": "Data", "title": "Datasets", "deck": "Tables we built ourselves from dated samples and official prices. Each page states the method, the sample size and the date, and offers the data as a CSV file.",
                   "items": datasets, "label": "Dataset"})
    for s in starts:
        s_body = wrap_tables(unlink_missing(md_html(s["body"], ids=True), live_paths))
        emit(f"start/{s['slug']}/index.html", "start.html", template="start", path=s["path"], meta=s["meta"], section="", s={**s, "body_html": s_body})

    for t, (label, blurb) in TOPICS.items():
        if by_topic[t]:
            pillar = next((a for a in by_topic[t] if a["kind"] == "pillar"), None)
            emit(f"{t}/index.html", "topic.html", template="topic", path=f"/{t}/", meta=blurb, section=f"/{t}/", topic={"label": label, "blurb": blurb},
                 pillar=pillar, articles=[a for a in by_topic[t] if a is not pillar], starts=[s for s in starts if t in s["topics"]],
                 tools=[x for x in tools.values() if x["topic"] == t], datasets=[d for d in datasets if d["topic"] == t])
    topics = [{"label": TOPICS[t][0], "blurb": TOPICS[t][1], "href": f"/{t}/", "count": len(by_topic[t])} for t in TOPICS if by_topic[t]]
    emit("index.html", "home.html", template="home", path="/", section="/", latest=arts[:12], topics=topics, starts=starts,
         tools=sorted(tools.values(), key=lambda x: (x["updated"], x["title"]), reverse=True), datasets=datasets,
         meta="Research-first guides for students, parents and alumni of Cornell University and Ithaca: housing, getting around, classes, money, daily life and careers.")
    for p in pages:
        emit(f"{p['slug']}/index.html", "page.html", template="page", path=p["path"], meta=p["meta"], section="", noindex=p["noindex"], **no_ads,
             p={**p, "body_html": md_html(p["body"])})
    emit("404.html", "not_found.html", template="not_found", path="", meta="", section="", **no_ads)   # no path: a 404 has no canonical

    # static assets, robots, sitemap, ads.txt
    (out / "static").mkdir()
    for name in STATIC_FILES:
        src = STATIC / name
        (shutil.copytree if src.is_dir() else shutil.copy2)(src, out / "static" / name)
    if production:
        robots = robots_txt(crawlers, site["base_url"])
        entries = [("/", today.isoformat())] + [(f"/{t}/", max(a["updated"] for a in by_topic[t]).isoformat()) for t in TOPICS if by_topic[t]]
        entries += [(a["path"], a["updated_iso"]) for a in arts]
        entries += ([("/tools/", max(x["updated"] for x in tools.values()).isoformat())] if tools else []) + [(x["path"], x["updated_iso"]) for x in tools.values()]
        entries += ([("/datasets/", max(d["updated"] for d in datasets).isoformat())] if datasets else []) + [(d["path"], d["updated_iso"]) for d in datasets]
        entries += [(s["path"], s["updated_iso"] or today.isoformat()) for s in starts]
        entries += [(p["path"], p["updated_iso"] or today.isoformat()) for p in pages if not p["noindex"]]
    else:
        robots, entries = "User-agent: *\nDisallow: /\n", []
    urls = "".join(f"<url><loc>{html.escape(site['base_url'] + path)}</loc><lastmod>{mod}</lastmod></url>\n" for path, mod in entries)
    (out / "robots.txt").write_text(robots, encoding="utf-8")
    key = indexnow_key(crawlers)
    if key:
        (out / f"{key}.txt").write_text(key + "\n", encoding="utf-8")   # IndexNow key file at the site root (scripts/v2/indexnow.py)
    (out / "sitemap.xml").write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + urls + "</urlset>\n", encoding="utf-8")
    (out / "ads.txt").write_text(ads_txt(cfg), encoding="utf-8")

    summary = (f"rendered {len(arts)} articles, {len(tools)} tools, {len(datasets)} datasets, {len(starts)} start pages, {len(topics)} topic pages, {len(pages)} pages to {out} "
               f"({'production' if production else 'noindex preview'}; ads {ads['provider'] or 'off'}; {len(WARNINGS)} warnings)")
    print(summary)
    log = REPO / "build" / "runs" / "v2"
    log.mkdir(parents=True, exist_ok=True)
    (log / f"render-{datetime.now():%Y%m%d-%H%M%S}.log").write_text("\n".join([summary, *written, *("warning: " + w for w in WARNINGS)]) + "\n", encoding="utf-8")
    return 0


# ------------------------------------------------------------------------------------------------ reports/to-read.md
DEFAULT_TO_READ_HEADER = "# To read: Ajay's spot check\n\nSee the header in reports/to-read.md in the repo for the conventions.\n"


def to_read(path: Path, queue_path: Path, articles_dir: Path) -> int:
    """Regenerate the entries of reports/to-read.md from the published queue rows (docs/v3/spec.md, step 8). The header (everything
    above the first entry) and every "Ajay:" mark already on the list are kept; entries are rewritten newest first, three lines each:
        - <updated> | <title> | <path> | <kind> | <topic>
          Summary: <meta>
          Ajay: <👍 or a one-line note>
    publish.sh may append entries in the same shape as it publishes; this helper is the alternative that rebuilds the list from the queue."""
    text = path.read_text(encoding="utf-8") if path.exists() else DEFAULT_TO_READ_HEADER
    lines = text.split("\n")
    first = next((i for i, l in enumerate(lines) if TO_READ_ENTRY.match(l)), len(lines))
    header = "\n".join(lines[:first]).rstrip("\n")
    marks: dict[str, str] = {}
    cur = None
    for l in lines[first:]:
        m = TO_READ_ENTRY.match(l)
        if m:
            cur = m.group(3)
            continue
        mm = re.match(r"^\s+Ajay:\s*(.*)$", l)
        if mm and cur and mm.group(1).strip():
            marks[cur] = mm.group(1).strip()
    pub = published_ids(queue_path)
    entries = []
    for p in sorted(articles_dir.glob("*/*.md")):
        try:
            fm, _ = frontmatter(p.read_text(encoding="utf-8"))
        except ValueError:
            continue
        if str(fm.get("queue_id") or "") not in pub:
            continue
        d = to_date(fm.get("updated")) or date.today()
        kind = str(fm.get("kind") or "").strip() or f"{fm.get('type') or 'article'} (v2)"
        entries.append((d, " ".join(str(fm.get("title") or p.stem).split()), f"/{p.parent.name}/{p.stem}/", kind, p.parent.name, " ".join(str(fm.get("meta") or "").split())))
    entries.sort(key=lambda e: (e[0], e[1]), reverse=True)
    out = [header, ""]
    for d, title, path_, kind, topic, summary in entries:
        out += [f"- {d.isoformat()} | {title} | {path_} | {kind} | {topic}", f"  Summary: {summary}", f"  Ajay: {marks.get(path_, '')}".rstrip(), ""]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(out).rstrip("\n") + "\n", encoding="utf-8")
    print(f"{len(entries)} published article(s) listed in {path} ({len(marks)} mark(s) kept)")
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default=str(REPO / "build" / "site"))
    ap.add_argument("--production", action="store_true", help="no noindex, crawlable robots.txt, full sitemap, third-party scripts and ad slots on")
    ap.add_argument("--all", action="store_true", help="render every article, tool and dataset, not only those whose queue row is published (a local preview)")
    ap.add_argument("--articles-dir", default=str(REPO / "content" / "articles"))
    ap.add_argument("--pages-dir", default=str(REPO / "content" / "pages"))
    ap.add_argument("--images-dir", default=str(REPO / "content" / "images"))
    ap.add_argument("--reviews-dir", default=str(REPO / "content" / "reviews"))
    ap.add_argument("--tools-dir", default=str(REPO / "content" / "tools"))
    ap.add_argument("--datasets-dir", default=str(REPO / "content" / "datasets"))
    ap.add_argument("--start-dir", default=str(REPO / "content" / "start"))
    ap.add_argument("--queue", default=str(REPO / "queue" / "queue.csv"))
    ap.add_argument("--config", default=str(REPO / "config" / "monetization.yml"))
    ap.add_argument("--crawlers", default=str(REPO / "config" / "crawlers.yml"), help="crawler allow and disallow lists and the IndexNow key file")
    ap.add_argument("--to-read", nargs="?", const=str(REPO / "reports" / "to-read.md"), metavar="FILE",
                    help="instead of rendering, regenerate the entries of reports/to-read.md from the published rows (keeps the header and Ajay's marks)")
    a = ap.parse_args(argv)
    if a.to_read:
        return to_read(Path(a.to_read), Path(a.queue), Path(a.articles_dir))
    return build(a)


if __name__ == "__main__":
    sys.exit(main())
