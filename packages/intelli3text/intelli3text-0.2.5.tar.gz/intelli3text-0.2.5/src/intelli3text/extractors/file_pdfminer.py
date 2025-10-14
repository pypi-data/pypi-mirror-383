from __future__ import annotations

from pathlib import Path
from typing import Union

from pdfminer.high_level import extract_text as pdf_extract_text

from .base import IExtractor


class PDFExtractor(IExtractor):
    """Local PDF extractor using `pdfminer.six`.

    Returns the best-effort linearized text. Complex layouts may not be perfect,
    but follow-up cleaners/normalizers handle common artifacts (hyphenation, breaks).
    """

    def extract(self, source: str) -> str:
        p = Path(source)
        if not p.exists() or p.suffix.lower() != ".pdf":
            return ""
        try:
            text = pdf_extract_text(p)
            return text or ""
        except Exception:
            return ""
