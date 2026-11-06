#!/usr/bin/env bash
# Deploy the local site build (build/site, the R8 local publish output) to the Netlify preview site.
# The site id is not a secret; the Netlify login lives in ~/.config/netlify (run `npx netlify-cli@17 login` once).
# This is a hosted PREVIEW of the staging render (noindex; no banner since the reader-first decision of 2026-11-06). Going live and indexable is a separate decision:
# set CAMPUS_LIVE_DOMAIN and CAMPUS_ENVIRONMENT=production in worker/.env so the renderer drops noindex and the live ramp releases pages.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SITE_ID="${NETLIFY_SITE_ID:-2fd93a6a-bf8f-4fae-9c66-f0fdc1b82c56}"   # campus-ledger-preview.netlify.app
[ -d "$ROOT/build/site" ] || { echo "no build/site: publish a page locally first (campus_worker.pipeline publish)"; exit 1; }
cd "$ROOT"
exec "${NPX:-$HOME/.local/bin/npx}" --yes netlify-cli@17 deploy --dir build/site --prod --site "$SITE_ID" --message "build/site $(git rev-parse --short HEAD) $(date -u +%FT%TZ)"
