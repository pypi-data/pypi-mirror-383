from __future__ import annotations

import re
from .base import ICleaner


class PDFLineBreaksCleaner(ICleaner):
    """Heuristics to fix PDF artifacts:
    - De-hyphenate across line breaks (e.g., "intelli-\n gence" → "intelligence")
    - Merge spurious single line breaks within sentences
    - Collapse 3+ line breaks into double line breaks (section separation)
    """

    # Precompiled regex to speed up repeated calls
    _re_hyphen = re.compile(r"(\w)-\s*\n\s*(\w)")
    _re_merge = re.compile(r"([^\.\!\?])\n(?=[^\n])")
    _re_collapse = re.compile(r"\n{3,}")

    def apply(self, text: str) -> str:
        if not text:
            return text

        # 1) Remove hyphenation around linebreaks
        out = self._re_hyphen.sub(r"\1\2", text)

        # 2) Merge single line breaks that likely occur mid-sentence
        out = self._re_merge.sub(r"\1 ", out)

        # 3) Collapse multiple blank lines (>=3) to exactly 2
        out = self._re_collapse.sub("\n\n", out)

        return out
