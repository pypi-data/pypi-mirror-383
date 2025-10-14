import re
from typing import List

HEADING_RE = re.compile(r"^(abstract|resumo|introdu[cç][aã]o|conclus[aã]o|references?|refer[eê]ncias)\b", re.I)

def split_into_paragraphs(text: str, *, max_chars: int = 2500) -> List[str]:
    """
    Split text into paragraphs:
      - break on double-newline or headings
      - collapse tiny fragments
      - chunk paragraphs longer than `max_chars`
    """
    if not text:
        return []

    # primeiro, normaliza quebras múltiplas
    norm = re.sub(r"\r\n?", "\n", text)
    # separa por blocos vazios
    cand = re.split(r"\n{2,}", norm)
    parts: List[str] = []

    buf = []
    def _flush():
        if buf:
            p = " ".join(buf).strip()
            if p:
                parts.append(p)
            buf.clear()

    for block in cand:
        b = block.strip()
        if not b:
            _flush()
            continue

        # se bloco parece heading, força quebra antes dele
        if HEADING_RE.match(b):
            _flush()
            parts.append(b)
            _flush()
            continue

        # linhas internas pequenas juntam
        lines = [ln.strip() for ln in b.split("\n") if ln.strip()]
        merged = " ".join(lines)
        if merged:
            buf.append(merged)

    _flush()

    # agora, chunk em fatias <= max_chars
    final: List[str] = []
    for p in parts:
        if len(p) <= max_chars:
            final.append(p)
        else:
            # corta em limites de frase/pontuação se possível
            # primeiro tenta por pontos
            start = 0
            while start < len(p):
                end = min(start + max_chars, len(p))
                # tenta recuar para a última pontuação antes do limite
                cut = p.rfind(". ", start, end)
                if cut == -1:
                    cut = p.rfind("! ", start, end)
                if cut == -1:
                    cut = p.rfind("? ", start, end)
                if cut == -1:
                    cut = p.rfind(" ", start, end)
                if cut == -1 or cut <= start + 200:  # não achou ponto “bom”
                    cut = end
                final.append(p[start:cut].strip())
                start = cut
    return final
