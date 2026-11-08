import { defineCollection, z } from 'astro:content';
import { glob } from 'astro/loaders';

const dateish = z.union([z.string(), z.date()]).transform((v) => (v instanceof Date ? v.toISOString().slice(0, 10) : String(v).slice(0, 10)));

const source = z.object({ url: z.string(), title: z.string().optional().default(''), accessed: dateish.optional() }).passthrough();
const image = z.object({
  file: z.string(), alt: z.string().optional().default(''), caption: z.string().optional().default(''),
  credit: z.string().optional().default(''), credit_url: z.string().optional().default(''),
  license: z.string().optional().default(''), license_url: z.string().optional().default(''),
}).passthrough();

export const articleSchema = z.object({
  title: z.string(),
  meta: z.string(),
  primary_query: z.string().optional(),
  topic: z.string(),
  school: z.string().optional(),
  type: z.string().optional(),       // v2: how-to | decision | scenario | comparison | place | checklist | roundup
  kind: z.string().optional(),       // v3: pillar | spoke | reader_guide | rewrite
  page_type: z.enum(['pillar', 'answer', 'place', 'data', 'comparison', 'hub', 'guide']).optional(),  // explicit template choice
  updated: dateish,
  queue_id: z.string().optional(),
  sources: z.array(source).default([]),
  images: z.array(image).default([]),
  pillar: z.string().optional(),
  readers: z.array(z.string()).optional(),
  brief: z.string().optional(),
  author: z.string().optional(),
  reviewed_by: z.string().optional(),
  year: z.number().optional(),
  cross_school: z.boolean().optional(),      // renders at /guides/{slug}/ with no school sub-nav
  school_versions: z.array(z.object({ school: z.string(), url: z.string(), title: z.string() })).optional(),
  // place pages (page_type: place)
  place: z.object({ name: z.string(), category: z.string(), facts: z.record(z.string()), verdict: z.string(), best_for: z.string(), skip_if: z.string(),
    pros: z.array(z.string()).default([]), cons: z.array(z.string()).default([]), compare_with: z.array(z.string()).default([]), comparison_url: z.string().optional(),
    schema_type: z.string().optional() }).optional(),
  // data pages (page_type: data)
  data: z.object({ updated: dateish, unit: z.string().optional(), chart: z.object({ title: z.string(), unit: z.string().optional(), rows: z.array(z.object({ label: z.string(), value: z.number() })), source: z.string().optional() }).optional(),
    columns: z.array(z.string()), rows: z.array(z.array(z.union([z.string(), z.number()]))), csv: z.string().optional(), license: z.string().optional() }).optional(),
  // comparison pages (page_type: comparison)
  comparison: z.object({ fields: z.array(z.string()), items: z.array(z.object({ name: z.string(), url: z.string().optional(), values: z.record(z.union([z.string(), z.number()])) })) }).optional(),
  sample: z.boolean().optional(),
}).passthrough();

const articles = defineCollection({
  loader: glob({ pattern: '**/*.md', base: '../content/articles' }),
  schema: articleSchema,
});

// Sample pages: clearly labeled sample content for the templates that have no real page yet (styleguide only, noindex).
const samples = defineCollection({
  loader: glob({ pattern: '*.md', base: './src/content/samples' }),
  schema: articleSchema,
});

const pages = defineCollection({
  loader: glob({ pattern: ['content/pages/*.md', 'site/src/content/pages-extra/*.md'], base: '..', generateId: ({ entry }) => entry.split('/').pop()!.replace(/\.md$/, '') }),
  schema: z.object({ title: z.string(), meta: z.string(), updated: dateish.optional(), noindex: z.boolean().optional(), hidden: z.boolean().optional(), eyebrow: z.string().optional() }).passthrough(),
});

export const collections = { articles, samples, pages };
