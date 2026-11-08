/* Markdown to HTML for the templates. One pass through unified with the fenced blocks scripts/v2/render_site.py knows
   (```figure cost_table | steps | timeline, ```glance, ```reader, ```tool), footnote markers on links to a listed source,
   internal-link rewriting to the Astro URLs, and the article split into short answer, sections, FAQ and related links. */
import { unified } from 'unified';
import remarkParse from 'remark-parse';
import remarkGfm from 'remark-gfm';
import remarkRehype from 'remark-rehype';
import rehypeRaw from 'rehype-raw';
import rehypeSlug from 'rehype-slug';
import { toHtml } from 'hast-util-to-html';
import { toString as hastText } from 'hast-util-to-string';
import { visit } from 'unist-util-visit';
import yaml from 'js-yaml';

export interface Heading { depth: number; id: string; text: string }
export interface Block { html: string; tag: string; words: number; id?: string; text?: string }
export interface Section { heading?: Heading; blocks: Block[]; words: number }
export interface FaqItem { q: string; a: string; text: string }
export interface Link { title: string; url: string }
export interface RenderContext {
  sources?: { url: string }[];
  linkMap?: Map<string, string>;     // old internal URL -> new URL
  knownUrls?: Set<string>;           // new URLs that exist on the site
}
export interface RenderedArticle {
  shortAnswer: string;              // HTML of the opening paragraph
  intro: Block[];                   // blocks between the short answer and the first H2
  sections: Section[];
  headings: Heading[];
  faq: FaqItem[];
  related: Link[];
  words: number;
  footnotes: Map<number, string>;   // source index (1-based) -> id of its first in-text marker
}

const esc = (s: string) => String(s ?? '').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
export const stripTags = (html: string) => html.replace(/<[^>]+>/g, ' ').replace(/&nbsp;/g, ' ').replace(/\s+/g, ' ').trim();
export const countWords = (html: string) => { const t = stripTags(html); return t ? t.split(/\s+/).length : 0; };
export const normalizeUrl = (u: string) => u.trim().replace(/^https?:\/\//, '').replace(/^www\./, '').replace(/#.*$/, '').replace(/\/+$/, '').toLowerCase();

/* ---------- fenced blocks ---------- */
/** The YAML of a figure block. Labels often carry a colon ("Move-in (2025 dates: August 18 and 19)"), which strict YAML rejects,
 *  so on failure every `key: value` scalar is quoted and parsed again (the same fallback as scripts/v2/render_site.py figure_yaml). */
export function figureYaml(text: string): any {
  try { return yaml.load(text); } catch {
    const quoted = text.replace(/^([ \t]*(?:-[ \t]+)?\w+:[ \t]+)(?!["'\[{])(.+?)[ \t]*$/gm, (_m, k: string, v: string) => k + '"' + v.replace(/\\/g, '\\\\').replace(/"/g, '\\"') + '"');
    try { return yaml.load(quoted); } catch { return null; }
  }
}

function figureHtml(body: string): string {
  const fig: any = figureYaml(body);
  if (!fig || typeof fig !== 'object' || !Array.isArray(fig.rows) || !fig.rows.length) return '';
  const title = esc(fig.title ?? '');
  const rows = fig.rows.map((r: any) => (typeof r === 'object' && r ? r : { label: String(r) }));
  if (fig.kind === 'cost_table') {
    return `<figure class="facts"><figcaption class="facts__title">${title}</figcaption><table class="facts__table"><tbody>` +
      rows.map((r: any) => `<tr class="facts__row"><th class="facts__label" scope="row">${esc(r.label)}</th><td class="facts__value">${esc(r.value ?? '')}</td></tr>`).join('') +
      `</tbody></table></figure>`;
  }
  if (fig.kind === 'steps') {
    return `<section class="steps"><h3 class="steps__title">${title}</h3><ol class="steps__list">` +
      rows.map((r: any, i: number) => `<li class="steps__item"><span class="steps__num" aria-hidden="true">${i + 1}</span><div class="steps__body"><p class="steps__label">${esc(r.label)}</p>${r.value ? `<p class="steps__detail">${esc(r.value)}</p>` : ''}</div></li>`).join('') +
      `</ol></section>`;
  }
  if (fig.kind === 'timeline') {
    return `<figure class="timeline"><figcaption class="timeline__title">${title}</figcaption><ol class="timeline__list">` +
      rows.map((r: any) => `<li class="timeline__item"><span class="timeline__date">${esc(r.date ?? r.value ?? '')}</span><span class="timeline__label">${esc(r.label)}</span></li>`).join('') +
      `</ol></figure>`;
  }
  return '';
}

function glanceHtml(body: string): string {
  const items = body.split('\n').map((l) => l.replace(/^\s*[-*]\s*/, '').trim()).filter(Boolean);
  if (!items.length) return '';
  return `<aside class="note note--glance"><h3 class="note__title">At a glance</h3><ul class="note__list">${items.map((i) => `<li>${inlineMd(i)}</li>`).join('')}</ul></aside>`;
}

function inlineMd(s: string): string {
  // links, bold and italics only, for one-line items
  return esc(s)
    .replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2">$1</a>')
    .replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>')
    .replace(/\*([^*]+)\*/g, '<em>$1</em>');
}

function remarkFences() {
  return (tree: any) => {
    visit(tree, 'code', (node: any, index: number | undefined, parent: any) => {
      if (!parent || index === undefined) return;
      const lang = String(node.lang ?? '');
      const meta = String(node.meta ?? '');
      let html = '';
      if (lang === 'figure') html = figureHtml(node.value);
      else if (lang === 'glance') html = glanceHtml(node.value);
      else if (lang === 'reader') {
        const title = meta.replace(/^"|"$/g, '') || 'If you are';
        html = `<details class="reader" open><summary class="reader__title">${esc(title)}</summary><div class="reader__body">${renderMarkdown(node.value).html}</div></details>`;
      } else if (lang === 'tool') {
        html = `<p class="tool-ref">Interactive tool: ${esc(meta || node.value.trim())} (available on the current site).</p>`;
      } else return;
      parent.children[index] = html ? { type: 'html', value: html } : { type: 'html', value: '' };
    });
  };
}

/* ---------- rehype: links, footnotes, tables ---------- */
function rehypeLinks(ctx: RenderContext, footnotes: Map<number, string>, counters: { ref: number }) {
  const sourceIndex = new Map<string, number>();
  (ctx.sources ?? []).forEach((s, i) => { if (s?.url) sourceIndex.set(normalizeUrl(s.url), i + 1); });
  return (tree: any) => {
    visit(tree, 'element', (node: any, index: number | undefined, parent: any) => {
      if (node.tagName === 'table' && parent && index !== undefined && parent.tagName !== 'div' && parent.tagName !== 'figure') {
        const existing = ([] as string[]).concat((node.properties?.className as string[]) ?? []);
        node.properties = { ...(node.properties ?? {}), className: [...existing, 'table'] };
        parent.children[index] = { type: 'element', tagName: 'div', properties: { className: ['table-wrap'] }, children: [node] };
        return;
      }
      if (node.tagName !== 'a' || !node.properties?.href) return;
      const href = String(node.properties.href);
      if (href.startsWith('/')) {
        const key = href.replace(/#.*$/, '').replace(/\/?$/, '/');
        const mapped = ctx.linkMap?.get(key) ?? (ctx.knownUrls?.has(key) ? key : undefined);
        if (mapped) node.properties.href = mapped + (href.includes('#') ? href.slice(href.indexOf('#')) : '');
        else if (parent && index !== undefined) parent.children.splice(index, 1, ...node.children);   // a page not on this site: plain text
        return;
      }
      if (/^https?:\/\//.test(href)) {
        node.properties.rel = 'noopener';
        const n = sourceIndex.get(normalizeUrl(href));
        if (n && parent && index !== undefined) {
          counters.ref += 1;
          const id = `ref-${n}-${counters.ref}`;
          if (!footnotes.has(n)) footnotes.set(n, id);
          const sup = { type: 'element', tagName: 'sup', properties: { className: ['fn'] }, children: [
            { type: 'element', tagName: 'a', properties: { href: `#source-${n}`, id, className: ['fn__link'], 'aria-label': `Source ${n}` }, children: [{ type: 'text', value: String(n) }] },
          ] };
          parent.children.splice(index + 1, 0, sup);
        }
      }
    });
  };
}

function collectHeadings(headings: Heading[]) {
  return (tree: any) => {
    visit(tree, 'element', (node: any) => {
      if (/^h[2-4]$/.test(node.tagName) && node.properties?.id) headings.push({ depth: Number(node.tagName[1]), id: String(node.properties.id), text: hastText(node) });
    });
  };
}

/* ---------- public API ---------- */
export function renderMarkdown(md: string, ctx: RenderContext = {}): { html: string; headings: Heading[]; blocks: Block[]; footnotes: Map<number, string> } {
  const headings: Heading[] = [];
  const footnotes = new Map<number, string>();
  const processor = unified().use(remarkParse).use(remarkGfm).use(remarkFences).use(remarkRehype, { allowDangerousHtml: true })
    .use(rehypeRaw).use(rehypeSlug).use(rehypeLinks, ctx, footnotes, { ref: 0 }).use(collectHeadings, headings);
  const tree: any = processor.runSync(processor.parse(md));
  const blocks: Block[] = [];
  for (const child of tree.children) {
    if (child.type === 'text' && !child.value.trim()) continue;
    const html = toHtml(child, { allowDangerousHtml: true });
    if (!html.trim()) continue;
    const tag = child.type === 'element' ? child.tagName : (child.type === 'raw' ? (html.match(/^<([a-z0-9]+)/i)?.[1] ?? 'raw') : child.type);
    blocks.push({ html, tag, words: countWords(html), id: child.properties?.id ? String(child.properties.id) : undefined, text: child.type === 'element' ? hastText(child) : undefined });
  }
  return { html: blocks.map((b) => b.html).join('\n'), headings, blocks, footnotes };
}

const FAQ_HEAD = /^(faqs?|frequently asked questions|common questions|related questions|questions people ask)$/i;
const RELATED_HEAD = /^(related guides?|related articles?|related reading|read next|more guides?)$/i;
const TOC_HEAD = /^(what(’|'|&#x27;)?s in this guide|in this guide|contents|table of contents|on this page)$/i;

export function renderArticle(md: string, ctx: RenderContext = {}): RenderedArticle {
  const { blocks, headings, footnotes } = renderMarkdown(md, ctx);
  let shortAnswer = '';
  const rest = [...blocks];
  if (rest[0]?.tag === 'p') shortAnswer = rest.shift()!.html;

  // group into sections by h2
  const intro: Block[] = [];
  const sections: Section[] = [];
  let cur: Section | null = null;
  for (const b of rest) {
    if (b.tag === 'h2') { cur = { heading: { depth: 2, id: b.id ?? '', text: b.text ?? '' }, blocks: [], words: 0 }; sections.push(cur); continue; }
    if (cur) { cur.blocks.push(b); cur.words += b.words; } else intro.push(b);
  }

  // pull out the FAQ, the related list and a writer's own contents list
  const faq: FaqItem[] = [];
  const related: Link[] = [];
  const kept: Section[] = [];
  for (const s of sections) {
    const t = (s.heading?.text ?? '').trim();
    if (FAQ_HEAD.test(t)) {
      let q = '', a: string[] = [];
      const flush = () => { if (q) faq.push({ q, a: a.join('\n'), text: stripTags(a.join(' ')) }); q = ''; a = []; };
      for (const b of s.blocks) {
        if (b.tag === 'h3') { flush(); q = b.text ?? ''; }
        else if (b.tag === 'p' && !q && /^<p><strong>/.test(b.html)) { flush(); q = stripTags(b.html.match(/<strong>(.*?)<\/strong>/)?.[1] ?? ''); a.push(b.html.replace(/<strong>.*?<\/strong>\s*/, '').replace(/^<p>\s*<\/p>$/, '')); }
        else a.push(b.html);
      }
      flush();
      if (faq.length) continue;
    }
    if (RELATED_HEAD.test(t)) {
      for (const b of s.blocks) for (const m of b.html.matchAll(/<a href="([^"]+)"[^>]*>(.*?)<\/a>/g)) related.push({ url: m[1], title: stripTags(m[2]) });
      if (related.length) continue;
    }
    if (TOC_HEAD.test(t)) continue;
    kept.push(s);
  }
  const words = countWords(shortAnswer) + intro.reduce((n, b) => n + b.words, 0) + kept.reduce((n, s) => n + s.words, 0);
  const keptHeadings = headings.filter((h) => h.depth === 2 ? kept.some((s) => s.heading?.id === h.id) : true);
  return { shortAnswer, intro, sections: kept, headings: keptHeadings, faq, related, words, footnotes };
}

/* Marker highlights: the first two <strong> runs of the short answer become marker strokes; any further ones stay bold. */
export function markHighlights(html: string, max = 2): string {
  let n = 0;
  return html.replace(/<strong>(.*?)<\/strong>/g, (m, inner) => (n++ < max ? `<mark class="hl">${inner}</mark>` : m));
}
