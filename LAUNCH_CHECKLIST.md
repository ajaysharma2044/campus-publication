# Launch checklist (docs/v5/prelaunch-spec.md, Phase 9d): prepared, not executed

Nothing below has been run. Each step is Ajay's to approve and trigger; the commands are the ones the repo already carries.
The custom domain is www.eduexplained.com (Ajay, 2026-11-11), registered on GoDaddy and connected to Netlify; site/site.config.ts defaults the site URL to it and config/monetization.yml carries it.

## Before the cutover
- [ ] Put the domain in worker/.env as CAMPUS_LIVE_DOMAIN=www.eduexplained.com (the deploy script reads it; Claude never reads that file). Until then the production deploy is `CAMPUS_ENVIRONMENT=production CAMPUS_LIVE_DOMAIN=www.eduexplained.com bash scripts/deploy_netlify.sh` (used 2026-11-11 22:20 EST).
- [x] (2026-11-11) `worker/.venv/bin/python scripts/prelaunch/score_pages.py` is clean of surprises: reports/09-eligibility.csv lists the eligible pages and why the rest fail.
- [x] (2026-11-11, 336 pages) `worker/.venv/bin/python scripts/prelaunch/waves.py plan` wrote config/waves.json: wave 1 is the top 300 to 500 eligible pages, spread across sections, with the transfer section and the best housing, dining and tools pages included. Read the list.
- [x] (2026-11-11) `python3 scripts/lint-content.py` passes with no matches; `grep -r "—" content site/dist` prints nothing.

## Cutover (in this order)
Done 2026-11-11 22:20 EST: www.eduexplained.com is the primary domain on Netlify (eduexplained.com and eduexplained.netlify.app 301 to it), canonicals point at it, DNS at GoDaddy already pointed at Netlify. Still blocked: robots Disallow, noindex, empty sitemap, until the LAUNCHED step below.
1. Set the site base URL and every canonical to https://www.eduexplained.com: `CAMPUS_ENVIRONMENT=production CAMPUS_LIVE_DOMAIN=www.eduexplained.com` in worker/.env (scripts/deploy_netlify.sh exports SITE_URL from it).
2. In Netlify, set www.eduexplained.com as the primary domain of the project (id d857c4bd-18f3-47af-9a39-6d101c91cc0b) so every eduexplained.netlify.app URL 301s to the matching www.eduexplained.com URL (Netlify does this for the primary custom domain).
3. Set LAUNCHED=true for the build (`LAUNCHED=true` in the environment the deploy runs in), promote wave 1 only (`worker/.venv/bin/python scripts/prelaunch/waves.py promote 1`), rebuild and deploy (`bash scripts/deploy_netlify.sh`).
4. Verify with curl:
   - `curl -s https://www.eduexplained.com/robots.txt` allows crawling (search and retrieval crawlers allowed, AI training crawlers blocked, the sitemap URL listed);
   - a wave 1 page returns `<meta name="robots" content="index, follow">`; a page outside wave 1 returns `noindex, follow`;
   - `curl -s https://www.eduexplained.com/sitemap.xml` lists only wave 1 pages;
   - `curl -sI https://eduexplained.netlify.app/cornell/housing/cornell-off-campus-housing-guide/` returns a 301 to www.eduexplained.com.
5. Submit the sitemap in Google Search Console and Bing Webmaster Tools; enable IndexNow for Bing (scripts/v2/indexnow.py submits new and changed URLs after each deploy; the key file is config/indexnow.key).

## After the cutover
- Enter the Search Console numbers for wave 1 into config/wave-metrics.json after 3 to 4 weeks; `waves.py status` says whether wave 2 is allowed (50 percent indexed, impressions flat or rising, weekly audit error rate under 3 percent, no manual actions).
- Run `worker/.venv/bin/python scripts/prelaunch/audit_weekly.py` each week; its report is reports/audit-YYYY-MM-DD.md.
- Kill switch for a section: `worker/.venv/bin/python scripts/prelaunch/waves.py kill <section>`, then deploy.
