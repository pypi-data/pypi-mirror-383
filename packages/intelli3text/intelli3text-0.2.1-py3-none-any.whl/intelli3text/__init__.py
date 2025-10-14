"""
intelli3text public API.

This package provides a high-level, opinionated pipeline for:
- Text ingestion (Web/PDF/DOCX/TXT)
- Cleaning & normalization
- Per-paragraph Language Identification (PT/EN/ES)
- Optional export (e.g., PDF reports)

Typical usage (Python):

    from intelli3text import PipelineBuilder, Intelli3Config

    cfg = Intelli3Config(
        cleaners=["ftfy", "clean_text", "pdf_breaks"],
        nlp_model_pref="md",
        export={"pdf": {"path": "report.pdf", "include_global_normalized": True}},
    )
    pipeline = PipelineBuilder(cfg).build()
    result = pipeline.process("https://en.wikipedia.org/wiki/NLP")
    print(result["language_global"], len(result["paragraphs"]))

Public Re-exports
-----------------
- Intelli3Config: Configuration dataclass for the pipeline (cleaners, LID, spaCy model size, export, etc.)
- PipelineBuilder: Builder that wires up extractors, cleaners, LID, normalizer, and exporters into a ready-to-use Pipeline
"""

from .config import Intelli3Config
from .builder import PipelineBuilder

# Optional: expose package version (helps docs and users introspecting versions)
# Uses importlib.metadata on Python 3.8+ (available in stdlib).
try:  # pragma: no cover - version retrieval is environment-dependent
    from importlib.metadata import version, PackageNotFoundError  # type: ignore
    try:
        __version__ = version("intelli3text")
    except PackageNotFoundError:
        # When running from a source tree without an installed distribution.
        __version__ = "0.0.0.dev0"
except Exception:  # defensive fallback
    __version__ = "0.0.0"

# Explicitly define the public surface of the package.
__all__ = [
    "Intelli3Config",
    "PipelineBuilder",
    "__version__",
]
