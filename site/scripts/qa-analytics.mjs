/* Analytics instrumentation check against dist/ (build with SITE_ANALYTICS_PREVIEW=1; the id comes from config/monetization.yml,
   GTM-W9MM7GZL today, or GOOGLE_TAG_ID / GA4_MEASUREMENT_ID in the environment).
   Serves dist/, blocks Google hosts, reads each page's own dataLayer, interacts like a reader and asserts the events
   fire with no personal data. Usage from site/: node scripts/qa-analytics.mjs  (Playwright comes from the repo root). */
import { createRequire } from 'node:module';
import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';
const require = createRequire(path.resolve('../package.json'));
const { chromium } = require('playwright');
const dist = path.resolve(process.env.DIST || 'dist');
const MIME = { '.html': 'text/html', '.css': 'text/css', '.js': 'text/javascript', '.woff2': 'font/woff2', '.json': 'application/json', '.svg': 'image/svg+xml', '.png': 'image/png', '.avif': 'image/avif', '.webp': 'image/webp' };
const srv = http.createServer((req, res) => { let p = decodeURIComponent(req.url.split('?')[0]); if (p.endsWith('/')) p += 'index.html'; let f = path.join(dist, p);
  if (!fs.existsSync(f) && fs.existsSync(f + '.html')) f += '.html'; if (!fs.existsSync(f) || fs.statSync(f).isDirectory()) { res.writeHead(404); res.end(); return; }
  res.writeHead(200, { 'content-type': MIME[path.extname(f)] || 'application/octet-stream' }); fs.createReadStream(f).pipe(res); });
const PII = /@|\d{3}[-.\s]\d{3}[-.\s]\d{4}|test person|secret query/i;
const pick = (dir, re) => { const out = []; (function walk(d) { for (const e of fs.readdirSync(d, { withFileTypes: true })) { const p = path.join(d, e.name); if (e.isDirectory()) walk(p); else if (e.name === 'index.html' && re.test(p)) out.push('/' + path.relative(dist, path.dirname(p)).replace(/\\/g, '/') + '/'); } })(dir); return out; };
async function drain(page, events) { const items = await page.evaluate(() => (window.dataLayer || []).map(a => { if (a && typeof a === 'object' && !Array.isArray(a) && !(a.length >= 0 && a[0])) { if (a.event && a.event !== 'gtm.js') { const { event, ...rest } = a; return { name: event, params: rest }; } return null; } const arr = Array.from(a); if (arr[0] === 'event') return { name: arr[1], params: arr[2] || {} }; if (arr[0] === 'consent') return { name: '__consent_' + arr[1], params: arr[2] || {} }; return null; }).filter(Boolean)); events.push(...items); await page.evaluate(() => { if (window.dataLayer) window.dataLayer.length = 0; }); }
(async () => {
  await new Promise(r => srv.listen(0, '127.0.0.1', r)); const port = srv.address().port; const base = `http://127.0.0.1:${port}`;
  const article = pick(dist, /cornell\/(housing|money|transfer)\/[^/]+\/index\.html$/).find(u => !/\/(housing|money|transfer)\/$/.test(u));
  const tool = pick(dist, /\/tools\/[^/]+\/index\.html$/)[0];
  const browser = await chromium.launch(); const ctx = await browser.newContext({ viewport: { width: 1280, height: 800 } });
  let google = 0; await ctx.route(/googletagmanager\.com|google-analytics\.com|googlesyndication\.com|doubleclick\.net/, r => { google++; r.abort(); });
  const events = []; const page = await ctx.newPage();
  page.on('pageerror', e => console.log('pageerror', e.message));
  await page.goto(base + article, { waitUntil: 'networkidle' });
  console.log('article', article, 'dataLayer?', await page.evaluate(() => Array.isArray(window.dataLayer)));
  const loaders = await page.evaluate(() => document.querySelectorAll('script[src*="googletagmanager"]').length);
  const body = await page.evaluate(() => ({ ...document.body.dataset }));
  await page.waitForSelector('[data-consent]', { timeout: 5000 }); await drain(page, events); const before = events.slice();
  await page.click('[data-consent-choice="analytics"]'); await page.waitForTimeout(200);
  await page.mouse.wheel(0, 2500); await page.waitForTimeout(500); await page.mouse.wheel(0, 40000); await page.waitForTimeout(600);
  await page.evaluate(() => { const a = document.querySelector('.sources__list a'); if (a) { a.addEventListener('click', e => e.preventDefault()); a.click(); } });
  await page.evaluate(() => { const a = document.querySelector('.toc a'); if (a) a.click(); });
  await page.evaluate(() => { const f = document.querySelector('.feedback__form'); if (f) { f.addEventListener('submit', e => e.preventDefault()); f.querySelector('[name=need]').value = 'test person wants secret query'; f.requestSubmit(f.querySelector('button[value=no]')); } });
  await page.waitForTimeout(300); await drain(page, events);
  if (tool) { await page.goto(base + tool, { waitUntil: 'networkidle' }); const inp = await page.$('.tool-embed input[type=number], .tool-embed input[type=text], .tool-embed select'); if (inp) { await inp.fill('7').catch(() => {}); await inp.dispatchEvent('input'); await inp.dispatchEvent('change'); } await page.waitForTimeout(400); await drain(page, events); console.log('tool events', events.filter(e => /^tool_/.test(e.name)).map(e => e.name)); }
  await page.goto(base + '/search/', { waitUntil: 'networkidle' });
  await page.evaluate(() => { const f = document.querySelector('form.search'); if (f) { f.addEventListener('submit', e => e.preventDefault()); f.querySelector('input').value = 'meal plan test@example.com 555-123-4567'; f.requestSubmit(); } });
  await page.waitForTimeout(200); await drain(page, events);
  await page.goto(base + '/404.html', { waitUntil: 'networkidle' }); await page.waitForTimeout(200); await drain(page, events);
  const consentCookie = (await ctx.cookies()).find(c => c.name === 'ee_consent');
  await browser.close(); srv.close();
  const names = events.map(e => e.name); const has = n => names.includes(n);
  const cd = before.find(e => e.name === '__consent_default'); const cu = events.filter(e => e.name === '__consent_update').pop();
  const pii = events.filter(e => PII.test(JSON.stringify(e.params)));
  const report = { article, tool, tag_kind: body.tagKind, loaders_on_page: loaders, google_requests_blocked: google, body_data: body, consent_default_denied: !!(cd && cd.params.analytics_storage === 'denied'),
    consent_granted_after_choice: !!(cu && cu.params.analytics_storage === 'granted'), consent_cookie: consentCookie && consentCookie.value, page_views: names.filter(n => n === 'page_view').length,
    distinct_events: [...new Set(names.filter(n => !n.startsWith('__')))].sort(), pii_leaks: pii.length, sample_feedback: events.find(e => e.name === 'feedback_submit'), sample_search: events.find(e => e.name === 'search_submit') };
  console.log(JSON.stringify(report, null, 2));
  const ok = loaders === 1 && report.consent_default_denied && report.consent_granted_after_choice && report.page_views >= 3 && has('scroll_depth') && has('source_click') && has('feedback_submit') && has('search_submit') && has('error_404') && has('consent_choice') && pii.length === 0 && (!tool || has('tool_start'));
  process.exit(ok ? 0 : 1);
})();
