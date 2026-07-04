import { getCollection } from 'astro:content';
import type { APIRoute } from 'astro';
import { quinteCard, texteCard } from '../../lib/og.mjs';
import { prosePlain } from '../../lib/format';

// One 1200×630 social card per quinte and per texte, generated at build time.
// Article ids are disjoint across the two collections, so they share /og/<id>.png.
export async function getStaticPaths() {
  const quintes = (await getCollection('quintes'))
    .filter((q) => q.data.lines.length > 0)
    .map((q) => ({ params: { id: q.id }, props: { kind: 'quinte', d: q.data } }));
  const textes = (await getCollection('textes'))
    .map((t) => ({ params: { id: t.id }, props: { kind: 'texte', d: t.data } }));
  return [...quintes, ...textes];
}

export const GET: APIRoute = ({ props }) => {
  const { kind, d } = props;
  const png = kind === 'texte'
    ? texteCard({ title: d.title, excerpt: prosePlain(d.text).slice(0, 320), date: d.date })
    : quinteCard({ title: d.title, lines: d.lines, date: d.date });
  return new Response(png, {
    headers: { 'Content-Type': 'image/png' },
  });
};
