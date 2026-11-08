// Full-page screenshots of every template at 375px and 1280px into reports/templates/. Uses the repo's Playwright.
import { createRequire } from 'node:module';
import path from 'node:path';
import { promises as fs } from 'node:fs';
import { serve } from './serve.mjs';
import { TEMPLATES } from './templates.mjs';
const require = createRequire(path.resolve('..', 'package.json'));
const { chromium } = require('playwright');
const out = path.resolve('..', 'reports', 'templates');
await fs.mkdir(out, { recursive: true });
const { server, url } = await serve('dist');
const browser = await chromium.launch();
const lines = ['# Template screenshots', '', `Generated ${new Date().toISOString().slice(0, 10)} from the Astro build in site/dist at 375px and 1280px (full page).`, '',
  'design/reference-article.html is not in the repository, so the side-by-side of the pillar template against it could not be produced; the pillar screenshots stand alone until the owner supplies the file.', '', '| # | Template | Page | 375 | 1280 |', '|---|---|---|---|---|'];
for (const t of TEMPLATES) {
  const nn = String(t.n).padStart(2, '0');
  const files = {};
  for (const w of [375, 1280]) {
    const page = await browser.newPage({ viewport: { width: w, height: w < 768 ? 812 : 900 }, deviceScaleFactor: 1 });
    await page.goto(url + t.url, { waitUntil: 'networkidle' });
    // lazy images never enter the viewport in a full-page capture: switch them to eager and give them up to 5s to arrive
    await page.evaluate(async () => {
      document.querySelectorAll('img[loading="lazy"]').forEach((i) => { i.loading = 'eager'; });
      const pending = [...document.images].filter((i) => !i.complete).map((i) => new Promise((r) => { i.addEventListener('load', r, { once: true }); i.addEventListener('error', r, { once: true }); }));
      await Promise.race([Promise.all(pending), new Promise((r) => setTimeout(r, 5000))]);
    });
    await page.waitForTimeout(300);
    const file = `${nn}-${t.slug}-${w}.png`;
    await page.screenshot({ path: path.join(out, file), fullPage: true });
    files[w] = file;
    await page.close();
  }
  lines.push(`| ${t.n} | ${t.slug} | ${t.url} | ${files[375]} | ${files[1280]} |`);
  console.log(`${nn} ${t.slug}`);
}
await fs.writeFile(path.join(out, 'README.md'), lines.join('\n') + '\n');
await browser.close();
server.close();
