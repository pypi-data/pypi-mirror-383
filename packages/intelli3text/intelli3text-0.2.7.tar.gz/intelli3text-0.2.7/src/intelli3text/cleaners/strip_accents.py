from __future__ import annotations
import unicodedata
from .base import ICleaner

def _strip_accents(s: str) -> str:
    nfkd = unicodedata.normalize("NFD", s)
    no_marks = "".join(ch for ch in nfkd if unicodedata.category(ch) != "Mn")
    return unicodedata.normalize("NFC", no_marks)

class StripAccentsCleaner(ICleaner):
    """Remove todos os diacríticos (acentos)."""
    def apply(self, text: str) -> str:
        return _strip_accents(text)

    def apply_paragraph(self, text: str) -> str:
        return _strip_accents(text)
