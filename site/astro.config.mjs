import { defineConfig } from 'astro/config';
import tailwindcss from '@tailwindcss/vite';
import react from '@astrojs/react';
import keystatic from '@keystatic/astro';
import sitemap from '@astrojs/sitemap';

// Keystatic (+ React) only in the `npm run cms` session (CMS=1), so:
//  - `npm run dev`  → fast design dev, HMR on, no CMS
//  - `npm run cms`  → Keystatic admin at /keystatic, HMR off (Vite 8 rolldown
//                     fast-refresh builtin crashes with "Missing field moduleType")
//  - `npm run build`→ pure static (no React, no server routes, Pagefind indexes dist/)
const withCMS = process.env.CMS === '1';

export default defineConfig({
  site: 'https://ecrivanalyse.net',
  integrations: [...(withCMS ? [react(), keystatic()] : []), sitemap()],
  vite: {
    plugins: [tailwindcss()],
    // Vite 8's rolldown react-refresh builtin crashes ("Missing field moduleType");
    // the Keystatic admin doesn't need HMR, so disable it in the CMS dev session.
    ...(withCMS ? { server: { hmr: false } } : {}),
  },
});
