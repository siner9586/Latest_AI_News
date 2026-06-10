import { defineConfig } from 'astro/config';

const site = process.env.SITE_URL || 'https://aib.ccwu.cc';

export default defineConfig({
  site,
  output: 'static'
});
