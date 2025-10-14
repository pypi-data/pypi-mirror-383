from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Tuple


class ILanguageDetector(ABC):
    """Abstract interface for language detectors (LID).

    Implementations should return a (language_code, confidence) tuple.
    Language codes are expected to be ISO-639-1 (e.g., "pt", "en", "es").
    Confidence is a float in [0.0, 1.0].
    """

    @abstractmethod
    def detect(self, text: str) -> Tuple[str, float]:
        """Detect language for the given text.

        Args:
            text: Input text (any length). Implementations may truncate.

        Returns:
            Tuple (language_code, confidence).
        """
        raise NotImplementedError
