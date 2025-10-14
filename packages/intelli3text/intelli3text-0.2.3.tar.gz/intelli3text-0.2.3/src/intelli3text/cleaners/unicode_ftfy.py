from __future__ import annotations

from .base import ICleaner

try:
    from ftfy import fix_text
except Exception:  # graceful fallback if ftfy is unavailable
    fix_text = None


class FTFYCleaner(ICleaner):
    """Fix common Unicode issues using `ftfy`.

    If `ftfy` is unavailable, this cleaner becomes a no-op (returns input as-is).
    """

    def apply(self, text: str) -> str:
        if not text or fix_text is None:
            return text
        # ftfy is safe and idempotent for well-formed text
        return fix_text(text)

    # Paragraph-level behavior is identical for this cleaner
    # (inherits apply_paragraph from base)
