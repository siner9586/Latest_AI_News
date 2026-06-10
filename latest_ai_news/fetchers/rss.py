from __future__ import annotations

from datetime import datetime, timezone
from html import unescape
from urllib.request import Request, urlopen
import socket
import xml.etree.ElementTree as ET

socket.setdefaulttimeout(5)
try:
    import feedparser  # type: ignore
except Exception:
    feedparser = None


def _fallback_parse(url: str, limit: int) -> list[dict]:
    req = Request(url, headers={"User-Agent": "LatestAInewsBot/0.1 (+source-linked summaries)"})
    with urlopen(req, timeout=10) as resp:
        data = resp.read(2_000_000)
    root = ET.fromstring(data)
    rows: list[dict] = []
    for item in root.findall(".//item")[:limit]:
        rows.append({
            "title": unescape((item.findtext("title") or "").strip()),
            "link": (item.findtext("link") or "").strip(),
            "published": item.findtext("pubDate") or item.findtext("published") or item.findtext("updated") or datetime.now(timezone.utc).isoformat(),
            "summary": unescape((item.findtext("description") or "").strip()),
        })
    if not rows:
        ns = {"a": "http://www.w3.org/2005/Atom"}
        for entry in root.findall(".//a:entry", ns)[:limit]:
            link_el = entry.find("a:link", ns)
            rows.append({
                "title": unescape((entry.findtext("a:title", default="", namespaces=ns) or "").strip()),
                "link": link_el.attrib.get("href", "") if link_el is not None else "",
                "published": entry.findtext("a:published", default="", namespaces=ns) or entry.findtext("a:updated", default="", namespaces=ns) or datetime.now(timezone.utc).isoformat(),
                "summary": unescape(entry.findtext("a:summary", default="", namespaces=ns) or entry.findtext("a:content", default="", namespaces=ns) or ""),
            })
    return rows


def fetch_rss(source: dict, limit: int = 20) -> list[dict]:
    url = source.get("rss")
    if not url:
        return []
    entries: list[dict] = []
    if feedparser is not None:
        parsed = feedparser.parse(url)
        for entry in parsed.entries[:limit]:
            entries.append({
                "title": getattr(entry, "title", ""),
                "link": getattr(entry, "link", ""),
                "published": getattr(entry, "published", None) or getattr(entry, "updated", None) or datetime.now(timezone.utc).isoformat(),
                "summary": getattr(entry, "summary", "") or getattr(entry, "description", ""),
            })
    else:
        entries = _fallback_parse(url, limit)
    rows: list[dict] = []
    for entry in entries[:limit]:
        rows.append({
            "title": str(entry.get("title", "")).strip(),
            "url": str(entry.get("link", "")).strip(),
            "published_at": str(entry.get("published") or datetime.now(timezone.utc).isoformat()),
            "summary": str(entry.get("summary", ""))[:800],
            "source_name": source["name"],
            "source_url": source["url"],
            "source_type": source.get("type", "rss"),
            "language": source.get("language", "en"),
            "tags": source.get("tags", []),
            "priority": source.get("priority", "B"),
        })
    return [row for row in rows if row["title"] and row["url"]]
