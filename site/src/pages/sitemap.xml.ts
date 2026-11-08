import type { APIRoute } from 'astro';
import { site } from '../../site.config';
import { getSite, schoolUrl, topicUrl, dataIndexUrl, authorUrl } from '../lib/model';
export const GET: APIRoute = async () => {
  const m = await getSite();
  const urls: { loc: string; lastmod?: string }[] = [{ loc: '/' }, { loc: '/guides/' }, { loc: '/authors/' }];
  for (const s of site.schools) { urls.push({ loc: schoolUrl(s) }, { loc: dataIndexUrl(s) }); for (const t of site.topics) urls.push({ loc: topicUrl(s, t) }); }
  for (const p of m.pages) urls.push({ loc: p.url, lastmod: p.updated });
  for (const a of site.authors) urls.push({ loc: authorUrl(a) });
  for (const t of ['about', 'editorial-standards', 'sources', 'corrections', 'contact', 'privacy', 'advertise']) urls.push({ loc: `/${t}/` });
  const body = site.production
    ? `<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n${urls.map((u) => `  <url><loc>${site.url}${u.loc}</loc>${u.lastmod ? `<lastmod>${u.lastmod}</lastmod>` : ''}</url>`).join('\n')}\n</urlset>\n`
    : `<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"></urlset>\n`;
  return new Response(body, { headers: { 'Content-Type': 'application/xml; charset=utf-8' } });
};
