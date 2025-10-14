from __future__ import annotations

from typing import Dict, Optional

import spacy

from ..config import Intelli3Config
from ..errors import ModelNotFoundError

# Preferred model names by language + size
_MODEL_PREF = {
    "pt": {"lg": "pt_core_news_lg", "md": "pt_core_news_md", "sm": "pt_core_news_sm"},
    "en": {"lg": "en_core_web_lg", "md": "en_core_web_md", "sm": "en_core_web_sm"},
    "es": {"lg": "es_core_news_lg", "md": "es_core_news_md", "sm": "es_core_news_sm"},
}

# Cache of loaded spaCy Language objects keyed by (lang, size)
_NLP_CACHE: Dict[tuple[str, str], spacy.language.Language] = {}


def _try_load(name: str) -> Optional[spacy.language.Language]:
    try:
        return spacy.load(name)
    except Exception:
        return None


def _try_download_and_load(name: str) -> Optional[spacy.language.Language]:
    try:
        # Lazy import to avoid hard dependency at import time
        from spacy.cli import download as spacy_download

        spacy_download(name)
        return spacy.load(name)
    except Exception:
        return None


def get_nlp(lang: str, cfg: Intelli3Config) -> spacy.language.Language:
    """Return a spaCy Language object for `lang` honoring size preference and fallbacks.

    Order:
      1) Try preferred size (cfg.nlp_model_pref) e.g. 'lg'
      2) Fallback to next sizes (md → sm)
      3) Try downloading missing models once
      4) Fall back to `spacy.blank(lang)` with a sentencizer
    """
    lang = lang.lower()
    size = cfg.nlp_model_pref.lower()
    prefs = _MODEL_PREF.get(lang, {})

    # Build ordered list like ["lg", "md", "sm"] starting from preference
    sizes = ["lg", "md", "sm"]
    if size in sizes:
        sizes.insert(0, sizes.pop(sizes.index(size)))

    # 1) try loading any already-installed model in preference order
    for s in sizes:
        name = prefs.get(s)
        if not name:
            continue
        key = (lang, s)
        if key in _NLP_CACHE:
            return _NLP_CACHE[key]
        nlp = _try_load(name)
        if nlp is not None:
            _NLP_CACHE[key] = nlp
            return nlp

    # 2) attempt download+load once in preference order
    for s in sizes:
        name = prefs.get(s)
        if not name:
            continue
        key = (lang, s)
        nlp = _try_download_and_load(name)
        if nlp is not None:
            _NLP_CACHE[key] = nlp
            return nlp

    # 3) final fallback: blank pipeline (works offline)
    try:
        nlp = spacy.blank(lang if lang in {"pt", "en", "es"} else "pt")
    except Exception as e:
        raise ModelNotFoundError(
            f"spacy.blank({lang})",
            hint="Unexpected spaCy failure. Verify your spaCy installation.",
        ) from e

    if "sentencizer" not in nlp.pipe_names:
        try:
            nlp.add_pipe("sentencizer")
        except Exception:
            # Best-effort: ignore if even sentencizer cannot be added
            pass

    _NLP_CACHE[(lang, "blank")] = nlp
    return nlp
