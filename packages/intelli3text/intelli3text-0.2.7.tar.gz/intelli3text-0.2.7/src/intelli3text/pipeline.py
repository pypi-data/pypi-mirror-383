from __future__ import annotations

from typing import Dict, Tuple, Iterable, Mapping, Any, List
from .config import Intelli3Config


class Pipeline:
    """High-level façade that orchestrates extraction, cleaning, LID, normalization and export.

    Components (informal contracts):
        - Extractors: objects with `extract(path_or_url: str) -> str`
          Keys used: "web" | "pdf" | "docx" | "text"
        - Cleaners (chain object) exposing:
            * `apply(text: str) -> str` (full-document cleaning)
            * `apply_paragraph(text: str) -> str` (per-paragraph cleaning)
        - LID: objects with `detect(text: str) -> tuple[str, float]` (lang, confidence)
        - Normalizer:
            * `split_paragraphs(text: str) -> list[str]`
            * `normalize(text: str, lang: str) -> str`
        - Exporters: mapping name -> object exposing `export(result: dict) -> None`

    Notes:
        * Global language is chosen by paragraph frequency (tie-break by summed score),
          restricted to `cfg.languages_supported` when provided.
        * LID sampling prefers the cleaned paragraph; if too curto, usa o raw.
        * A document is flagged as "mixed" when a significant share of paragraphs either
          (a) have low confidence or (b) disagree with the global language.
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
        """Process a URL or local file and return a structured dictionary."""
        # 1) Extract and clean full text
        raw = self._extract(source)
        cleaned = self.cleaners.apply(raw)

        # 2) Paragraph segmentation (use the normalizer's splitter)
        paragraphs: List[str] = self.normalizer.split_paragraphs(cleaned)

        # 3) LID per paragraph
        supported = set(getattr(self.cfg, "languages_supported", []) or [])
        lid_min_chars = int(getattr(self.cfg, "lid_min_chars", 25) or 25)
        lid_max_chars = int(getattr(self.cfg, "lid_max_chars", 2500) or 2500)
        lid_threshold = float(getattr(self.cfg, "lid_threshold", 0.65))

        lang_counts: Dict[str, int] = {}
        lang_score_sums: Dict[str, float] = {}
        para_results: List[Dict[str, Any]] = []

        for p_raw in paragraphs:
            p_clean = self.cleaners.apply_paragraph(p_raw)

            # Decide sample for LID (prefer cleaned if long enough), with optional truncate
            unit = p_clean if len(p_clean) >= lid_min_chars else p_raw
            if lid_max_chars and len(unit) > lid_max_chars:
                unit = unit[:lid_max_chars]

            lang, score = self._detect_lang(unit)

            # Coerce to supported set if configured
            if supported and lang not in supported:
                lang2 = (lang or "").split("-")[0][:2]
                lang = lang2 if lang2 in supported else self._default_lang()

            # Tallies
            lang_counts[lang] = lang_counts.get(lang, 0) + 1
            lang_score_sums[lang] = lang_score_sums.get(lang, 0.0) + float(score)

            # Normalize paragraph with routed language
            normalized = self.normalizer.normalize(p_clean, lang)

            para_results.append(
                {
                    "language": lang,
                    "score": float(score),
                    "raw": p_raw,
                    "cleaned": p_clean,
                    "normalized": normalized,
                }
            )

        # 4) Global language + "mixed" flag
        global_lang = self._choose_global_language(
            lang_counts, lang_score_sums, fallback=self._default_lang()
        )

        mixed_share = 0.0
        if para_results:
            low_conf = sum(1 for pr in para_results if pr["score"] < lid_threshold)
            disagree = sum(1 for pr in para_results if pr["language"] != global_lang)
            mixed_share = max(low_conf, disagree) / float(len(para_results))
        language_mixed = mixed_share >= 0.15

        # 5) Concatenate normalized text
        normalized_all = " ".join(p["normalized"] for p in para_results)

        result = {
            "language_global": global_lang,
            "language_mixed": language_mixed,
            "language_distribution": dict(
                sorted(lang_counts.items(), key=lambda kv: (-kv[1], kv[0]))
            ),
            "raw": raw,
            "cleaned": cleaned,
            "normalized": normalized_all,
            "paragraphs": para_results,
        }

        # 6) Export (best-effort)
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
                pass

        # Fallback
        if self.lid_fallback:
            try:
                return self.lid_fallback.detect(text)
            except Exception:
                pass

        # Safe default
        return self._default_lang(), 0.0

    def _default_lang(self) -> str:
        # "pt" remains a safe default for the intended workflows
        return "pt"

    def _choose_global_language(
        self,
        lang_counts: Dict[str, int],
        lang_score_sums: Dict[str, float],
        *,
        fallback: str,
    ) -> str:
        """Choose document-level language with frequency, then score tie-break."""
        if not lang_counts:
            return fallback

        winner = None
        best = (-1, -1.0)  # (count, score_sum)
        for lang, cnt in lang_counts.items():
            sc = lang_score_sums.get(lang, 0.0)
            key = (cnt, sc)
            if key > best:
                best = key
                winner = lang
        return winner or fallback

    def _export_all(self, result: Dict[str, Any]) -> None:
        """Run all configured exporters; isolate failures per exporter."""
        for _, exp in self.exporters.items():
            try:
                exp.export(result)
            except Exception:
                # Best-effort: do not fail the whole pipeline
                continue
