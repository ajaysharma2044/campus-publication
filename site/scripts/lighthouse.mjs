// One Lighthouse run (mobile, the default) per template into reports/lighthouse/, plus a summary table.
import { spawnSync } from 'node:child_process';
import path from 'node:path';
import { promises as fs } from 'node:fs';
import { serve } from './serve.mjs';
import { TEMPLATES } from './templates.mjs';
const out = path.resolve('..', 'reports', 'lighthouse');
await fs.mkdir(out, { recursive: true });
const { server, url } = await serve('dist');
const chrome = process.env.CHROME_PATH || '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const bin = path.resolve('node_modules', '.bin', 'lighthouse');
const rows = [];
for (const t of TEMPLATES) {
  const nn = String(t.n).padStart(2, '0');
  const base = path.join(out, `${nn}-${t.slug}`);
  const r = spawnSync(bin, [url + t.url, '--output=html', '--output=json', `--output-path=${base}`, '--quiet', '--chrome-flags=--headless=new --no-sandbox --disable-gpu', '--only-categories=performance,accessibility,best-practices,seo'],
    { env: { ...process.env, CHROME_PATH: chrome }, stdio: ['ignore', 'inherit', 'inherit'], timeout: 180000 });
  let scores = null;
  try {
    const j = JSON.parse(await fs.readFile(`${base}.report.json`, 'utf8'));
    const c = j.categories, a = j.audits;
    scores = { perf: Math.round(c.performance.score * 100), a11y: Math.round(c.accessibility.score * 100), bp: Math.round(c['best-practices'].score * 100), seo: Math.round(c.seo.score * 100), lcp: a['largest-contentful-paint'].displayValue, cls: a['cumulative-layout-shift'].displayValue };
  } catch (e) { console.error(`${t.slug}: no report (${e.message}; exit ${r.status})`); }
  rows.push({ ...t, scores, file: `${nn}-${t.slug}.report.html` });
  console.log(nn, t.slug, scores);
}
const lines = ['# Lighthouse reports', '', `Generated ${new Date().toISOString().slice(0, 10)} with Lighthouse (mobile emulation, simulated throttling) against a local static server serving site/dist. Chrome: ${chrome}.`, '',
  '| # | Template | Performance | Accessibility | Best practices | SEO | LCP | CLS | Report |', '|---|---|---|---|---|---|---|---|---|',
  ...rows.map((r) => `| ${r.n} | ${r.slug} | ${r.scores ? r.scores.perf : 'n/a'} | ${r.scores ? r.scores.a11y : 'n/a'} | ${r.scores ? r.scores.bp : 'n/a'} | ${r.scores ? r.scores.seo : 'n/a'} | ${r.scores ? r.scores.lcp : ''} | ${r.scores ? r.scores.cls : ''} | ${r.file} |`),
  '', 'SEO scores on a non-production build are capped by the noindex meta tag that every preview page carries (site.config `production: false`).'];
await fs.writeFile(path.join(out, 'README.md'), lines.join('\n') + '\n');
server.close();
