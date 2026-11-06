"""Render a static preview site from LABELED SYNTHETIC fixtures to build/preview/.

    python -m campus_worker.render.preview [--out DIR]

Every page carries the staging banner. Nothing here is real institution data; the synthetic
school is "Fixture State University". The same templates render real records in the publish
path (cms/publisher.py) and in the WordPress theme.
"""
from __future__ import annotations

import json
import shutil
import sys

import yaml
from datetime import date, datetime, timezone
from pathlib import Path

from ..config import REPO_ROOT
from ..tools.calculator import LineItem, calculate
from . import engine

OUT_DEFAULT = REPO_ROOT / "build" / "preview"
POLICY_DIR = Path(__file__).parent / "content" / "policies"
TODAY = date.today()
VERIFIED = datetime(2026, 10, 28, 14, 0, tzinfo=timezone.utc)


def base_ctx(path: str, template_name: str, section: str = "", **extra) -> dict:
    ctx = engine.site_defaults(publication_name="Footnote Daily", environment="preview", base_url="")
    ctx.update(canonical_path=path, template_name=template_name, static_prefix="/static/", today=TODAY, noindex=True,
               compact_masthead=template_name not in ("home",), current_section=section, ad_slots={}, related=[])
    ctx.update(extra)
    return ctx


SOURCES = [
    {"url": "https://www.fixturestate.example.edu/housing/rates", "title": "Residence hall rates, 2026–27 (synthetic fixture)", "publisher": "Fixture State University Housing", "retrieved_at": VERIFIED, "kind": "official page"},
    {"url": "https://www.fixturestate.example.edu/housing/rate-sheet.pdf", "title": "Housing rate sheet (synthetic fixture PDF)", "publisher": "Fixture State University Housing", "retrieved_at": VERIFIED, "kind": "official PDF"},
]
IMG = "/static/img/placeholders/"
PHOTOS_DIR = REPO_ROOT / "content" / "images"          # owner-supplied photographs + credits.yml
PHOTOS_URL = "/static/img/photos/"
CREDIT = "Synthetic placeholder illustration (preview only; published pages carry credited, rights-cleared photographs)"


def _photo_credits() -> dict:
    f = PHOTOS_DIR / "credits.yml"
    if not f.exists():
        return {}
    data = yaml.safe_load(f.read_text()) or {}
    return data if isinstance(data, dict) else {}


PHOTOS = _photo_credits()


def pic(name: str, alt: str, caption: str | None = None) -> dict:
    """Image record for a slot: the owner's photo from content/images/ when credits.yml lists one
    (file + alt + credit required), else the labeled synthetic placeholder."""
    entry = PHOTOS.get(name)
    if isinstance(entry, dict) and entry.get("file") and entry.get("alt") and entry.get("credit") and (PHOTOS_DIR / entry["file"]).exists():
        stem = Path(entry["file"]).stem
        return {"src": f"{PHOTOS_URL}{entry['file']}", "src_small": f"{PHOTOS_URL}{stem}-800.jpg", "alt": entry["alt"],
                "caption": entry.get("caption") or caption, "credit": entry["credit"]}
    return {"src": f"{IMG}{name}.jpg", "src_small": f"{IMG}{name}-800.jpg", "alt": alt, "caption": caption, "credit": CREDIT}


def copy_photos(static_out: Path) -> None:
    """Copy credited photos into the build and write an 800px-wide card copy next to each."""
    used = [e for e in PHOTOS.values() if isinstance(e, dict) and e.get("file") and (PHOTOS_DIR / e["file"]).exists()]
    if not used:
        return
    from PIL import Image
    dest = static_out / "img" / "photos"
    dest.mkdir(parents=True, exist_ok=True)
    for e in used:
        src = PHOTOS_DIR / e["file"]
        shutil.copy2(src, dest / src.name)
        with Image.open(src) as im:
            im = im.convert("RGB")
            w, h = im.size
            im.resize((800, max(1, round(h * 800 / w))), Image.LANCZOS).save(dest / f"{src.stem}-800.jpg", quality=80, optimize=True)


NOTE = ("Produced by the publication's automated research and writing system from the sources listed, with deterministic fact checks and a "
        "model-based verification pass. No human editor reviewed this version. This preview uses synthetic fixture data.")

PROFILE_BODY = """Fixture Hall's double room costs $12,042 per person for the 2026-27 academic year, billed in two equal semester installments. That is the housing office's published rate, not an estimate, and it covers the room only. Dining is billed separately.

The building is air-conditioned, which matters in late August and early September more than the brochure suggests. Whether every floor has a kitchen is unknown: the housing site does not say, and we have not confirmed it with the housing office.

## What the room rate includes

The rate is per person, so two roommates each pay $12,042. The rate sheet excludes a $250 housing deposit, which is refundable under the cancellation policy and is therefore not a cost in our calculator.

## Building facts

The table below is rendered from the same verified records that feed the comparison and calculator, so a change to a rate updates all three at once.

[[fact-table]]

## Tradeoffs

Fixture Hall trades a higher double-room rate than Riverside Hall for air conditioning and a shorter walk to the main quad, according to the housing office's own distance note. Whether that is worth $460 a year depends on your class schedule and how you handle heat.

## What we could not verify

Kitchen access, in-building laundry, and contract length are unknown. Ask the housing office directly; their answer is authoritative and ours is not.
"""


def profile_ctx() -> dict:
    rows = [
        {"label": "Double room, 2026-27", "value": "$12,042 per academic year, per person", "status": "verified", "verified_at": VERIFIED, "numeric": True},
        {"label": "Single room, 2026-27", "value": "$13,770 per academic year, per person", "status": "verified", "verified_at": VERIFIED, "numeric": True},
        {"label": "Housing deposit", "value": "$250 one-time, refundable", "status": "verified", "verified_at": VERIFIED, "numeric": True, "note": "not a cost; shown separately"},
        {"label": "Air conditioning", "value": "Yes", "status": "verified", "verified_at": VERIFIED},
        {"label": "Kitchen access", "value": "Unknown", "status": "unknown", "status_label": "unknown"},
        {"label": "Laundry in building", "value": "Unknown", "status": "unknown"},
        {"label": "Who can live here", "value": "First-year and returning undergraduates", "status": "verified", "verified_at": VERIFIED},
        {"label": "Distance to central campus", "value": "About a 6-minute walk per the housing office's distance note", "status": "verified", "verified_at": VERIFIED},
    ]
    page = {"id": "00000000-0000-0000-0000-00000000f001", "headline": "Fixture Hall: what the double-room rate includes", "deck": "Per-person academic-year rate, who can live here, and what we could not verify.",
            "section": "Fixture State University · Housing", "section_href": "/schools/fixture-state/housing/", "byline": "Housing desk",
            "published_at": datetime(2026, 10, 29, tzinfo=timezone.utc), "updated_at": datetime(2026, 10, 29, tzinfo=timezone.utc), "audience_label": "first-year students",
            "image": pic("fixture-hall", "Fixture Hall, a synthetic residence hall (placeholder illustration)", "Fixture Hall faces the main quad"), "body_markdown": PROFILE_BODY, "fact_table": rows, "fact_table_caption": "Fixture Hall — verified facts", "fact_table_footnote": "Rates are per person, per academic year, as published by the housing office. Unknown means no verified source states it, not that the feature is absent.",
            "next_actions": [{"text": "Compare Fixture Hall with Riverside Hall on the same basis", "target": "/schools/fixture-state/housing/compare/fixture-hall-vs-riverside-hall/"},
                             {"text": "Estimate your total housing cost for the year", "target": "/tools/total-cost/?school=fixture-state"},
                             {"text": "Check whether you are eligible to live here", "target": "/schools/fixture-state/housing/eligibility/"}],
            "sources": SOURCES, "production_note": NOTE, "stale": False}
    sd = {"@context": "https://schema.org", "@type": "Article", "headline": page["headline"], "description": page["deck"], "datePublished": "2026-10-29",
          "dateModified": "2026-10-29", "author": {"@type": "Organization", "name": "Footnote Daily — Housing desk"}, "publisher": {"@type": "Organization", "name": "Footnote Daily"}}
    related = [{"text": "Riverside Hall profile", "href": "/schools/fixture-state/housing/riverside-hall/"}, {"text": "Housing deadlines at Fixture State", "href": "/schools/fixture-state/housing/deadlines/"}]
    return base_ctx("/schools/fixture-state/housing/fixture-hall/", "entity_profile", "/topics/housing/", page=page, structured_data=json.dumps(sd), related=related)


def comparison_ctx() -> dict:
    ents = [{"name": "Fixture Hall", "institution": "Fixture State University", "href": "/schools/fixture-state/housing/fixture-hall/"},
            {"name": "Riverside Hall", "institution": "Fixture State University", "href": "/schools/fixture-state/housing/riverside-hall/"}]
    rows = [
        {"label": "Room rate", "differs": True, "cells": [{"display": "$12,042 per academic year, per person (2026-27)", "status": "verified"}, {"display": "$11,582 per academic year, per person (2026-27)", "status": "verified"}]},
        {"label": "Air conditioning", "differs": True, "cells": [{"display": "Yes", "status": "verified"}, {"display": "No", "status": "verified"}]},
        {"label": "Kitchen access", "differs": False, "cells": [{"display": "Unknown", "status": "unknown"}, {"display": "Yes, one per floor", "status": "verified"}]},
        {"label": "Laundry in building", "differs": False, "cells": [{"display": "Unknown", "status": "unknown"}, {"display": "Unknown", "status": "unknown"}]},
        {"label": "Who can live here", "differs": False, "cells": [{"display": "First-year and returning undergraduates", "status": "verified"}, {"display": "First-year and returning undergraduates", "status": "verified"}]},
        {"label": "Distance to central campus", "differs": True, "cells": [{"display": "About 6 minutes' walk (housing office note)", "status": "verified"}, {"display": "About 14 minutes' walk (housing office note)", "status": "verified"}]},
        {"label": "Contract length", "differs": False, "cells": [{"display": "Unknown", "status": "unknown"}, {"display": "Unknown", "status": "unknown"}]},
    ]
    comp = {"id": "00000000-0000-0000-0000-00000000f002", "title": "Fixture Hall vs. Riverside Hall: same basis, real differences", "description": "Two first-year halls compared on the published per-person academic-year rate and the facts we could verify.",
            "section": "Fixture State University · Housing", "section_href": "/schools/fixture-state/housing/", "byline": "Housing desk", "verified_at": VERIFIED,
            "period": "per_academic_year", "basis": "per_person", "room_type": "double", "entities": ents, "rows": rows,
            "notes": ["3 cell(s) are unknown because no verified source states them. Unknown does not mean the feature is absent."],
            "tradeoffs": ["On the same per academic year, per-person basis, Riverside Hall is $460 less than Fixture Hall for a double room.",
                          "Air conditioning differs — Fixture Hall: Yes; Riverside Hall: No.",
                          "Distance to central campus differs — Fixture Hall: about 6 minutes' walk; Riverside Hall: about 14 minutes' walk."],
            "limitations": "It does not tell you which hall is better. Noise, community, maintenance and room condition are not in any verified record we hold, and we do not invent resident consensus. Rates are the published figures for 2026-27 and can change with Board approval.",
            "next_actions": [{"text": "Add dining and fees in the total-cost calculator", "target": "/tools/total-cost/?school=fixture-state"}, {"text": "Read the Fixture Hall profile", "target": "/schools/fixture-state/housing/fixture-hall/"}],
            "sources": SOURCES, "production_note": NOTE}
    return base_ctx("/schools/fixture-state/housing/compare/fixture-hall-vs-riverside-hall/", "comparison", "/topics/housing/", comp=comp)


def calculator_ctx() -> dict:
    items = [LineItem("Fixture Hall double room", 1204200, "per_academic_year", "per_person", claim_id="c1"),
             LineItem("Meal plan A", 295000, "per_semester", "per_person", claim_id="c2"),
             LineItem("Housing deposit", 25000, "one_time", "per_person", refundable_deposit=True, claim_id="c3"),
             LineItem("Student activity fee", 15000, "per_semester", "per_person", claim_id="c4"),
             LineItem("Parking permit (optional)", None, "per_academic_year", "per_person", mandatory=False),
             LineItem("Renter's insurance (optional)", None, "per_month", "per_person", mandatory=False)]
    res = calculate(items, target_period="per_academic_year")
    calc = {"id": "00000000-0000-0000-0000-00000000f003", "title": "Total housing cost calculator — Fixture State University", "description": "Add the published room rate, meal plan and mandatory fees on one comparison period. Unknowns stay unknown; your own figures are labeled as assumptions.",
            "section": "Tools", "section_href": "/tools/", "action": "/tools/total-cost/", "target_period": "per_academic_year", "occupants": None,
            "periods": [{"value": "per_academic_year", "label": "Academic year"}, {"value": "per_semester", "label": "Semester"}, {"value": "per_month", "label": "Month (9-month year)"}],
            "line_items": [dict(label=i.label, amount_minor=i.amount_minor, period=i.period, basis=i.basis, mandatory=i.mandatory, refundable_deposit=i.refundable_deposit, is_assumption=i.is_assumption, claim_id=i.claim_id, verified_at=VERIFIED) for i in items],
            "result": res, "method": "Each charge is converted to the chosen period using the stated billing period (2 semesters or 9 months per academic year). Per-unit prices are divided by the occupants you enter. Refundable deposits are shown separately and never added to cost. Blank amounts remain unknown and are listed, not zeroed.",
            "limitations": "This is an estimate from published rates, not an official bill or a financial-aid award. Fees change; check the school's billing office for your situation.",
            "next_actions": [{"text": "Compare halls on the same basis", "target": "/schools/fixture-state/housing/compare/fixture-hall-vs-riverside-hall/"}],
            "sources": SOURCES, "production_note": NOTE}
    return base_ctx("/tools/total-cost/", "calculator", "/tools/", calc=calc)


def home_ctx(empty: bool = False) -> dict:
    lead = None if empty else {"section": "Housing · Fixture State University", "section_href": "/schools/fixture-state/housing/", "href": "/schools/fixture-state/housing/fixture-hall/",
                               "headline": "Fixture Hall: what the double-room rate includes", "deck": "Per-person academic-year rate, who can live here, and what we could not verify.", "byline": "Housing desk", "updated": VERIFIED,
                               "image": pic("fixture-hall", "Fixture Hall, a synthetic residence hall (placeholder illustration)")}
    supporting = [] if empty else [{"section": "Housing", "href": "/schools/fixture-state/housing/compare/fixture-hall-vs-riverside-hall/", "headline": "Fixture Hall vs. Riverside Hall: same basis, real differences", "deck": "Two first-year halls compared on the published per-person rate.", "image": pic("riverside-hall", "Riverside Hall (placeholder illustration)")},
                                  {"section": "Housing", "href": "/schools/fixture-state/housing/", "headline": "Housing at Fixture State: rates, eligibility and deadlines", "deck": "The housing hub: every verified page for this school in one place.", "image": pic("quad", "The main quad (placeholder illustration)")}]
    return base_ctx("/", "home", "/", lead=lead, supporting=supporting, coverage={"schools_with_coverage": 0 if empty else 1, "registry_count": 7},
                    tools=[{"label": "Total housing cost calculator", "href": "/tools/total-cost/", "state": "ready"}, {"label": "Side-by-side comparison", "href": "/schools/fixture-state/housing/compare/fixture-hall-vs-riverside-hall/", "state": "ready"}],
                    schools=[] if empty else [{"name": "Fixture State University (synthetic)", "href": "/schools/fixture-state/", "pages": 3, "image": pic("fixture-state-campus", "Fixture State University campus (placeholder illustration)")}],
                    updates=[] if empty else [{"href": "/schools/fixture-state/housing/fixture-hall/", "headline": "Fixture Hall double-room rate", "change": "2026-27 rate added; 2025-26 marked historical", "date": VERIFIED}])


def school_hub_ctx(commuter: bool = False) -> dict:
    if commuter:
        school = {"name": "Riverbend Community College (synthetic)", "city": "Riverbend", "state": "OH", "type_label": "Community college", "control": "public", "identity_status": "synthetic_fixture",
                  "identity_note": "Synthetic fixture — not a real institution", "coverage_note": "Onboarding; no verified pages", "coverage_status": "onboarding",
                  "topics": [{"label": "Transfer pathways", "applicability": "applicable", "href": "#", "page_count": 0}, {"label": "Academic programs", "applicability": "applicable", "href": "#", "page_count": 0},
                             {"label": "Transportation and parking", "applicability": "applicable", "href": "#", "page_count": 0}, {"label": "Costs and financial aid", "applicability": "applicable", "href": "#", "page_count": 0},
                             {"label": "Housing", "applicability": "not_applicable"}, {"label": "Dining", "applicability": "unknown"}],
                  "guides": [], "tools": [], "changes": [], "topics_applicable": ["transfer", "programs", "transportation", "costs and aid"]}
        return base_ctx("/schools/riverbend-community-college/", "school_hub", "/schools/", school=school)
    school = {"name": "Fixture State University (synthetic)", "city": "Fixtureville", "state": "NY", "type_label": "University", "control": "public", "identity_status": "synthetic_fixture",
              "identity_note": "Synthetic fixture — not a real institution", "coverage_note": "Pilot: housing", "coverage_status": "pilot", "image": pic("fixture-state-campus", "Fixture State University campus (placeholder illustration)"),
              "topics": [{"label": "Housing", "applicability": "applicable", "href": "/schools/fixture-state/housing/", "page_count": 3}, {"label": "Dining", "applicability": "applicable", "href": "#", "page_count": 0},
                         {"label": "Costs and financial aid", "applicability": "applicable", "href": "#", "page_count": 0}, {"label": "Transfer pathways", "applicability": "applicable", "href": "#", "page_count": 0}],
              "guides": [{"topic": "Housing", "href": "/schools/fixture-state/housing/fixture-hall/", "headline": "Fixture Hall: what the double-room rate includes", "deck": "Per-person academic-year rate, who can live here, and what we could not verify."}],
              "tools": [{"label": "Fixture Hall vs. Riverside Hall", "href": "/schools/fixture-state/housing/compare/fixture-hall-vs-riverside-hall/", "state": "ready"}, {"label": "Total housing cost", "href": "/tools/total-cost/", "state": "ready"}],
              "changes": [{"href": "/schools/fixture-state/housing/fixture-hall/", "headline": "Fixture Hall double-room rate", "change": "2026-27 rate added", "date": VERIFIED}],
              "topics_applicable": ["housing", "dining", "costs and aid", "transfer"]}
    return base_ctx("/schools/fixture-state/", "school_hub", "/schools/", school=school)


def topic_hub_ctx(empty: bool = False) -> dict:
    school = {"name": "Fixture State University (synthetic)", "href": "/schools/fixture-state/"}
    if empty:
        topic = {"label": "Housing", "description": "Residence halls, rates, eligibility and deadlines.", "applicability": "not_applicable",
                 "not_applicable_note": "Riverbend Community College has no residence halls, so housing coverage is not applicable. Commuting and parking are covered under Transportation."}
        return base_ctx("/schools/riverbend-community-college/housing/", "topic_hub", "/topics/housing/", school={"name": "Riverbend Community College (synthetic)", "href": "#"}, topic=topic)
    topic = {"label": "Housing", "description": "Residence halls, published rates on a per-person basis, who can live where, and the deadlines that matter.", "applicability": "applicable", "key_fact_label": "Double room, 2026-27",
             "profiles": [{"name": "Fixture Hall", "href": "/schools/fixture-state/housing/fixture-hall/", "key_fact": "$12,042 / yr", "verified_at": VERIFIED}, {"name": "Riverside Hall", "href": "#", "key_fact": "$11,582 / yr", "verified_at": VERIFIED}, {"name": "Oak Hall", "href": "#", "key_fact": "Unknown", "verified_at": VERIFIED}],
             "guides": [], "tools": [{"label": "Compare two halls", "href": "/schools/fixture-state/housing/compare/fixture-hall-vs-riverside-hall/", "state": "ready"}, {"label": "Total housing cost", "href": "/tools/total-cost/", "state": "ready"}],
             "unknowns": ["Whether transfer students are guaranteed housing", "Oak Hall 2026-27 rate"], "empty_note": ""}
    return base_ctx("/schools/fixture-state/housing/", "topic_hub", "/topics/housing/", school=school, topic=topic)


def search_ctx(mode: str) -> dict:
    filters = [{"value": "school", "label": "Schools", "checked": True}, {"value": "profile", "label": "Building & program profiles", "checked": True}, {"value": "guide", "label": "Guides", "checked": True}, {"value": "tool", "label": "Tools", "checked": True}]
    if mode == "disambiguation":
        return base_ctx("/search/", "search", "/", query="Fixture State University", filters=filters, results=[], disambiguation=[
            {"name": "Fixture State University", "href": "/schools/fixture-state/", "city": "Fixtureville", "state": "NY", "type_label": "University", "is_system": False},
            {"name": "Fixture State University", "href": "#", "city": "Other Town", "state": "NY", "type_label": "University", "is_system": False},
            {"name": "Fixture State University System Office", "href": "#", "city": "Fixtureville", "state": "NY", "type_label": "System", "is_system": True}])
    if mode == "empty":
        return base_ctx("/search/", "search", "/", query="quantum basket weaving dorm", filters=filters, results=[], disambiguation=[])
    return base_ctx("/search/", "search", "/", query=None, filters=filters, results=[], disambiguation=[])


def policy_ctx(key: str) -> dict:
    md = (POLICY_DIR / f"{key}.md").read_text()
    title, _, body = md.partition("\n")
    summary_line = body.strip().split("\n")[0]
    return base_ctx(f"/about/{key}/", "policy", "/about/methods/", policy={"title": title.lstrip("# ").strip(), "summary": summary_line, "body_markdown": body, "updated_at": TODAY})


PAGES = {
    "index.html": lambda: ("home.html", home_ctx()),
    "home-empty.html": lambda: ("home.html", home_ctx(empty=True)),
    "schools/index.html": lambda: ("schools_index.html", base_ctx("/schools/", "schools_index", "/schools/", registry_count=7, release="SYNTHETIC_HD",
                                                                   schools=[{"name": "Fixture State University (synthetic)", "href": "/schools/fixture-state/", "city": "Fixtureville", "state": "NY", "type_label": "University", "pages": 3}])),
    "schools/fixture-state/index.html": lambda: ("school_hub.html", school_hub_ctx()),
    "schools/riverbend-community-college/index.html": lambda: ("school_hub.html", school_hub_ctx(commuter=True)),
    "schools/fixture-state/housing/index.html": lambda: ("topic_hub.html", topic_hub_ctx()),
    "schools/riverbend-community-college/housing/index.html": lambda: ("topic_hub.html", topic_hub_ctx(empty=True)),
    "schools/fixture-state/housing/fixture-hall/index.html": lambda: ("entity_profile.html", profile_ctx()),
    "schools/fixture-state/housing/compare/fixture-hall-vs-riverside-hall/index.html": lambda: ("comparison.html", comparison_ctx()),
    "tools/total-cost/index.html": lambda: ("calculator.html", calculator_ctx()),
    "search/index.html": lambda: ("search.html", search_ctx("blank")),
    "search/disambiguation.html": lambda: ("search.html", search_ctx("disambiguation")),
    "search/empty.html": lambda: ("search.html", search_ctx("empty")),
    "404.html": lambda: ("not_found.html", base_ctx("/404", "not_found", "/")),
    "about/methods/index.html": lambda: ("policy.html", policy_ctx("methods")),
    "about/corrections/index.html": lambda: ("policy.html", policy_ctx("corrections")),
    "about/privacy/index.html": lambda: ("policy.html", policy_ctx("privacy")),
    "about/independence/index.html": lambda: ("policy.html", policy_ctx("independence")),
}


def build(out: Path = OUT_DEFAULT) -> list[Path]:
    out.mkdir(parents=True, exist_ok=True)
    static_out = out / "static"
    if static_out.exists():
        shutil.rmtree(static_out)
    shutil.copytree(engine.STATIC_DIR, static_out)
    copy_photos(static_out)
    written = []
    for rel, fn in PAGES.items():
        template, ctx = fn()
        html = engine.render(template, **ctx)
        p = out / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(html)
        written.append(p)
    (out / "PREVIEW-README.txt").write_text("Static preview rendered from SYNTHETIC fixtures. Not a published site. Serve with: python -m http.server -d build/preview 8080\n")
    return written


if __name__ == "__main__":
    target = OUT_DEFAULT
    if "--out" in sys.argv:
        target = Path(sys.argv[sys.argv.index("--out") + 1])
    files = build(target)
    print(f"rendered {len(files)} pages to {target}")
