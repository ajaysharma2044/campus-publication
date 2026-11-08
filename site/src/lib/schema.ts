/* schema.org JSON-LD builders. Every builder returns a plain object; Base.astro serializes the list it is given. */
import { site } from '../../site.config';

const abs = (u: string) => (u.startsWith('http') ? u : new URL(u, site.url).toString());
export const SITE_ID = `${site.url}/#organization`;

export const organization = () => ({
  '@type': 'Organization', '@id': SITE_ID, name: site.name, url: site.url + '/',
  logo: { '@type': 'ImageObject', url: abs('/icon-512.png'), width: 512, height: 512 },
  sameAs: site.organization.sameAs,
});

export const webSite = () => ({
  '@type': 'WebSite', '@id': `${site.url}/#website`, name: site.name, url: site.url + '/', publisher: { '@id': SITE_ID }, inLanguage: site.language,
  potentialAction: { '@type': 'SearchAction', target: { '@type': 'EntryPoint', urlTemplate: `${site.url}/search/?q={search_term_string}` }, 'query-input': 'required name=search_term_string' },
});

export interface Crumb { label: string; href?: string }
export const breadcrumbList = (crumbs: Crumb[]) => ({
  '@type': 'BreadcrumbList',
  itemListElement: crumbs.map((c, i) => ({ '@type': 'ListItem', position: i + 1, name: c.label, ...(c.href ? { item: abs(c.href) } : {}) })),
});

export interface ArticleLike { title: string; dek: string; url: string; updated: string; image?: string; author: { name: string; url: string; kind: 'person' | 'organization' }; words?: number }
export const article = (p: ArticleLike, type = 'Article') => ({
  '@type': type, headline: p.title, description: p.dek, mainEntityOfPage: abs(p.url), dateModified: p.updated,
  ...(p.image ? { image: [abs(p.image)] } : {}),
  author: { '@type': p.author.kind === 'person' ? 'Person' : 'Organization', name: p.author.name, url: abs(p.author.url) },
  publisher: { '@id': SITE_ID }, inLanguage: site.language, ...(p.words ? { wordCount: p.words } : {}),
});

export const faqPage = (items: { q: string; text: string }[]) => ({
  '@type': 'FAQPage', mainEntity: items.map((f) => ({ '@type': 'Question', name: f.q, acceptedAnswer: { '@type': 'Answer', text: f.text } })),
});

export const itemList = (items: { title: string; url: string }[], name?: string) => ({
  '@type': 'ItemList', ...(name ? { name } : {}), numberOfItems: items.length,
  itemListElement: items.map((it, i) => ({ '@type': 'ListItem', position: i + 1, name: it.title, url: abs(it.url) })),
});

export const collectionPage = (p: { title: string; dek: string; url: string; items: { title: string; url: string }[] }) => ({
  '@type': 'CollectionPage', name: p.title, description: p.dek, url: abs(p.url), isPartOf: { '@id': `${site.url}/#website` }, mainEntity: itemList(p.items),
});

export const dataset = (p: { title: string; dek: string; url: string; updated: string; csv?: string; license?: string }) => ({
  '@type': 'Dataset', name: p.title, description: p.dek, url: abs(p.url), dateModified: p.updated, creator: { '@id': SITE_ID },
  ...(p.license ? { license: p.license } : {}),
  ...(p.csv ? { distribution: [{ '@type': 'DataDownload', encodingFormat: 'text/csv', contentUrl: abs(p.csv) }] } : {}),
});

export const place = (p: { name: string; type?: string; url: string; description: string; facts: Record<string, string> }) => ({
  '@type': p.type ?? 'Place', name: p.name, url: abs(p.url), description: p.description,
  additionalProperty: Object.entries(p.facts).map(([name, value]) => ({ '@type': 'PropertyValue', name, value })),
});

export const person = (a: { name: string; url: string; role: string; bio: string; kind: 'person' | 'organization' }) => ({
  '@type': a.kind === 'person' ? 'Person' : 'Organization', name: a.name, url: abs(a.url), description: a.bio, ...(a.kind === 'person' ? { jobTitle: a.role, worksFor: { '@id': SITE_ID } } : {}),
});

export const profilePage = (a: { name: string; url: string; role: string; bio: string; kind: 'person' | 'organization' }) => ({
  '@type': 'ProfilePage', mainEntity: person(a), url: abs(a.url),
});

export const webPage = (p: { title: string; dek: string; url: string; updated?: string }) => ({
  '@type': 'WebPage', name: p.title, description: p.dek, url: abs(p.url), isPartOf: { '@id': `${site.url}/#website` }, ...(p.updated ? { dateModified: p.updated } : {}),
});

export const graph = (nodes: object[]) => ({ '@context': 'https://schema.org', '@graph': nodes });
