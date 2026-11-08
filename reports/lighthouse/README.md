# Lighthouse reports

Generated 2026-11-08 with Lighthouse (mobile emulation, simulated throttling) against a local static server serving site/dist. Chrome: /Users/ajaysharma/Library/Caches/ms-playwright/chromium-1248/chrome-mac-arm64/Google Chrome for Testing.app/Contents/MacOS/Google Chrome for Testing.

| # | Template | Performance | Accessibility | Best practices | SEO | LCP | CLS | Report |
|---|---|---|---|---|---|---|---|---|
| 1 | homepage | 98 | 100 | 100 | 100 | 2.4 s | 0 | 01-homepage.report.html |
| 2 | school-hub | 100 | 100 | 100 | 100 | 0.8 s | 0 | 02-school-hub.report.html |
| 3 | topic-hub | 97 | 100 | 100 | 100 | 2.6 s | 0 | 03-topic-hub.report.html |
| 4 | audience-hub | 100 | 100 | 100 | 100 | 0.8 s | 0 | 04-audience-hub.report.html |
| 5 | pillar | 97 | 100 | 100 | 100 | 2.6 s | 0 | 05-pillar.report.html |
| 6 | answer | 100 | 100 | 100 | 100 | 0.8 s | 0 | 06-answer.report.html |
| 7 | place | 97 | 100 | 100 | 69 | 2.6 s | 0 | 07-place.report.html |
| 8 | data | 100 | 100 | 100 | 66 | 0.8 s | 0 | 08-data.report.html |
| 9 | comparison | 100 | 100 | 100 | 66 | 0.8 s | 0 | 09-comparison.report.html |
| 10 | cross-school-guide | 100 | 100 | 100 | 66 | 0.8 s | 0 | 10-cross-school-guide.report.html |
| 11 | author | 100 | 100 | 100 | 100 | 0.8 s | 0 | 11-author.report.html |
| 12 | trust | 100 | 100 | 100 | 100 | 0.8 s | 0 | 12-trust.report.html |
| 13 | search | 99 | 100 | 100 | 66 | 2.3 s | 0 | 13-search.report.html |
| 14 | 404 | 100 | 100 | 100 | 66 | 0.8 s | 0 | 14-404.report.html |
| 15 | styleguide | 100 | 100 | 100 | 69 | 0.8 s | 0 | 15-styleguide.report.html |
| 16 | pillar-sample | 97 | 100 | 100 | 69 | 2.6 s | 0 | 16-pillar-sample.report.html |
| 17 | tool | 100 | 95 | 100 | 100 | 0.8 s | 0 | 17-tool.report.html |
| 18 | dataset | 100 | 100 | 100 | 100 | 0.8 s | 0 | 18-dataset.report.html |
| 19 | start | 100 | 100 | 100 | 100 | 0.8 s | 0 | 19-start.report.html |

Rows 1 to 16 measure a local production-flag build (indexable, Brotli, long cache headers) served by site/scripts/serve.mjs. Rows 7 to 10, 15 and 16 are the labeled sample pages under /styleguide/ and row 13 is the search page: those are noindex by design, which caps their SEO score; the same templates on real, indexable pages (rows 5 and 6) score 100. Row 14 measures dist/404.html served as a file, because Lighthouse refuses to audit a page delivered with a 404 status; the real 404 status was verified separately with curl.

## Deployed preview (https://footnote-daily.netlify.app)

The live Netlify deploy is a noindex preview, so its SEO score is capped; performance here includes the real CDN and this network.

| # | Page | Performance | Accessibility | Best practices | SEO | LCP | CLS | Report |
|---|---|---|---|---|---|---|---|---|
| L1 | live-homepage | 100 | 100 | 100 | 66 | 1.8 s | 0 | L1-live-homepage.report.html |
| L2 | live-pillar | 98 | 100 | 100 | 69 | 2.4 s | 0 | L2-live-pillar.report.html |
| L3 | live-topic-hub | 98 | 100 | 100 | 66 | 2.3 s | 0 | L3-live-topic-hub.report.html |
