from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from latest_ai_news.pipeline.run_daily import run

latest = ROOT / 'data' / 'index' / 'latest.json'

if latest.exists():
    print('data exists; skip generation')
else:
    run(date.today().isoformat(), 18, False)
    print('generated initial data')
