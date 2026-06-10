from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

ROOT = Path(__file__).resolve().parents[1]
errors: list[str] = []
TRACKING_PARAMS = {"utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content", "utm_id", "ref", "ref_src", "fbclid", "gclid"}


def canonical_url(url: str) -> str:
    if not url:
        return ""
    try:
        parts = urlsplit(url.strip())
        query = urlencode([(k, v) for k, v in parse_qsl(parts.query, keep_blank_values=True) if k.lower() not in TRACKING_PARAMS])
        path = parts.path.rstrip("/") or "/"
        return urlunsplit((parts.scheme.lower(), parts.netloc.lower(), path, query, ""))
    except Exception:
        return url.strip().rstrip("/")


def title_key(title: str) -> str:
    text = (title or "").lower()
    text = re.sub(r"[^\w\u4e00-\u9fff]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def load(path: Path):
    if not path.exists():
        errors.append(f"missing {path.relative_to(ROOT)}")
        return None
    return json.loads(path.read_text(encoding="utf-8"))

latest = load(ROOT / "data" / "index" / "latest.json")
sources = load(ROOT / "data" / "sources" / "sources.json")
people = load(ROOT / "data" / "entities" / "people.json")
companies = load(ROOT / "data" / "entities" / "companies.json")

if isinstance(sources, list):
    if len(sources) < 80:
        errors.append(f"sources registry too small: {len(sources)} < 80")
    for rec in sources:
        if not rec.get("name") or not rec.get("type") or not rec.get("url"):
            errors.append(f"bad source record: {rec}")
        if rec.get("url") and not rec["url"].startswith("http"):
            errors.append(f"bad source url: {rec}")
else:
    errors.append("sources registry must be a list")

if isinstance(people, list):
    if len(people) < 80:
        errors.append(f"people registry too small: {len(people)} < 80")
else:
    errors.append("people registry must be a list")

if isinstance(companies, list):
    if len(companies) < 50:
        errors.append(f"companies registry too small: {len(companies)} < 50")
    for rec in companies:
        if rec.get("url") and not rec["url"].startswith("http"):
            errors.append(f"bad company url: {rec}")
else:
    errors.append("companies registry must be a list")

if latest:
    for key in ["date", "items", "source_count", "candidate_count", "selected_count", "title_zh", "title_en"]:
        if key not in latest:
            errors.append(f"missing latest field {key}")
    urls: set[str] = set()
    titles: set[str] = set()
    for idx, item in enumerate(latest.get("items", [])):
        for key in ["title", "source_name", "source_url", "original_url", "published_at", "category", "summary_zh", "summary_en", "importance_score", "freshness_score", "credibility_score", "duplicate_group_id"]:
            if item.get(key) in [None, ""]:
                errors.append(f"item {idx} missing {key}")
        url = item.get("original_url")
        canonical = canonical_url(str(url or ""))
        tkey = title_key(str(item.get("title", "")))
        if canonical in urls:
            errors.append(f"duplicate url: {url}")
        urls.add(canonical)
        if tkey in titles:
            errors.append(f"duplicate title: {item.get('title')}")
        titles.add(tkey)
        if url and not str(url).startswith("http"):
            errors.append(f"bad item url: {url}")
        if re.search(r"\b(mock|lorem ipsum)\b", item.get("title", ""), re.I):
            errors.append(f"item {idx} looks like test data")
    d = latest.get("date")
    for path in [
        ROOT / "data" / "daily" / f"{d}.json",
        ROOT / "content" / "zh" / "daily" / f"{d}.md",
        ROOT / "content" / "en" / "daily" / f"{d}.md",
        ROOT / "data" / "index" / "archive.json",
        ROOT / "public" / "rss.xml",
        ROOT / "public" / "robots.txt",
    ]:
        if not path.exists():
            errors.append(f"missing generated artifact {path.relative_to(ROOT)}")
    for old_path in (ROOT / "data" / "daily").glob("*.json"):
        if old_path.name == f"{d}.json":
            continue
        try:
            old = json.loads(old_path.read_text(encoding="utf-8"))
        except Exception:
            continue
        old_urls = {canonical_url(str(x.get("original_url", ""))) for x in old.get("items", [])}
        old_titles = {title_key(str(x.get("title", ""))) for x in old.get("items", [])}
        overlap_urls = sorted(urls & old_urls)
        overlap_titles = sorted(titles & old_titles)
        if overlap_urls:
            errors.append(f"latest reuses historical urls from {old_path.name}: {overlap_urls[:3]}")
        if overlap_titles:
            errors.append(f"latest reuses historical titles from {old_path.name}: {overlap_titles[:3]}")

if errors:
    print("\n".join(errors))
    sys.exit(1)

print("validation passed")
