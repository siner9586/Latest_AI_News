import latest from '../../data/index/latest.json';
import archive from '../../data/index/archive.json';
import people from '../../data/entities/people.json';
import companies from '../../data/entities/companies.json';
import sources from '../../data/sources/sources.json';

export const latestBrief: any = latest;
export const archiveIndex: any = archive;
export const peopleIndex: any[] = people;
export const companyIndex: any[] = companies;
export const sourceIndex: any[] = sources;

export function groupBy<T extends Record<string, any>>(items: T[], key: string) {
  return (items || []).reduce((acc: Record<string, T[]>, item: T) => {
    const k = item[key] || 'other';
    (acc[k] ||= []).push(item);
    return acc;
  }, {});
}
