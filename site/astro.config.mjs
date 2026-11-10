// EduExplained site templates (Astro). Parallel to scripts/v2/render_site.py; reads the same content/ tree.
import { defineConfig } from 'astro/config';
import { site } from './site.config.ts';

export default defineConfig({
  site: site.url,
  output: 'static',
  trailingSlash: 'always',
  build: { format: 'directory', inlineStylesheets: 'never' },
  compressHTML: true,
  markdown: { syntaxHighlight: false },   // the renderer in src/lib/markdown.ts handles the fenced blocks; no Shiki

  devToolbar: { enabled: false },
  vite: { server: { fs: { allow: ['..'] } } },
});
