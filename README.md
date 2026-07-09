# Latest AI News

Latest AI News 是一个 Astro + Python 的中文优先 AI 情报站。它从结构化 RSS、公司博客、研究机构、开发者生态、播客、媒体与投资来源中生成每日 AI 情报流，并把首页阅读链路升级为“站内中文研究阅读页”。

## 核心变化

- 中文首页标题优先使用 `title_zh`，不再默认展示英文原标题。
- 中文首页标题优先跳转 `/zh/items/YYYY-MM-DD/slug/` 站内详情页。
- 原始来源仍保留，但降级为详情页和卡片中的“原始来源”按钮。
- 每条 item 增加中文标题、中文摘要、研究解读、核心要点、背景说明、影响判断、术语卡、证据卡、站内路径、slug、抓取/翻译状态和质量提示。
- 不绕过付费墙，不伪造来源，不用测试数据冒充真实新闻。
- 没有 `OPENAI_API_KEY` 时使用规则型中文生成逻辑；有密钥时可选启用增强汉化，失败自动回退。

## 中文研究阅读页

每条中文 item 会生成一个静态详情页：

```text
/zh/items/YYYY-MM-DD/slug/
```

页面包含：

- 中文标题
- 来源、发布时间、抓取时间、分类
- 原始来源按钮
- 一句话结论
- 核心要点
- 背景说明
- 详细解读
- 影响判断
- 相关公司、人物、标签
- 术语卡
- 证据与来源
- 质量提示

默认页面名称是“中文研究阅读版”或“中文研究解读”，不是“全文翻译”。只有当 `content_mode=full_zh_mirror` 且 `source_license_mode` 允许时，才展示完整中文镜像模块。

## 为什么首页标题跳转站内中文页

首页的目标是让中文读者先完成研究阅读，而不是被迫跳到英文原文。原始链接仍然存在，保留在：

1. 首页卡片的“原始来源”按钮；
2. 中文详情页顶部的“查看原始来源 / Source”按钮；
3. 证据与来源模块；
4. RSS 条目链接或描述中。

## 数据结构

每个 item 至少应包含以下字段：

```text
title
title_original
title_zh
title_en
summary_zh
summary_en
insight_zh
key_points_zh
background_zh
impact_zh
terms_zh
evidence_zh
source_name
source_url
original_url
localized_url
slug
source_license_mode
content_mode
full_text_zh
fetched_at
published_at
category
people
companies
tags
importance_score
freshness_score
credibility_score
duplicate_group_id
language
translation_status
extraction_status
quality_warnings
```

旧数据缺字段时，`scripts/ensure_data.py` 和 `scripts/backfill_localized_items.py` 会补齐，页面也会走 fallback，不应崩溃。

## content_mode 与 source_license_mode

`source_license_mode` 支持：

- `summary_only`：只保存摘要、元数据、证据转述和链接。
- `official_public`：官方公开内容，可做更详尽摘要，但默认不全文镜像。
- `open_license`：开放许可来源。
- `owned`：自有内容。
- `allow_full_mirror`：允许全文镜像。

`content_mode` 支持：

- `research_digest`：默认模式，生成中文研究解读。
- `full_zh_mirror`：仅在 private research 且来源许可允许时使用。

启用私人研究模式：

```bash
PRIVATE_RESEARCH_MODE=true python -m latest_ai_news.pipeline.run_daily --date 2026-07-09 --force
```

## LOCALIZATION_PROVIDER

默认不需要任何付费 API：

```bash
LOCALIZATION_PROVIDER=rule
```

可选启用 OpenAI 增强：

```bash
export LOCALIZATION_PROVIDER=openai
export OPENAI_API_KEY=你的密钥
python -m latest_ai_news.pipeline.run_daily --date 2026-07-09 --max-items 18 --language all --force
```

增强模式只发送标题、公开摘要、来源、分类和必要短文本；输出必须是 JSON；失败会自动回退规则生成。

缓存位置：

```text
data/cache/localized/*.json
```

## 本地验证

```bash
npm install
pip install -r requirements.txt
python -m latest_ai_news.pipeline.run_daily --date 2026-07-09 --max-items 18 --language all --force
python scripts/backfill_localized_items.py --date 2026-07-09
python scripts/validate_daily.py
npm run build
```

日常开发：

```bash
npm run dev
npm run build
npm run validate
npm run backfill -- --date 2026-07-09
```

## 手动生成某天内容

```bash
python -m latest_ai_news.pipeline.run_daily \
  --date 2026-07-09 \
  --max-items 18 \
  --language all
```

可选参数：

- `--force`：强制重新生成当天内容。
- `--dry-run`：只打印结果，不写文件。
- `--max-items N`：限制入选条数。
- `--language all|zh|en`：兼容旧参数。

## 回填历史中文标题与详情页

回填单日：

```bash
python scripts/backfill_localized_items.py --date 2026-07-09
```

预览不写入：

```bash
python scripts/backfill_localized_items.py --date 2026-07-09 --dry-run
```

回填全部历史：

```bash
python scripts/backfill_localized_items.py --all
```

强制重写中文字段：

```bash
python scripts/backfill_localized_items.py --all --force
```

## 正文抽取策略

新增轻量抽取模块：

```text
latest_ai_news/fetchers/article_page.py
latest_ai_news/pipeline/content_enrichment.py
```

优先使用：

- `requests`
- `BeautifulSoup`
- `trafilatura`
- `readability-lxml`
- `html2text`

抽取失败不会中断 daily pipeline，只会写入 `extraction_status` 和 `quality_warnings`。X、YouTube、播客、付费媒体等难以抽取正文的来源，会自动降级为元数据摘要。

## GitHub Actions

`.github/workflows/daily-news.yml` 保持多时点冗余调度：

```yaml
cron: '18 22 * * *'  # 06:18 Beijing/Taipei primary
cron: '33 22 * * *'  # 06:33 compensation
cron: '48 22 * * *'  # 06:48 compensation
cron: '3 23 * * *'   # 07:03 compensation
cron: '18 23 * * *'  # 07:18 compensation
cron: '33 23 * * *'  # 07:33 compensation
cron: '48 23 * * *'  # 07:48 compensation
cron: '3 0 * * *'    # 08:03 compensation
cron: '18 0 * * *'   # 08:18 compensation
cron: '33 0 * * *'   # 08:33 compensation
cron: '48 0 * * *'   # 08:48 compensation
cron: '3 1 * * *'    # 09:03 compensation
cron: '18 1 * * *'   # 09:18 compensation
cron: '33 1 * * *'   # 09:33 final compensation
```

跳过条件现在不仅检查当天 JSON 和 Markdown 是否存在，还检查 `data/daily/YYYY-MM-DD.json` 是否已经包含 `localized_url`。如果旧格式内容已经存在但尚未中文化，补偿任务不会误跳过。

## 验证规则

```bash
python scripts/validate_daily.py
```

会检查：

- 必需字段是否齐全；
- `localized_url` 是否以 `/zh/items/` 开头；
- 中文标题是否大面积英文；
- 中文摘要是否残留“围绕”“重点：”“Focus:”等模板；
- 原始 URL 是否存在且以 http 开头；
- 同日 URL 是否重复；
- 跨期 URL 是否重复；
- 是否出现 mock / lorem ipsum 测试数据；
- 动态详情页路由是否存在。

`quality_warnings` 只打印，不作为失败条件。

## 部署

静态部署适用于 GitHub Pages、Cloudflare Pages、Netlify。

推荐构建命令：

```bash
npm install && npm run build
```

输出目录：

```text
dist
```

## 合规与来源说明

- 不伪造来源。
- 不保存不可验证来源。
- 不绕过付费墙。
- 默认不公开完整全文镜像。
- 公开站点只保存标题、摘要、必要证据转述、元数据和原始链接。
- 对政策、融资、上市公司、医疗、法律等高风险内容使用克制表述。

## 故障排查

- 如果没有 RSS 候选，pipeline 会发布未展示过的来源索引，不会制造假新闻。
- 如果单个来源失败，记录到 `failures`，不会中断整期生成。
- 如果中文字段缺失，运行 `python scripts/backfill_localized_items.py --date YYYY-MM-DD`。
- 如果首页标题仍直连外部，检查 item 是否有 `localized_url`，并运行回填脚本。
- 如果构建失败，先运行 `python scripts/validate_daily.py` 定位字段、URL 或模板残留问题。
