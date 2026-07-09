from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from latest_ai_news.pipeline.localize import ensure_localized_brief
from latest_ai_news.pipeline.run_daily import write_outputs


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def changed_fields(before: dict[str, Any], after: dict[str, Any]) -> list[str]:
    fields = ["title_zh", "title_original", "title_en", "summary_zh", "insight_zh", "key_points_zh", "background_zh", "impact_zh", "terms_zh", "evidence_zh", "localized_url", "slug", "source_license_mode", "content_mode", "translation_status", "extraction_status", "quality_warnings"]
    return [field for field in fields if before.get(field) != after.get(field)]


def process_file(path: Path, force: bool, dry_run: bool, max_items: int | None = None) -> bool:
    data = read_json(path)
    if max_items is not None and max_items > 0:
        data["items"] = (data.get("items") or [])[:max_items]
    before_items = list(data.get("items") or [])
    patched = ensure_localized_brief(data, force=force)
    changed = patched != data
    print(f"{path.relative_to(ROOT)}: {'changed' if changed else 'ok'}")
    for idx, (before, after) in enumerate(zip(before_items, patched.get("items", []))):
        fields = changed_fields(before, after)
        if fields:
            print(f"  item {idx + 1}: {', '.join(fields)}")
    if changed and not dry_run:
        path.write_text(json.dumps(patched, ensure_ascii=False, indent=2), encoding="utf-8")
        latest = ROOT / "data" / "index" / "latest.json"
        if path.name == f"{patched.get('date')}.json":
            current_latest = read_json(latest) if latest.exists() else None
            if not current_latest or current_latest.get("date") == patched.get("date"):
                write_outputs(patched)
    return changed


def main() -> None:
    parser = argparse.ArgumentParser(description="Backfill Chinese localized item fields for daily JSON files.")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--date", help="Backfill one date, YYYY-MM-DD")
    group.add_argument("--all", action="store_true", help="Backfill every data/daily/*.json file")
    parser.add_argument("--force", action="store_true", help="Regenerate rule-based Chinese fields even if they already exist")
    parser.add_argument("--dry-run", action="store_true", help="Print changes without writing files")
    parser.add_argument("--max-items", type=int, default=None, help="Optional cap for debugging")
    args = parser.parse_args()

    daily_dir = ROOT / "data" / "daily"
    if args.date:
        paths = [daily_dir / f"{args.date}.json"]
    else:
        paths = sorted(daily_dir.glob("*.json"))
    missing = [p for p in paths if not p.exists()]
    if missing:
        raise SystemExit("missing daily files: " + ", ".join(str(p.relative_to(ROOT)) for p in missing))
    changed = 0
    for path in paths:
        changed += int(process_file(path, args.force, args.dry_run, args.max_items))
    latest = ROOT / "data" / "index" / "latest.json"
    if latest.exists() and not args.dry_run:
        data = read_json(latest)
        patched = ensure_localized_brief(data, force=args.force)
        if patched != data:
            latest.write_text(json.dumps(patched, ensure_ascii=False, indent=2), encoding="utf-8")
            changed += 1
    print(f"backfill complete: {changed} file(s) changed")


if __name__ == "__main__":
    main()
