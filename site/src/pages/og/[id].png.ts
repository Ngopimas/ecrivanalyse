import { getCollection } from 'astro:content';
import type { APIRoute } from 'astro';
import { quinteCard } from '../../lib/og.mjs';

// One 1200×630 social card per quinte, generated at build time.
export async function getStaticPaths() {
  const all = (await getCollection('quintes')).filter((q) => q.data.lines.length > 0);
  return all.map((q) => ({ params: { id: q.id }, props: { q: q.data } }));
}

export const GET: APIRoute = ({ props }) => {
  const { title, lines, date } = props.q;
  return new Response(quinteCard({ title, lines, date }), {
    headers: { 'Content-Type': 'image/png' },
  });
};
