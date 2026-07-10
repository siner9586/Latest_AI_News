from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from latest_ai_news.config import DATA


def load_json(path: Path) -> dict | None:
    try:
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        print(f"skip invalid json {path}: {exc}")
    return None


def write_daily_index(limit: int = 366) -> dict:
    index_dir = DATA / "index"
    daily_dir = DATA / "daily"
    index_dir.mkdir(parents=True, exist_ok=True)

    briefs: list[dict] = []
    seen: set[str] = set()

    for path in sorted(daily_dir.glob("*.json"), reverse=True) if daily_dir.exists() else []:
        brief = load_json(path)
        d = str((brief or {}).get("date") or path.stem).strip()
        if not brief or not d or d in seen:
            continue
        seen.add(d)
        briefs.append(brief)
        if len(briefs) >= limit:
            break

    latest = load_json(index_dir / "latest.json")
    latest_date = str((latest or {}).get("date") or "").strip()
    if latest and latest_date and latest_date not in seen:
        briefs.insert(0, latest)
        seen.add(latest_date)

    briefs.sort(key=lambda item: str(item.get("date") or ""), reverse=True)
    payload = {
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "count": len(briefs[:limit]),
        "briefs": briefs[:limit],
    }
    path = index_dir / "daily_index.json"
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"wrote {path.relative_to(ROOT)} with {payload['count']} briefs")
    return payload


if __name__ == "__main__":
    write_daily_index()
