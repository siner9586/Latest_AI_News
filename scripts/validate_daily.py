from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

ROOT = Path(__file__).resolve().parents[1]
errors: list[str] = []
warnings: list[str] = []
TRACKING_PARAMS = {"utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content", "utm_id", "ref", "ref_src", "fbclid", "gclid"}
REQUIRED_ITEM_FIELDS = [
    "title", "title_original", "title_zh", "title_en", "summary_zh", "summary_en", "insight_zh",
    "key_points_zh", "background_zh", "impact_zh", "terms_zh", "evidence_zh", "source_name",
    "source_url", "original_url", "localized_url", "slug", "source_license_mode", "content_mode",
    "fetched_at", "published_at", "category", "people", "companies", "tags", "importance_score",
    "freshness_score", "credibility_score", "duplicate_group_id", "language", "translation_status",
    "extraction_status", "quality_warnings",
]
BANNED_SUMMARY_BITS = ["围绕“", "围绕\"", "Focus:", "key discussion", "new AI-related development around", "重点：", "lorem ipsum"]
LICENSE_MODES = {"summary_only", "official_public", "open_license", "owned", "allow_full_mirror"}
CONTENT_MODES = {"research_digest", "full_zh_mirror"}
TRANSLATION_STATUS = {"success", "fallback", "failed"}
EXTRACTION_STATUS = {"success", "partial", "failed"}


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


def mostly_english(text: str) -> bool:
    cjk = len(re.findall(r"[\u4e00-\u9fff]", text or ""))
    alpha = len(re.findall(r"[A-Za-z]", text or ""))
    return alpha > max(18, cjk * 1.8)


def require_path(path: Path, label: str | None = None) -> None:
    if not path.exists():
        errors.append(f"missing {label or path.relative_to(ROOT)}")


def validate_redirects() -> None:
    path = ROOT / "public" / "_redirects"
    require_path(path)
    if not path.exists():
        return
    text = path.read_text(encoding="utf-8")
    required = [
        "/daily/* /daily/index.html 200",
        "/zh/items/* /zh/item/index.html 200",
    ]
    for line in required:
        if line not in text:
            errors.append(f"missing redirect rule: {line}")


def validate_no_fragile_dynamic_routes() -> None:
    banned = [
        ROOT / "src" / "pages" / "daily" / "[date].astro",
        ROOT / "src" / "pages" / "zh" / "items" / "[date]" / "[slug].astro",
    ]
    for path in banned:
        if path.exists():
            errors.append(f"fragile getStaticPaths route must not exist: {path.relative_to(ROOT)}")


latest = load(ROOT / "data" / "index" / "latest.json")
sources = load(ROOT / "data" / "sources" / "sources.json")
people = load(ROOT / "data" / "entities" / "people.json")
companies = load(ROOT / "data" / "entities" / "companies.json")
daily_index = load(ROOT / "data" / "index" / "daily_index.json")

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

if isinstance(daily_index, dict):
    if "briefs" not in daily_index or not isinstance(daily_index.get("briefs"), list):
        errors.append("daily_index.briefs must be a list")
else:
    errors.append("daily_index must be an object")

if latest:
    for key in ["date", "items", "source_count", "candidate_count", "selected_count", "title_zh", "title_en"]:
        if key not in latest:
            errors.append(f"missing latest field {key}")
    urls: set[str] = set()
    titles: set[str] = set()
    d = latest.get("date")
    for idx, item in enumerate(latest.get("items", [])):
        for key in REQUIRED_ITEM_FIELDS:
            if item.get(key) in [None, ""] and key != "full_text_zh":
                errors.append(f"item {idx} missing {key}")
        url = item.get("original_url")
        canonical = canonical_url(str(url or ""))
        tkey = title_key(str(item.get("title_original") or item.get("title") or ""))
        if canonical in urls:
            errors.append(f"duplicate url: {url}")
        urls.add(canonical)
        if tkey in titles:
            errors.append(f"duplicate title: {item.get('title_original') or item.get('title')}")
        titles.add(tkey)
        if url and not str(url).startswith("http"):
            errors.append(f"bad item url: {url}")
        if re.search(r"\b(mock|lorem ipsum)\b", str(item.get("title", "")), re.I):
            errors.append(f"item {idx} looks like test data")
        localized = str(item.get("localized_url") or "")
        if not localized.startswith("/zh/items/"):
            errors.append(f"item {idx} bad localized_url: {localized}")
        if d and not localized.startswith(f"/zh/items/{d}/"):
            errors.append(f"item {idx} localized_url date mismatch: {localized}")
        if mostly_english(str(item.get("title_zh") or "")):
            errors.append(f"item {idx} title_zh looks English: {item.get('title_zh')}")
        summary = str(item.get("summary_zh") or "")
        if mostly_english(summary):
            errors.append(f"item {idx} summary_zh looks English: {summary[:80]}")
        if any(bit in summary for bit in BANNED_SUMMARY_BITS):
            errors.append(f"item {idx} summary_zh has template residue: {summary[:100]}")
        if item.get("source_license_mode") not in LICENSE_MODES:
            errors.append(f"item {idx} bad source_license_mode: {item.get('source_license_mode')}")
        if item.get("content_mode") not in CONTENT_MODES:
            errors.append(f"item {idx} bad content_mode: {item.get('content_mode')}")
        if item.get("translation_status") not in TRANSLATION_STATUS:
            errors.append(f"item {idx} bad translation_status: {item.get('translation_status')}")
        if item.get("extraction_status") not in EXTRACTION_STATUS:
            errors.append(f"item {idx} bad extraction_status: {item.get('extraction_status')}")
        if not isinstance(item.get("key_points_zh"), list) or len(item.get("key_points_zh") or []) < 3:
            errors.append(f"item {idx} key_points_zh too short")
        if not isinstance(item.get("evidence_zh"), list) or not item.get("evidence_zh"):
            errors.append(f"item {idx} missing evidence_zh")
        for w in item.get("quality_warnings") or []:
            warnings.append(f"item {idx} warning: {w}")

    for path in [
        ROOT / "data" / "daily" / f"{d}.json",
        ROOT / "content" / "zh" / "daily" / f"{d}.md",
        ROOT / "content" / "en" / "daily" / f"{d}.md",
        ROOT / "data" / "index" / "archive.json",
        ROOT / "data" / "index" / "daily_index.json",
        ROOT / "public" / "rss.xml",
        ROOT / "public" / "robots.txt",
        ROOT / "src" / "pages" / "daily" / "index.astro",
        ROOT / "src" / "pages" / "zh" / "item" / "index.astro",
        ROOT / "public" / "_redirects",
    ]:
        require_path(path)
    validate_redirects()
    validate_no_fragile_dynamic_routes()

    for old_path in (ROOT / "data" / "daily").glob("*.json"):
        if old_path.name == f"{d}.json":
            continue
        try:
            old = json.loads(old_path.read_text(encoding="utf-8"))
        except Exception:
            continue
        old_urls = {canonical_url(str(x.get("original_url", ""))) for x in old.get("items", [])}
        old_titles = {title_key(str(x.get("title_original") or x.get("title", ""))) for x in old.get("items", [])}
        overlap_urls = sorted(urls & old_urls)
        overlap_titles = sorted(titles & old_titles)
        if overlap_urls:
            errors.append(f"latest reuses historical urls from {old_path.name}: {overlap_urls[:3]}")
        if overlap_titles:
            errors.append(f"latest reuses historical titles from {old_path.name}: {overlap_titles[:3]}")

if warnings:
    print("warnings:")
    print("\n".join(warnings[:40]))

if errors:
    print("\n".join(errors))
    sys.exit(1)

print("validation passed")
