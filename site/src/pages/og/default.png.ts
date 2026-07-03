import type { APIRoute } from 'astro';
import { defaultCard } from '../../lib/og.mjs';

// Site-wide social card (landing, archive, recherche, projet…).
export const GET: APIRoute = () =>
  new Response(defaultCard(), { headers: { 'Content-Type': 'image/png' } });
