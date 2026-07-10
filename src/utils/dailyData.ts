import latest from '../../data/index/latest.json';
import archive from '../../data/index/archive.json';
import dailyIndex from '../../data/index/daily_index.json';

function briefDate(brief: any) {
  return String(brief?.date || '').trim();
}

const latestAny: any = latest;
const archiveAny: any = archive;
const dailyIndexAny: any = dailyIndex;

const dailyByDate = new Map<string, any>();

for (const brief of dailyIndexAny?.briefs || []) {
  const d = briefDate(brief);
  if (d && !dailyByDate.has(d)) dailyByDate.set(d, brief);
}

const latestDate = briefDate(latestAny);
if (latestDate && !dailyByDate.has(latestDate)) {
  dailyByDate.set(latestDate, latestAny);
}

export function dailyArchiveRows() {
  const rows = Array.isArray(archiveAny?.items) && archiveAny.items.length
    ? archiveAny.items
    : [{ date: latestAny.date, source_count: latestAny.source_count, candidate_count: latestAny.candidate_count, selected_count: latestAny.selected_count }];
  return rows.filter((row: any) => row?.date);
}

export function dailyBriefByDate(date: string) {
  const d = String(date);
  if (dailyByDate.has(d)) return dailyByDate.get(d);
  const row = dailyArchiveRows().find((item: any) => String(item.date) === d);
  return {
    date: d,
    title_zh: row?.title || `AI 新闻简报 · ${d}`,
    title_en: `English AI News Brief · ${d}`,
    overview_zh: '该归档日期缺少完整 JSON，当前仅保留归档入口。下一次日更会自动重建静态索引。',
    overview_en: 'This archive entry is missing its full JSON payload; the static index will be rebuilt by the next daily run.',
    source_count: row?.source_count || 0,
    candidate_count: row?.candidate_count || 0,
    skipped_history_count: row?.skipped_history_count || 0,
    selected_count: row?.selected_count || 0,
    categories: [],
    items: [],
    failures: [],
  };
}

export function allDailyBriefs() {
  return Array.from(dailyByDate.values()).sort((a: any, b: any) => String(b.date).localeCompare(String(a.date)));
}
