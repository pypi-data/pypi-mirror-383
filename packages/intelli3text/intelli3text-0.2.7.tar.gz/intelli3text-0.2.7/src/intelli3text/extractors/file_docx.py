from __future__ import annotations

from pathlib import Path

from docx import Document

from .base import IExtractor


class DocxExtractor(IExtractor):
    """Local DOCX extractor using `python-docx`."""

    def extract(self, source: str) -> str:
        p = Path(source)
        if not p.exists() or p.suffix.lower() != ".docx":
            return ""
        try:
            doc = Document(p)
            return "\n".join(par.text for par in doc.paragraphs) or ""
        except Exception:
            return ""
