import type { APIRoute } from 'astro';
import { readFileSync, existsSync } from 'node:fs';
import path from 'node:path';
import yaml from 'js-yaml';
import { site } from '../../site.config';

/** The production robots.txt follows config/crawlers.yml (allow and disallow lists per user agent), like scripts/v2/render_site.py;
 *  a preview build stays Disallow: / for everyone. */
export const GET: APIRoute = () => {
  if (!site.launched) return new Response('User-agent: *\nDisallow: /\n', { headers: { 'Content-Type': 'text/plain; charset=utf-8' } });   // docs/v5 Phase 9b: LAUNCHED=true opens the site
  const file = path.resolve('..', 'config', 'crawlers.yml');
  const crawlers: any = existsSync(file) ? (yaml.load(readFileSync(file, 'utf8')) as any) : {};
  const lines = ['# EduExplained crawler policy; the lists live in config/crawlers.yml'];
  for (const ua of crawlers?.allow ?? []) lines.push('', `User-agent: ${ua}`, 'Allow: /');
  for (const ua of crawlers?.disallow ?? []) lines.push('', `User-agent: ${ua}`, 'Disallow: /');
  lines.push('', 'User-agent: *', 'Allow: /', 'Disallow: /search/', 'Disallow: /styleguide/', '', `Sitemap: ${site.url}/sitemap.xml`, '');
  return new Response(lines.join('\n'), { headers: { 'Content-Type': 'text/plain; charset=utf-8' } });
};
