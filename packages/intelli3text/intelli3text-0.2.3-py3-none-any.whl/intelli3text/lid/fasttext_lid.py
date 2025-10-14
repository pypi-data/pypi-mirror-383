from __future__ import annotations

from pathlib import Path
from typing import Optional, Tuple

from .base import ILanguageDetector
from ..utils import cached_path, download_file
from ..errors import ModelNotFoundError


# Public URL of fastText LID model
# Reference: https://fasttext.cc/docs/en/language-identification.html
FASTTEXT_LID_URL = "https://dl.fbaipublicfiles.com/fasttext/supervised-models/lid.176.bin"
FASTTEXT_LID_NAME = "lid.176.bin"


class FastTextLID(ILanguageDetector):
    """Language detector backed by fastText's LID model (176 languages).

    Features:
        - Auto-download `lid.176.bin` to the library cache on first use
        - Robust to missing network (raises ModelNotFoundError if download fails)
        - Truncates very long texts for speed (default ~2000 chars)
        - Returns (lang, score) with lang normalized to iso-639-1 when possible

    Args:
        model_path: Optional absolute path to an existing `lid.176.bin`.
        max_chars: Maximum number of characters used from the input text.
                   Longer inputs are truncated. Default: 2000.
    """

    def __init__(self, *, model_path: Optional[str] = None, max_chars: int = 2000) -> None:
        self.max_chars = max_chars
        self._model_path = Path(model_path) if model_path else cached_path(FASTTEXT_LID_NAME)
        self._model = None  # lazy loaded

    # -----------------
    # Public API
    # -----------------

    def detect(self, text: str) -> Tuple[str, float]:
        """Detect language using fastText LID.

        Returns:
            (language_code, confidence) where language_code is lowercased ISO-639-1
            if available (e.g. "en", "pt", "es"). If fastText returns a label like
            "__label__pt", it's mapped to "pt". Unknown labels are returned as-is,
            lowercased, or coerced to "pt" as a safe default.
        """
        if not text:
            return "pt", 0.0

        model = self._ensure_model()
        sample = text.strip().replace("\n", " ")
        if self.max_chars and len(sample) > self.max_chars:
            sample = sample[: self.max_chars]

        try:
            labels, scores = model.predict(sample, k=1)
        except Exception as e:  # extremely defensive
            _ = e
            return "pt", 0.0

        if not labels:
            return "pt", 0.0

        raw_label = labels[0]
        score = float(scores[0]) if scores is not None and len(scores) else 0.0
        lang = self._normalize_label(raw_label)
        return lang, score

    # -----------------
    # Internals
    # -----------------

    def _ensure_model(self):
        """Lazy-load (and if needed, auto-download) the fastText model."""
        if self._model is not None:
            return self._model

        # Import inside to avoid mandatory dependency at import time
        try:
            import fasttext
        except Exception as e:
            raise ModelNotFoundError(
                "fasttext",
                hint="Install 'fasttext-wheel' (prebuilt wheels) or 'fasttext'.",
            ) from e

        # If file doesn't exist, try downloading to cache
        if not self._model_path.exists():
            try:
                download_file(FASTTEXT_LID_URL, self._model_path)
            except Exception as e:
                raise ModelNotFoundError(
                    FASTTEXT_LID_NAME,
                    hint=f"Could not download from {FASTTEXT_LID_URL}. "
                         f"Set INTELLI3TEXT_CACHE_DIR or provide model_path.",
                ) from e

        try:
            self._model = fasttext.load_model(str(self._model_path))
        except Exception as e:
            raise ModelNotFoundError(
                str(self._model_path),
                hint="File exists but could not be loaded by fastText. "
                     "Re-download or verify file integrity.",
            ) from e

        return self._model

    @staticmethod
    def _normalize_label(label: str) -> str:
        """Turn '__label__pt' into 'pt' and fallback safely."""
        lang = label.replace("__label__", "").strip().lower()
        # FastText sometimes returns longer tags (e.g., 'zh-cn').
        # Keep as-is if already a two-letter code; otherwise, trust fastText value.
        if not lang:
            return "pt"
        return lang
