from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Iterable, Any, Optional

from .base import IExporter


def _ensure_dir(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def export_json(path: str | Path, result: Dict[str, Any], *, pretty: bool = True) -> None:
    """Write a single JSON file (atomic).

    Args:
        path: Destination file path.
        result: Dictionary to serialize.
        pretty: When True, writes indented JSON (indent=2).
    """
    dst = Path(path)
    _ensure_dir(dst)
    tmp = dst.with_suffix(dst.suffix + ".part")

    with tmp.open("w", encoding="utf-8") as f:
        if pretty:
            json.dump(result, f, ensure_ascii=False, indent=2)
        else:
            json.dump(result, f, ensure_ascii=False, separators=(",", ":"))

    tmp.replace(dst)


def export_jsonl(path: str | Path, items: Iterable[Dict[str, Any]]) -> None:
    """Write a JSON Lines file (atomic), one object per line.

    Args:
        path: Destination file path.
        items: Iterable of dictionaries to write as lines.
    """
    dst = Path(path)
    _ensure_dir(dst)
    tmp = dst.with_suffix(dst.suffix + ".part")

    with tmp.open("w", encoding="utf-8") as f:
        for it in items:
            f.write(json.dumps(it, ensure_ascii=False))
            f.write("\n")

    tmp.replace(dst)


class JSONExporter(IExporter):
    """Exporter that writes the full pipeline `result` to a single JSON file."""

    def __init__(self, *, path: str, pretty: bool = True) -> None:
        if not path:
            raise ValueError("JSONExporter requires a non-empty 'path'.")
        self.path = path
        self.pretty = pretty

    def export(self, result: Dict[str, Any]) -> None:
        export_json(self.path, result, pretty=self.pretty)


class JSONLExporter(IExporter):
    """Exporter that writes paragraph items to a JSON Lines file.

    It looks for `result["paragraphs"]` and writes each item as one line.
    If the key is missing or empty, it writes nothing (but still creates the file).
    """

    def __init__(self, *, path: str) -> None:
        if not path:
            raise ValueError("JSONLExporter requires a non-empty 'path'.")
        self.path = path

    def export(self, result: Dict[str, Any]) -> None:
        items = result.get("paragraphs") or []
        if not isinstance(items, Iterable):
            items = []
        export_jsonl(self.path, items)  # atomic write
