#!/usr/bin/env bash
# Deploy the site to Netlify. Since 2026-11-08 (Ajay's decision) the deployed site is the Astro build in site/ (templates spec;
# DECISIONS.md), published to the footnote-daily Netlify project: https://footnote-daily.netlify.app. The Jinja render in
# build/site is still produced by publish.sh (lint, local preview) but is no longer what readers see.
#   CAMPUS_DEPLOY_LEGACY=1   deploys build/site to the old campus-ledger-preview project instead (the pre-2026-11-08 behavior).
#   NETLIFY_SITE_ID          overrides the target project id. The id is not a secret; the Netlify login lives in ~/.config/netlify.
# Preview vs live: with CAMPUS_ENVIRONMENT=production and CAMPUS_LIVE_DOMAIN set in the environment (worker/.env, exported by the
# caller) the Astro build drops noindex, writes robots.txt from config/crawlers.yml, fills the sitemap and serves the IndexNow key;
# otherwise it is a noindex preview with canonical URLs on footnote-daily.netlify.app. Going live is still a separate decision.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
export PATH="$HOME/.local/node/bin:$PATH"
NETLIFY_BIN="$(command -v netlify || true)"
deploy() { # dir message
  if [ -n "$NETLIFY_BIN" ]; then exec "$NETLIFY_BIN" deploy --dir "$1" --prod --site "$SITE_ID" --message "$2"; fi
  exec "${NPX:-$HOME/.local/bin/npx}" --yes netlify-cli@17 deploy --dir "$1" --prod --site "$SITE_ID" --message "$2"
}
STAMP="$(git rev-parse --short HEAD) $(date -u +%FT%TZ)"

if [ "${CAMPUS_DEPLOY_LEGACY:-}" = "1" ]; then
  SITE_ID="${NETLIFY_SITE_ID:-2fd93a6a-bf8f-4fae-9c66-f0fdc1b82c56}"   # campus-ledger-preview.netlify.app
  [ -d "$ROOT/build/site" ] || { echo "no build/site: run scripts/v2/render_site.py first"; exit 1; }
  deploy build/site "build/site $STAMP"
fi

SITE_ID="${NETLIFY_SITE_ID:-d857c4bd-18f3-47af-9a39-6d101c91cc0b}"   # footnote-daily.netlify.app
if [ "${CAMPUS_ENVIRONMENT:-}" = "production" ] && [ -n "${CAMPUS_LIVE_DOMAIN:-}" ]; then
  export SITE_PRODUCTION=1 SITE_URL="https://${CAMPUS_LIVE_DOMAIN}"
else
  export SITE_URL="${SITE_URL:-https://footnote-daily.netlify.app}"
fi
cd "$ROOT/site"
[ -d node_modules ] || npm ci --no-audit --no-fund
npm run build            # prebuild photo variants, astro build, check-build (a failed check stops the deploy), Pagefind index
cd "$ROOT"
deploy site/dist "site/dist (Astro) $STAMP"
