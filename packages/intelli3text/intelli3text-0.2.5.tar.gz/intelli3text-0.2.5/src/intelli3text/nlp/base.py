from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List


class INormalizer(ABC):
    """Abstract interface for paragraph splitting and text normalization.

    Implementations should:
      - Split a raw document into paragraphs robustly (handling PDF/HTML quirks).
      - Normalize text for downstream tasks (e.g., lemmatization, stopword removal).
    """

    @abstractmethod
    def split_paragraphs(self, text: str) -> List[str]:
        """Return a list of cleaned paragraph strings from a raw document."""
        raise NotImplementedError

    @abstractmethod
    def normalize(self, text: str, lang: str) -> str:
        """Return a normalized version of `text` for the specified language."""
        raise NotImplementedError
