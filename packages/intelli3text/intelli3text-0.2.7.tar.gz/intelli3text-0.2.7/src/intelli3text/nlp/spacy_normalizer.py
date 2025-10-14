from __future__ import annotations

import re
from typing import List

from .base import INormalizer
from .registry import get_nlp
from ..config import Intelli3Config


class SpacyNormalizer(INormalizer):
    """spaCy-based paragraph splitter and normalizer with robust PDF heuristics.

    - Paragraph splitting:
        * De-hyphenate across line breaks (e.g., "informa-\n ção" → "informação")
        * Merge lone line breaks likely occurring mid-sentence
        * Inject smart paragraph breaks when PDFs come as a single block
        * Collapse >=3 line breaks to exactly two (section separators)
        * Drop very short blocks (headers/footers), honoring cfg.paragraph_min_chars
        * Fallback: sentence-based chunking when everything stays in one paragraph

    - Normalization:
        * Tokenize with spaCy
        * Remove only espaços/pontuação/stopwords
        * Mantém números/símbolos úteis
        * Lematiza quando disponível; senão, mantém a forma de superfície
    """

    _re_hyphen = re.compile(r"(\w)-\s*\n\s*(\w)")                         # une hifens de quebra
    _re_merge_mid = re.compile(r"([^\.\!\?\:\;])\n(?=[^\n])")             # une \n no meio de sentença
    _re_collapse = re.compile(r"\n{3,}")                                  # >=3 \n -> 2 \n
    _re_drop_page_num = re.compile(r"^\s*\d+\s*$")
    _re_drop_page_word = re.compile(r"^\s*(Página|Page)\s*\d+\s*$", flags=re.I)
    _re_drop_references = re.compile(r"^\s*(References|Referências)\s*$", flags=re.I)

    _re_inject_after_sentence = re.compile(
        r"([\.!?][\)\]»\"”']?)\s*\n\s*([“\"(\[]?[A-ZÁÀÂÃÉÊÍÓÔÕÚÜÇ0-9])"
    )

    # quebra antes de padrões típicos de cabeçalho/numeração/bullets
    _re_inject_before_header = re.compile(
        r"\n\s*((?:\d+(?:\.\d+){0,3}[)\.]|[IVXLCM]{1,4}\.|[•\-–—\*])\s+[A-ZÁÀÂÃÉÊÍÓÔÕÚÜÇ])"
    )

    def __init__(self, cfg: Intelli3Config) -> None:
        self.cfg = cfg

    # -------------------
    # Paragraph handling
    # -------------------

    def _normalize_breaks(self, text: str) -> str:
        if not text:
            return text
        out = self._re_hyphen.sub(r"\1\2", text)
        out = self._re_merge_mid.sub(r"\1 ", out)
        out = self._re_collapse.sub("\n\n", out)
        return out

    def _smart_paragraph_breaks(self, text: str) -> str:
        """Insere quebras de parágrafo em PDFs sem linhas em branco."""
        if not text:
            return text
        out = text

        # 1) Após final de sentença → força \n\n antes da próxima "linha" com maiúscula/numeração
        out = self._re_inject_after_sentence.sub(r"\1\n\n\2", out)

        # 2) Antes de cabeçalhos/numeração/bullets mais comuns
        out = self._re_inject_before_header.sub(r"\n\n\1", out)

        # 3) Normaliza excesso de quebras
        out = self._re_collapse.sub("\n\n", out)
        return out

    def _fallback_split_by_sentences(self, text: str) -> List[str]:
        """Quando tudo vira um bloco só, divide por sentenças e agrupa por janelas."""
        # split simples por pontuação final + espaço
        sentences = re.split(r"(?<=[\.\!\?])\s+", text.strip())
        sentences = [s.strip() for s in sentences if s and len(s.strip()) > 0]

        if not sentences:
            return [text.strip()]

        max_chunk = getattr(self.cfg, "paragraph_max_chars", 1200) or 1200
        min_chunk = max(300, int(getattr(self.cfg, "paragraph_min_chars", 80) or 80))

        chunks: List[str] = []
        buf = []

        def flush():
            if buf:
                chunk = " ".join(buf).strip()
                if chunk:
                    chunks.append(chunk)

        current_len = 0
        for s in sentences:
            s_len = len(s) + (1 if buf else 0)
            if current_len + s_len > max_chunk and current_len >= min_chunk:
                flush()
                buf = []
                current_len = 0  # noqa: F841 (redefinido abaixo)
            buf.append(s)
            current_len = sum(len(x) for x in buf) + (len(buf) - 1)

        flush()
        return chunks or [text.strip()]

    def split_paragraphs(self, text: str) -> List[str]:
        if not text:
            return []

        # passo 1: normaliza \n problemáticos
        txt = self._normalize_breaks(text)

        # passo 2: injeta quebras “inteligentes”
        txt = self._smart_paragraph_breaks(txt)

        # passo 3: split por blocos vazios
        parts = re.split(r"\n\s*\n", txt)
        out: List[str] = []
        min_len = max(0, int(getattr(self.cfg, "paragraph_min_chars", 80) or 80))

        for p in parts:
            p = p.strip()
            if not p:
                continue
            # limpa boilerplate típico
            if self._re_drop_page_num.match(p):
                continue
            if self._re_drop_page_word.match(p):
                continue
            if self._re_drop_references.match(p):
                continue
            if len(p) >= min_len:
                out.append(p)

        if len(out) <= 1:
            out = self._fallback_split_by_sentences(txt)

        return out or [text.strip()]

    # --------------  
    # Normalization
    # --------------

    def normalize(self, text: str, lang: str) -> str:
        """Normalize `text` according to `lang` using spaCy.

        Mantém tudo que “existe” semanticamente:
        - remove só espaços/pontuação/stopwords;
        - mantém números/símbolos; tokens 1-char só são removidos se forem puramente espaço/pontuação.
        """
        nlp = get_nlp(lang, self.cfg)
        doc = nlp(text)

        toks = []
        for t in doc:
            if getattr(t, "is_space", False) or getattr(t, "is_punct", False):
                continue
            if getattr(t, "is_stop", False):
                if getattr(t, "like_num", False) or re.search(r"[0-9A-Za-z]\d|\d[A-Za-z]", t.text):
                    pass
                else:
                    continue
            text_tok = t.text.strip()
            if not text_tok:
                continue
            lemma = getattr(t, "lemma_", None)
            toks.append(lemma if lemma else text_tok)

        return " ".join(toks)