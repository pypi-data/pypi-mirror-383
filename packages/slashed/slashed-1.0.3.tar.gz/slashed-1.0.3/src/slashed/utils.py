"""Common completion providers."""

from __future__ import annotations

import os
from typing import TYPE_CHECKING

from slashed.log import get_logger


if TYPE_CHECKING:
    from pathlib import Path

    import upath


type PathType = str | os.PathLike[str]


logger = get_logger(__name__)


def get_file_kind(path: Path | upath.UPath) -> str:
    """Get more specific file kind based on extension."""
    ext = path.suffix.lower()
    return {
        ".py": "python",
        ".yml": "yaml",
        ".yaml": "yaml",
        ".json": "json",
        ".md": "markdown",
        ".txt": "text",
    }.get(ext, "file")


def format_size(size: int) -> str:
    """Format file size in human readable format."""
    for unit in ["B", "KB", "MB", "GB"]:
        if size < 1024:  # noqa: PLR2004
            return f"{size:.1f} {unit}"
        size /= 1024  # type: ignore
    return f"{size:.1f} TB"


def get_metadata(path: Path | upath.UPath) -> str:
    """Get metadata for path entry."""
    try:
        if path.is_dir():
            return f"Directory ({len(list(path.iterdir()))} items)"
        size = format_size(path.stat().st_size)
        return f"{path.suffix[1:].upper()} file, {size}"
    except Exception:  # noqa: BLE001
        return ""


def get_first_line(text: str | None) -> str | None:
    """Get first line of text, stripped of whitespace.

    Args:
        text: Input text or None

    Returns:
        First line without whitespace if text is provided, None otherwise
    """
    if not text:
        return None
    return text.split("\n")[0].strip()
