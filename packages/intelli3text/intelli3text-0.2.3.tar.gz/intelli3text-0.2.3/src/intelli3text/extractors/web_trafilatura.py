from __future__ import annotations

from pathlib import Path
from typing import Optional

import requests
import trafilatura

from .base import IExtractor


class WebExtractor(IExtractor):
    """HTML/HTTP extractor using `trafilatura` with a `requests` fallback.

    Strategy:
        1) Try `trafilatura.fetch_url(url)` (handles many site quirks).
        2) If it returns None, fall back to `requests.get(url)` + `trafilatura.extract(html)`.

    The result is the **main article text** (readability-like), not raw HTML.
    """

    def __init__(
        self,
        *,
        timeout: float | tuple[float, float] = (10, 20),
        user_agent: Optional[str] = None,
    ) -> None:
        self.timeout = timeout
        self.user_agent = user_agent or "intelli3text/1.0 (+https://github.com/jeffersonspeck/intelli3text)"

    def extract(self, source: str) -> str:
        if not source.startswith(("http://", "https://")):
            return ""  # not a URL

        # 1) Try trafilatura built-in fetcher
        try:
            downloaded = trafilatura.fetch_url(source)
        except Exception:
            downloaded = None

        # 2) Fallback: raw requests
        if not downloaded:
            try:
                r = requests.get(source, timeout=self.timeout, headers={"User-Agent": self.user_agent})
                r.raise_for_status()
                downloaded = r.text
            except Exception:
                return ""

        try:
            text = trafilatura.extract(
                downloaded,
                include_comments=False,
                include_tables=False,
            )
            return text or ""
        except Exception:
            return ""
