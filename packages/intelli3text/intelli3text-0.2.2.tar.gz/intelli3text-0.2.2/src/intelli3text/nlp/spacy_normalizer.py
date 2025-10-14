from __future__ import annotations

import re
from typing import List

import spacy

from .base import INormalizer
from .registry import get_nlp
from ..config import Intelli3Config


class SpacyNormalizer(INormalizer):
    """spaCy-based paragraph splitter and normalizer with robust PDF heuristics.

    - Paragraph splitting:
        * De-hyphenate across line breaks (e.g., "informa-\n ção" → "informação")
        * Merge lone line breaks likely occurring mid-sentence
        * Collapse >=3 line breaks to exactly two (section separators)
        * Drop very short blocks (headers/footers), honoring cfg.paragraph_min_chars

    - Normalization:
        * Tokenize with spaCy
        * Remove spaces, punctuation, and stop words
        * Lemmatize when model provides lexical attributes
        * Join lemmas with single spaces
    """

    _re_hyphen = re.compile(r"(\w)-\s*\n\s*(\w)")
    _re_merge = re.compile(r"([^\.\!\?])\n(?=[^\n])")
    _re_collapse = re.compile(r"\n{3,}")
    _re_drop_page_num = re.compile(r"^\s*\d+\s*$")
    _re_drop_page_word = re.compile(r"^\s*(Página|Page)\s*\d+\s*$", flags=re.I)
    _re_drop_references = re.compile(r"^\s*References\s*$", flags=re.I)

    def __init__(self, cfg: Intelli3Config) -> None:
        self.cfg = cfg

    # -------------------
    # Paragraph handling
    # -------------------

    def _normalize_breaks(self, text: str) -> str:
        if not text:
            return text
        out = self._re_hyphen.sub(r"\1\2", text)
        out = self._re_merge.sub(r"\1 ", out)
        out = self._re_collapse.sub("\n\n", out)
        return out

    def split_paragraphs(self, text: str) -> List[str]:
        if not text:
            return []

        txt = self._normalize_breaks(text)
        parts = re.split(r"\n\s*\n", txt)
        out: List[str] = []
        min_len = max(0, int(self.cfg.paragraph_min_chars))

        for p in parts:
            p = p.strip()
            if not p:
                continue
            # Drop common boilerplate lines
            if self._re_drop_page_num.match(p):
                continue
            if self._re_drop_page_word.match(p):
                continue
            if self._re_drop_references.match(p):
                continue

            if len(p) >= min_len:
                out.append(p)

        # Fallback: if everything was filtered out, return the whole text
        return out or [text.strip()]

    # --------------
    # Normalization
    # --------------

    def normalize(self, text: str, lang: str) -> str:
        """Normalize `text` according to `lang` using spaCy.

        Steps:
          - Load cached spaCy pipeline for the language (with size preference)
          - Tokenize
          - Remove spaces/punctuation/stopwords
          - Use lemma_ when available, else surface form
        """
        nlp = get_nlp(lang, self.cfg)
        doc = nlp(text)

        toks = []
        for t in doc:
            # Defensive getattr for blank pipelines
            if getattr(t, "is_space", False) or getattr(t, "is_punct", False) or getattr(t, "is_stop", False):
                continue
            if len(t.text.strip()) <= 1:
                continue
            lemma = getattr(t, "lemma_", None)
            toks.append(lemma if lemma else t.text)

        return " ".join(toks)
