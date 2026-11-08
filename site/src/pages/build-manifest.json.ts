/* Read by scripts/check-build.mjs after the build (which deletes it): every page with its school, topic and type. */
import type { APIRoute } from 'astro';
import { getSite, topicUrl } from '../lib/model';
export const GET: APIRoute = async () => {
  const m = await getSite();
  const pages = m.pages.map((p) => ({ url: p.url, oldUrl: p.oldUrl, title: p.title, school: p.school.slug, topic: p.topic.id, pageType: p.pageType, crossSchool: p.crossSchool, hub: p.crossSchool ? '/guides/' : p.pageType === 'data' ? `/${p.school.slug}/data/` : topicUrl(p.school, p.topic) }));
  return new Response(JSON.stringify({ pages, samples: m.samples.map((p) => p.url) }), { headers: { 'Content-Type': 'application/json' } });
};
