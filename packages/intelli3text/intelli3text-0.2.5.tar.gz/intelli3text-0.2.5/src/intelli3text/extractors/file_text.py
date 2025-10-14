from __future__ import annotations

from pathlib import Path

from .base import IExtractor


class TextExtractor(IExtractor):
    """Local plain-text extractor for TXT/MD/CSV and other text-like files.

    Tries UTF-8 with errors ignored (robust for heterogeneous corpora).
    """

    def __init__(self, *, encoding: str = "utf-8", errors: str = "ignore") -> None:
        self.encoding = encoding
        self.errors = errors

    def extract(self, source: str) -> str:
        p = Path(source)
        if not p.exists():
            return ""
        try:
            return p.read_text(encoding=self.encoding, errors=self.errors)
        except Exception:
            return ""
