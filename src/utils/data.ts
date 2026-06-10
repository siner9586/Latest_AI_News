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

function subjectOf(item: any, lang: 'zh' | 'en') {
  const names = [...(item.companies || []), ...(item.people || [])].filter(Boolean).slice(0, 2);
  if (names.length) return lang === 'zh' ? names.join('、') : names.join(', ');
  return item.source_name || (lang === 'zh' ? '该来源' : 'this source');
}

export function newsFocus(item: any, lang: 'zh' | 'en' = 'zh') {
  const title = String(item.title || '').trim();
  const category = String(item.category || '');
  const low = title.toLowerCase();
  const subject = subjectOf(item, lang);

  if (lang === 'en') {
    if (category === 'podcasts-interviews') return `${subject}: key discussion on ${title}, useful for tracking executive views, product direction and AI industry strategy.`;
    if (/introducing|launch|release|announces|unveils|new\b/.test(low)) return `${subject}: new release or product update around ${title}, pointing to changes in model capability, developer tooling or AI adoption.`;
    if (/benchmark|research|paper|study|evaluat/.test(low)) return `${subject}: research or evaluation update on ${title}, with attention to methods, metrics and practical limits.`;
    if (/funding|raises|investment|acquire|deal/.test(low)) return `${subject}: funding, deal or investment signal around ${title}, reflecting AI startup and infrastructure momentum.`;
    return `${subject}: new AI-related development around ${title}, relevant to product, industry or technical direction.`;
  }

  if (category === 'podcasts-interviews') return `${subject}：围绕“${title}”展开访谈或播客讨论，重点看高管判断、产品方向与 AI 产业战略。`;
  if (/introducing|launch|release|announces|unveils|new\b/.test(low)) return `${subject}：围绕“${title}”发布新产品或能力更新，重点看模型能力、开发者工具与应用落地变化。`;
  if (/benchmark|research|paper|study|evaluat/.test(low)) return `${subject}：围绕“${title}”给出研究或评测进展，重点看方法、指标、结论和应用边界。`;
  if (/funding|raises|investment|acquire|deal/.test(low)) return `${subject}：围绕“${title}”出现融资、交易或投资信号，反映 AI 创业与基础设施投入方向。`;
  return `${subject}：围绕“${title}”出现新动态，重点关注其对 AI 产品、产业落地或技术路线的影响。`;
}
