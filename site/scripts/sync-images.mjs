// Copies the licensed photos from content/images/<slug>/*.webp into site/public/images/<slug>/ as responsive AVIF and WebP
// variants (480, 800, 1200 wide) and records their sizes in src/data/images.json. Runs before every build (prebuild).
import { promises as fs } from 'node:fs';
import path from 'node:path';
import sharp from 'sharp';

const root = path.resolve(new URL('..', import.meta.url).pathname);
const src = path.join(root, '..', 'content', 'images');
const out = path.join(root, 'public', 'images');
const WIDTHS = [480, 800, 1200];
const SKIP = new Set(['candidates', 'inbox', 'README.md', 'credits.yml']);
const manifest = {};

const dirs = (await fs.readdir(src, { withFileTypes: true })).filter((d) => d.isDirectory() && !SKIP.has(d.name));
for (const d of dirs) {
  const files = (await fs.readdir(path.join(src, d.name))).filter((f) => /\.(webp|jpe?g|png)$/i.test(f));
  for (const f of files) {
    const input = path.join(src, d.name, f);
    const stem = f.replace(/\.[^.]+$/, '');
    const meta = await sharp(input).metadata();
    const entry = { width: meta.width, height: meta.height, variants: {} };
    await fs.mkdir(path.join(out, d.name), { recursive: true });
    for (const w of WIDTHS) {
      if (w > meta.width && w !== WIDTHS[0]) continue;
      const width = Math.min(w, meta.width);
      for (const fmt of ['avif', 'webp']) {
        const target = path.join(out, d.name, `${stem}-${w}.${fmt}`);
        try { await fs.access(target); } catch {
          await sharp(input).resize({ width }).toFormat(fmt, fmt === 'avif' ? { quality: 55 } : { quality: 78 }).toFile(target);
        }
        (entry.variants[fmt] ??= []).push({ w, src: `/images/${d.name}/${stem}-${w}.${fmt}` });
      }
    }
    (manifest[d.name] ??= {})[f] = entry;
  }
}
await fs.mkdir(path.join(root, 'src', 'data'), { recursive: true });
await fs.writeFile(path.join(root, 'src', 'data', 'images.json'), JSON.stringify(manifest, null, 1));
console.log(`images: ${Object.keys(manifest).length} article folders synced`);
