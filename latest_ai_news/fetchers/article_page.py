from __future__ import annotations

import html
import re
from dataclasses import dataclass
from typing import Any
from urllib.parse import urlparse

import requests

USER_AGENT = "LatestAInewsBot/0.2 (Chinese research digests; no paywall bypass; +https://aib.ccwu.cc)"
METADATA_ONLY_HOSTS = ("x.com", "twitter.com", "youtube.com", "youtu.be", "spotify.com", "podcasts.apple.com")


@dataclass
class ArticleExtract:
    extracted_title: str = ""
    extracted_excerpt: str = ""
    extracted_text_for_analysis: str = ""
    extraction_status: str = "failed"
    quality_warnings: list[str] | None = None

    def as_dict(self) -> dict[str, Any]:
        return {
            "extracted_title": self.extracted_title,
            "extracted_excerpt": self.extracted_excerpt,
            "extracted_text_for_analysis": self.extracted_text_for_analysis,
            "extraction_status": self.extraction_status,
            "quality_warnings": self.quality_warnings or [],
        }


def clean_html_text(value: str, limit: int | None = None) -> str:
    text = html.unescape(value or "")
    text = re.sub(r"<script\b[^>]*>.*?</script>", " ", text, flags=re.I | re.S)
    text = re.sub(r"<style\b[^>]*>.*?</style>", " ", text, flags=re.I | re.S)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    if limit and len(text) > limit:
        return text[:limit].rsplit(" ", 1)[0].strip()
    return text


def meta(content: str, name: str) -> str:
    patterns = [
        rf'<meta[^>]+property=["\']{re.escape(name)}["\'][^>]+content=["\']([^"\']+)["\']',
        rf'<meta[^>]+name=["\']{re.escape(name)}["\'][^>]+content=["\']([^"\']+)["\']',
        rf'<meta[^>]+content=["\']([^"\']+)["\'][^>]+property=["\']{re.escape(name)}["\']',
        rf'<meta[^>]+content=["\']([^"\']+)["\'][^>]+name=["\']{re.escape(name)}["\']',
    ]
    for pattern in patterns:
        found = re.search(pattern, content, flags=re.I)
        if found:
            return clean_html_text(found.group(1), 260)
    return ""


def basic_extract(content: str) -> tuple[str, str, str]:
    title = meta(content, "og:title") or meta(content, "twitter:title")
    if not title:
        found = re.search(r"<title[^>]*>(.*?)</title>", content, flags=re.I | re.S)
        title = clean_html_text(found.group(1), 220) if found else ""
    excerpt = meta(content, "og:description") or meta(content, "description") or meta(content, "twitter:description")
    body = content
    article = re.search(r"<article\b[^>]*>(.*?)</article>", content, flags=re.I | re.S)
    if article:
        body = article.group(1)
    paragraphs = re.findall(r"<p\b[^>]*>(.*?)</p>", body, flags=re.I | re.S)
    text = clean_html_text(" ".join(paragraphs), 7000)
    if len(text) < 280:
        text = clean_html_text(body, 7000)
    return title, excerpt, text


def extract_article_page(url: str, timeout: int = 12) -> dict[str, Any]:
    warnings: list[str] = []
    if not url or not str(url).startswith("http"):
        return ArticleExtract(extraction_status="failed", quality_warnings=["bad_url"]).as_dict()
    host = urlparse(url).netloc.lower()
    if any(h in host for h in METADATA_ONLY_HOSTS):
        return ArticleExtract(extraction_status="partial", quality_warnings=["metadata_only_source"]).as_dict()
    try:
        response = requests.get(
            url,
            timeout=timeout,
            headers={"User-Agent": USER_AGENT, "Accept": "text/html,application/xhtml+xml"},
            allow_redirects=True,
        )
        if response.status_code in {401, 402, 403, 451}:
            return ArticleExtract(extraction_status="partial", quality_warnings=["restricted_or_paywalled"]).as_dict()
        if response.status_code >= 400:
            return ArticleExtract(extraction_status="failed", quality_warnings=[f"http_{response.status_code}"]).as_dict()
        content = response.text[:2_500_000]
    except Exception as exc:
        return ArticleExtract(extraction_status="failed", quality_warnings=[f"request_failed:{type(exc).__name__}"]).as_dict()

    extracted_title = ""
    extracted_excerpt = ""
    extracted_text = ""
    try:
        import trafilatura  # type: ignore

        extracted_text = trafilatura.extract(
            content,
            url=url,
            include_comments=False,
            include_tables=False,
            favor_precision=True,
        ) or ""
        extracted_text = clean_html_text(extracted_text, 7000)
    except Exception:
        warnings.append("trafilatura_unavailable")
    try:
        title, excerpt, fallback_text = basic_extract(content)
        extracted_title = title
        extracted_excerpt = excerpt
        if len(extracted_text) < 400:
            extracted_text = fallback_text
    except Exception as exc:
        warnings.append(f"html_extract_failed:{type(exc).__name__}")
    status = "success" if len(extracted_text) >= 500 else ("partial" if extracted_title or extracted_excerpt or extracted_text else "failed")
    if status != "success":
        warnings.append("limited_extracted_text")
    return ArticleExtract(
        extracted_title=extracted_title,
        extracted_excerpt=extracted_excerpt,
        extracted_text_for_analysis=extracted_text,
        extraction_status=status,
        quality_warnings=warnings,
    ).as_dict()
