from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Dict, Any


class IExporter(ABC):
    """Abstract interface for result exporters.

    Implementations take the pipeline's structured `result` dictionary and
    produce a side-effect (e.g., write a PDF/HTML/CSV file).

    The exporter **must not** mutate the incoming `result`.
    """

    @abstractmethod
    def export(self, result: Dict[str, Any]) -> None:
        """Export the pipeline result.

        Args:
            result: The structured dictionary produced by `Pipeline.process(...)`.
        """
        raise NotImplementedError
