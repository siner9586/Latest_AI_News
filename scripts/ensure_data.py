from __future__ import annotations

import json
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from latest_ai_news.pipeline.localize import ensure_localized_brief
from latest_ai_news.pipeline.run_daily import run

latest = ROOT / "data" / "index" / "latest.json"

if latest.exists():
    try:
        data = json.loads(latest.read_text(encoding="utf-8"))
        patched = ensure_localized_brief(data)
        if patched != data:
            latest.write_text(json.dumps(patched, ensure_ascii=False, indent=2), encoding="utf-8")
            daily = ROOT / "data" / "daily" / f"{patched.get('date')}.json"
            if daily.exists():
                daily.write_text(json.dumps(patched, ensure_ascii=False, indent=2), encoding="utf-8")
            print("data exists; localized fields patched")
        else:
            print("data exists; skip generation")
    except Exception as exc:
        print(f"data exists but localization check failed: {exc}; skip generation")
else:
    run(date.today().isoformat(), 18, False)
    print("generated initial data")
