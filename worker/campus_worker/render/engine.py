"""Server-side rendering engine (SPEC §04, §18, §20).

One Jinja environment renders every public template. The WordPress theme mirrors these templates;
the worker uses them for static previews, QA screenshots and for the body HTML pushed to the CMS.
Markdown bodies are converted and then sanitized with nh3 (allowlist) before any CMS insertion.
"""
from __future__ import annotations

import html
import re
from datetime import date, datetime
from pathlib import Path

import markdown
import nh3
from jinja2 import Environment, FileSystemLoader, Undefined, select_autoescape

TEMPLATE_DIR = Path(__file__).parent / "templates"
STATIC_DIR = Path(__file__).parent / "static"

ALLOWED_TAGS = {"a", "abbr", "b", "blockquote", "br", "caption", "cite", "code", "dd", "del", "dfn", "dl", "dt", "em", "figcaption", "figure",
                "h2", "h3", "h4", "hr", "i", "ins", "kbd", "li", "mark", "ol", "p", "pre", "q", "s", "small", "span", "strong", "sub", "sup",
                "table", "tbody", "td", "tfoot", "th", "thead", "time", "tr", "ul"}
ALLOWED_ATTRS = {"a": {"href", "title"}, "abbr": {"title"}, "td": {"colspan", "rowspan"}, "th": {"colspan", "rowspan", "scope"},
                 "time": {"datetime"}, "span": {"class"}, "table": {"class"}, "p": {"class"}, "figure": {"class"}, "q": {"cite"}}
ALLOWED_SCHEMES = {"https", "http", "mailto"}


def money(minor: int | None, currency: str = "USD", *, cents: bool = False) -> str:
    if minor is None:
        return "Unknown"
    sym = {"USD": "$"}.get(currency, currency + " ")
    if cents or minor % 100:
        return f"{sym}{minor / 100:,.2f}"
    return f"{sym}{minor // 100:,}"


def period_label(p: str | None) -> str:
    return {"per_month": "per month", "per_semester": "per semester", "per_academic_year": "per academic year", "per_term": "per term",
            "per_year": "per year", "one_time": "one-time", "per_week": "per week", "per_day": "per day", "unknown": "billing period not stated", None: ""}.get(p, p or "")


def basis_label(b: str | None) -> str:
    return {"per_person": "per person", "per_unit": "per unit", "per_bed": "per bed", "unknown": "basis not stated", None: ""}.get(b, b or "")


def datefmt(d: date | datetime | str | None, fmt: str = "%B %-d, %Y") -> str:
    if d is None:
        return ""
    if isinstance(d, str):
        d = datetime.fromisoformat(d)
    return d.strftime(fmt)


def isodate(d: date | datetime | str | None) -> str:
    if d is None:
        return ""
    if isinstance(d, str):
        return d[:10]
    return d.date().isoformat() if isinstance(d, datetime) else d.isoformat()


def md_to_html(md_text: str) -> str:
    raw = markdown.markdown(md_text or "", extensions=["tables", "sane_lists", "smarty"], output_format="html5")
    # demote any h1 the model produced (the template owns the H1)
    raw = re.sub(r"<(/?)h1\b", r"<\1h2", raw)
    return nh3.clean(raw, tags=ALLOWED_TAGS, attributes=ALLOWED_ATTRS, url_schemes=ALLOWED_SCHEMES, link_rel="noopener")


def sanitize_html(fragment: str) -> str:
    return nh3.clean(fragment or "", tags=ALLOWED_TAGS, attributes=ALLOWED_ATTRS, url_schemes=ALLOWED_SCHEMES, link_rel="noopener")


def reading_time(md_text: str) -> int:
    words = len(re.findall(r"\w+", md_text or ""))
    return max(1, round(words / 230))


def make_env() -> Environment:
    env = Environment(loader=FileSystemLoader(str(TEMPLATE_DIR)), autoescape=select_autoescape(["html"]), undefined=Undefined,
                      trim_blocks=True, lstrip_blocks=True)
    env.filters.update(money=money, period=period_label, basis=basis_label, datefmt=datefmt, isodate=isodate, md=md_to_html,
                       reading_time=reading_time, e=lambda s: html.escape(str(s)))
    return env


_ENV: Environment | None = None


def render(template: str, **ctx) -> str:
    global _ENV
    if _ENV is None:
        _ENV = make_env()
    return _ENV.get_template(template).render(**ctx)


def site_defaults(*, publication_name: str = "Footnote Daily", environment: str = "development", base_url: str = "",
                  ads_loader_tag: str = "", analytics_tag: str = "", consent_required: bool = True) -> dict:
    """Context shared by every page. Ads/analytics tags are empty unless the adapters emit them."""
    return {
        "site": {
            "name": publication_name,
            "working_title": False,  # brand decided 2026-11-06: "Footnote Daily"; True re-adds the working-masthead note
            "environment": environment,
            "base_url": base_url,
            "staging_banner": False,  # owner decision 2026-11-06 (reader-first): no banner on the hosted preview; non-production builds stay noindex
            "ads_loader_tag": ads_loader_tag,
            "analytics_tag": analytics_tag,
            "consent_required": consent_required,
            "nav": [
                {"label": "Schools", "href": "/schools/"},
                {"label": "Housing", "href": "/topics/housing/"},
                {"label": "Transfer", "href": "/topics/transfer/"},
            ],  # the site renderer replaces this with the topics that have guides (empty sections are hidden)
            "footer_links": [
                {"label": "How we verify", "href": "/about/methods/"},
                {"label": "Corrections", "href": "/about/corrections/"},
                {"label": "Privacy", "href": "/about/privacy/"},
                {"label": "Independence", "href": "/about/independence/"},
            ],
        }
    }
