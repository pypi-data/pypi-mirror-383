from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Optional

import requests

# Environment variable allows overriding the cache directory location.
# Default: ~/.cache/intelli3text  (cross-platform friendly with Path.home()).
CACHE_DIR: Path = Path(
    os.getenv("INTELLI3TEXT_CACHE_DIR", Path.home() / ".cache" / "intelli3text")
)


def ensure_dir(p: Path) -> None:
    """Ensure directory exists (mkdir -p)."""
    p.mkdir(parents=True, exist_ok=True)


def cached_path(name: str) -> Path:
    """Return a Path within the library cache directory."""
    return CACHE_DIR / name


def _human_bytes(n: int) -> str:
    """Return a human-readable byte size."""
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if n < 1024:
            return f"{n:.1f} {unit}"
        n /= 1024.0
    return f"{n:.1f} PB"


def download_file(
    url: str,
    dest: Path,
    *,
    chunk: int = 1 << 20,  # 1 MiB
    timeout: float | tuple[float, float] = (10, 60),  # (connect, read)
    user_agent: Optional[str] = None,
    show_progress: Optional[bool] = None,
) -> None:
    """Download a file to ``dest`` with basic progress reporting and atomic write.

    The file is streamed and first written to ``dest.with_suffix(dest.suffix + '.part')``.
    Once complete, it is atomically moved to ``dest``. If the process is interrupted,
    the partially downloaded file is left on disk and may be overwritten by a future run.

    Args:
        url: Source URL.
        dest: Output file path.
        chunk: Stream chunk size in bytes (default 1 MiB).
        timeout: Requests timeout; single float or (connect, read) tuple.
        user_agent: Optional custom User-Agent header.
        show_progress: Whether to show progress to stderr. Defaults to True when
            stderr is a TTY, False otherwise.

    Raises:
        requests.HTTPError: On non-2xx responses.
        requests.RequestException: On networking issues/timeouts.
        OSError: On filesystem errors.
    """
    ensure_dir(dest.parent)
    tmp = dest.with_suffix(dest.suffix + ".part")

    if show_progress is None:
        show_progress = sys.stderr.isatty()

    headers = {"User-Agent": user_agent or "intelli3text/1.0 (+https://github.com/jeffersonspeck/intelli3text)"}

    with requests.get(url, stream=True, timeout=timeout, headers=headers) as r:
        r.raise_for_status()
        total = int(r.headers.get("Content-Length", "0")) if r.headers.get("Content-Length") else 0
        done = 0

        with open(tmp, "wb") as f:
            for block in r.iter_content(chunk_size=chunk):
                if not block:
                    continue
                f.write(block)
                done += len(block)
                if show_progress:
                    if total > 0:
                        pct = (done / total) * 100.0
                        sys.stderr.write(
                            f"\rDownloading {dest.name}: {pct:5.1f}% ({_human_bytes(done)}/{_human_bytes(total)})"
                        )
                    else:
                        sys.stderr.write(f"\rDownloading {dest.name}: {_human_bytes(done)}")
                    sys.stderr.flush()

    # Finish progress line
    if show_progress:
        sys.stderr.write("\n")

    # Atomic rename at the end
    tmp.replace(dest)
