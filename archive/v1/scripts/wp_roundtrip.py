"""Local WordPress staging round-trip proof (specs/continuous-local-run.md R32, AT31).

Publishes one clearly-labeled fixture page twice through the real WordPressAdapter and asserts:
  first upsert  → created=True
  second upsert → created=False, changed=False  (content-hash no-op: no duplicate post)
Reads CAMPUS_WP_* from the environment (scripts source worker/.env). Prints no secret values.

    scripts/wp_roundtrip.py
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "worker"))

from campus_worker.adapters.cms import PublishRequest, WordPressAdapter  # noqa: E402
from campus_worker.config import get_settings  # noqa: E402


def main() -> int:
    settings = get_settings()
    cms = WordPressAdapter.from_settings(settings)
    cap = cms.capability()
    print(f"cms capability: {cap.state} — {cap.reason}")
    if not cap.connected:
        return 2
    req = PublishRequest(
        external_id="fixture-roundtrip-0000-0000-000000000001",
        post_type="campus_guide",
        title="SYNTHETIC FIXTURE — round-trip check (not a real page)",
        slug="fixture-roundtrip",
        path="/schools/riverbend-cc-synthetic/housing/fixture-roundtrip/",
        content_html="<p>Synthetic fixture page used only to prove the idempotent CMS upsert. Not an institution fact.</p>",
        status="draft",
        meta={"fixture": True, "institution_id": "synthetic"},
    )
    r1 = cms.upsert(req)
    r2 = cms.upsert(req)
    print(f"first upsert : id={r1.cms_id} created={r1.created} changed={r1.changed}")
    print(f"second upsert: id={r2.cms_id} created={r2.created} changed={r2.changed}")
    ok = r1.created and (not r2.created) and (not r2.changed) and r1.cms_id == r2.cms_id
    print("ROUNDTRIP " + ("PASS: hash no-op, no duplicate" if ok else "FAIL"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
