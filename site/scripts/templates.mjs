// The 14 templates and the page that represents each one in screenshots and Lighthouse runs.
export const TEMPLATES = [
  { n: 1, slug: 'homepage', url: '/' },
  { n: 2, slug: 'school-hub', url: '/cornell/' },
  { n: 3, slug: 'topic-hub', url: '/cornell/money/' },
  { n: 4, slug: 'audience-hub', url: '/cornell/parents/' },
  { n: 5, slug: 'pillar', url: '/cornell/housing/cornell-transfer-housing/' },
  { n: 6, slug: 'answer', url: '/cornell/alumni/cornell-fitness-centers-alumni-membership/' },
  { n: 7, slug: 'place', url: '/styleguide/place/' },
  { n: 8, slug: 'data', url: '/styleguide/data/' },
  { n: 9, slug: 'comparison', url: '/styleguide/comparison/' },
  { n: 10, slug: 'cross-school-guide', url: '/styleguide/guide/' },
  { n: 11, slug: 'author', url: '/authors/eduexplained-editors/' },
  { n: 12, slug: 'trust', url: '/editorial-standards/' },
  { n: 13, slug: 'search', url: '/search/?q=meal+plan' },
  { n: 14, slug: '404', url: '/404.html' },
  { n: 15, slug: 'styleguide', url: '/styleguide/' },
  { n: 16, slug: 'pillar-sample', url: '/styleguide/pillar/' },
  { n: 17, slug: 'tool', url: '/tools/', first: true },        // resolved to the first listed tool, dataset or start page when one exists
  { n: 18, slug: 'dataset', url: '/datasets/', first: true },
  { n: 19, slug: 'start', url: '/start/', first: true },
];

// The pipeline kinds point at their index page; when the built index lists entries, measure the first entry instead.
import { promises as fs } from 'node:fs';
import path from 'node:path';
export async function resolveTemplates(distDir) {
  const out = [];
  for (const t of TEMPLATES) {
    if (!t.first) { out.push(t); continue; }
    try {
      const html = await fs.readFile(path.join(distDir, t.url, 'index.html'), 'utf8');
      const m = html.match(/class="glist__title"><a href="([^"]+)"/);
      out.push(m ? { ...t, url: m[1] } : t);
    } catch { out.push(t); }
  }
  return out;
}
