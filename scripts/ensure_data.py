from __future__ import annotations

from pathlib import Path
from latest_ai_news.pipeline.run_daily import run

ROOT = Path(__file__).resolve().parents[1]
latest = ROOT / 'data' / 'index' / 'latest.json'

if latest.exists():
    print('data exists; skip generation')
else:
    run(__import__('datetime').date.today().isoformat(), 18, False)
    print('generated initial data')
