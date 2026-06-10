from pathlib import Path
import os

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data'
TIMEZONE = os.getenv('TIMEZONE', 'Asia/Shanghai')
SITE_URL = os.getenv('SITE_URL', 'https://siner9586.github.io/Latest_AI_News')
