from __future__ import annotations

from dataclasses import dataclass
from typing import List, Dict, Type

from .base import ICleaner
from .unicode_ftfy import FTFYCleaner
from .clean_text import CleanTextCleaner
from .pdf_linebreaks import PDFLineBreaksCleaner


# Registry of available cleaner names → classes
NAME2CLEANER: Dict[str, Type[ICleaner]] = {
    "ftfy": FTFYCleaner,
    "clean_text": CleanTextCleaner,
    "pdf_breaks": PDFLineBreaksCleaner,
}


@dataclass
class CleanerChain:
    """Chain-of-responsibility for text cleaners.

    The chain runs cleaners **in order** both for document-level cleaning
    (`apply`) and paragraph-level cleaning (`apply_paragraph`).
    """

    cleaners: List[ICleaner]

    @classmethod
    def from_names(cls, names: List[str]) -> "CleanerChain":
        """Create a chain from a list of cleaner names.

        Args:
            names: Cleaner identifiers (e.g. ["ftfy", "clean_text", "pdf_breaks"]).

        Returns:
            CleanerChain instance.
        """
        instances: List[ICleaner] = []
        for name in names:
            name = name.strip().lower()
            if not name:
                continue
            if name not in NAME2CLEANER:
                raise ValueError(f"Unknown cleaner: {name}. Available: {sorted(NAME2CLEANER.keys())}")
            instances.append(NAME2CLEANER[name]())
        return cls(cleaners=instances)

    # -----------------------
    # Document-level cleaning
    # -----------------------

    def apply(self, text: str) -> str:
        """Run the chain on the full document text."""
        out = text
        for c in self.cleaners:
            out = c.apply(out)
        return out

    # ------------------------
    # Paragraph-level cleaning
    # ------------------------

    def apply_paragraph(self, text: str) -> str:
        """Run the chain on a single paragraph."""
        out = text
        for c in self.cleaners:
            out = c.apply_paragraph(out)
        return out
