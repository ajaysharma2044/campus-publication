"""Render hub pages from real database state into the preview site (honest coverage).

    python -m campus_worker.render.from_db

- /schools/ lists only institutions with at least one staged or published page (none yet) and
  states the registry size and release provenance.
- /schools/<slug>/ renders a school hub for every institution that has any page row (held drafts
  included), showing identity status, topic applicability, verified page counts (0 is 0) and held
  drafts as "in review", never as content.
- /schools/<slug>/<topic>/ renders the topic hub likewise.
"""
from __future__ import annotations

from datetime import datetime, timezone

from ..db import connect
from . import engine, preview

TYPE_LABEL = {"university": "University", "college": "College", "community_college": "Community college", "technical_college": "Technical college",
              "graduate_school": "Graduate school", "system": "University system (not a campus)", "other": "Institution"}


def render_all(conn) -> list[str]:
    out = []
    cur = conn.cursor()
    cur.execute("SELECT count(*) AS n FROM institutions")
    registry_count = cur.fetchone()["n"]
    cur.execute("SELECT DISTINCT source_release FROM institution_external_ids WHERE system_name='ipeds_unitid' AND source_release LIKE 'IPEDS%' LIMIT 1")
    r = cur.fetchone()
    release = r["source_release"] if r else None
    cur.execute("""SELECT i.id, i.canonical_name, i.slug, i.city, i.state_code, i.institution_type, i.control, i.identity_status,
                          (SELECT count(*) FROM pages p WHERE p.institution_id=i.id AND p.status IN ('staged','published')) AS verified_pages,
                          (SELECT count(*) FROM pages p WHERE p.institution_id=i.id AND p.status IN ('held','drafting')) AS held_pages
                   FROM institutions i WHERE EXISTS (SELECT 1 FROM pages p WHERE p.institution_id=i.id) ORDER BY i.canonical_name""")
    schools = cur.fetchall()
    covered = [s for s in schools if s["verified_pages"] > 0]
    ctx = preview.base_ctx("/schools/", "schools_index", "/schools/", registry_count=registry_count, release=release,
                           schools=[{"name": s["canonical_name"], "href": f"/schools/{_slug(s)}/", "city": s["city"], "state": s["state_code"], "type_label": TYPE_LABEL.get(s["institution_type"], "Institution"), "pages": s["verified_pages"]} for s in covered])
    out.append(_write("schools/index.html", engine.render("schools_index.html", **ctx)))
    for s in schools:
        slug = _slug(s)
        cur.execute("""SELECT t.key, t.label, COALESCE(sta.applicability,'unknown') AS applicability,
                              (SELECT count(*) FROM pages p WHERE p.institution_id=%s AND p.topic_id=t.id AND p.status IN ('staged','published')) AS verified,
                              (SELECT count(*) FROM pages p WHERE p.institution_id=%s AND p.topic_id=t.id AND p.status IN ('held','drafting')) AS held
                       FROM topics t LEFT JOIN school_configs sc ON sc.institution_id=%s
                       LEFT JOIN school_topic_applicability sta ON sta.school_config_id=sc.id AND sta.topic_id=t.id ORDER BY t.sort_order""", (s["id"], s["id"], s["id"]))
        topics = cur.fetchall()
        cur.execute("""SELECT p.path, v.headline, v.deck, t.label AS topic, p.status FROM pages p JOIN page_versions v ON v.id = COALESCE(p.current_version_id, (SELECT id FROM page_versions WHERE page_id=p.id ORDER BY version_no DESC LIMIT 1))
                       LEFT JOIN topics t ON t.id=p.topic_id WHERE p.institution_id=%s ORDER BY p.created_at""", (s["id"],))
        pages = cur.fetchall()
        school = {"name": s["canonical_name"], "city": s["city"], "state": s["state_code"], "type_label": TYPE_LABEL.get(s["institution_type"], "Institution"), "control": (s["control"] or "").replace("_", " "),
                  "identity_status": s["identity_status"], "identity_note": _identity_note(s), "coverage_status": "onboarding",
                  "coverage_note": f"{s['verified_pages']} verified page(s); {s['held_pages']} draft(s) held in review (not published)",
                  "topics": [{"label": t["label"], "applicability": t["applicability"], "href": f"/schools/{slug}/{t['key'].replace('_', '-')}/", "page_count": t["verified"]} for t in topics],
                  "guides": [{"topic": p["topic"], "href": p["path"], "headline": p["headline"] + (" — DRAFT HELD, unverified" if p["status"] in ("held", "drafting") else ""), "deck": p["deck"]} for p in pages],
                  "tools": [], "changes": [], "topics_applicable": [t["label"].lower() for t in topics if t["applicability"] == "applicable"]}
        out.append(_write(f"schools/{slug}/index.html", engine.render("school_hub.html", **preview.base_ctx(f"/schools/{slug}/", "school_hub", "/schools/", school=school))))
        for t in topics:
            if t["applicability"] == "unknown" and not (t["verified"] or t["held"]):
                continue
            tkey = t["key"].replace("_", "-")
            tpages = [p for p in pages if p["topic"] == t["label"]]
            topic = {"label": t["label"], "description": f"{t['label']} at {s['canonical_name']}: only facts verified against the institution's own sources are published.", "applicability": t["applicability"],
                     "not_applicable_note": f"{t['label']} is recorded as not applicable at this institution.", "key_fact_label": "", "profiles": [],
                     "guides": [{"href": p["path"], "headline": p["headline"] + (" — DRAFT HELD, unverified" if p["status"] in ("held", "drafting") else ""), "deck": p["deck"]} for p in tpages],
                     "tools": [], "unknowns": [], "empty_note": "No verified pages yet."}
            out.append(_write(f"schools/{slug}/{tkey}/index.html", engine.render("topic_hub.html", **preview.base_ctx(f"/schools/{slug}/{tkey}/", "topic_hub", "/topics/housing/", school={"name": s["canonical_name"], "href": f"/schools/{slug}/"}, topic=topic))))
    return out


def _slug(s) -> str:
    # URL slug without the UNITID suffix for the pilot school; keep the registry slug otherwise
    return "cornell-university" if s["slug"].startswith("cornell-university") else s["slug"]


def _identity_note(s) -> str:
    return {"verified": "Verified against the NCES IPEDS release",
            "pending_verification": "Registry record from an IPEDS mirror; not yet verified against the NCES release",
            "synthetic_fixture": "Synthetic fixture — not a real institution"}.get(s["identity_status"], s["identity_status"])


def _write(rel: str, html: str) -> str:
    p = preview.OUT_DEFAULT / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(html)
    return str(p)


if __name__ == "__main__":
    conn = connect()
    try:
        for p in render_all(conn):
            print(p)
    finally:
        conn.close()
