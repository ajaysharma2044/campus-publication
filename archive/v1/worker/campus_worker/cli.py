"""Operator CLI.

  python -m campus_worker.cli status      operating status: auth mode, budget, queue, heartbeat, integrations
  python -m campus_worker.cli seed        seed permissions + school configs from fixtures (labeled)
  python -m campus_worker.cli run-once    one bounded scheduler tick (see scheduler.py)
"""
from __future__ import annotations

import json
import sys

from . import budget as budgetmod
from . import queue as queuemod
from .config import get_settings
from .db import connect


def integrations_status(settings) -> dict:
    from .adapters.model import AnthropicProvider
    from .adapters.cms import WordPressAdapter
    from .adapters.search import KeywordProviderAdapter, SerpProviderAdapter
    from .adapters.ads import AdSenseAdapter
    from .adapters.search_console import SearchConsoleAdapter

    caps = [
        AnthropicProvider().capability(),
        WordPressAdapter.from_settings(settings).capability(),
        KeywordProviderAdapter().capability(),
        SerpProviderAdapter().capability(),
        AdSenseAdapter.from_settings(settings).capability(),
        SearchConsoleAdapter().capability(),
    ]
    return {c.provider: c.as_dict() for c in caps}


def status(conn, settings) -> dict:
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM heartbeats ORDER BY component")
        hb = [dict(r) for r in cur.fetchall()]
        cur.execute("SELECT count(*) AS n FROM exceptions WHERE resolved_at IS NULL AND severity IN ('error','critical')")
        open_exc = cur.fetchone()["n"]
    return {
        "environment": settings.environment,
        "publication_name": settings.publication_name,
        "auth_mode": settings.auth_mode(),
        "model_routing": {k: getattr(settings.model_routing, k) for k in (
            "coordinator_model", "classification_model", "extraction_model", "writing_model",
            "editorial_model", "verification_model", "escalation_model")},
        "budget": budgetmod.status(conn, settings.budget, execution_mode=settings.execution_mode),
        "execution_mode": settings.execution_mode,
        "live": settings.is_live,
        "quotas": settings.quotas.__dict__,
        "queue": queuemod.counts(conn),
        "held_or_dead": [dict(r, id=str(r["id"]), age=str(r["age"])) for r in queuemod.held_and_dead(conn)],
        "heartbeats": hb,
        "open_errors": open_exc,
        "integrations": integrations_status(settings),
        "ads_enabled": settings.ads_enabled,
        "auto_publish_enabled": settings.auto_publish_enabled,
    }


def main(argv: list[str]) -> int:
    settings = get_settings()
    if not argv or argv[0] == "status":
        conn = connect(settings.database_url)
        try:
            print(json.dumps(status(conn, settings), indent=2, default=str))
        finally:
            conn.close()
        return 0
    if argv[0] == "seed":
        from .seed import seed_all
        conn = connect(settings.database_url)
        try:
            print(json.dumps(seed_all(conn), indent=2, default=str))
        finally:
            conn.close()
        return 0
    if argv[0] == "run-once":
        from .scheduler import run_once
        conn = connect(settings.database_url)
        try:
            result = run_once(conn, settings)
            print(json.dumps(result, indent=2, default=str))
            return result.get("exit_code", 0)
        finally:
            conn.close()
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
