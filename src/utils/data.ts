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

export const categoryLabelsZh: Record<string, string> = {
  'models-products': '模型与产品',
  'research-open-source': '研究与开源',
  'company-industry': '公司与产业',
  'policy-regulation': '政策与监管',
  'podcasts-interviews': '访谈与播客',
  'funding-startups': '投资与创业',
  executives: '高管动态',
  'source-index': '来源索引',
};

export const categoryLabelsEn: Record<string, string> = {
  'models-products': 'Models & Products',
  'research-open-source': 'Research & Open Source',
  'company-industry': 'Companies & Industry',
  'policy-regulation': 'Policy & Regulation',
  'podcasts-interviews': 'Podcasts & Interviews',
  'funding-startups': 'Funding & Startups',
  executives: 'Executives',
  'source-index': 'Source Index',
};

export function groupBy<T extends Record<string, any>>(items: T[], key: string) {
  return (items || []).reduce((acc: Record<string, T[]>, item: T) => {
    const k = item[key] || 'other';
    (acc[k] ||= []).push(item);
    return acc;
  }, {});
}

export function categoryLabel(code: string, lang: 'zh' | 'en' = 'zh') {
  return (lang === 'en' ? categoryLabelsEn : categoryLabelsZh)[code] || code || (lang === 'en' ? 'Other' : '其他');
}

export function itemLocalizedUrl(item: any, date?: string) {
  if (item?.localized_url) return item.localized_url;
  const slug = item?.slug || String(item?.duplicate_group_id || item?.title || 'item').toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '') || 'item';
  const d = date || latestBrief?.date || 'latest';
  return `/zh/items/${d}/${slug}/`;
}

export function itemTitle(item: any, lang: 'zh' | 'en' = 'zh') {
  if (lang === 'en') return item?.title_en || item?.title_original || item?.title || item?.title_zh || 'Untitled';
  return item?.title_zh || item?.title || item?.title_original || '未命名情报';
}

export function itemSummary(item: any, lang: 'zh' | 'en' = 'zh') {
  if (lang === 'en') return item?.summary_en || item?.summary || newsFocus(item, 'en');
  return item?.summary_zh || item?.insight_zh || newsFocus(item, 'zh');
}

function subjectOf(item: any, lang: 'zh' | 'en') {
  const names = [...(item.companies || []), ...(item.people || [])].filter(Boolean).slice(0, 2);
  if (names.length) return lang === 'zh' ? names.join('、') : names.join(', ');
  return item.source_name || (lang === 'zh' ? '该来源' : 'this source');
}

export function newsFocus(item: any, lang: 'zh' | 'en' = 'zh') {
  const category = String(item.category || '');
  const subject = subjectOf(item, lang);
  const title = itemTitle(item, lang);

  if (lang === 'en') {
    if (category === 'podcasts-interviews') return `${subject} shares a new interview or podcast signal, useful for tracking executive views, AI strategy and product direction.`;
    if (category === 'research-open-source') return `${subject} shares research or open-source work, with attention to methods, metrics and practical limits.`;
    if (category === 'funding-startups') return `${subject} has a funding or market signal that may affect AI startup and infrastructure momentum.`;
    return `${subject} has an AI update relevant to product, industry or technical direction.`;
  }

  if (category === 'podcasts-interviews') return `${subject} 的新访谈提供了一线判断，可用于观察产品方向、组织取舍和 AI 产业节奏。`;
  if (category === 'research-open-source') return `${subject} 披露了研究或开源进展，重点在评测方法、复现条件和真实应用边界。`;
  if (category === 'funding-startups') return `${subject} 释放了资本或创业信号，说明 AI 基础设施、工具链和应用场景仍在快速重排。`;
  if (category === 'policy-regulation') return `${subject} 更新了治理或监管信息，可能影响企业采用 AI 时的责任边界和合规成本。`;
  if (category === 'models-products') return `${subject} 更新了模型或产品能力，需要观察它对开发者工作流、部署成本和企业采用的影响。`;
  return `${subject} 发布了新的 AI 动态，核心价值在于判断它是否会改变产品落地、产业竞争或技术路线。`;
}
