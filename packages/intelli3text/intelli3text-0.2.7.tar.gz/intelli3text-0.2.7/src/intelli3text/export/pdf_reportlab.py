from __future__ import annotations

import datetime as _dt
from typing import Dict, Any, List, Optional
from xml.sax.saxutils import escape as _xml_escape

from reportlab.lib.pagesizes import A4, letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak,
)

from .base import IExporter


def _safe(s: Any) -> str:
    """Escape text for ReportLab Paragraph (basic XML entities)."""
    if s is None:
        return ""
    return _xml_escape(str(s))


def _truncate(s: str, max_len: int = 240) -> str:
    """Shorten long previews for the summary table."""
    if s is None:
        return ""
    s = str(s)
    return s if len(s) <= max_len else s[: max_len - 1] + "…"


class PDFExporter(IExporter):
    """Export the pipeline result to a nicely formatted PDF report.

    Sections:
        1) Header + summary (global language, paragraph count, timestamp)
        2) (Optional) Global normalized text
        3) Paragraph overview table (language, score, normalized preview)
        4) Per-paragraph details (Normalized, Cleaned, Raw)

    Args:
        path: Output PDF path (required).
        include_global_normalized: Include the full concatenated normalized text.
        title: Optional document title (shown in the header).
        page_size: ReportLab page size (e.g., `A4`, `letter`).
        margin_cm: Page margin in centimeters.

    Example:
        >>> exporter = PDFExporter(path="report.pdf", include_global_normalized=True, title="intelli3text Report")
        >>> exporter.export(result_dict)
    """

    def __init__(
        self,
        *,
        path: str,
        include_global_normalized: bool = True,
        title: Optional[str] = None,
        page_size=A4,
        margin_cm: float = 2.0,
    ) -> None:
        if not path:
            raise ValueError("PDFExporter requires a non-empty 'path'.")

        self.path = path
        self.include_global_normalized = include_global_normalized
        self.title = title or "intelli3text Report"
        self.page_size = page_size
        self.margin = margin_cm * cm

        # Base stylesheet + a few tuned styles
        self.styles = getSampleStyleSheet()
        self.styles.add(
            ParagraphStyle(
                name="Heading1Center",
                parent=self.styles["Heading1"],
                alignment=1,  # TA_CENTER
                spaceAfter=12,
            )
        )
        self.styles.add(
            ParagraphStyle(
                name="MonoSmall",
                parent=self.styles["Code"],
                fontSize=8,
                leading=10,
            )
        )
        self.styles.add(
            ParagraphStyle(
                name="BodySmall",
                parent=self.styles["BodyText"],
                fontSize=9,
                leading=12,
            )
        )

    # ---------------
    # Public API
    # ---------------

    def export(self, result: Dict[str, Any]) -> None:
        """Write a PDF report to `self.path` based on `result`."""
        doc = SimpleDocTemplate(
            self.path,
            pagesize=self.page_size,
            leftMargin=self.margin,
            rightMargin=self.margin,
            topMargin=self.margin,
            bottomMargin=self.margin,
            title=self.title,
        )

        story: List[Any] = []
        self._build_header(story, result)
        self._build_summary(story, result)

        if self.include_global_normalized:
            self._build_global_normalized(story, result)

        self._build_paragraph_overview(story, result)
        self._build_paragraph_details(story, result)

        doc.build(story)

    # ---------------
    # Document parts
    # ---------------

    def _build_header(self, story: List[Any], result: Dict[str, Any]) -> None:
        story.append(Paragraph(_safe(self.title), self.styles["Heading1Center"]))
        ts = _dt.datetime.now().isoformat(timespec="seconds")
        info = f"Generated: {ts}"
        story.append(Paragraph(_safe(info), self.styles["BodyText"]))
        story.append(Spacer(1, 8))

    def _build_summary(self, story: List[Any], result: Dict[str, Any]) -> None:
        lg = result.get("language_global", "n/a")
        n_pars = len(result.get("paragraphs", []) or [])
        data = [
            ["Global language", _safe(lg)],
            ["Paragraphs", str(n_pars)],
        ]
        tbl = Table(data, hAlign="LEFT", colWidths=[4 * cm, None])
        tbl.setStyle(
            TableStyle(
                [
                    ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
                    ("BACKGROUND", (0, 0), (0, -1), colors.whitesmoke),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
                    ("FONTSIZE", (0, 0), (-1, -1), 10),
                ]
            )
        )
        story.append(tbl)
        story.append(Spacer(1, 12))

    def _build_global_normalized(self, story: List[Any], result: Dict[str, Any]) -> None:
        story.append(Paragraph("Global Normalized Text", self.styles["Heading2"]))
        text = result.get("normalized", "") or ""
        if not text.strip():
            story.append(Paragraph("<i>(empty)</i>", self.styles["BodyText"]))
        else:
            # Use smaller style for long content
            story.append(Paragraph(_safe(text), self.styles["BodySmall"]))
        story.append(Spacer(1, 12))

    def _build_paragraph_overview(self, story: List[Any], result: Dict[str, Any]) -> None:
        story.append(Paragraph("Paragraph Overview", self.styles["Heading2"]))

        rows = [["#", "Language", "Score", "Normalized (preview)"]]
        paragraphs = result.get("paragraphs", []) or []
        for i, item in enumerate(paragraphs, 1):
            rows.append(
                [
                    str(i),
                    _safe(item.get("language", "")),
                    f"{float(item.get('score', 0.0)):.3f}",
                    _safe(_truncate(item.get("normalized", ""))),
                ]
            )

        col_widths = [1.2 * cm, 3 * cm, 2.5 * cm, None]
        tbl = Table(rows, hAlign="LEFT", colWidths=col_widths, repeatRows=1)
        tbl.setStyle(
            TableStyle(
                [
                    ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f0f0f0")),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
                    ("FONTSIZE", (0, 0), (-1, -1), 9),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ]
            )
        )
        story.append(tbl)
        story.append(Spacer(1, 12))

    def _build_paragraph_details(self, story: List[Any], result: Dict[str, Any]) -> None:
        story.append(PageBreak())
        story.append(Paragraph("Paragraph Details", self.styles["Heading2"]))
        story.append(Spacer(1, 6))

        paragraphs = result.get("paragraphs", []) or []
        for idx, item in enumerate(paragraphs, 1):
            story.append(Paragraph(f"Paragraph {idx}", self.styles["Heading3"]))
            meta = f"Language: {item.get('language', 'n/a')} | Score: {float(item.get('score', 0.0)):.3f}"
            story.append(Paragraph(_safe(meta), self.styles["BodyText"]))
            story.append(Spacer(1, 4))

            # Normalized
            story.append(Paragraph("<b>Normalized</b>", self.styles["BodyText"]))
            norm = item.get("normalized", "") or ""
            story.append(Paragraph(_safe(norm) if norm.strip() else "<i>(empty)</i>", self.styles["BodySmall"]))
            story.append(Spacer(1, 6))

            # Cleaned
            story.append(Paragraph("<b>Cleaned</b>", self.styles["BodyText"]))
            cleaned = item.get("cleaned", "") or ""
            story.append(Paragraph(_safe(cleaned) if cleaned.strip() else "<i>(empty)</i>", self.styles["BodySmall"]))
            story.append(Spacer(1, 6))

            # Raw
            story.append(Paragraph("<b>Raw</b>", self.styles["BodyText"]))
            raw = item.get("raw", "") or ""
            story.append(Paragraph(_safe(raw) if raw.strip() else "<i>(empty)</i>", self.styles["BodySmall"]))
            story.append(Spacer(1, 10))

            # Page break between items for readability (optional)
            if idx < len(paragraphs):
                story.append(PageBreak())
