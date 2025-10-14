from __future__ import annotations
import re
from typing import final
from .base import ICleaner

# Map helpers
_ACUTE = str.maketrans({
    "a": "á", "e": "é", "i": "í", "o": "ó", "u": "ú",
    "A": "Á", "E": "É", "I": "Í", "O": "Ó", "U": "Ú",
})
_CIRC = str.maketrans({
    "a": "â", "e": "ê", "i": "î", "o": "ô", "u": "û",
    "A": "Â", "E": "Ê", "I": "Î", "O": "Ô", "U": "Û",
})
_TILDE = {"a": "ã", "A": "Ã", "o": "õ", "O": "Õ"}

# --- padrões OCR comuns em PDFs em PT-BR ---
# c ,  -> ç   (antes de "ao" vira "ção")
RE_C_COMMA = re.compile(r"([cC])\s*,\s*")
# ^vogal  ou  vogal^
RE_CARET_BEFORE = re.compile(r"\^\s*([AEIOUaeiou])")
RE_CARET_AFTER  = re.compile(r"([AEIOUaeiou])\s*\^")
# 'vogal   ou   vogal'
RE_ACUTE_BEFORE = re.compile(r"'\s*([AEIOUaeiou])")
RE_ACUTE_AFTER  = re.compile(r"([AEIOUaeiou])\s*'")
# ~a/~o formas soltas e com espaços
RE_TIL_SOLO_BEFORE = re.compile(r"~\s*([aAoO])")
RE_TIL_SOLO_AFTER  = re.compile(r"([aAoO])\s*~")
# Casos compostos comuns:   ~ ao,  ~ o,  ~ oes,  ~ es
RE_TIL_AO   = re.compile(r"\s*~\s*ao(s?)\b", flags=re.I)   # -> ão / ões (ajuste depois)
RE_TIL_O    = re.compile(r"\s*~\s*o\b", flags=re.I)        # (usado em pares tipo a ~ o -> ão)
RE_TIL_OES  = re.compile(r"\s*~\s*oes\b", flags=re.I)      # -> ões
RE_TIL_ES   = re.compile(r"\s*~\s*es\b", flags=re.I)       # -> ês (nem sempre, tratamos via contexto)
# a ~ o -> ão   (e variantes com espaços)
RE_A_TIL_O  = re.compile(r"([aA])\s*~\s*([oO])\b")
# apóstrofo perdido no meio da palavra
RE_APOS_MID = re.compile(r"(\w)'\s*(\w)")
# resíduos repetidos de espaços
RE_WS = re.compile(r"\s{2,}")

@final
class PtDiacriticsRepairCleaner(ICleaner):
    """Repara diacríticos comuns deturpados em PDFs/OCR de PT-BR.

    Regras:
      - c ,  -> ç
      - ^a / a^ -> â (idem para e,i,o,u; maiúsculas ok)
      - 'a / a' -> á (idem para e,i,o,u)
      - ~a/~o (antes/depois) -> ã/õ
      - padrões com  ~ ao / ~ oes / a ~ o -> ão/ões/ão
      - remove apóstrofos residuais dentro de palavras
    """

    # --------- API do ICleaner ---------
    def apply(self, text: str) -> str:
        return self._repair(text)

    def apply_paragraph(self, text: str) -> str:
        return self._repair(text)

    # --------- Implementação ---------
    def _repair(self, s: str) -> str:
        if not s:
            return s

        # 1) cedilha via "c ,"
        s = RE_C_COMMA.sub(lambda m: ("Ç" if m.group(1).isupper() else "ç"), s)

        # 2) circunflexo
        s = RE_CARET_BEFORE.sub(lambda m: m.group(1).translate(_CIRC), s)
        s = RE_CARET_AFTER.sub(lambda m: m.group(1).translate(_CIRC), s)

        # 3) agudo
        s = RE_ACUTE_BEFORE.sub(lambda m: m.group(1).translate(_ACUTE), s)
        s = RE_ACUTE_AFTER.sub(lambda m: m.group(1).translate(_ACUTE), s)

        # 4) til simples (antes/depois)
        s = RE_TIL_SOLO_BEFORE.sub(lambda m: _TILDE.get(m.group(1), m.group(1)), s)
        s = RE_TIL_SOLO_AFTER.sub(lambda m: _TILDE.get(m.group(1), m.group(1)), s)

        # 5) compostos frequentes
        #    5.1  ... c , ~ ao  -> (já viramos c , em ç) +  ção / ções
        #         Se a palavra termina com "~ ao" após um "ç", muito provavelmente é "ção/ções"
        def _til_ao(m):
            plural = m.group(1)
            return ("ções" if plural and plural.lower() == "s" else "ção")
        s = RE_TIL_AO.sub(_til_ao, s)

        #    5.2  a ~ o  -> ão (respeita maiúsculas)
        def _a_til_o(m):
            a, o = m.group(1), m.group(2)
            return ("ÃO" if a.isupper() and o.isupper() else "ão")
        s = RE_A_TIL_O.sub(_a_til_o, s)

        #    5.3  ~ oes  -> ões
        s = RE_TIL_OES.sub("ões", s)

        #    5.4  ~ o  após 'a' já foi tratado por a ~ o; os restantes são raros – não forçamos mais.

        # 6) apóstrofo perdido no meio de palavra (remoção segura)
        s = RE_APOS_MID.sub(r"\1\2", s)

        # 7) limpeza de espaços múltiplos
        s = RE_WS.sub(" ", s)

        return s
