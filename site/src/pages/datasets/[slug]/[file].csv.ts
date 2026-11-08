import type { APIRoute } from 'astro';
import { getSite } from '../../../lib/model';
/** The dataset's CSV at the renderer's path, /datasets/<slug>/<slug>.csv, byte for byte. */
export async function getStaticPaths() {
  const m = await getSite();
  return m.datasets.filter((d) => d.csvText).map((d) => ({ params: { slug: d.slug, file: d.slug }, props: { csv: d.csvText } }));
}
export const GET: APIRoute = ({ props }) => new Response((props as any).csv, { headers: { 'Content-Type': 'text/csv; charset=utf-8' } });
