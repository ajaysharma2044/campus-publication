/* Screenshot QA (SPEC §31): renders every preview page at 360/390/768/1280/1440, checks horizontal
   overflow, missing fonts, focus visibility and body font size, and writes PNGs + a JSON report.
   Usage: node scripts/qa_screens.js [previewDir] [outDir]   (serves previewDir on a local port) */
const { chromium } = require('playwright');
const http = require('http');
const fs = require('fs');
const path = require('path');

const previewDir = path.resolve(process.argv[2] || 'build/preview');
const outDir = path.resolve(process.argv[3] || 'build/qa');
const WIDTHS = [360, 390, 768, 1280, 1440];
const MIME = { '.html': 'text/html', '.css': 'text/css', '.js': 'text/javascript', '.woff2': 'font/woff2', '.png': 'image/png', '.txt': 'text/plain' };

function serve(dir) {
  return http.createServer((req, res) => {
    let p = decodeURIComponent(req.url.split('?')[0]);
    if (p.endsWith('/')) p += 'index.html';
    const f = path.join(dir, p);
    if (!f.startsWith(dir) || !fs.existsSync(f) || fs.statSync(f).isDirectory()) { res.writeHead(404); res.end('404'); return; }
    res.writeHead(200, { 'content-type': MIME[path.extname(f)] || 'application/octet-stream' });
    fs.createReadStream(f).pipe(res);
  });
}

function listPages(dir, base = '') {
  const out = [];
  for (const e of fs.readdirSync(path.join(dir, base), { withFileTypes: true })) {
    const rel = path.join(base, e.name);
    if (e.isDirectory()) { if (e.name !== 'static') out.push(...listPages(dir, rel)); }
    else if (e.name.endsWith('.html')) out.push('/' + rel.replace(/\\/g, '/'));
  }
  return out;
}

(async () => {
  fs.mkdirSync(outDir, { recursive: true });
  const server = serve(previewDir);
  await new Promise(r => server.listen(0, '127.0.0.1', r));
  const port = server.address().port;
  const browser = await chromium.launch();
  const report = [];
  for (const url of listPages(previewDir)) {
    for (const w of WIDTHS) {
      const page = await browser.newPage({ viewport: { width: w, height: 900 }, deviceScaleFactor: 1 });
      await page.goto(`http://127.0.0.1:${port}${url}`, { waitUntil: 'networkidle' });
      const metrics = await page.evaluate(() => {
        const doc = document.documentElement;
        const overflow = doc.scrollWidth > doc.clientWidth + 1;
        const wide = [];
        document.querySelectorAll('body *').forEach(el => { const r = el.getBoundingClientRect(); if (r.right > doc.clientWidth + 1 && r.width > 0 && getComputedStyle(el).position !== 'fixed') wide.push(el.tagName.toLowerCase() + (el.className ? '.' + String(el.className).split(' ')[0] : '')); });
        const body = getComputedStyle(document.body);
        const h1 = document.querySelector('h1,.masthead__name');
        const fontsLoaded = document.fonts ? Array.from(document.fonts).filter(f => f.status === 'loaded').map(f => f.family) : [];
        const ads = document.querySelectorAll('.ad-slot, script[src*="adsbygoogle"]').length;
        const analytics = document.querySelectorAll('script[src*="gtag"], script[src*="analytics"]').length;
        const skip = !!document.querySelector('.skip-link');
        const main = !!document.querySelector('main#main');
        const h1count = document.querySelectorAll('h1').length;
        const unlabeled = Array.from(document.querySelectorAll('input,select')).filter(i => !i.labels || i.labels.length === 0).filter(i => !i.getAttribute('aria-label') && i.type !== 'hidden').length;
        return { overflow, wide: Array.from(new Set(wide)).slice(0, 8), bodyFontPx: parseFloat(body.fontSize), lineHeight: body.lineHeight, h1Px: h1 ? parseFloat(getComputedStyle(h1).fontSize) : null,
                 fontsLoaded: Array.from(new Set(fontsLoaded)), adElements: ads, analyticsScripts: analytics, skipLink: skip, main, h1count, unlabeledInputs: unlabeled, title: document.title };
      });
      const file = path.join(outDir, url.replace(/\//g, '_').replace(/^_/, '').replace(/\.html$/, '') + `__${w}.png`);
      await page.screenshot({ path: file, fullPage: true });
      // focus visibility: tab once and check outline on active element
      await page.keyboard.press('Tab');
      const focus = await page.evaluate(() => { const a = document.activeElement; const s = getComputedStyle(a); return { tag: a.tagName, outline: s.outlineStyle !== 'none' && parseFloat(s.outlineWidth) > 0, text: (a.textContent || '').trim().slice(0, 30) }; });
      report.push({ url, width: w, file: path.relative(process.cwd(), file), ...metrics, firstFocus: focus });
      await page.close();
    }
  }
  await browser.close();
  server.close();
  fs.writeFileSync(path.join(outDir, 'report.json'), JSON.stringify(report, null, 2));
  const problems = report.filter(r => r.overflow || r.adElements || r.analyticsScripts || !r.skipLink || !r.main || r.h1count !== 1 || r.unlabeledInputs || !r.firstFocus.outline);
  console.log(`pages×widths: ${report.length}; problems: ${problems.length}`);
  for (const p of problems) console.log(` - ${p.url} @${p.width}: overflow=${p.overflow} wide=${JSON.stringify(p.wide)} ads=${p.adElements} analytics=${p.analyticsScripts} skip=${p.skipLink} main=${p.main} h1=${p.h1count} unlabeled=${p.unlabeledInputs} focusOutline=${p.firstFocus.outline}`);
  console.log(`fonts loaded on home@1280: ${JSON.stringify((report.find(r => r.url === '/index.html' && r.width === 1280) || {}).fontsLoaded)}`);
  process.exit(problems.length ? 1 : 0);
})();
