from __future__ import annotations

from typing import Tuple, Optional

from .base import ILanguageDetector


class CLD3LID(ILanguageDetector):
    """Language detector backed by `pycld3` (optional dependency).

    Notes:
        - Requires `pip install intelli3text[cld3]`
        - Uses Google's Compact Language Detector 3 neural model
        - Returns ISO-639-1 codes (e.g., 'en', 'pt', 'es') with probability in [0,1]
    """

    def __init__(self, *, max_chars: int = 2000) -> None:
        self.max_chars = max_chars
        try:
            from pycld3 import NNetLanguageIdentifier  # type: ignore
        except Exception as e:
            raise ImportError(
                "pycld3 is not installed. Install with: pip install intelli3text[cld3]"
            ) from e

        # 0..max controls the number of bytes considered
        self._identifier = NNetLanguageIdentifier(min_num_bytes=0, max_num_bytes=max_chars)

    def detect(self, text: str) -> Tuple[str, float]:
        if not text:
            return "pt", 0.0

        sample = text.strip()
        if len(sample) > self.max_chars:
            sample = sample[: self.max_chars]

        try:
            result = self._identifier.FindLanguage(text=sample)
        except Exception:
            return "pt", 0.0

        # result: language (str), probability (float), is_reliable (bool), proportion (float)
        lang = (result.language or "").lower()
        prob = float(result.probability or 0.0)

        # CLD3 returns 'und' for undefined
        if not lang or lang == "und":
            return "pt", 0.0

        return lang, prob
