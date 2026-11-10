// Renders the brand mark (a Newsreader E in gold on navy) and the default Open Graph card to PNG with the repo's Playwright, and
// copies scripts/brand/favicon.svg (the same E as a glyph outline, so it needs no installed font) to public/.
import { createRequire } from 'node:module';
import path from 'node:path';
import { promises as fs } from 'node:fs';
import { serve } from './serve.mjs';
const require = createRequire(path.resolve('..', 'package.json'));
const { chromium } = require('playwright');
const { server, url } = await serve('.');
const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1300, height: 1300 }, deviceScaleFactor: 1 });
await page.goto(`${url}/scripts/brand/brand.html`, { waitUntil: 'networkidle' });
await page.evaluate(() => document.fonts.ready);
const og = await page.$('#og');
const sharp = (await import('sharp')).default;
// the icon PNGs come from the glyph-outline SVG (centered by its bounds), so icon and favicon are the same drawing
const svgPage = await browser.newPage({ viewport: { width: 600, height: 600 }, deviceScaleFactor: 1 });
await svgPage.setContent(`<!doctype html><body style="margin:0;background:#0E1B33"><img id="m" src="${url}/scripts/brand/favicon.svg" width="512" height="512" style="display:block"></body>`);
await svgPage.waitForFunction(() => document.getElementById('m').complete);
const big = await (await svgPage.$('#m')).screenshot({ type: 'png' });
for (const [name, size] of [['icon-512.png', 512], ['icon-192.png', 192], ['apple-touch-icon.png', 180], ['favicon-32.png', 32], ['social-avatar-400.png', 400]]) {
  await sharp(big).resize(size, size).png().toFile(path.join('public', name));
}
await og.screenshot({ type: 'png', path: path.join('public', 'og-default.png') });
await fs.copyFile(path.join('scripts', 'brand', 'favicon.svg'), path.join('public', 'favicon.svg'));
await fs.writeFile(path.join('public', 'site.webmanifest'), JSON.stringify({ name: 'EduExplained', short_name: 'EduExplained', icons: [{ src: '/icon-192.png', sizes: '192x192', type: 'image/png' }, { src: '/icon-512.png', sizes: '512x512', type: 'image/png' }], theme_color: '#0E1B33', background_color: '#FFFFFF', display: 'browser' }, null, 1));
await browser.close(); server.close();
console.log('brand assets written to public/');
