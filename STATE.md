# STATE

Last updated: 2026-11-02 (session 1). Update after every completed task.

## Environment inventory (observed 2026-11-02)
- Container: Linux, Python 3.13, Node 22, PHP 8.3 (pdo_sqlite, pdo_pgsql, mysqli, curl, gd, mbstring, zip), PostgreSQL 16 server (local, started), git, gh, Playwright 1.63 + Chromium. No docker daemon. No wp-cli.
- Network: package registries (PyPI, npm) and github.com reachable. **Blocked (403 by proxy policy):** cornell.edu, nces.ed.gov, ed.gov, wordpress.org, developers.google.com, cdnjs, api.data.gov. Live source collection and IPEDS download are therefore impossible from this container; collectors are tested against fixtures.
- Credentials: no `ANTHROPIC_API_KEY` (Claude Code itself runs on subscription/session auth; worker model calls would be separately API-billed and are **unconnected**). No WordPress, AdSense, Search Console, keyword-provider, or Reddit credentials. `GH_TOKEN` present (not used; no remote repository was requested).
- Existing project: none. Clean directory. Repository created at `/home/user/campus-publication` (local git, branch `main`, no remote).

## Evidence states
| Component | implemented | tested locally | connected | deployed | scheduled |
|-----------|-------------|----------------|-----------|----------|-----------|
| Control files (SPEC/BACKLOG/STATE/CLAUDE) | yes | n/a | n/a | n/a | n/a |
| PostgreSQL research DB | local cluster | yes (select 1) | local only | no | no |
| Everything else | not yet | — | — | — | — |

## Current task
A3 migration runner → A4 core schema.

## Blockers (owner action required; do not block other work)
See BACKLOG.md "Owner dependencies" OD1–OD10.

## Assumptions recorded
- Working masthead text "The Campus Ledger" is a placeholder, editable in config; not a brand decision.
- Local PostgreSQL role `campus` / password `campus_local_dev` is development-only and documented in `.env.example`; not a production secret.
- Cornell identity is seeded from a hand-entered IPEDS UNITID (190415) that must be re-verified against a downloaded IPEDS release once network access permits; it is marked `identity_status = 'pending_verification'`.

## Next actions
1. A3–A12 (Stage A) with tests.
2. B1–B9.
3. C, D, E, F, G in order; G5 remains blocked.
