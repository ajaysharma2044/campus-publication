"""Copy a produced page version into a headless worker's folder as a writer-contract draft (specs/bulk-mode.md section 3 fallback; B5).

  worker/.venv/bin/python scripts/headless_draft.py <version_id> --out build/bulk/headless/<run>/worker-<i>/<slug>.json

Reads page_versions + pages (DATABASE_URL from the environment, as every campus_worker command does) and writes headline, deck,
body_markdown, fact_table, next_actions, claim_refs (the writer contract, worker/campus_worker/contracts/schemas/writer.json) plus
version_id, page_path, gate_status, version_no, contract_valid and exported_at. Refuses an --out path outside build/bulk/headless/
(or $CAMPUS_HEADLESS_ROOT): a worker writes only inside its own folder. Exit 2 on a bad path, 3 when the version does not exist.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from uuid import UUID

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "worker"))
SCHEMA = REPO_ROOT / "worker" / "campus_worker" / "contracts" / "schemas" / "writer.json"


def allowed_roots() -> list[Path]:
    roots = [REPO_ROOT / "build" / "bulk" / "headless"]
    if os.environ.get("CAMPUS_HEADLESS_ROOT"):
        roots.append(Path(os.environ["CAMPUS_HEADLESS_ROOT"]))
    return [r.resolve() for r in roots]


def export(conn, version_id: UUID) -> dict | None:
    with conn.cursor() as cur:
        cur.execute("""SELECT v.id, v.version_no, v.headline, v.deck, v.body_markdown, v.structured, v.gate_status, v.rubric, v.created_at, p.path
                       FROM page_versions v JOIN pages p ON p.id=v.page_id WHERE v.id=%s""", (version_id,))
        v = cur.fetchone()
        if not v:
            return None
        cur.execute("SELECT DISTINCT claim_id FROM page_claims WHERE page_version_id=%s", (version_id,))
        claim_rows = [str(r["claim_id"]) for r in cur.fetchall()]
    structured = v["structured"] or {}
    draft = {"headline": v["headline"], "deck": v["deck"] or "", "body_markdown": v["body_markdown"], "fact_table": structured.get("fact_table") or [],
             "next_actions": structured.get("next_actions") or [], "claim_refs": [str(c) for c in (structured.get("claim_refs") or claim_rows)]}
    valid, errors = None, []
    try:
        import jsonschema
        schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
        errors = [e.message[:200] for e in sorted(jsonschema.Draft202012Validator(schema).iter_errors(draft), key=lambda e: list(e.path))][:5]
        valid = not errors
    except ImportError:
        pass
    return dict(draft, version_id=str(v["id"]), page_path=v["path"], version_no=v["version_no"], gate_status=v["gate_status"], rubric=v["rubric"],
                created_at=v["created_at"].isoformat(timespec="seconds") if v["created_at"] else None, contract_valid=valid, contract_errors=errors,
                exported_at=datetime.now(timezone.utc).isoformat(timespec="seconds"))


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("version_id")
    ap.add_argument("--out", required=True, help="build/bulk/headless/<run>/worker-<i>/<slug>.json")
    a = ap.parse_args(argv)
    try:
        vid = UUID(a.version_id)
    except ValueError:
        print(f"headless_draft: {a.version_id!r} is not a version id", file=sys.stderr)
        return 2
    out = Path(a.out).resolve()
    if out.suffix != ".json" or not any(root == out or root in out.parents for root in allowed_roots()):
        print(f"headless_draft: refusing to write {out}: drafts go only under build/bulk/headless/<run>/worker-<i>/ as <slug>.json", file=sys.stderr)
        return 2
    from campus_worker.config import get_settings
    from campus_worker.db import connect
    conn = connect(get_settings().database_url)
    try:
        doc = export(conn, vid)
    finally:
        conn.close()
    if doc is None:
        print(f"headless_draft: no page version {vid}", file=sys.stderr)
        return 3
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(doc, indent=1, default=str))
    print(json.dumps({"written": str(out), "version_id": doc["version_id"], "page_path": doc["page_path"], "gate_status": doc["gate_status"], "contract_valid": doc["contract_valid"]}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
