/* A plain Markdown loader for the content collections: frontmatter (YAML) and body, nothing else. Astro's own glob loader runs
   every .md file through its Markdown pipeline (syntax highlighting, relative image resolution), which the templates never use and
   which fails the build when an article links an image Astro cannot resolve. The templates render bodies with src/lib/markdown.ts. */
import type { Loader } from 'astro/loaders';
import { promises as fs } from 'node:fs';
import path from 'node:path';
import yaml from 'js-yaml';

async function walk(dir: string): Promise<string[]> {
  const out: string[] = [];
  let entries: import('node:fs').Dirent[] = [];
  try { entries = await fs.readdir(dir, { withFileTypes: true }); } catch { return out; }
  for (const e of entries) {
    const p = path.join(dir, e.name);
    if (e.isDirectory()) out.push(...(await walk(p)));
    else if (e.isFile() && e.name.endsWith('.md')) out.push(p);
  }
  return out.sort();
}

export function markdownLoader(opts: { bases: string[]; idFrom?: 'relative' | 'basename' }): Loader {
  return {
    name: 'footnote-markdown',
    load: async ({ store, parseData, generateDigest, logger }) => {
      store.clear();
      let count = 0;
      for (const base of opts.bases) {
        const root = path.resolve(base);
        for (const file of await walk(root)) {
          const raw = await fs.readFile(file, 'utf8');
          const m = raw.match(/^---\r?\n([\s\S]*?)\r?\n---[ \t]*(?:\r?\n|$)/);
          let fm: Record<string, unknown> = {};
          try { fm = (m ? (yaml.load(m[1]) as Record<string, unknown>) : {}) ?? {}; }
          catch (e) { throw new Error(`${path.relative(process.cwd(), file)}: frontmatter is not valid YAML (${(e as Error).message.split('\n')[0]})`); }
          const body = m ? raw.slice(m[0].length) : raw;
          const rel = path.relative(root, file).replace(/\\/g, '/').replace(/\.md$/, '');
          const id = opts.idFrom === 'basename' ? path.basename(rel) : rel;
          const data = await parseData({ id, data: fm, filePath: file });
          store.set({ id, data, body, filePath: path.relative(process.cwd(), file), digest: generateDigest(raw) });
          count += 1;
        }
      }
      logger.info(`${count} Markdown files loaded from ${opts.bases.join(', ')}`);
    },
  };
}
