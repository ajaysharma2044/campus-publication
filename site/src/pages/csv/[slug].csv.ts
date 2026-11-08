import type { APIRoute } from 'astro';
import { getSite } from '../../lib/model';
export async function getStaticPaths() {
  const m = await getSite();
  return [...m.pages, ...m.samples].filter((p) => p.pageType === 'data').map((p) => ({ params: { slug: p.slug }, props: { page: p } }));
}
const cell = (v: unknown) => { const s = String(v ?? ''); return /[",\n]/.test(s) ? `"${s.replace(/"/g, '""')}"` : s; };
export const GET: APIRoute = ({ props }) => {
  const d = (props as any).page.data.data;
  const body = [d.columns, ...d.rows].map((r: unknown[]) => r.map(cell).join(',')).join('\n') + '\n';
  return new Response(body, { headers: { 'Content-Type': 'text/csv; charset=utf-8' } });
};
