import type { APIRoute } from 'astro';
import { site } from '../../site.config';
import { getSite, schoolUrl, topicUrl, dataIndexUrl, authorUrl } from '../lib/model';
export const GET: APIRoute = async () => {
  const m = await getSite();
  // docs/v5 Phase 9b: the sitemap lists every page (Ajay, 2026-11-12: everything indexable), and only once LAUNCHED=true
  const urls: { loc: string; lastmod?: string }[] = [];
  for (const p of m.pages) urls.push({ loc: p.url, lastmod: p.updated });
  for (const t of m.tools) urls.push({ loc: t.url, lastmod: t.updated });
  for (const d of m.datasets) urls.push({ loc: d.url, lastmod: d.updated });
  for (const s of m.starts) urls.push({ loc: s.url, ...(s.updated ? { lastmod: s.updated } : {}) }); urls.unshift({ loc: '/' }); for (const sc of m.schools) { urls.push({ loc: schoolUrl(sc) }, { loc: dataIndexUrl(sc) }); for (const t of m.topics) urls.push({ loc: topicUrl(sc, t) }); }   // the homepage, school hubs, data indexes and topic hubs are indexable once launched (Base.astro)
  const body = site.launched && urls.length
    ? `<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n${urls.map((u) => `  <url><loc>${site.url}${u.loc}</loc>${u.lastmod ? `<lastmod>${u.lastmod}</lastmod>` : ''}</url>`).join('\n')}\n</urlset>\n`
    : `<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"></urlset>\n`;
  return new Response(body, { headers: { 'Content-Type': 'application/xml; charset=utf-8' } });
};
