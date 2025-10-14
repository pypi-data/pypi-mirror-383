from __future__ import annotations
import re
from .base import ICleaner

class OcrTildeFixCleaner(ICleaner):
    """
    Corrige artefatos comuns de OCR para pt:
    - padrões com til “solto” (~) em 'ao'/'oes'
    - vírgula + til vindo de PDF (c, ~ao -> ção)
    - apóstrofo no meio das vogais (Universit'ario -> Universitario)
    Obs.: é propositalmente leve; o ajuste fino fica no pt_diacritics_repair.
    """
    _rules = [
        # vírgula+til colados
        (r"c\s*,\s*~\s*ao", "ção"),
        (r",\s*~\s*ao", "ão"),
        (r",\s*~\s*oes", "ões"),

        # til “solto” antes de sequências
        (r"~\s*ao\b", "ão"),
        (r"~\s*oes\b", "ões"),

        # casos frequentes com consoantes + ~ + ao (n~ao, s~ao)
        (r"\b([ns])\s*~\s*ao\b", r"\1ão"),

        # apóstrofo entre letras (Universit'ario -> Universitario)
        (r"(\w)'\s*(\w)", r"\1\2"),
    ]
    _compiled = [(re.compile(p, re.IGNORECASE), r) for p, r in _rules]

    def _fix(self, s: str) -> str:
        out = s
        for rx, repl in self._compiled:
            out = rx.sub(repl, out)
        return out

    def apply(self, text: str) -> str:
        return self._fix(text)

    def apply_paragraph(self, text: str) -> str:
        return self._fix(text)
