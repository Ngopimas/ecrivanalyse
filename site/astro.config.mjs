import { defineConfig } from 'astro/config';
import tailwindcss from '@tailwindcss/vite';
import sitemap from '@astrojs/sitemap';

export default defineConfig({
  site: 'https://ecrivanalyse.net',
  // hover-prefetch: pages are tiny static HTML, so a hovered link is already loaded by click
  prefetch: { prefetchAll: true, defaultStrategy: 'hover' },
  integrations: [sitemap()],
  vite: {
    plugins: [tailwindcss()],
  },
});
