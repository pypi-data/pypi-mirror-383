# src/intelli3text/lid/fasttext_lid.py

import os
from pathlib import Path
from typing import Optional, Tuple
from importlib.resources import files

from .base import ILanguageDetector
from ..utils import cached_path, download_file
from ..errors import ModelNotFoundError

# Defaults (can be overridden by env)
DEFAULT_FTZ_URL = "https://dl.fbaipublicfiles.com/fasttext/supervised-models/lid.176.ftz"
FASTTEXT_LID_FTZ = "lid.176.ftz"
FASTTEXT_LID_BIN = "lid.176.bin"  # legacy format that fastText also loads

ENV_LID_PATH = "INTELLI3TEXT_LID_PATH"
ENV_LID_URL = "INTELLI3TEXT_LID_URL"


class FastTextLID(ILanguageDetector):
    """fastText LID (176 languages) with install/run-time resilience.

    Resolution order for the model file:
        1) Explicit `model_path` arg
        2) $INTELLI3TEXT_LID_PATH (if set)
        3) Packaged data: intelli3text/lid/models/lid.176.ftz (wheel data)
        4) Cache: cached_path('lid.176.ftz') or cached_path('lid.176.bin'); download if missing

    Args:
        model_path: absolute/relative path to an existing fastText model (.ftz or .bin).
        max_chars: max characters taken from input text before prediction (performance).
    """

    def __init__(self, *, model_path: Optional[str] = None, max_chars: int = 2000) -> None:
        self.max_chars = max_chars
        self._model = None  # lazy loaded

        # 1) explicit arg
        if model_path:
            self._model_path = Path(model_path)
        else:
            # 2) ENV override
            env_path = os.environ.get(ENV_LID_PATH)
            if env_path:
                self._model_path = Path(env_path)
            else:
                # 3) packaged data inside the wheel
                packaged_ftz = files("intelli3text").joinpath("lid", "models", FASTTEXT_LID_FTZ)
                packaged_bin = files("intelli3text").joinpath("lid", "models", FASTTEXT_LID_BIN)
                if packaged_ftz.is_file():
                    self._model_path = Path(str(packaged_ftz))
                elif packaged_bin.is_file():
                    self._model_path = Path(str(packaged_bin))
                else:
                    # 4) cache location (prefer ftz)
                    cp_ftz = cached_path(FASTTEXT_LID_FTZ)
                    cp_bin = cached_path(FASTTEXT_LID_BIN)
                    # choose whichever already exists; otherwise default to ftz path (and we may download)
                    if Path(cp_ftz).exists():
                        self._model_path = Path(cp_ftz)
                    elif Path(cp_bin).exists():
                        self._model_path = Path(cp_bin)
                    else:
                        self._model_path = Path(cp_ftz)  # expected destination for a download

    # -----------------
    # Public API
    # -----------------

    def detect(self, text: str) -> Tuple[str, float]:
        """Return (lang, score) using fastText LID; safe defaults on errors."""
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

    # -----------------
    # Internals
    # -----------------

    def _ensure_model(self):
        """Lazy-load the fastText model; download to cache if necessary."""
        if self._model is not None:
            return self._model

        try:
            import fasttext  # type: ignore
        except Exception as e:
            raise ModelNotFoundError(
                "fasttext",
                hint="Install dependency failed; ensure 'fasttext-wheel>=0.9.2' or 'fasttext>=0.9.2' is available.",
            ) from e

        model_path = self._model_path

        # If the target path doesn't exist, try to download FTZ to that path (cache)
        if not model_path.exists():
            url = os.environ.get(ENV_LID_URL, DEFAULT_FTZ_URL)
            try:
                # ensure parent dir exists (cached_path may have created it already)
                model_path.parent.mkdir(parents=True, exist_ok=True)
                download_file(url, model_path)
            except Exception as e:
                raise ModelNotFoundError(
                    str(model_path),
                    hint=(
                        f"Could not obtain fastText LID model. Tried download from {url}. "
                        f"Set {ENV_LID_PATH} to a local file, or {ENV_LID_URL} to a reachable URL."
                    ),
                ) from e

        # Try loading; if .ftz/.bin ambiguity, try both names in the same folder
        try:
            self._model = fasttext.load_model(str(model_path))
        except Exception as primary_exc:
            # If we defaulted to FTZ but BIN exists alongside, try it (and vice-versa)
            alt = None
            if model_path.name.endswith(".ftz"):
                candidate = model_path.with_name(FASTTEXT_LID_BIN)
                if candidate.exists():
                    alt = candidate
            elif model_path.name.endswith(".bin"):
                candidate = model_path.with_name(FASTTEXT_LID_FTZ)
                if candidate.exists():
                    alt = candidate

            if alt is not None:
                try:
                    self._model = fasttext.load_model(str(alt))
                    self._model_path = alt  # record working path
                except Exception:
                    raise ModelNotFoundError(
                        str(model_path),
                        hint=(
                            "Model file exists but could not be loaded by fastText. "
                            "Re-download, verify integrity, or provide a valid '.ftz'/'.bin'."
                        ),
                    ) from primary_exc
            else:
                raise ModelNotFoundError(
                    str(model_path),
                    hint=(
                        "Model file exists but could not be loaded by fastText. "
                        "Re-download, verify integrity, or provide a valid '.ftz'/'.bin'."
                    ),
                ) from primary_exc

        return self._model

    @staticmethod
    def _normalize_label(label: str) -> str:
        """Turn '__label__pt' into 'pt'; keep subtags if present (e.g., 'zh-cn')."""
        lang = (label or "").replace("__label__", "").strip().lower()
        return lang or "pt"
