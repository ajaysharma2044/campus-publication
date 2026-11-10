// Renders the brand mark (gold superscript 1 on navy) and the default Open Graph card to PNG with the repo's Playwright.
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
const mark = await page.$('#mark'), og = await page.$('#og');
const sharp = (await import('sharp')).default;
const big = await mark.screenshot({ type: 'png' });
for (const [name, size] of [['icon-512.png', 512], ['icon-192.png', 192], ['apple-touch-icon.png', 180], ['favicon-32.png', 32], ['social-avatar-400.png', 400]]) {
  await sharp(big).resize(size, size).png().toFile(path.join('public', name));
}
await og.screenshot({ type: 'png', path: path.join('public', 'og-default.png') });
await fs.writeFile(path.join('public', 'favicon.svg'), `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" fill="#0E1B33"/><text x="32" y="50" text-anchor="middle" font-family="Newsreader, Georgia, serif" font-weight="600" font-size="52" fill="#D6A738">1</text></svg>\n`);
await fs.writeFile(path.join('public', 'site.webmanifest'), JSON.stringify({ name: 'EduExplained', short_name: 'EduExplained', icons: [{ src: '/icon-192.png', sizes: '192x192', type: 'image/png' }, { src: '/icon-512.png', sizes: '512x512', type: 'image/png' }], theme_color: '#0E1B33', background_color: '#FFFFFF', display: 'browser' }, null, 1));
await browser.close(); server.close();
console.log('brand assets written to public/');
