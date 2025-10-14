from __future__ import annotations

from typing import Dict, Tuple, Iterable, Mapping, Any
from .config import Intelli3Config


class Pipeline:
    """High-level façade that orchestrates extraction, cleaning, LID, normalization and export.

    The pipeline delegates responsibilities to strategy components provided by
    :class:`PipelineBuilder`, so each piece is easily swappable.

    Expected component interfaces (informal):
        - Extractors: objects with ``extract(path_or_url: str) -> str``
          Keys used: ``"web" | "pdf" | "docx" | "text"``
        - Cleaners: a chain object exposing:
            * ``apply(text: str) -> str`` for full-document cleaning
            * ``apply_paragraph(text: str) -> str`` for per-paragraph cleaning
        - LID: objects with ``detect(text: str) -> tuple[str, float]`` (lang, confidence)
        - Normalizer: object with:
            * ``split_paragraphs(text: str) -> list[str]``
            * ``normalize(text: str, lang: str) -> str``
        - Exporters: mapping of name -> object exposing ``export(result: dict) -> None``

    Notes:
        * Global language is chosen as the most frequent paragraph language
          within ``cfg.languages_supported``.
        * LID sampling uses the cleaned paragraph if it has at least
          ``cfg.lid_min_chars`` characters; otherwise, uses the raw paragraph.
    """

    def __init__(
        self,
        *,
        cfg: Intelli3Config,
        extractors: Mapping[str, Any],
        cleaners: Any,
        lid_primary: Any,
        lid_fallback: Any,
        normalizer: Any,
        exporters: Mapping[str, Any],
    ) -> None:
        self.cfg = cfg
        self.extractors = extractors
        self.cleaners = cleaners
        self.lid_primary = lid_primary
        self.lid_fallback = lid_fallback
        self.normalizer = normalizer
        self.exporters = exporters

    # --------------------
    # Public entry point
    # --------------------

    def process(self, source: str) -> Dict[str, Any]:
        """Process a URL or local file and return a structured dictionary.

        Args:
            source: URL (http/https) or local file path.

        Returns:
            Dict with fields:
                - language_global (str)
                - raw (str)
                - cleaned (str)
                - normalized (str)
                - paragraphs (list[dict]) with keys:
                    * language (str)
                    * score (float)
                    * raw (str)
                    * cleaned (str)
                    * normalized (str)
        """
        raw = self._extract(source)
        cleaned = self.cleaners.apply(raw)
        paragraphs = self.normalizer.split_paragraphs(raw)

        supported = set(self.cfg.languages_supported)
        lang_counts: Dict[str, int] = {code: 0 for code in supported}
        para_results = []

        for p in paragraphs:
            p_clean = self.cleaners.apply_paragraph(p)
            # Use cleaned text for LID when long enough, otherwise raw paragraph
            unit = p_clean if len(p_clean) >= self.cfg.lid_min_chars else p

            lang, score = self._detect_lang(unit)
            # Use fallback label if detector returns something unexpected
            if lang not in supported:
                # Keep detector's score but coerce to a default language
                # (pt is a safe default for Portuguese-centric workflows)
                lang = "pt"

            if lang in lang_counts:
                lang_counts[lang] += 1

            normalized = self.normalizer.normalize(p_clean, lang)
            para_results.append(
                {
                    "language": lang,
                    "score": float(score),
                    "raw": p,
                    "cleaned": p_clean,
                    "normalized": normalized,
                }
            )

        global_lang = self._choose_global_language(lang_counts, fallback="pt", paragraphs=paragraphs)
        normalized_all = " ".join(p["normalized"] for p in para_results)

        result = {
            "language_global": global_lang,
            "raw": raw,
            "cleaned": cleaned,
            "normalized": normalized_all,
            "paragraphs": para_results,
        }

        self._export_all(result)
        return result

    # --------------------
    # Internal utilities
    # --------------------

    def _extract(self, source: str) -> str:
        """Route extraction by scheme/extension."""
        if source.startswith(("http://", "https://")):
            return self.extractors["web"].extract(source)

        s = source.lower()
        if s.endswith(".pdf"):
            return self.extractors["pdf"].extract(source)
        if s.endswith(".docx"):
            return self.extractors["docx"].extract(source)
        return self.extractors["text"].extract(source)

    def _detect_lang(self, text: str) -> Tuple[str, float]:
        """Detect language using primary detector, then fallback, then a safe default."""
        # Primary
        if self.lid_primary:
            try:
                return self.lid_primary.detect(text)
            except Exception:
                pass  # fall through

        # Fallback
        if self.lid_fallback:
            try:
                return self.lid_fallback.detect(text)
            except Exception:
                pass

        # Safe default
        return "pt", 0.0

    def _choose_global_language(
        self,
        lang_counts: Dict[str, int],
        *,
        fallback: str,
        paragraphs: Iterable[str],
    ) -> str:
        """Choose the document-level language based on paragraph frequencies.

        Args:
            lang_counts: map of language -> count.
            fallback: language code to use if counts are empty or tie.
            paragraphs: the original paragraph list, used to decide on empty docs.

        Returns:
            Selected language code.
        """
        if not paragraphs:
            return fallback
        # Pick the language with the highest count; if all zero, use fallback
        winner, count = max(lang_counts.items(), key=lambda kv: kv[1]) if lang_counts else (fallback, 0)
        return winner if count > 0 else fallback

    def _export_all(self, result: Dict[str, Any]) -> None:
        """Run all configured exporters; isolate failures per exporter."""
        for name, exp in self.exporters.items():
            try:
                exp.export(result)
            except Exception as e:
                # Don't fail the whole pipeline if a specific exporter breaks
                # (the caller still gets the JSON result).
                # In a real app, consider logging this.
                # Example: logger.exception("Exporter %s failed: %s", name, e)
                _ = e  # silence flake/linters
                continue
