import json
from pathlib import Path

import pytest

from intelli3text import PipelineBuilder, Intelli3Config


def _make_sample_text(tmp_path: Path) -> Path:
    p = tmp_path / "sample.txt"
    p.write_text(
        (
            "Howard Gardner is known for the theory of multiple intelligences.\n"
            "This paragraph contains a URL that should be removed: https://example.org\n\n"
            "A segunda parte está em português para simular conteúdo bilíngue.\n"
            "Quebras de linha\nno meio da frase devem ser normalizadas.\n\n"
            "Tercera parte en español para probar la detección por párrafo."
        ),
        encoding="utf-8",
    )
    return p


def test_smoke_pipeline_local_text(tmp_path: Path):
    # Arrange
    source = _make_sample_text(tmp_path)

    # Disable LID to avoid downloading fastText / cld3 in CI or offline envs
    cfg = Intelli3Config(export=None)
    pipeline = PipelineBuilder(cfg).build()
    pipeline.lid_primary = None
    pipeline.lid_fallback = None

    # Act
    res = pipeline.process(str(source))

    # Assert: basic structure
    assert isinstance(res, dict)
    for key in ("language_global", "raw", "cleaned", "normalized", "paragraphs"):
        assert key in res

    # Assert: paragraphs shape
    assert isinstance(res["paragraphs"], list)
    assert len(res["paragraphs"]) >= 1
    first = res["paragraphs"][0]
    for k in ("language", "score", "raw", "cleaned", "normalized"):
        assert k in first

    # With cleaners active, ensure URL got removed from cleaned text
    cleaned_concat = " ".join(p["cleaned"] for p in res["paragraphs"])
    assert "http://example.org" not in cleaned_concat
    assert "https://example.org" not in cleaned_concat

    # Normalized text should be non-empty and not equal to raw
    assert isinstance(res["normalized"], str)
    assert res["normalized"]
    assert res["normalized"] != res["raw"]


def test_pdf_export_writes_file(tmp_path: Path):
    # Arrange
    pdf_out = tmp_path / "report.pdf"
    cfg = Intelli3Config(
        export={"pdf": {"path": str(pdf_out), "include_global_normalized": True}}
    )
    pipeline = PipelineBuilder(cfg).build()
    pipeline.lid_primary = None  # avoid network
    pipeline.lid_fallback = None

    source = _make_sample_text(tmp_path)

    # Act
    res = pipeline.process(str(source))

    # Assert: file created and non-empty
    assert pdf_out.exists(), "PDF file was not created"
    assert pdf_out.stat().st_size > 0, "PDF file is empty"

    # Spot-check result keys
    assert "language_global" in res
    assert "paragraphs" in res


def test_json_roundtrip(tmp_path: Path):
    # Arrange
    source = _make_sample_text(tmp_path)

    cfg = Intelli3Config(export=None)
    pipeline = PipelineBuilder(cfg).build()
    pipeline.lid_primary = None
    pipeline.lid_fallback = None

    # Act
    res = pipeline.process(str(source))

    # Assert: JSON serializable
    js = json.dumps(res, ensure_ascii=False)
    assert isinstance(js, str) and js.startswith("{")
