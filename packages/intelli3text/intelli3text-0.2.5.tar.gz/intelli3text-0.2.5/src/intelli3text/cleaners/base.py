from __future__ import annotations

from abc import ABC, abstractmethod


class ICleaner(ABC):
    """Abstract cleaner interface.

    A cleaner receives a text input and returns a cleaned version. Cleaners are
    composed into a :class:`CleanerChain` to form a pipeline. Implementations
    should be **pure** (no side effects) and idempotent whenever possible.

    Notes:
        * Cleaners operate at both document-level and paragraph-level.
        * If you need different behavior per paragraph, override
          :meth:`apply_paragraph` accordingly. The default implementation just
          calls :meth:`apply`.
    """

    @abstractmethod
    def apply(self, text: str) -> str:
        """Apply cleaning to an arbitrary text block (document-level).

        Args:
            text: Input text.

        Returns:
            Cleaned text.
        """
        raise NotImplementedError

    def apply_paragraph(self, text: str) -> str:
        """Apply cleaning to a paragraph.

        Default implementation delegates to :meth:`apply`. Override if the
        paragraph case requires special handling.
        """
        return self.apply(text)
