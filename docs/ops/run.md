# Run, deploy, rollback

Everything below has been exercised in the build container except where marked **owner step**.

## Local development (verified)

```bash
# PostgreSQL 16 (local cluster; dev-only role in .env.example)
service postgresql start
cd worker && cp .env.example .env            # edit DATABASE_URL etc.; never commit .env
python -m campus_worker.db migrate            # forward-only SQL migrations with checksums
python -m campus_worker.cli seed              # permissions + labeled fixture school configs
python -m campus_worker.cli status            # auth mode, budget, queue, heartbeat, integrations
pytest -q                                     # full suite (needs TEST_DATABASE_URL)
python -m campus_worker.render.preview        # static preview from synthetic fixtures → build/preview
python ../scripts/check_css.py                # contrast + forbidden-decoration checks
node ../scripts/qa_screens.js ../build/preview ../build/qa   # 5-width screenshots + a11y/overflow report
```

## Local WordPress staging on SQLite (verified)

```bash
# one-time: clone WordPress and the SQLite integration monorepo into wp-local/
git clone --depth 1 https://github.com/WordPress/WordPress.git wp-local/wordpress
git clone --depth 1 https://github.com/WordPress/sqlite-database-integration.git wp-local/sqlite-plugin
scripts/wp_local.sh setup                     # db drop-in, symlinks plugin + theme, wp-config (staging env type)
(cd wp-local/wordpress && php ../../scripts/wp_install.php)   # installs, activates Campus Core + Campus Editorial, prints an application password
scripts/wp_local.sh start                     # php -S 127.0.0.1:8089
CAMPUS_WP_BASE_URL=http://127.0.0.1:8089 CAMPUS_WP_USER=campusadmin CAMPUS_WP_APP_PASSWORD=<printed> python -m campus_worker.cli status
scripts/wp_local.sh stop
```
Staging facts: `WP_ENVIRONMENT_TYPE=staging` → every page carries `noindex,nofollow`, `/ads.txt` says advertising is not enabled, no ad loader is emitted, the staging banner is shown. The `mu-plugins/local-dev.php` file only allows application passwords over plain HTTP on 127.0.0.1 and must never be deployed.

## Scheduler (local, bounded)

```bash
python -m campus_worker.cli run-once          # one tick: reclaim leases, dispatch eligible jobs within budget/quotas, heartbeat, exit
scripts/continuation_demo.sh                  # bounded multi-iteration run with lock + stop reason (see docs/ops/continuation.md)
```
Exit codes: 0 executing/completed, 10 waiting (no eligible work), 20 usage-paused (budget), 30 blocked (credentials), 1 failed.

## Production deployment (**owner steps**; nothing below has been run)

1. Managed PostgreSQL: set `DATABASE_URL`; run `python -m campus_worker.db migrate` from a release job. Keep a backup before each migration (`scripts/backup.sh`).
2. Managed WordPress: upload `wp/plugins/campus-core` and `wp/themes/campus-editorial`; activate both; set `WP_ENVIRONMENT_TYPE` to `production` only on the live host; create an application password for a least-privilege editor user; set `CAMPUS_WP_BASE_URL/USER/APP_PASSWORD` in the worker's secret store.
3. Worker host: any Linux host or container with Python 3.12+; install `worker/` (`pip install -e worker`), set env from the secret store, and schedule `run-once` hourly (cron, systemd timer, or a cloud scheduled task). Add `--daily` and `--weekly` ticks per `scheduler.py`. Use `flock` or the built-in DB lock to prevent overlap.
4. Model credential: `ANTHROPIC_API_KEY` (API-billed). Until set, every model job holds with `provider_auth`.
5. Ads: only after AdSense approval — set `campus_adsense_publisher_id` and `campus_ads_enabled` options in WordPress and `CAMPUS_ADSENSE_PUBLISHER_ID` / `CAMPUS_ADS_ENABLED=true` in the worker, production only.
6. Search Console: verify the property, create a service account, set `CAMPUS_GSC_CREDENTIALS_PATH` / `CAMPUS_GSC_PROPERTY`.

## Rollback

- Code: redeploy the previous git tag; the worker is stateless between ticks.
- Database: `python -m campus_worker.db migrate-down --to N` applies the documented down script for versions > N. Down scripts are labelled safe/unsafe in their header; for unsafe ones restore from backup (`scripts/restore_test.sh` proves the restore path on a scratch DB).
- Content: every page keeps all `page_versions`; republishing an older passed version is `publisher.publish_version(conn, cms, <older_version_id>)`. The CMS upsert is idempotent by page id, so this overwrites in place and records the change.
- Ads/analytics: flip the environment/option flags; no template change needed.
