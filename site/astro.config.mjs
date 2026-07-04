import { defineConfig } from 'astro/config';
import tailwindcss from '@tailwindcss/vite';
import sitemap from '@astrojs/sitemap';

// GitHub Pages serves the repo under /ecrivanalyse/ until the custom domain
// is attached: CI sets BASE_PATH + SITE_URL (see .github/workflows/deploy.yml);
// local dev and the future domain use the defaults. Hand-written URLs go
// through u() in src/lib/format.ts so they work under both.
const base = process.env.BASE_PATH ?? '/';
const site = process.env.SITE_URL ?? 'https://ecrivanalyse.net';

export default defineConfig({
  site,
  base,
  // hover-prefetch: pages are tiny static HTML, so a hovered link is already loaded by click
  prefetch: { prefetchAll: true, defaultStrategy: 'hover' },
  integrations: [sitemap()],
  vite: {
    plugins: [tailwindcss()],
  },
});
