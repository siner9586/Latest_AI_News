import { archiveIndex } from '../utils/data';

const site = (import.meta.env.SITE_URL || 'https://aib.ccwu.cc').replace(/\/$/, '');

export async function GET() {
  const staticPaths = [
    '/',
    '/zh/',
    '/en/',
    '/archive/',
    '/sources/',
    '/people/',
    '/companies/',
    '/tags/',
    '/about/'
  ];

  const dailyPaths = (archiveIndex.items || []).flatMap((item: any) => [
    `/daily/${item.date}/`,
    `/en/daily/${item.date}/`
  ]);

  const urls = [...staticPaths, ...dailyPaths]
    .map((path) => `  <url><loc>${site}${path}</loc></url>`)
    .join('\n');

  return new Response(
    `<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n${urls}\n</urlset>\n`,
    {
      headers: {
        'Content-Type': 'application/xml; charset=utf-8'
      }
    }
  );
}
