from pathlib import Path
from typing import Optional, Tuple
from importlib.resources import files

from .base import ILanguageDetector
from ..utils import cached_path, download_file
from ..errors import ModelNotFoundError

FASTTEXT_LID_URL = "https://dl.fbaipublicfiles.com/fasttext/supervised-models/lid.176.ftz"
FASTTEXT_LID_NAME = "lid.176.ftz"

class FastTextLID(ILanguageDetector):
    def __init__(self, *, model_path: Optional[str] = None, max_chars: int = 2000) -> None:
        self.max_chars = max_chars

        packaged = files("intelli3text").joinpath("lid", "models", FASTTEXT_LID_NAME)
        if packaged.is_file():
            self._model_path = Path(str(packaged))
        elif model_path:
            self._model_path = Path(model_path)
        else:
            self._model_path = cached_path(FASTTEXT_LID_NAME)

        self._model = None  # lazy

    def detect(self, text: str) -> Tuple[str, float]:
        if not text:
            return "pt", 0.0
        model = self._ensure_model()
        sample = text.strip().replace("\n", " ")
        if self.max_chars and len(sample) > self.max_chars:
            sample = sample[: self.max_chars]
        try:
            labels, scores = model.predict(sample, k=1)
        except Exception:
            return "pt", 0.0
        if not labels:
            return "pt", 0.0
        raw_label = labels[0]
        score = float(scores[0]) if scores is not None and len(scores) else 0.0
        return self._normalize_label(raw_label), score

    def _ensure_model(self):
        if self._model is not None:
            return self._model
        try:
            import fasttext
        except Exception as e:
            raise ModelNotFoundError("fasttext", hint="Install 'fasttext-wheel' or 'fasttext'.") from e

        if not self._model_path.exists():
            try:
                download_file(FASTTEXT_LID_URL, self._model_path)
            except Exception as e:
                raise ModelNotFoundError(
                    FASTTEXT_LID_NAME,
                    hint=f"Could not download from {FASTTEXT_LID_URL}. Provide model_path or set INTELLI3TEXT_CACHE_DIR.",
                ) from e

        try:
            self._model = fasttext.load_model(str(self._model_path))
        except Exception as e:
            raise ModelNotFoundError(
                str(self._model_path),
                hint="File exists but could not be loaded by fastText. Re-download or verify integrity.",
            ) from e
        return self._model

    @staticmethod
    def _normalize_label(label: str) -> str:
        lang = label.replace("__label__", "").strip().lower()
        return lang or "pt"