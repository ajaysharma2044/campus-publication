// Build-time checks on dist/ (runs after astro build; a failure exits 1 and fails `npm run build`):
//  - every page: exactly one H1, no inline style attributes, title, description, canonical, og:image, JSON-LD, a main landmark
//  - every internal link resolves to a built file
//  - no orphans: every page links to at least 3 other pages from its main content (breadcrumbs and the shell excluded)
//  - every child page of a topic appears on its topic hub (and data pages on the data index, cross-school guides on /guides/)
//  - writes dist/_redirects: the Jinja site's URLs (/{topic}/{slug}/, /{topic}/, /editorial-policy/) 301 to the new ones
//  - page_type, required fields and place fact fields are checked earlier, in src/lib/model.ts, where a throw fails the build
import { promises as fs } from 'node:fs';
import path from 'node:path';
const dist = path.resolve('dist');
const failures = [];
const warn = [];
async function walk(d) { const out = []; for (const e of await fs.readdir(d, { withFileTypes: true })) { const p = path.join(d, e.name); if (e.isDirectory()) out.push(...await walk(p)); else if (e.name.endsWith('.html')) out.push(p); } return out; }
const files = await walk(dist);
const exists = new Set();
for (const f of files) exists.add('/' + path.relative(dist, f).replace(/index\.html$/, '').replace(/\\/g, '/'));
const manifestPath = path.join(dist, 'build-manifest.json', 'index.html');
let manifest = { pages: [], samples: [] };
try { manifest = JSON.parse(await fs.readFile(path.join(dist, 'build-manifest.json'), 'utf8')); await fs.rm(path.join(dist, 'build-manifest.json')); } catch { try { manifest = JSON.parse(await fs.readFile(manifestPath, 'utf8')); await fs.rm(path.dirname(manifestPath), { recursive: true }); } catch { warn.push('no build-manifest.json; hub completeness not checked'); } }
const IGNORE_LINKS = ['/newsletter/subscribe/', '/pagefind/'];
const fileExists = async (p) => { try { await fs.access(path.join(dist, p)); return true; } catch { return false; } };
const hubHtml = new Map();
for (const f of files) {
  const rel = '/' + path.relative(dist, f).replace(/\\/g, '/');
  const url = rel.replace(/index\.html$/, '');
  const html = await fs.readFile(f, 'utf8');
  const own = html.replace(/<section class="tool-embed[\s\S]*?<\/section>/g, '');   // tool fragments are the pipeline's HTML (scripts/v2/lint.py checks them)
  const h1s = (own.match(/<h1[\s>]/g) || []).length;
  if (h1s !== 1) failures.push(`${url}: ${h1s} H1 elements`);
  if (/\sstyle="/.test(own)) failures.push(`${url}: inline style attribute`);
  for (const [re, what] of [[/<title>[^<]+<\/title>/, 'title'], [/<meta name="description" content="[^"]+"/, 'meta description'], [/<link rel="canonical"/, 'canonical'], [/<meta property="og:image"/, 'og:image'], [/application\/ld\+json/, 'JSON-LD'], [/<main\b/, 'main landmark'], [/class="skip"/, 'skip link']]) if (!re.test(html)) failures.push(`${url}: missing ${what}`);
  const mainHtml = (html.match(/<main[\s\S]*?<\/main>/) || [''])[0].replace(/<nav class="crumbs"[\s\S]*?<\/nav>/, '');
  const links = new Set();
  for (const m of mainHtml.matchAll(/href="(\/[^"#?]*)/g)) { const h = m[1]; if (h !== url && !IGNORE_LINKS.some((i) => h.startsWith(i)) && !/\.(csv|png|svg|webp|avif|txt|xml|json|js)$/.test(h)) links.add(h); }
  if (links.size < 3 && !url.startsWith('/styleguide/') ) failures.push(`${url}: orphan risk, only ${links.size} outbound internal links in main content`);
  for (const m of html.matchAll(/href="(\/[^"#?]*)/g)) {
    const h = m[1];
    if (IGNORE_LINKS.some((i) => h.startsWith(i))) continue;
    const ok = exists.has(h) || exists.has(h.replace(/\/?$/, '/')) || (await fileExists(h));
    if (!ok) failures.push(`${url}: broken internal link ${h}`);
  }
  if (manifest.pages.some((p) => p.hub === url)) hubHtml.set(url, html);
}
for (const p of manifest.pages) {
  const hub = hubHtml.get(p.hub);
  if (!hub) { failures.push(`${p.url}: its hub ${p.hub} was not built`); continue; }
  if (!hub.includes(`href="${p.url}"`)) failures.push(`${p.hub}: does not list its child page ${p.url}`);
}
// Netlify redirects from the Jinja renderer's URLs to the Astro ones
const redirects = [];
const seen = new Set();
for (const p of manifest.pages) { if (p.oldUrl && p.oldUrl !== p.url && !seen.has(p.oldUrl)) { seen.add(p.oldUrl); redirects.push(`${p.oldUrl} ${p.url} 301`); } }
// redirect_from: earlier URLs of moved or merged pages, tools and datasets (docs/v5 Phases 3 to 5)
for (const p of [...manifest.pages, ...(manifest.tools ?? []), ...(manifest.datasets ?? [])]) for (const r of (p.redirectFrom ?? [])) { if (r !== p.url && !seen.has(r)) { seen.add(r); redirects.push(`${r} ${p.url} 301`); } }
// no internal link may hit a redirect: every href on every page is checked against the redirect sources
const redirectSources = new Set(redirects.map((l) => l.split(' ')[0]));
for (const f of files) { const url = '/' + path.relative(dist, f).replace(/\\/g, '/').replace(/index\.html$/, ''); const html = await fs.readFile(f, 'utf8'); for (const m of html.matchAll(/href="(\/[^"#?]*)/g)) { if (redirectSources.has(m[1])) failures.push(`${url}: internal link hits a redirect: ${m[1]}`); } }
for (const t of new Set(manifest.pages.map((p) => p.topic))) { const from = `/${t}/`; if (!exists.has(from) && !seen.has(from)) { seen.add(from); redirects.push(`${from} /${manifest.pages.find((p) => p.topic === t).school}/${t}/ 301`); } }
redirects.push('/editorial-policy/ /editorial-standards/ 301');
redirects.push('/authors/footnote-daily-editors/ /authors/eduexplained-editors/ 301');   // the editors' page before the 2026-11-10 rename
await fs.writeFile(path.join(dist, '_redirects'), redirects.join('\n') + '\n');
console.log(`check-build: ${files.length} pages, ${manifest.pages.length} content pages checked against their hubs, ${redirects.length} redirects written`);
for (const w of warn) console.log('warning:', w);
if (failures.length) { console.error(`check-build: ${failures.length} failure(s)`); for (const f of failures) console.error(' -', f); process.exit(1); }
console.log('check-build: all checks passed');
