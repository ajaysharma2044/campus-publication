import type { APIRoute } from 'astro';
import { site } from '../../site.config';
export const GET: APIRoute = () => {
  const body = site.production
    ? `User-agent: *\nAllow: /\nDisallow: /search/\nDisallow: /styleguide/\n\nSitemap: ${site.url}/sitemap.xml\n`
    : `User-agent: *\nDisallow: /\n`;
  return new Response(body, { headers: { 'Content-Type': 'text/plain; charset=utf-8' } });
};
