"""First-party questions supplied by the owner (continuous-local-run R46): data/first_party/*.csv | *.jsonl.

Accepted columns: question (required), audience, topic_hint, asked_on (YYYY-MM-DD). Anything that looks like an
identity (email, phone, a name column, "my name is …") rejects the row — these files must be anonymized before they
land in the repo.
"""
from __future__ import annotations

import csv
import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from uuid import UUID

import psycopg

from ..config import REPO_ROOT
from ..discovery import QuestionInput

DIR_DEFAULT = REPO_ROOT / "data" / "first_party"
ALLOWED_COLUMNS = {"question", "audience", "topic_hint", "asked_on"}
EMAIL = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")
PHONE = re.compile(r"(\+?\d[\d\s().-]{8,}\d)")
NAME_PHRASES = re.compile(r"\b(my name is|i am [A-Z][a-z]+ [A-Z][a-z]+|this is [A-Z][a-z]+ [A-Z][a-z]+)\b", re.I)


@dataclass
class LoadResult:
    accepted: list[QuestionInput]
    rejected: list[tuple[int, str]]


def _check_row(i: int, row: dict) -> str | None:
    extra = set(row) - ALLOWED_COLUMNS
    if extra:
        return f"row {i}: disallowed columns {sorted(extra)} (only {sorted(ALLOWED_COLUMNS)})"
    q = (row.get("question") or "").strip()
    if not q:
        return f"row {i}: empty question"
    blob = " ".join(str(v) for k, v in row.items() if v and k != "asked_on")  # the date column is not PII
    if EMAIL.search(blob):
        return f"row {i}: contains an email address"
    for m in PHONE.finditer(blob):
        if sum(ch.isdigit() for ch in m.group(0)) >= 7:
            return f"row {i}: contains a phone number"
    if NAME_PHRASES.search(blob):
        return f"row {i}: contains a name phrase"
    return None


def load_file(path: Path, *, institution_id: UUID | None = None) -> LoadResult:
    rows: list[dict] = []
    if path.suffix.lower() == ".csv":
        with path.open(newline="", encoding="utf-8") as fh:
            rows = list(csv.DictReader(fh))
    elif path.suffix.lower() in (".jsonl", ".ndjson"):
        rows = [json.loads(l) for l in path.read_text(encoding="utf-8").splitlines() if l.strip()]
    else:
        raise ValueError(f"unsupported first-party file type: {path.name}")
    accepted, rejected = [], []
    for i, row in enumerate(rows, 1):
        err = _check_row(i, {k: (v or "") for k, v in row.items()})
        if err:
            rejected.append((i, err))
            continue
        asked = row.get("asked_on")
        observed = datetime.strptime(asked, "%Y-%m-%d").replace(tzinfo=timezone.utc) if asked else None
        accepted.append(QuestionInput(raw_text=row["question"].strip()[:300], origin="first_party", institution_id=institution_id,
                                      topic_key=(row.get("topic_hint") or None), observed_at=observed,
                                      source_ref=f"first_party:{path.name}:{i}", constraints=[f"audience:{row['audience']}"] if row.get("audience") else []))
    return LoadResult(accepted, rejected)


def load_all(conn: psycopg.Connection, *, directory: Path = DIR_DEFAULT, institution_id: UUID | None = None) -> dict:
    from .. import discovery

    out = {"files": 0, "accepted": 0, "rejected": [], "stored": 0}
    if not directory.exists():
        return out
    for p in sorted(directory.glob("*")):
        if p.suffix.lower() not in (".csv", ".jsonl", ".ndjson"):
            continue
        res = load_file(p, institution_id=institution_id)
        out["files"] += 1
        out["accepted"] += len(res.accepted)
        out["rejected"] += [f"{p.name}: {e}" for _, e in res.rejected]
        if res.accepted:
            out["stored"] += discovery.ingest(conn, res.accepted)["stored"]
    return out
