# Launch checklist (docs/v5/prelaunch-spec.md, Phase 9d): prepared, not executed

Nothing below has been run. Each step is Ajay's to approve and trigger; the commands are the ones the repo already carries.
{{DOMAIN}} is the custom domain registered on GoDaddy and connected to Netlify; it is not in the repo config yet (site/site.config.ts
defaults the site URL to https://www.eduexplained.com, marked OWNER: confirm), so the first step is to confirm it.

## Before the cutover
- [ ] Confirm {{DOMAIN}} (www or bare host) and put it in worker/.env as CAMPUS_LIVE_DOMAIN={{DOMAIN}} (the deploy script reads it; Claude never reads that file).
- [ ] `worker/.venv/bin/python scripts/prelaunch/score_pages.py` is clean of surprises: reports/09-eligibility.csv lists the eligible pages and why the rest fail.
- [ ] `worker/.venv/bin/python scripts/prelaunch/waves.py plan` wrote config/waves.json: wave 1 is the top 300 to 500 eligible pages, spread across sections, with the transfer section and the best housing, dining and tools pages included. Read the list.
- [ ] `python3 scripts/lint-content.py` passes with no matches; `grep -r "—" content site/dist` prints nothing.

## Cutover (in this order)
1. Set the site base URL and every canonical to https://{{DOMAIN}}: `CAMPUS_ENVIRONMENT=production CAMPUS_LIVE_DOMAIN={{DOMAIN}}` in worker/.env (scripts/deploy_netlify.sh exports SITE_URL from it).
2. In Netlify, set {{DOMAIN}} as the primary domain of the project (id d857c4bd-18f3-47af-9a39-6d101c91cc0b) so every eduexplained.netlify.app URL 301s to the matching {{DOMAIN}} URL (Netlify does this for the primary custom domain).
3. Set LAUNCHED=true for the build (`LAUNCHED=true` in the environment the deploy runs in), promote wave 1 only (`worker/.venv/bin/python scripts/prelaunch/waves.py promote 1`), rebuild and deploy (`bash scripts/deploy_netlify.sh`).
4. Verify with curl:
   - `curl -s https://{{DOMAIN}}/robots.txt` allows crawling (search and retrieval crawlers allowed, AI training crawlers blocked, the sitemap URL listed);
   - a wave 1 page returns `<meta name="robots" content="index, follow">`; a page outside wave 1 returns `noindex, follow`;
   - `curl -s https://{{DOMAIN}}/sitemap.xml` lists only wave 1 pages;
   - `curl -sI https://eduexplained.netlify.app/cornell/housing/cornell-off-campus-housing-guide/` returns a 301 to {{DOMAIN}}.
5. Submit the sitemap in Google Search Console and Bing Webmaster Tools; enable IndexNow for Bing (scripts/v2/indexnow.py submits new and changed URLs after each deploy; the key file is config/indexnow.key).

## After the cutover
- Enter the Search Console numbers for wave 1 into config/wave-metrics.json after 3 to 4 weeks; `waves.py status` says whether wave 2 is allowed (50 percent indexed, impressions flat or rising, weekly audit error rate under 3 percent, no manual actions).
- Run `worker/.venv/bin/python scripts/prelaunch/audit_weekly.py` each week; its report is reports/audit-YYYY-MM-DD.md.
- Kill switch for a section: `worker/.venv/bin/python scripts/prelaunch/waves.py kill <section>`, then deploy.
