import type { APIRoute } from 'astro';
import { site } from '../../site.config';

/** /ads.txt as scripts/v2/render_site.py writes it: Google's authorized-seller line for the AdSense publisher id in
 *  site.config.ts (the "ca-" prefix dropped, as AdSense's own ads.txt line has it); a comment line when no id is set. */
export const GET: APIRoute = () => {
  const client = site.ads.adsenseClient.trim();
  const body = client ? `google.com, ${client.replace(/^ca-/, '')}, DIRECT, f08c47fec0942fa0\n` : '# no ad network configured (site/site.config.ts ads)\n';
  return new Response(body, { headers: { 'Content-Type': 'text/plain; charset=utf-8' } });
};
