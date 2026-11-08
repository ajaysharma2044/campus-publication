// A tiny static server for dist/ (screenshots and Lighthouse). Serves 404.html with a real 404 status, like Netlify.
import http from 'node:http';
import { promises as fs } from 'node:fs';
import path from 'node:path';
const MIME = { '.html': 'text/html; charset=utf-8', '.css': 'text/css', '.js': 'text/javascript', '.mjs': 'text/javascript', '.json': 'application/json', '.woff2': 'font/woff2', '.png': 'image/png', '.svg': 'image/svg+xml', '.webp': 'image/webp', '.avif': 'image/avif', '.txt': 'text/plain', '.xml': 'application/xml', '.csv': 'text/csv', '.webmanifest': 'application/manifest+json', '.wasm': 'application/wasm', '.pf_meta': 'application/octet-stream', '.pf_index': 'application/octet-stream', '.pf_fragment': 'application/octet-stream', '.pagefind': 'application/octet-stream' };
export function serve(dir, port = 0) {
  const root = path.resolve(dir);
  const server = http.createServer(async (req, res) => {
    let p = decodeURIComponent(req.url.split('?')[0]);
    if (p.endsWith('/')) p += 'index.html';
    let file = path.join(root, p);
    let status = 200;
    try { const st = await fs.stat(file); if (st.isDirectory()) { res.writeHead(301, { Location: p + '/' }); res.end(); return; } }
    catch { file = path.join(root, '404.html'); status = 404; }
    try {
      const body = await fs.readFile(file);
      res.writeHead(status, { 'content-type': MIME[path.extname(file)] || 'application/octet-stream', 'cache-control': 'no-store' });
      res.end(body);
    } catch { res.writeHead(404); res.end('404'); }
  });
  return new Promise((resolve) => server.listen(port, '127.0.0.1', () => resolve({ server, url: `http://127.0.0.1:${server.address().port}` })));
}
if (process.argv[1] && import.meta.url.endsWith(path.basename(process.argv[1]))) {
  const { url } = await serve(process.argv[2] || 'dist', Number(process.argv[3] || 4381));
  console.log(`serving at ${url}`);
}
