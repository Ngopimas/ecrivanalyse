import { getCollection } from 'astro:content';
import type { APIRoute } from 'astro';
import { diveData } from '../../../lib/format';

// One small JSON per divable quinte (same pool as the landing: 2-8 lines,
// no prose). The landing fetches it during the encounter beat, so
// « rencontre au hasard » can land on the whole corpus instead of the
// ~90 quintes inlined in the page.
export async function getStaticPaths() {
  const pool = (await getCollection('quintes'))
    .filter((q) => q.data.lines.length >= 2 && q.data.lines.length <= 8 && !q.data.prose);
  return pool.map((q) => ({ params: { id: q.id }, props: { d: q.data } }));
}

export const GET: APIRoute = ({ params, props }) =>
  new Response(JSON.stringify(diveData(String(params.id), props.d)), {
    headers: { 'Content-Type': 'application/json' },
  });
