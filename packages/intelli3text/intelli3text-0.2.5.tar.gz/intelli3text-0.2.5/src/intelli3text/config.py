from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional, Set, List, Dict, Any

# Default set of supported languages. This can be overridden via config.
DEFAULT_LANGS: Set[str] = {"pt", "en", "es"}


@dataclass
class Intelli3Config:
    """Configuration object for the intelli3text pipeline.

    This dataclass centralizes all user-tunable parameters that control
    ingestion, cleaning, language identification (LID), spaCy model
    preferences, and exporters.

    Attributes:
        cleaners:
            Ordered list of cleaner names to apply (Chain of Responsibility).
            Defaults to ``["ftfy", "clean_text", "pdf_breaks"]``.
        lid_primary:
            Primary language detector strategy. Supported values:
            - ``"fasttext"`` (default): uses fastText LID (auto-downloads `lid.176.bin`).
            - ``"cld3"``: optional, requires the extra dependency.
        lid_fallback:
            Optional fallback language detector (e.g., ``"cld3"``). Set to
            ``None`` (default) to disable fallback.
        languages_supported:
            Set of languages expected/considered by the pipeline. This does not
            hard-filter LID output but is used by downstream heuristics/presenters.
            Defaults to ``{"pt", "en", "es"}``.
        nlp_model_pref:
            Preferred spaCy model size: ``"lg"`` (default), ``"md"``, or ``"sm"``.
            The system falls back md→sm→blank if the requested size isn't available.
        paragraph_min_chars:
            Minimum length (in characters) for a block to be considered a paragraph
            after PDF/HTML heuristics. Helps filter headers/footers. Default: 30.
        lid_min_chars:
            Minimum character length for the cleaned text sample to be used by the
            LID model (shorter ones may yield unreliable predictions). Default: 60.
        lid_threshold:
            Reserved threshold for downstream decisions based on LID confidence.
            Not strictly enforced by detectors; consumers may use it to flag low confidence.
            Default: 0.60.
        export:
            Optional exporters configuration. For example:
            ``{"pdf": {"path": "report.pdf", "include_global_normalized": True}}``.
            If ``None`` (default), no exporters are invoked.

    Example:
        >>> cfg = Intelli3Config(
        ...     cleaners=["ftfy", "clean_text", "pdf_breaks"],
        ...     lid_primary="fasttext",
        ...     nlp_model_pref="md",
        ...     export={"pdf": {"path": "out.pdf", "include_global_normalized": True}},
        ... )
    """

    # Cleaning pipeline (ordered)
    cleaners: List[str] = field(default_factory=lambda: ["ftfy", "clean_text", "pdf_breaks"])

    # Language identification strategy
    lid_primary: str = "fasttext"                 # "fasttext" | "cld3"
    lid_fallback: Optional[str] = None            # "cld3" | None

    # Supported/expected languages for reporting and heuristics
    languages_supported: Set[str] = field(default_factory=lambda: set(DEFAULT_LANGS))

    # spaCy model preference: large → medium → small (with blank fallback)
    nlp_model_pref: str = "lg"                    # "lg" | "md" | "sm"

    # Paragraph processing and LID sampling thresholds
    paragraph_min_chars: int = 30
    lid_min_chars: int = 60
    lid_threshold: float = 0.60

    # Exporters configuration (e.g., PDF)
    export: Optional[Dict[str, Any]] = None
