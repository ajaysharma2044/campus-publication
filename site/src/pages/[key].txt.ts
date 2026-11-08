import type { APIRoute } from 'astro';
import { readFileSync, existsSync } from 'node:fs';
import path from 'node:path';
import yaml from 'js-yaml';
import { site } from '../../site.config';

/** Serves the IndexNow key as /<key>.txt on production builds, as scripts/v2/render_site.py does. */
function key(): string {
  const cfg = path.resolve('..', 'config', 'crawlers.yml');
  if (!site.production || !existsSync(cfg)) return '';
  const crawlers: any = yaml.load(readFileSync(cfg, 'utf8'));
  const kf = path.resolve('..', String(crawlers?.indexnow?.key_file ?? ''));
  if (!crawlers?.indexnow?.key_file || !existsSync(kf)) return '';
  const k = readFileSync(kf, 'utf8').trim();
  return /^[0-9a-f]{32}$/i.test(k) ? k : '';
}
export function getStaticPaths() { const k = key(); return k ? [{ params: { key: k } }] : []; }
export const GET: APIRoute = () => new Response(key() + '\n', { headers: { 'Content-Type': 'text/plain; charset=utf-8' } });
