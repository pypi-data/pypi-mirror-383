from __future__ import annotations

from typing import Optional, List, Dict, Any

from .config import Intelli3Config
from .pipeline import Pipeline
from .cleaners.chain import CleanerChain
from .extractors.web_trafilatura import WebExtractor
from .extractors.file_pdfminer import PDFExtractor
from .extractors.file_docx import DocxExtractor
from .extractors.file_text import TextExtractor
from .lid.fasttext_lid import FastTextLID
from .export.pdf_reportlab import PDFExporter
from .nlp.spacy_normalizer import SpacyNormalizer


class PipelineBuilder:
    """Builder for the high-level processing :class:`Pipeline`.

    This class wires together strategy components (extractors, cleaners, LID, normalizer,
    exporters) according to an :class:`Intelli3Config`. It exposes a fluent API so you can
    override parts of the pipeline before calling :meth:`build`.

    Defaults:
        - Extractors: Web/PDF/DOCX/TXT
        - Cleaners: taken from ``cfg.cleaners`` via :class:`CleanerChain`
        - LID primary: :class:`FastTextLID` (with auto-download of ``lid.176.bin``)
        - LID fallback: ``None`` (CLD3 optional if installed)
        - Normalizer: :class:`SpacyNormalizer` with spaCy size preference from config
        - Exporters: PDF when configured in ``cfg.export['pdf']`` with a valid ``path``

    Example:
        >>> builder = PipelineBuilder(Intelli3Config())
        >>> pipeline = builder.with_lid(primary="fasttext").build()
        >>> result = pipeline.process("https://example.com")
    """

    def __init__(self, cfg: Optional[Intelli3Config] = None) -> None:
        """Initialize the builder with an optional configuration.

        Args:
            cfg: Optional pipeline configuration. If not provided, a default
                :class:`Intelli3Config` is created.
        """
        self.cfg: Intelli3Config = cfg or Intelli3Config()

        # Extractors (Strategy): fixed set for now, extend here if you add new sources.
        self._extractors = {
            "web": WebExtractor(),
            "pdf": PDFExtractor(),
            "docx": DocxExtractor(),
            "text": TextExtractor(),
        }

        # Cleaners (Chain of Responsibility): from config names, in order.
        self._cleaners: CleanerChain = CleanerChain.from_names(self.cfg.cleaners)

        # Language ID (Strategy): default to fastText; CLD3 remains optional.
        self._lid_primary = FastTextLID()
        self._lid_fallback = None  # set via with_lid()

        # Normalizer (Strategy): spaCy-based, with size preference and fallbacks.
        self._normalizer = SpacyNormalizer(self.cfg)

        # Exporters (Strategy): configured through cfg.export; PDF is supported by default.
        self._exporters: Dict[str, Any] = {}
        if self.cfg.export and "pdf" in self.cfg.export and self.cfg.export["pdf"].get("path"):
            self._exporters["pdf"] = PDFExporter(**self.cfg.export["pdf"])

    # -----------------------
    # Fluent customization API
    # -----------------------

    def with_cleaners(self, names: List[str]) -> "PipelineBuilder":
        """Override the cleaners chain by names.

        Args:
            names: Cleaner identifiers in the execution order (e.g. ``["ftfy", "clean_text", "pdf_breaks"]``).

        Returns:
            PipelineBuilder: self (for chaining).
        """
        self._cleaners = CleanerChain.from_names(names)
        return self

    def with_lid(self, primary: str, fallback: Optional[str] = None) -> "PipelineBuilder":
        """Configure language identification strategies.

        Args:
            primary: ``"fasttext"`` (default) or ``"cld3"`` (requires optional extra).
            fallback: optional fallback (``"cld3"`` or ``None``).

        Returns:
            PipelineBuilder: self (for chaining).
        """
        if primary == "cld3":
            try:
                from .lid.cld3_lid import CLD3LID
                self._lid_primary = CLD3LID(self.cfg)
            except Exception:
                # Be defensive: if CLD3 is not available, prefer not to break the pipeline
                # and keep the default (fastText) or None (but we choose fastText).
                self._lid_primary = FastTextLID()
        else:
            # Explicitly re-import to ensure local context if the class is optional in some envs.
            from .lid.fasttext_lid import FastTextLID as _FastTextLID
            self._lid_primary = _FastTextLID()

        if fallback == "cld3":
            try:
                from .lid.cld3_lid import CLD3LID
                self._lid_fallback = CLD3LID(self.cfg)
            except Exception:
                self._lid_fallback = None
        else:
            self._lid_fallback = None

        return self

    def with_exporter(self, name: str, **kwargs: Any) -> "PipelineBuilder":
        """Add or override an exporter by name.

        Args:
            name: Exporter name (currently supports ``"pdf"``).
            **kwargs: Arbitrary keyword arguments forwarded to the exporter constructor.

        Returns:
            PipelineBuilder: self (for chaining).
        """
        if name == "pdf":
            from .export.pdf_reportlab import PDFExporter as _PDFExporter
            self._exporters["pdf"] = _PDFExporter(**kwargs)
        # Future exporters could be handled here (e.g., "html", "markdown", "csv")
        return self

    # -------------
    # Finalization
    # -------------

    def build(self) -> Pipeline:
        """Create a :class:`Pipeline` instance with the current configuration and strategies.

        Returns:
            Pipeline: A ready-to-use pipeline facade.
        """
        return Pipeline(
            cfg=self.cfg,
            extractors=self._extractors,
            cleaners=self._cleaners,
            lid_primary=self._lid_primary,
            lid_fallback=self._lid_fallback,
            normalizer=self._normalizer,
            exporters=self._exporters,
        )
