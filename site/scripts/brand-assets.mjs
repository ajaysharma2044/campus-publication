// Renders the brand assets with the repo's Playwright and sharp: the PNG icons (favicon-32, icon-192, icon-512, apple-touch-icon,
// the social avatar) from scripts/brand/favicon.svg (the wordmark's E in white on navy, an outline, so no installed font is needed)
// and the default Open Graph card from scripts/brand/brand.html with the wordmark outline (scripts/brand/wordmark.svg, the owner's
// artwork traced; scripts/brand/README.md) injected in place of its <!--wordmark--> comment. Copies favicon.svg and writes the manifest.
import { createRequire } from 'node:module';
import path from 'node:path';
import { promises as fs } from 'node:fs';
import { serve } from './serve.mjs';
const require = createRequire(path.resolve('..', 'package.json'));
const { chromium } = require('playwright');
const { server, url } = await serve('.');
const browser = await chromium.launch();
const wordmark = (await fs.readFile(path.join('scripts', 'brand', 'wordmark.svg'), 'utf8')).replace('<svg ', '<svg class="logo" ');
const card = (await fs.readFile(path.join('scripts', 'brand', 'brand.html'), 'utf8')).replace('<!--wordmark-->', wordmark);
const page = await browser.newPage({ viewport: { width: 1300, height: 700 }, deviceScaleFactor: 1 });
await page.route('**/scripts/brand/brand.html', (route) => route.fulfill({ body: card, contentType: 'text/html' }));
await page.goto(`${url}/scripts/brand/brand.html`, { waitUntil: 'networkidle' });
await page.evaluate(() => document.fonts.ready);
const og = await page.$('#og');
const sharp = (await import('sharp')).default;
// the icon PNGs come from the favicon SVG, so icon and favicon are the same drawing
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
