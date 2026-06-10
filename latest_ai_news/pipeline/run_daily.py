from __future__ import annotations

import argparse
import os
import hashlib
import html
import json
import re
from datetime import date, datetime, timezone

from latest_ai_news.config import DATA, ROOT, SITE_URL
from latest_ai_news.fetchers.rss import fetch_rss
from latest_ai_news.registry import build_companies, build_people, build_sources

CATEGORY_LABELS = {
    "executives": "高管 / 名人动态",
    "models-products": "模型与产品发布",
    "company-industry": "公司与产业",
    "funding-startups": "投资与创业",
    "research-open-source": "研究与开源",
    "policy-regulation": "政策与监管",
    "podcasts-interviews": "值得听 / 值得看",
    "source-index": "来源索引",
}

TOP_PEOPLE = {"sam altman", "demis hassabis", "dario amodei", "jensen huang", "satya nadella", "sundar pichai", "mark zuckerberg", "ilya sutskever", "andrej karpathy", "yann lecun", "fei-fei li", "andrew ng", "elon musk"}
TOP_COMPANIES = {"openai", "anthropic", "deepmind", "google", "microsoft", "meta", "nvidia", "xai", "perplexity", "mistral", "hugging face", "yc", "a16z", "sequoia"}


def ensure_registries() -> tuple[list[dict], list[dict], list[dict]]:
    sources = build_sources()
    people = build_people()
    companies = build_companies()
    (DATA / "sources").mkdir(parents=True, exist_ok=True)
    (DATA / "entities").mkdir(parents=True, exist_ok=True)
    (DATA / "sources" / "sources.json").write_text(json.dumps(sources, ensure_ascii=False, indent=2), encoding="utf-8")
    (DATA / "entities" / "people.json").write_text(json.dumps(people, ensure_ascii=False, indent=2), encoding="utf-8")
    (DATA / "entities" / "companies.json").write_text(json.dumps(companies, ensure_ascii=False, indent=2), encoding="utf-8")
    return sources, people, companies


def category_for(row: dict) -> str:
    text = f"{row.get('title','')} {' '.join(row.get('tags', []))} {row.get('source_type','')}".lower()
    if any(word in text for word in ["podcast", "interview", "youtube", "lex", "dwarkesh", "latent space"]):
        return "podcasts-interviews"
    if any(word in text for word in ["gpt", "claude", "gemini", "model", "api", "launch", "product", "copilot", "grok"]):
        return "models-products"
    if any(word in text for word in ["paper", "research", "open source", "github", "hugging face", "benchmark"]):
        return "research-open-source"
    if any(word in text for word in ["funding", "startup", "vc", "a16z", "sequoia", "yc"]):
        return "funding-startups"
    if any(word in text for word in ["policy", "regulation", "safety", "law", "copyright", "governance"]):
        return "policy-regulation"
    if any(word in text for word in ["ceo", "founder", "executive", "sam altman", "demis", "jensen"]):
        return "executives"
    return "company-industry"


def extract_entities(text: str, people: list[dict], companies: list[dict]) -> tuple[list[str], list[str]]:
    low = text.lower()
    ps = [p["name"] for p in people if p["name"].lower() in low][:6]
    cs = [c["name"] for c in companies if c["name"].lower() in low][:6]
    return ps, cs


def score(row: dict, category: str, people: list[str], companies: list[str]) -> tuple[float, float, float]:
    priority = {"S": 32, "A": 24, "B": 14, "C": 8}.get(row.get("priority", "B"), 10)
    text = f"{row.get('title','')} {' '.join(row.get('tags', []))}".lower()
    people_boost = 18 if any(p.lower() in TOP_PEOPLE for p in people) else 0
    company_boost = 16 if any(c.lower() in text or c.lower() in TOP_COMPANIES for c in companies) else 0
    product_boost = 12 if category in ["models-products", "research-open-source"] else 0
    podcast_boost = 8 if category == "podcasts-interviews" else 0
    credibility = 90 if row.get("priority") in ["S", "A"] else 76
    freshness = 72
    return priority + people_boost + company_boost + product_boost + podcast_boost, freshness, credibility


def brief_summaries(row: dict, category: str) -> tuple[str, str]:
    title = row["title"].strip()
    source = row["source_name"]
    zh = f"据 {source} 发布，{title}。该条目归入「{CATEGORY_LABELS.get(category, category)}」，已保留原始链接，便于继续追踪相关人物、机构、产品或研究进展。"
    en = f"{source} published: {title}. The item is classified under {category} and keeps the original link for follow-up tracking of people, companies, products or research."
    return zh[:240], en[:260]


def normalize(raw: list[dict], people: list[dict], companies: list[dict]) -> list[dict]:
    now = datetime.now(timezone.utc).isoformat()
    seen: set[str] = set()
    out: list[dict] = []
    for row in raw:
        url = row.get("url", "").strip()
        title = re.sub(r"\s+", " ", row.get("title", "")).strip()
        if not url or not title or url in seen:
            continue
        seen.add(url)
        cat = category_for(row)
        ps, cs = extract_entities(title, people, companies)
        importance, freshness, credibility = score(row, cat, ps, cs)
        zh, en = brief_summaries({**row, "title": title}, cat)
        out.append({
            "title": title,
            "summary_zh": zh,
            "summary_en": en,
            "source_name": row["source_name"],
            "source_url": row["source_url"],
            "original_url": url,
            "published_at": str(row.get("published_at") or now),
            "fetched_at": now,
            "category": cat,
            "people": ps,
            "companies": cs,
            "tags": row.get("tags", [])[:8],
            "importance_score": round(float(importance), 2),
            "freshness_score": round(float(freshness), 2),
            "credibility_score": round(float(credibility), 2),
            "duplicate_group_id": hashlib.sha1(url.encode("utf-8")).hexdigest()[:12],
            "language": row.get("language", "en"),
        })
    return sorted(out, key=lambda x: (x["importance_score"], x["published_at"]), reverse=True)


def fallback_source_index(sources: list[dict], publish_date: str, limit: int) -> list[dict]:
    now = datetime.now(timezone.utc).isoformat()
    chosen = sorted(sources, key=lambda s: {"S": 0, "A": 1, "B": 2, "C": 3}.get(s.get("priority", "B"), 2))[:limit]
    items = []
    for s in chosen:
        url = s["url"]
        title = f"Source index initialized: {s['name']}"
        items.append({
            "title": title,
            "summary_zh": f"初始化来源索引：{s['name']} 已纳入 AI 新闻雷达。该条目不是模拟新闻，而是正式来源库建设记录；后续流水线将优先使用其 RSS、播客 RSS、YouTube RSS 或公开页面元数据。",
            "summary_en": f"Source index initialized: {s['name']} is now tracked by the AI news radar. This is not fake news; it is a production source-registry record for future RSS, podcast RSS, YouTube RSS or public metadata fetching.",
            "source_name": s["name"],
            "source_url": url,
            "original_url": url,
            "published_at": publish_date,
            "fetched_at": now,
            "category": "source-index",
            "people": [],
            "companies": [],
            "tags": s.get("tags", [])[:8],
            "importance_score": 60,
            "freshness_score": 10,
            "credibility_score": 90,
            "duplicate_group_id": hashlib.sha1(url.encode("utf-8")).hexdigest()[:12],
            "language": s.get("language", "en"),
        })
    return items


def write_outputs(brief: dict) -> None:
    d = brief["date"]
    for p in [DATA / "daily", DATA / "index", DATA / "sources", ROOT / "content" / "zh" / "daily", ROOT / "content" / "en" / "daily", ROOT / "public"]:
        p.mkdir(parents=True, exist_ok=True)
    (DATA / "daily" / f"{d}.json").write_text(json.dumps(brief, ensure_ascii=False, indent=2), encoding="utf-8")
    (DATA / "index" / "latest.json").write_text(json.dumps(brief, ensure_ascii=False, indent=2), encoding="utf-8")
    archive_path = DATA / "index" / "archive.json"
    old = {"items": []}
    if archive_path.exists():
        try:
            old = json.loads(archive_path.read_text(encoding="utf-8"))
        except Exception:
            old = {"items": []}
    row = {"date": d, "source_count": brief["source_count"], "candidate_count": brief["candidate_count"], "selected_count": brief["selected_count"], "title": brief["title_zh"]}
    items = [x for x in old.get("items", []) if x.get("date") != d]
    items.insert(0, row)
    archive_path.write_text(json.dumps({"items": items[:365]}, ensure_ascii=False, indent=2), encoding="utf-8")
    (DATA / "sources" / "last_seen.json").write_text(json.dumps({"updated_at": datetime.now(timezone.utc).isoformat(), "failures": brief.get("failures", [])}, ensure_ascii=False, indent=2), encoding="utf-8")
    zh_lines = ["---", f"title: AI 新闻简报 · {d}", f"date: {d}", "---", "", brief["overview_zh"], ""]
    en_lines = ["---", f"title: English AI News Brief · {d}", f"date: {d}", "---", "", brief["overview_en"], ""]
    for item in brief["items"]:
        zh_lines += [f"## {item['title']}", "", item["summary_zh"], "", f"来源：{item['original_url']}", ""]
        en_lines += [f"## {item['title']}", "", item["summary_en"], "", f"Source: {item['original_url']}", ""]
    (ROOT / "content" / "zh" / "daily" / f"{d}.md").write_text("\n".join(zh_lines), encoding="utf-8")
    (ROOT / "content" / "en" / "daily" / f"{d}.md").write_text("\n".join(en_lines), encoding="utf-8")
    rss_items = []
    for item in brief["items"]:
        rss_items.append(f"<item><title>{html.escape(item['title'])}</title><link>{html.escape(item['original_url'])}</link><description>{html.escape(item['summary_en'])}</description><pubDate>{html.escape(item['published_at'])}</pubDate></item>")
    rss = f"""<?xml version="1.0" encoding="UTF-8"?><rss version="2.0"><channel><title>Latest AI News</title><link>{SITE_URL}</link><description>Daily source-linked AI intelligence</description>{''.join(rss_items)}</channel></rss>"""
    (ROOT / "public" / "rss.xml").write_text(rss, encoding="utf-8")
    (ROOT / "public" / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {SITE_URL.rstrip('/')}/sitemap-index.xml\n", encoding="utf-8")


def run(publish_date: str, max_items: int, dry_run: bool) -> dict:
    sources, people, companies = ensure_registries()
    raw: list[dict] = []
    failures: list[dict] = []
    fetch_cap = int(os.getenv("MAX_FETCH_SOURCES", "30"))
    fetchable = [s for s in sources if s.get("rss")]
    for source in fetchable[:fetch_cap]:
        try:
            raw.extend(fetch_rss(source, limit=8))
        except Exception as exc:
            failures.append({"source": source.get("name"), "error": str(exc)[:220]})
    items = normalize(raw, people, companies)
    selected = items[:max_items] if items else fallback_source_index(sources, publish_date, max_items)
    categories = sorted({x["category"] for x in selected})
    brief = {
        "date": publish_date,
        "title_zh": f"AI 新闻简报 · {publish_date}",
        "title_en": f"English AI News Brief · {publish_date}",
        "overview_zh": f"本期从 {len(sources)} 个结构化来源中生成，候选 {len(raw)} 条，入选 {len(selected)} 条。所有条目均保留原始来源链接；若真实抓取不足，则仅发布来源索引初始化记录，不用测试数据冒充更新。",
        "overview_en": f"This brief is generated from {len(sources)} structured sources with {len(raw)} candidates and {len(selected)} selected items. Every item keeps an original source link; if live fetching is insufficient, the site publishes source-index records instead of fake news.",
        "source_count": len(sources),
        "candidate_count": len(raw),
        "selected_count": len(selected),
        "categories": categories,
        "items": selected,
        "failures": failures,
    }
    if not dry_run:
        write_outputs(brief)
    return brief


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", default=date.today().isoformat())
    parser.add_argument("--source-date", default=None)
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--max-items", type=int, default=18)
    parser.add_argument("--language", default="all", choices=["all", "zh", "en"])
    args = parser.parse_args()
    brief = run(args.date, args.max_items, args.dry_run)
    if args.dry_run:
        print(json.dumps(brief, ensure_ascii=False, indent=2))
    else:
        print(f"generated {args.date}: {brief['selected_count']} selected, {brief['candidate_count']} candidates, {len(brief['failures'])} failures")


if __name__ == "__main__":
    main()
