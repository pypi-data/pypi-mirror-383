# src/intelli3text/cleaners/chain.py
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import List, Dict, Type

from .base import ICleaner
from .unicode_ftfy import FTFYCleaner
from .clean_text import CleanTextCleaner
from .pdf_linebreaks import PDFLineBreaksCleaner
from .ocr_tilde_fix import OcrTildeFixCleaner
from .pt_diacritics_repair import PtDiacriticsRepairCleaner
from .strip_accents import StripAccentsCleaner


NAME2CLEANER: Dict[str, Type[ICleaner]] = {
    "ftfy": FTFYCleaner,
    "clean_text": CleanTextCleaner,
    "pdf_breaks": PDFLineBreaksCleaner,
    "pdf_linebreaks": PDFLineBreaksCleaner,  # alias
    "ocr_tilde_fix": OcrTildeFixCleaner,
    "pt_diacritics_repair": PtDiacriticsRepairCleaner,
    "strip_accents": StripAccentsCleaner,
}


# --- Heurísticas de ruído OCR (til solto, vírgula+til, apóstrofos no meio de palavras etc.) ---
_RE_TILDE = re.compile(r"~")
_RE_COMMA_TILDE = re.compile(r",\s*~")
_RE_APOS_BETWEEN = re.compile(r"(\w)'\s*(\w)")
# padrões ainda “quebrados” típicos em PT
_RE_A_TILDE_BROKEN = re.compile(r"[aA]\s*~\s*[oO]\b")           # a ~ o  ->  ão (ainda não reparado)
_RE_O_TILDE_PL_BROKEN = re.compile(r"[oO]\s*~\s*(e?s?)\b")      # o ~ es / o ~ s  ->  ões / ãos
_RE_C_COMMA_TILDE_AO = re.compile(r"[cC]\s*,\s*~\s*ao")         # c , ~ ao ->  ção


def _noise_score(text: str) -> int:
    """Conta ocorrências de padrões indicativos de OCR mal extraído."""
    return sum(
        pat.search(text) is not None and len(pat.findall(text)) or 0
        for pat in (
            _RE_TILDE,
            _RE_COMMA_TILDE,
            _RE_APOS_BETWEEN,
            _RE_A_TILDE_BROKEN,
            _RE_O_TILDE_PL_BROKEN,
            _RE_C_COMMA_TILDE_AO,
        )
    )


@dataclass
class CleanerChain:
    """
    Executa os cleaners em cadeia (ordem importa) e adiciona um fallback dinâmico:
    - Depois de `PtDiacriticsRepairCleaner`, mede ruído OCR.
    - Se o ruído por 1000 chars ultrapassar o limiar, aplica `StripAccents` no texto atual.
    """
    cleaners: List[ICleaner]

    # Parâmetros do modo dinâmico
    auto_ascii_fallback: bool = True
    noise_threshold_per_k: float = 3.0    # ocorrências / 1000 chars
    min_chars_for_ascii: int = 120        # evita ativar em blocos curtíssimos (refs, cabeçalhos etc.)

    @classmethod
    def from_names(cls, names: List[str]) -> "CleanerChain":
        instances: List[ICleaner] = []
        for name in names:
            key = (name or "").strip().lower()
            if not key:
                continue
            if key not in NAME2CLEANER:
                raise ValueError(f"Unknown cleaner: {key}. Available: {sorted(NAME2CLEANER.keys())}")
            instances.append(NAME2CLEANER[key]())
        return cls(cleaners=instances)

    # --------------- Helpers internos ---------------

    def _maybe_ascii(self, txt: str, *, paragraph: bool) -> str:
        """Aplica StripAccents se heurística de ruído exceder o limiar."""
        if not self.auto_ascii_fallback:
            return txt
        if len(txt) < self.min_chars_for_ascii:
            return txt
        score = _noise_score(txt)
        per_k = (score * 1000.0) / max(1, len(txt))
        if per_k > self.noise_threshold_per_k:
            sa = StripAccentsCleaner()
            return sa.apply_paragraph(txt) if paragraph else sa.apply(txt)
        return txt

    def _run_chain_with_dynamic_ascii(self, text: str, *, paragraph: bool) -> str:
        out = text
        for c in self.cleaners:
            out = c.apply_paragraph(out) if paragraph else c.apply(out)

            # Ponto de decisão: logo após o reparo de diacríticos
            if isinstance(c, PtDiacriticsRepairCleaner):
                out = self._maybe_ascii(out, paragraph=paragraph)

        return out

    # ---------------- Limpeza documento inteiro ----------------

    def apply(self, text: str) -> str:
        return self._run_chain_with_dynamic_ascii(text, paragraph=False)

    # ---------------- Limpeza por parágrafo --------------------

    def apply_paragraph(self, text: str) -> str:
        return self._run_chain_with_dynamic_ascii(text, paragraph=True)
