/* Read by scripts/check-build.mjs after the build (which deletes it): every page with its school, topic and type. */
import type { APIRoute } from 'astro';
import { getSite, topicUrl } from '../lib/model';
export const GET: APIRoute = async () => {
  const m = await getSite();
  const pages = m.pages.map((p) => ({ url: p.url, oldUrl: p.oldUrl, title: p.title, school: p.school.slug, topic: p.topic.id, pageType: p.pageType, crossSchool: p.crossSchool, hub: p.crossSchool ? '/guides/' : p.pageType === 'data' ? `/${p.school.slug}/data/` : topicUrl(p.school, p.topic) }));
  const kinds = [
    ...m.tools.map((t) => ({ url: t.url, title: t.title, school: t.school.slug, topic: t.topic.id, pageType: 'tool', crossSchool: false, hub: topicUrl(t.school, t.topic) })),
    ...m.datasets.map((d) => ({ url: d.url, title: d.title, school: d.school.slug, topic: d.topic.id, pageType: 'dataset', crossSchool: false, hub: topicUrl(d.school, d.topic) })),
    ...m.starts.flatMap((s) => s.topics.map((t) => ({ url: s.url, title: s.title, school: s.school.slug, topic: t.id, pageType: 'start', crossSchool: false, hub: topicUrl(s.school, t) }))),
  ];
  return new Response(JSON.stringify({ pages: [...pages, ...kinds], samples: m.samples.map((p) => p.url) }), { headers: { 'Content-Type': 'application/json' } });
};
