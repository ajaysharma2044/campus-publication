/* The site model: every article mapped to a template (page_type), a URL, a school, a topic and a rendered body, plus the
   groupings the hubs need. Built once per build and cached. Throws (failing the build) on an unknown page type, a missing
   required field, an unknown school or topic, or a place/data/comparison page without its block. */
import { getCollection, type CollectionEntry } from 'astro:content';
import { promises as fs } from 'node:fs';
import path from 'node:path';
import { site, type School, type Topic, type Author, type Audience } from '../../site.config';
import { renderArticle, countWords, type RenderedArticle } from './markdown';
import manifest from '../data/images.json';

export type PageType = 'pillar' | 'answer' | 'place' | 'data' | 'comparison' | 'guide';
export const PAGE_TYPES: PageType[] = ['pillar', 'answer', 'place', 'data', 'comparison', 'guide'];
export const TYPE_LABELS: Record<PageType, string> = { pillar: 'Guide', answer: 'Quick answer', place: 'Review', data: 'Data', comparison: 'Comparison', guide: 'Guide' };

export interface Photo {
  file: string; src: string; width: number; height: number; srcsetAvif: string; srcsetWebp: string;
  alt: string; caption: string; credit: string; creditUrl: string; license: string; licenseUrl: string;
}
export interface Source { url: string; title: string; accessed?: string }
export interface Page {
  id: string; slug: string; url: string; oldUrl: string; title: string; dek: string; school: School; topic: Topic;
  pageType: PageType; updated: string; year: number; words: number; sources: Source[]; images: Photo[]; lead: Photo | null;
  author: Author; reviewedBy?: string; body: RenderedArticle; sample: boolean; crossSchool: boolean; typeLabel: string;
  data: CollectionEntry<'articles'>['data']; file: string; primaryQuery: string;
}
export interface SiteModel {
  pages: Page[];        // real pages (no samples)
  samples: Page[];
  schools: School[]; topics: Topic[]; linkMap: Map<string, string>; knownUrls: Set<string>;
}

export const fmtDate = (iso: string) => {
  const d = new Date(iso + 'T00:00:00Z');
  return isNaN(d.getTime()) ? iso : d.toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric', timeZone: 'UTC' });
};
export const schoolUrl = (s: School) => `/${s.slug}/`;
export const topicUrl = (s: School, t: Topic | string) => `/${s.slug}/${typeof t === 'string' ? t : t.id}/`;
export const dataIndexUrl = (s: School) => `/${s.slug}/data/`;
export const authorUrl = (a: Author) => `/authors/${a.slug}/`;
export const schoolById = (id?: string) => site.schools.find((s) => s.id === id || s.slug === id);
export const topicById = (id?: string) => site.topics.find((t) => t.id === id);
export const authorBySlug = (slug?: string) => site.authors.find((a) => a.slug === slug) ?? site.authors.find((a) => a.slug === site.defaultAuthor)!;
export const audienceById = (id: string) => site.audiences.find((a) => a.id === id);
export const isAudience = (topicId: string) => site.audiences.some((a) => a.id === topicId);

function photosFor(slug: string, images: any[]): Photo[] {
  const dir = (manifest as any)[slug] ?? {};
  return images.map((im) => {
    const m = dir[im.file];
    if (!m) return null;
    const webp = m.variants.webp ?? [], avif = m.variants.avif ?? [];
    const biggest = webp[webp.length - 1];
    return {
      file: im.file, src: biggest?.src ?? '', width: biggest?.w ?? m.width, height: Math.round((biggest?.w ?? m.width) * m.height / m.width),
      srcsetWebp: webp.map((v: any) => `${v.src} ${v.w}w`).join(', '), srcsetAvif: avif.map((v: any) => `${v.src} ${v.w}w`).join(', '),
      alt: im.alt ?? '', caption: im.caption ?? '', credit: im.credit ?? '', creditUrl: im.credit_url ?? '', license: im.license ?? '', licenseUrl: im.license_url ?? '',
    } as Photo;
  }).filter(Boolean) as Photo[];
}

function decidePageType(d: any, words: number, file: string): PageType {
  if (d.page_type) {
    if (d.page_type === 'hub') throw new Error(`${file}: page_type "hub" is reserved for generated hub pages; articles take pillar, answer, place, data, comparison or guide`);
    return d.page_type;
  }
  if (d.cross_school) return 'guide';
  if (d.data) return 'data';
  if (d.place) return 'place';
  if (d.comparison) return 'comparison';
  if (d.kind === 'pillar') return 'pillar';
  return words >= site.content.pillarMinWords ? 'pillar' : 'answer';
}

function validate(p: Page) {
  const f = p.file;
  const need = (cond: any, msg: string) => { if (!cond) throw new Error(`${f}: ${msg}`); };
  need(p.title, 'missing title'); need(p.dek, 'missing meta (the dek)'); need(p.updated, 'missing updated');
  need(PAGE_TYPES.includes(p.pageType), `unknown page_type "${p.pageType}"`);
  need(p.sources.length >= 1, 'a page needs at least one source');
  if (p.pageType === 'pillar' || p.pageType === 'guide') need(p.sources.length >= 5, `a pillar guide needs at least 5 sources (has ${p.sources.length})`);
  if (p.pageType === 'place') {
    const pl = p.data.place; need(pl, 'a place page needs a `place` block (name, category, facts, verdict, best_for, skip_if)');
    const fields = site.placeCategories[pl!.category]; need(fields, `unknown place category "${pl!.category}" (site.config placeCategories)`);
    for (const k of fields!) need(pl!.facts[k], `place page is missing the "${k}" fact required for every ${pl!.category}`);
  }
  if (p.pageType === 'data') { const dt = p.data.data; need(dt, 'a data page needs a `data` block'); need(dt!.columns.length && dt!.rows.length, 'data page has no table rows'); }
  if (p.pageType === 'comparison') { const c = p.data.comparison; need(c, 'a comparison page needs a `comparison` block'); need(c!.items.length >= 2, 'a comparison needs at least two items'); }
}

async function publishedIds(): Promise<Set<string> | null> {
  if (site.content.includeUnpublished) return null;
  try {
    const csv = await fs.readFile(path.resolve('..', 'queue', 'queue.csv'), 'utf8');
    const out = new Set<string>();
    for (const line of csv.split('\n').slice(1)) { const id = line.split(',')[0]; if (line.trim().endsWith(',published')) out.add(id); }
    return out;
  } catch { return new Set(); }
}

let cache: Promise<SiteModel> | null = null;
export function getSite(): Promise<SiteModel> { return (cache ??= build()); }

async function build(): Promise<SiteModel> {
  const articles = await getCollection('articles');
  const samples = await getCollection('samples');
  const published = await publishedIds();
  const draft: { entry: any; sample: boolean }[] = [
    ...articles.filter((e) => !published || !e.data.queue_id || published.has(e.data.queue_id)).map((entry) => ({ entry, sample: false })),
    ...samples.map((entry) => ({ entry, sample: true })),
  ];
  const linkMap = new Map<string, string>();
  const knownUrls = new Set<string>();
  const pre = draft.map(({ entry, sample }) => {
    const d = entry.data;
    const file = sample ? `site/src/content/samples/${entry.id}.md` : `content/articles/${entry.id}.md`;
    const slug = entry.id.split('/').pop()!;
    const school = schoolById(d.school) ?? site.schools[0];
    const topic = topicById(d.topic);
    if (!school) throw new Error(`${file}: unknown school "${d.school}"`);
    if (!topic) throw new Error(`${file}: unknown topic "${d.topic}" (site.config topics)`);
    const words = countWords(entry.body ?? '');
    const pageType = decidePageType(d, words, file);
    const crossSchool = pageType === 'guide';
    const url = sample ? `/styleguide/${slug}/` : crossSchool ? `/guides/${slug}/` : pageType === 'data' ? `/${school.slug}/data/${slug}/` : `/${school.slug}/${topic.id}/${slug}/`;
    const oldUrl = `/${topic.id}/${slug}/`;
    if (!sample) { linkMap.set(oldUrl, url); knownUrls.add(url); }
    return { entry, sample, d, file, slug, school, topic, pageType, crossSchool, url, oldUrl };
  });
  for (const s of site.schools) {
    knownUrls.add(schoolUrl(s)); knownUrls.add(dataIndexUrl(s));
    for (const t of site.topics) { knownUrls.add(topicUrl(s, t)); linkMap.set(`/${t.id}/`, topicUrl(s, t)); }
  }
  for (const u of ['/about/', '/editorial-standards/', '/sources/', '/corrections/', '/contact/', '/privacy/', '/advertise/', '/search/', '/guides/', '/authors/']) knownUrls.add(u);
  linkMap.set('/editorial-policy/', '/editorial-standards/');
  for (const a of site.authors) knownUrls.add(authorUrl(a));

  const make = (p: typeof pre[number]): Page => {
    const sources: Source[] = (p.d.sources ?? []).map((s: any) => ({ url: s.url, title: s.title || s.url, accessed: s.accessed }));
    const images = photosFor((p.d as any).images_from ?? p.slug, p.d.images ?? []);
    const body = renderArticle(p.entry.body ?? '', { sources, linkMap, knownUrls, photos: images });
    const page: Page = {
      id: p.entry.id, slug: p.slug, url: p.url, oldUrl: p.oldUrl, title: p.d.title.trim(), dek: p.d.meta.trim(), school: p.school, topic: p.topic,
      pageType: p.pageType, updated: p.d.updated, year: p.d.year ?? Number(String(p.d.updated).slice(0, 4)), words: body.words, sources, images, lead: images[0] ?? null,
      author: authorBySlug(p.d.author), reviewedBy: p.d.reviewed_by, body, sample: p.sample, crossSchool: p.crossSchool, typeLabel: TYPE_LABELS[p.pageType],
      data: p.d, file: p.file, primaryQuery: p.d.primary_query ?? '',
    };
    validate(page);
    return page;
  };
  const all = pre.map(make);
  return { pages: all.filter((p) => !p.sample).sort((a, b) => (a.updated < b.updated ? 1 : -1)), samples: all.filter((p) => p.sample), schools: site.schools, topics: site.topics, linkMap, knownUrls };
}

/* ---------- groupings ---------- */
export const forSchool = (m: SiteModel, s: School) => m.pages.filter((p) => p.school.id === s.id && !p.crossSchool);
export const forTopic = (m: SiteModel, s: School, t: Topic | string) => forSchool(m, s).filter((p) => p.topic.id === (typeof t === 'string' ? t : t.id));
export const pillars = (pages: Page[]) => pages.filter((p) => p.pageType === 'pillar').sort((a, b) => b.words - a.words);
export const dataPages = (pages: Page[]) => pages.filter((p) => p.pageType === 'data');

/** Traffic-ranked lists come from site.config; without analytics the fallback is the longest pillar guides, labeled honestly. */
export function mostRead(m: SiteModel, s: School | null, n = 5): { label: string; items: Page[] } {
  const pool = s ? forSchool(m, s) : m.pages;
  const configured = site.mostRead.map((u) => pool.find((p) => p.url === u)).filter(Boolean) as Page[];
  if (configured.length) return { label: 'Most read', items: configured.slice(0, n) };
  const items = [...pillars(pool), ...pool.filter((p) => p.pageType !== 'pillar')].slice(0, n);
  return { label: 'Start here', items };
}
export function featured(m: SiteModel, n = 4): Page[] {
  const configured = site.featured.map((u) => m.pages.find((p) => p.url === u)).filter(Boolean) as Page[];
  if (configured.length >= n) return configured.slice(0, n);
  const withPhoto = pillars(m.pages).filter((p) => p.lead);
  const rest = pillars(m.pages).filter((p) => !p.lead);
  return [...configured, ...withPhoto, ...rest].filter((p, i, a) => a.indexOf(p) === i).slice(0, n);
}
export function related(m: SiteModel, page: Page, n = 6): Page[] {
  const same = forTopic(m, page.school, page.topic).filter((p) => p.url !== page.url);
  const others = forSchool(m, page.school).filter((p) => p.url !== page.url && p.topic.id !== page.topic.id);
  const rank = (p: Page) => (p.pageType === 'pillar' ? 2 : 1) * 10000 + p.words;
  return [...same.sort((a, b) => rank(b) - rank(a)), ...others.sort((a, b) => rank(b) - rank(a))].slice(0, n);
}
export function parentPillar(m: SiteModel, page: Page): Page | null {
  if (page.data.pillar) { const p = m.pages.find((x) => x.url === page.data.pillar || x.oldUrl === page.data.pillar); if (p) return p; }
  return pillars(forTopic(m, page.school, page.topic)).find((p) => p.url !== page.url) ?? null;
}
export function groupByType(pages: Page[]): { key: PageType; label: string; items: Page[] }[] {
  const groups: [PageType, string][] = [['pillar', 'Guides'], ['place', 'Reviews'], ['comparison', 'Comparisons'], ['answer', 'Quick answers'], ['data', 'Data']];
  return groups.map(([key, label]) => ({ key, label, items: pages.filter((p) => p.pageType === key) })).filter((g) => g.items.length);
}
export function audienceGroups(m: SiteModel, s: School, a: Audience): { name: string; items: Page[] }[] {
  const pool = forSchool(m, s);
  const used = new Set<string>();
  const groups = a.stages.map((stage) => {
    const items = pool.filter((p) => !used.has(p.url) && (stage.match.some((re) => re.test(p.title) || re.test(p.primaryQuery)) && (p.topic.id === a.id || stage.topics === undefined || stage.topics.includes(p.topic.id))));
    items.forEach((p) => used.add(p.url));
    return { name: stage.name, items };
  });
  const rest = pool.filter((p) => p.topic.id === a.id && !used.has(p.url));
  if (rest.length) groups.push({ name: 'More guides', items: rest });
  return groups.filter((g) => g.items.length);
}
export function byAuthor(m: SiteModel, a: Author) {
  return { written: m.pages.filter((p) => p.author.slug === a.slug), reviewed: m.pages.filter((p) => p.reviewedBy === a.slug) };
}
export function crumbsFor(page: Page) {
  if (page.sample) return [{ label: 'Home', href: '/' }, { label: 'Styleguide', href: '/styleguide/' }, { label: page.title }];
  if (page.crossSchool) return [{ label: 'Home', href: '/' }, { label: 'Guides', href: '/guides/' }, { label: page.title }];
  if (page.pageType === 'data') return [{ label: 'Home', href: '/' }, { label: page.school.short, href: schoolUrl(page.school) }, { label: 'Data', href: dataIndexUrl(page.school) }, { label: page.title }];
  return [{ label: 'Home', href: '/' }, { label: page.school.short, href: schoolUrl(page.school) }, { label: page.topic.label, href: topicUrl(page.school, page.topic) }, { label: page.title }];
}
