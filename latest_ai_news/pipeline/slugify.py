from __future__ import annotations

import hashlib
import re
import unicodedata
from urllib.parse import urlsplit


def stable_slug(title: str, url: str = "", fallback_prefix: str = "ai-item") -> str:
    """Create a stable, URL-safe slug.

    English words, model names and company names are preserved where possible. Chinese
    or symbol-heavy titles fall back to a short hash suffix so localized URLs stay
    deterministic across reruns.
    """
    text = unicodedata.normalize("NFKD", title or "")
    text = text.encode("ascii", "ignore").decode("ascii").lower()
    text = re.sub(r"[^a-z0-9]+", "-", text).strip("-")
    text = re.sub(r"-{2,}", "-", text)
    if not text:
        try:
            path_bits = [p for p in urlsplit(url or "").path.split("/") if p]
            text = "-".join(path_bits[-3:]).lower()
            text = re.sub(r"[^a-z0-9]+", "-", text).strip("-")
        except Exception:
            text = ""
    digest = hashlib.sha1((url or title or fallback_prefix).encode("utf-8")).hexdigest()[:8]
    if not text:
        text = fallback_prefix
    text = text[:72].strip("-") or fallback_prefix
    if digest not in text:
        text = f"{text}-{digest}"
    return text
