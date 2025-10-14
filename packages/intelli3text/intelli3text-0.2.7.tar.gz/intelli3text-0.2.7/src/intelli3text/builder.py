# src/intelli3text/builder.py (ou onde você mantém o PipelineBuilder)

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

    Wires strategy components (extractors, cleaners, LID, normalizer, exporters)
    according to an :class:`Intelli3Config`. Fluent API allows overriding parts
    before :meth:`build`.

    Defaults:
        - Extractors: Web/PDF/DOCX/TXT
        - Cleaners: names from ``cfg.cleaners`` (via :class:`CleanerChain`)
        - LID primary: :class:`FastTextLID` (auto-download of ``lid.176.ftz``)
        - LID fallback: ``None`` (optional CLD3 if installed)
        - Normalizer: :class:`SpacyNormalizer` (size per config, with fallbacks)
        - Exporters: PDF when configured in ``cfg.export['pdf']`` with a valid ``path``

    Example:
        >>> builder = PipelineBuilder(Intelli3Config())
        >>> pipeline = builder.with_lid(primary="fasttext").build()
        >>> result = pipeline.process("https://example.com")
    """

    def __init__(self, cfg: Optional[Intelli3Config] = None) -> None:
        self.cfg: Intelli3Config = cfg or Intelli3Config()

        # Extractors (Strategy)
        self._extractors = {
            "web": WebExtractor(),
            "pdf": PDFExtractor(),
            "docx": DocxExtractor(),
            "text": TextExtractor(),
        }

        # Cleaners (Chain of Responsibility)
        self._cleaners: CleanerChain = CleanerChain.from_names(self.cfg.cleaners)

        # Language ID (Strategy): fastText por padrão; CLD3 é opcional
        self._lid_primary = FastTextLID()
        self._lid_fallback = None  # configurável via with_lid()

        # Normalizer (Strategy)
        self._normalizer = SpacyNormalizer(self.cfg)

        # Exporters (Strategy)
        self._exporters: Dict[str, Any] = {}
        if self.cfg.export and "pdf" in self.cfg.export and self.cfg.export["pdf"].get("path"):
            self._exporters["pdf"] = PDFExporter(**self.cfg.export["pdf"])

    # -----------------------
    # Fluent customization API
    # -----------------------

    def with_cleaners(self, names: List[str]) -> "PipelineBuilder":
        """Override the cleaners chain by names."""
        self._cleaners = CleanerChain.from_names(names)
        return self

    def with_lid(self, primary: str, fallback: Optional[str] = None) -> "PipelineBuilder":
        """Configure language identification strategies.

        Args:
            primary: "fasttext" (default) or "cld3" (requires optional extra).
            fallback: optional fallback ("cld3" or None).
        """
        if primary == "cld3":
            try:
                from .lid.cld3_lid import CLD3LID
                self._lid_primary = CLD3LID(self.cfg)
            except Exception:
                # Se CLD3 não estiver disponível, fica no fastText
                self._lid_primary = FastTextLID()
        else:
            self._lid_primary = FastTextLID()

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
        """Add or override an exporter by name."""
        if name == "pdf":
            from .export.pdf_reportlab import PDFExporter as _PDFExporter
            self._exporters["pdf"] = _PDFExporter(**kwargs)
        return self

    # -------------
    # Finalization
    # -------------

    def build(self) -> Pipeline:
        """Create a :class:`Pipeline` instance with the current configuration and strategies."""
        return Pipeline(
            cfg=self.cfg,
            extractors=self._extractors,
            cleaners=self._cleaners,
            lid_primary=self._lid_primary,
            lid_fallback=self._lid_fallback,
            normalizer=self._normalizer,
            exporters=self._exporters,
        )