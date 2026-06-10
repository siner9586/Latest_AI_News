import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';

export default defineConfig({
  site: process.env.SITE_URL || 'https://siner9586.github.io/Latest_AI_News',
  integrations: [sitemap()],
  output: 'static'
});
