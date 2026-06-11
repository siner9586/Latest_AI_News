# Latest AI News

Latest AI News is a lightweight bilingual AI intelligence site for AI executives, founders, researchers, investors, top podcasts, YouTube channels, X accounts, company blogs, research labs, developer ecosystems and major media coverage.

The project is initialized for `siner9586/Latest_AI_News` as an Astro + TypeScript static site and a Python source-linked news pipeline. It updates every day at **06:18 Beijing/Taipei time**, with redundant compensation checks every 15 minutes until **09:33 Beijing/Taipei time**. If the issue for the current date already exists, compensation runs skip automatically and do not publish duplicates.

## Core features

- Daily bilingual AI news brief with Chinese and English pages using the same layout.
- Structured source registry for podcasts, YouTube, X accounts, media, company blogs, research labs, investor content, newsletters and developer sources.
- Structured entity registry for AI people, companies, labs, platforms and investors.
- Source-linked generation: every selected item must include `original_url`, `source_name`, `published_at`, `category`, bilingual summaries and scoring fields.
- Lightweight static output: Markdown, JSON, RSS and Astro pages; no database required.
- Failure-tolerant fetching: RSS failures are logged but do not break the whole workflow.
- Redundant idempotent scheduling: GitHub Actions gets multiple chances each morning; existing daily issues are detected and skipped.
- Compliance principles: no paywall bypass, no full-text copying, no fake links, no test data in production briefs.

## Initial registry coverage

The seed registry contains more than the required baseline:

- 148 structured sources
- 89 people
- 62 companies and institutions

Key source groups include Lenny's Podcast, Peter Yang, Every, Redpoint, Sequoia, South Park Commons, Google DeepMind, No Priors, a16z AI, Latent Space, The AI Daily Brief, Y Combinator, Lex Fridman, Dwarkesh, Hard Fork, OpenAI, Anthropic, Meta AI, Microsoft AI, NVIDIA, Hugging Face, MIT Technology Review, TechCrunch, The Verge, Reuters, Bloomberg, FT, WSJ, NYT, The Information, Simon Willison, Interconnects and selected Chinese AI media.

## Local development

```bash
npm install
pip install -r requirements.txt
python -m latest_ai_news.pipeline.run_daily --date 2026-06-10
python scripts/validate_daily.py
npm run dev
npm run build
```

`npm run build` runs the Python pipeline first, then builds Astro, so a fresh clone can generate `data/index/latest.json`, daily Markdown, RSS and archive files before the static build.

## Manual daily generation

```bash
python -m latest_ai_news.pipeline.run_daily \
  --date 2026-06-10 \
  --max-items 18 \
  --language all
```

Optional flags:

- `--source-date YYYY-MM-DD`: reserved for future source-date backfill logic.
- `--force`: force regeneration.
- `--dry-run`: print generated brief without writing files.
- `--max-items`: maximum selected items.
- `--language`: `all`, `zh`, or `en`.

## GitHub Actions

### Daily AI News

`.github/workflows/daily-news.yml` uses multi-point redundant scheduling:

```yaml
cron: '18 22 * * *'  # 06:18 Beijing/Taipei time, primary run
cron: '33 22 * * *'  # 06:33 compensation check
cron: '48 22 * * *'  # 06:48 compensation check
cron: '3 23 * * *'   # 07:03 compensation check
cron: '18 23 * * *'  # 07:18 compensation check
cron: '33 23 * * *'  # 07:33 compensation check
cron: '48 23 * * *'  # 07:48 compensation check
cron: '3 0 * * *'    # 08:03 compensation check
cron: '18 0 * * *'   # 08:18 compensation check
cron: '33 0 * * *'   # 08:33 compensation check
cron: '48 0 * * *'   # 08:48 compensation check
cron: '3 1 * * *'    # 09:03 compensation check
cron: '18 1 * * *'   # 09:18 compensation check
cron: '33 1 * * *'   # 09:33 final compensation check
```

This means the project no longer has only one daily chance. The 06:18 run attempts generation first; later runs check whether the current Beijing/Taipei date already has `data/daily/YYYY-MM-DD.json`, `content/zh/daily/YYYY-MM-DD.md` and `content/en/daily/YYYY-MM-DD.md`. If all exist and `force` is not enabled, the run exits cleanly without generating or committing duplicate content.

The workflow also uses `concurrency` with `cancel-in-progress: false`, so redundant runs are serialized rather than racing each other. Before the idempotency gate, it pulls the latest `main` so a compensation run sees content committed by an earlier run.

The workflow supports manual `workflow_dispatch` with `publish_date`, `source_date`, `force`, `dry_run`, `max_items` and `language`.

Main steps:

1. checkout
2. pull latest branch state
3. resolve Beijing/Taipei publish date
4. skip if today's issue already exists, unless forced
5. setup Python and Node
6. install dependencies
7. run daily pipeline
8. validate generated data
9. build Astro site
10. commit generated content and push to `main`

### Build

`.github/workflows/build.yml` runs the daily generator, validation, source checks and `npm run build` on push and pull request.

## Environment variables

Core flow does not require paid APIs.

- `SITE_URL`: canonical deployed site URL.
- `TIMEZONE`: default `Asia/Shanghai`.
- `YOUTUBE_API_KEY`: optional future YouTube enrichment; RSS works without it.
- `X_BEARER_TOKEN`: optional future X API fetching; without it X accounts remain metadata-only.
- `OPENAI_API_KEY`: optional future high-quality summarization; without it rule-based summaries are generated.
- `GITHUB_TOKEN`: automatically provided by GitHub Actions.

## Data layout

Generated by the pipeline:

```text
data/sources/sources.json
data/sources/last_seen.json
data/entities/people.json
data/entities/companies.json
data/daily/YYYY-MM-DD.json
data/index/latest.json
data/index/archive.json
content/zh/daily/YYYY-MM-DD.md
content/en/daily/YYYY-MM-DD.md
public/rss.xml
```

Seeded in code:

```text
latest_ai_news/registry.py
```

## Adding sources

Add or edit source records after generation under `data/sources/sources.json`, then back-port stable additions into `latest_ai_news/registry.py` or replace the compressed registry through the pipeline tools. Required fields include `name`, `type`, `url`, `rss`, `language`, `priority`, `paywall`, `fetch_method` and `tags`.

Prefer official RSS, podcast RSS or YouTube RSS. For media behind paywalls, keep only title, public metadata and outbound links.

## Deployment

The repository is static and can deploy to GitHub Pages, Cloudflare Pages or Netlify.

Recommended build command:

```bash
npm install && npm run build
```

Output directory:

```text
dist
```

## Copyright and compliance

- Do not copy full media articles.
- Do not save full podcast transcripts or video captions as public content.
- Do not bypass paywalls.
- Always link to the original source.
- Clearly distinguish official announcements, media reports, rumors and analysis.
- Use cautious language for policy, financing, markets, medicine, law and public-company topics.

## Troubleshooting

- If no RSS candidates are found, the pipeline publishes a source-index brief rather than inventing news.
- If one source fails, the workflow logs it in `failures` and continues.
- If the first scheduled run is missed by GitHub, the compensation schedule checks again every 15 minutes until 09:33 Beijing/Taipei time.
- If a daily issue already exists, compensation runs skip cleanly and do not duplicate the date.
- Run `python scripts/validate_daily.py` before build to catch missing URLs, missing fields, duplicate URLs or insufficient registry size.
- Run `python scripts/check_sources.py` to inspect source coverage by type.
