from __future__ import annotations

from collections import Counter
from latest_ai_news.registry import build_sources, build_people, build_companies

sources = build_sources()
people = build_people()
companies = build_companies()

print(f"sources={len(sources)} people={len(people)} companies={len(companies)}")
for typ, count in sorted(Counter(s["type"] for s in sources).items()):
    print(f"{typ}: {count}")

if len(sources) < 80 or len(people) < 80 or len(companies) < 50:
    raise SystemExit("registry coverage below required baseline")

bad = [s for s in sources if not s.get("url", "").startswith("http")]
if bad:
    raise SystemExit(f"bad source urls: {bad[:3]}")
