from __future__ import annotations

import os
from typing import Any

from latest_ai_news.fetchers.article_page import extract_article_page
from latest_ai_news.pipeline.localize import ensure_localized_item


def should_extract(item: dict[str, Any]) -> bool:
    url = str(item.get("original_url") or "")
    if not url.startswith("http"):
        return False
    low_url = url.lower()
    if any(x in low_url for x in ["x.com/", "twitter.com/", "youtube.com/", "youtu.be/", "spotify.com", "podcasts.apple.com"]):
        return False
    tags = " ".join(item.get("tags") or []).lower()
    if "paywall" in tags:
        return False
    source = f"{item.get('source_name','')} {item.get('source_type','')}".lower()
    if any(x in source for x in ["company_blog", "research_lab", "developer", "newsletter", "openai", "anthropic", "deepmind", "nvidia", "hugging face", "microsoft", "meta", "vercel"]):
        return True
    return os.getenv("EXTRACT_MEDIA_ARTICLES", "false").lower() == "true"


def enrich_selected_items(items: list[dict[str, Any]], publish_date: str, force: bool = False) -> list[dict[str, Any]]:
    max_extract = int(os.getenv("ARTICLE_EXTRACT_MAX_ITEMS", str(min(8, len(items)))))
    enriched: list[dict[str, Any]] = []
    for idx, item in enumerate(items):
        if idx < max_extract and should_extract(item):
            try:
                extracted = extract_article_page(str(item.get("original_url") or ""))
            except Exception as exc:
                extracted = {"extraction_status": "failed", "quality_warnings": [f"extract_exception:{type(exc).__name__}"]}
        else:
            extracted = {"extraction_status": item.get("extraction_status") or "partial", "quality_warnings": ["metadata_only_source"]}
        enriched.append(ensure_localized_item(item, publish_date, extracted=extracted, force=force))
    return enriched
