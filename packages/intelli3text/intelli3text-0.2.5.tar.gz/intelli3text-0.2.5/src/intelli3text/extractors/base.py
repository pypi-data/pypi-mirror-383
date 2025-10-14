from __future__ import annotations

from abc import ABC, abstractmethod


class IExtractor(ABC):
    """Abstract interface for source extractors.

    Implementations convert a given source (URL or file path) into raw text.

    Notes:
        * Extractors should be side-effect free (no global state).
        * Return an empty string on irrecoverable failures instead of raising,
          unless a hard failure is truly desired by the caller.
    """

    @abstractmethod
    def extract(self, source: str) -> str:
        """Extract raw text from the given source.

        Args:
            source: URL or file path specific to the extractor.

        Returns:
            Extracted raw text (empty string if nothing could be extracted).
        """
        raise NotImplementedError
