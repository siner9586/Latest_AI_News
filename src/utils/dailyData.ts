import latest from '../../data/index/latest.json';
import archive from '../../data/index/archive.json';

const dailyModules = import.meta.glob('../../data/daily/*.json', { eager: true });

function moduleData(mod: unknown): any {
  return (mod as any)?.default || mod;
}

function dateFromPath(path: string) {
  return path.match(/(\d{4}-\d{2}-\d{2})\.json$/)?.[1] || '';
}

const dailyByDate = new Map<string, any>();

for (const [path, mod] of Object.entries(dailyModules)) {
  const brief = moduleData(mod);
  const d = String(brief?.date || dateFromPath(path)).trim();
  if (d) dailyByDate.set(d, brief);
}

const latestAny: any = latest;
const archiveAny: any = archive;

export function dailyArchiveRows() {
  const rows = Array.isArray(archiveAny?.items) && archiveAny.items.length
    ? archiveAny.items
    : [{ date: latestAny.date, source_count: latestAny.source_count, candidate_count: latestAny.candidate_count, selected_count: latestAny.selected_count }];
  return rows.filter((row: any) => row?.date);
}

export function dailyBriefByDate(date: string) {
  return dailyByDate.get(String(date)) || latestAny;
}

export function allDailyBriefs() {
  const briefs = Array.from(dailyByDate.values()).filter((brief: any) => brief?.date);
  if (!briefs.some((brief: any) => brief.date === latestAny.date)) {
    briefs.push(latestAny);
  }
  return briefs.sort((a: any, b: any) => String(b.date).localeCompare(String(a.date)));
}
