"""SEO gate (continuous-local-run R45; AT44). Deterministic, every page must pass it before it can publish; a failing
page is held with the item named. The seo agent adds judgment on intent fit against the strategist's win plan; this
code is the authority on the checkable items:

  title ≤ 60 chars, contains the primary query (or its closest natural form), no clickbait, unique site-wide
  meta description 120–155 chars, unique site-wide
  exactly one H1; H2/H3s cover the secondary questions from search intel (when given)
  URL short, lowercase, hyphenated, matches the SPEC §20 policy (/schools/… or /towns/…), stable (changes need a 301)
  answer first: the opening paragraph answers within 50 words
  structured data valid for the page type; BreadcrumbList on every page; FAQPage only with real observed questions
  internal links: ≥ 3 contextual links + topic hub + school/town hub links with descriptive anchors; ≥ 1 backlink; no orphan
  canonical tag; sitemap lastmod only on substantive updates; indexable in production (noindex only in staging)
  images (if any): alt text, width/height, rights recorded
  performance: screenshot QA at 5 widths with no horizontal overflow; HTML + CSS ≤ 150 KB before images
  freshness: visible Updated date and academic year on any time-bound fact
  cannibalization: the primary query is not targeted by any other published page
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import UUID

import psycopg

from .search_cache import query_norm

MAX_TITLE, MIN_DESC, MAX_DESC = 60, 120, 155
MAX_HTML_CSS_BYTES = 150 * 1024
URL_RE = re.compile(r"^/(schools|towns)/[a-z0-9-]+/[a-z0-9-]+/(compare/[a-z0-9-]+-vs-[a-z0-9-]+|tools/[a-z0-9-]+|[a-z0-9-]+)/$")
CLICKBAIT = re.compile(r"(you won't believe|shocking|secret|hack|\bbest\b.*\bever\b|\d+ things|!!|\?\?|ultimate guide)", re.I)
GENERIC_ANCHORS = {"click here", "here", "read more", "more", "link", "this page", "learn more"}


@dataclass
class Item:
    name: str
    ok: bool
    detail: str = ""


@dataclass
class GateResult:
    passed: bool
    items: list[Item] = field(default_factory=list)
    failed: list[str] = field(default_factory=list)

    def as_dict(self) -> dict:
        return {"passed": self.passed, "failed": self.failed, "items": [i.__dict__ for i in self.items], "checked_at": datetime.now(timezone.utc).isoformat()}


@dataclass
class PageInput:
    path: str
    title: str
    meta_description: str
    h1s: list[str]
    h2h3s: list[str]
    opening_paragraph: str
    primary_query: str
    secondary_questions: list[str] = field(default_factory=list)
    json_ld: list[dict] = field(default_factory=list)                   # every JSON-LD block on the page
    page_type: str = "Article"                                          # Article | Place | CollegeOrUniversity
    real_faq_questions: list[str] = field(default_factory=list)         # observed questions only
    internal_links: list[dict] = field(default_factory=list)            # [{href, anchor}]
    topic_hub: str = ""
    scope_hub: str = ""
    backlinks: int = 0                                                  # existing pages that link here (hubs count once the hub links)
    has_sibling_pages: bool = True                                      # first page under a hub is exempt from the non-hub backlink rule
    canonical: str | None = None
    noindex: bool = False
    environment: str = "production"
    sitemap_lastmod_changed_without_substantive_update: bool = False
    images: list[dict] = field(default_factory=list)                    # [{alt, width, height, rights_recorded, bytes}]
    html_css_bytes: int = 0
    qa_overflow_widths: list[int] = field(default_factory=list)         # widths with horizontal overflow (from scripts/qa_screens.js)
    qa_checked_widths: int = 5
    visible_updated_date: bool = True
    time_bound_facts_with_year: bool = True
    published: bool = False


def _words(s: str) -> int:
    return len(re.findall(r"\b\w+\b", s or ""))


# intent words and the natural forms a title may use instead (the spec's example title for a "<hall> review" query is
# "Boldt Tower: Rooms, Cost, Location and What to Know (2026-27)")
INTENT_FORMS = {
    "review": ("review", "rooms", "cost", "what to know", "guide", "facts", "pros", "worth"), "reviews": ("review", "rooms", "cost", "what to know"),
    "cost": ("cost", "rate", "price", "fee", "$", "how much"), "costs": ("cost", "rate", "price", "fee", "$"), "price": ("price", "cost", "rate", "$"),
    "hours": ("hours", "open", "opening", "closes"), "parking": ("parking", "park"), "schedule": ("schedule", "times", "hours", "when"),
    "requirements": ("requirements", "require", "need", "eligib"), "prerequisites": ("prerequisite", "prereq", "requirements"), "vs": ("vs", "versus", "compared", "or"),
    "good": ("good", "worth", "right", "best fit", "what to know"), "transfers": ("transfer",), "transfer": ("transfer",), "guaranteed": ("guarantee",),
    "size": ("size", "square", "sq", "dimensions"), "room": ("room",), "apply": ("apply", "application", "how to"), "deadline": ("deadline", "due", "by"),
}
STOP = {"the", "a", "an", "is", "are", "do", "does", "at", "in", "for", "to", "of", "and", "or", "can", "i", "my", "how", "what", "which", "much", "it", "there", "get"}


def _contains_query(title: str, query: str) -> bool:
    """The primary query or its closest natural form: every content word of the query (or an accepted natural form of an
    intent word) appears in the title."""
    words = [w for w in re.findall(r"[a-z0-9']+", query.lower()) if w not in STOP]
    t = title.lower()
    for w in words:
        forms = INTENT_FORMS.get(w, (w,))
        if not any(f in t for f in forms) and w.rstrip("s") not in t:
            return False
    return True


def evaluate(p: PageInput, *, existing_titles: set[str] | None = None, existing_descriptions: set[str] | None = None, other_page_for_primary: str | None = None) -> GateResult:
    items: list[Item] = []
    add = lambda name, ok, detail="": items.append(Item(name, bool(ok), detail))
    add("title_length", len(p.title) <= MAX_TITLE and len(p.title) >= 10, f"{len(p.title)} chars")
    add("title_contains_primary_query", _contains_query(p.title, p.primary_query), p.primary_query)
    add("title_no_clickbait", not CLICKBAIT.search(p.title), p.title)
    add("title_unique", p.title.strip().lower() not in {t.lower() for t in (existing_titles or set())}, "site-wide")
    add("meta_length", MIN_DESC <= len(p.meta_description) <= MAX_DESC, f"{len(p.meta_description)} chars")
    add("meta_unique", p.meta_description.strip().lower() not in {d.lower() for d in (existing_descriptions or set())}, "site-wide")
    add("one_h1", len(p.h1s) == 1, f"{len(p.h1s)} H1s")
    missing_secondary = [q for q in p.secondary_questions if not any(_contains_query(h, q) for h in p.h2h3s)]
    add("headings_cover_secondary_questions", not missing_secondary, "; ".join(missing_secondary)[:200])
    add("url_policy", bool(URL_RE.match(p.path)) and p.path == p.path.lower() and " " not in p.path and len(p.path) <= 120, p.path)
    add("answer_first", _words(p.opening_paragraph) <= 50 and _words(p.opening_paragraph) >= 8 and bool(re.search(r"\d|\byes\b|\bno\b|\bmust\b|\bis\b|\bare\b|\bcosts?\b|\brequire", p.opening_paragraph, re.I)), f"{_words(p.opening_paragraph)} words")
    types = [b.get("@type") for b in p.json_ld]
    add("structured_data_breadcrumb", "BreadcrumbList" in types, str(types))
    add("structured_data_page_type", p.page_type in types, f"expected {p.page_type}")
    add("structured_data_faq_only_real", ("FAQPage" not in types) or bool(p.real_faq_questions), "FAQPage requires observed questions")
    contextual = [l for l in p.internal_links if l.get("href") not in (p.topic_hub, p.scope_hub) and (l.get("anchor") or "").strip().lower() not in GENERIC_ANCHORS and (l.get("href") or "").startswith("/")]
    add("internal_links_three_contextual", len(contextual) >= 3, f"{len(contextual)} contextual links")
    add("internal_links_hub_uplinks", any(l.get("href") == p.topic_hub for l in p.internal_links) and any(l.get("href") == p.scope_hub for l in p.internal_links), "topic hub + school/town hub")
    add("internal_links_descriptive_anchors", all((l.get("anchor") or "").strip().lower() not in GENERIC_ANCHORS and len(l.get("anchor") or "") >= 3 for l in p.internal_links), "no 'click here'")
    add("backlink_exists", p.backlinks >= 1 or not p.has_sibling_pages, f"{p.backlinks} inbound links" + ("" if p.has_sibling_pages else " (first page under its hub: exempt)"))
    add("not_orphan", p.backlinks >= 1, f"{p.backlinks} inbound")
    add("canonical_tag", bool(p.canonical) and p.canonical.endswith(p.path), str(p.canonical))
    add("indexable", (p.environment != "production") or (not p.noindex), "noindex only in staging")
    add("sitemap_lastmod_honest", not p.sitemap_lastmod_changed_without_substantive_update, "lastmod changes only on substantive updates")
    img_ok = all(i.get("alt") and i.get("width") and i.get("height") and i.get("rights_recorded") for i in p.images)
    add("images", img_ok, f"{len(p.images)} images")
    add("performance_size", p.html_css_bytes <= MAX_HTML_CSS_BYTES, f"{p.html_css_bytes} bytes (limit {MAX_HTML_CSS_BYTES})")
    add("performance_no_overflow", not p.qa_overflow_widths and p.qa_checked_widths >= 5, f"overflow at {p.qa_overflow_widths}" if p.qa_overflow_widths else f"{p.qa_checked_widths} widths clean")
    add("freshness_updated_date", p.visible_updated_date, "visible Updated date")
    add("freshness_academic_year", p.time_bound_facts_with_year, "academic year on time-bound facts")
    add("no_cannibalization", other_page_for_primary is None, f"primary query also targeted by {other_page_for_primary}" if other_page_for_primary else "")
    failed = [i.name for i in items if not i.ok]
    return GateResult(not failed, items, failed)


def site_uniques(conn: psycopg.Connection, *, exclude_page_id: UUID | None = None) -> tuple[set[str], set[str]]:
    with conn.cursor() as cur:
        cur.execute("""SELECT v.headline, v.deck FROM pages p JOIN page_versions v ON v.id=p.current_version_id WHERE p.status IN ('staged','published') AND (%s::uuid IS NULL OR p.id<>%s)""", (exclude_page_id, exclude_page_id))
        rows = cur.fetchall()
    return {r["headline"] for r in rows if r["headline"]}, {r["deck"] for r in rows if r["deck"]}


def record(conn: psycopg.Connection, version_id: UUID, result: GateResult, *, hold_page: bool = True) -> None:
    """Store the record on the version; a failing gate holds the page with the items named (R45)."""
    with conn.cursor() as cur:
        cur.execute("UPDATE page_versions SET seo_gate=%s::jsonb WHERE id=%s", (json.dumps(result.as_dict()), version_id))
        if not result.passed and hold_page:
            cur.execute("""UPDATE pages SET status='held', revalidation_required=TRUE, revalidation_reason=%s WHERE id=(SELECT page_id FROM page_versions WHERE id=%s) AND status<>'published'""",
                        ("seo_gate failed: " + ", ".join(result.failed), version_id))
    conn.commit()


def passed_record(conn: psycopg.Connection, version_id: UUID) -> bool:
    with conn.cursor() as cur:
        cur.execute("SELECT (seo_gate->>'passed')::boolean AS ok FROM page_versions WHERE id=%s", (version_id,))
        r = cur.fetchone()
    return bool(r and r["ok"])
