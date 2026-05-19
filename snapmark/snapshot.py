"""Snapshot and restore bookmark trees to/from JSON files."""

from __future__ import annotations
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Union

from snapmark.models import BookmarkFolder, Bookmark

BookmarkNode = Union[BookmarkFolder, Bookmark]

DEFAULT_SNAPSHOT_DIR = Path.home() / ".snapmark" / "snapshots"


def _ensure_snapshot_dir(directory: Path) -> None:
    """Create snapshot directory if it does not exist."""
    directory.mkdir(parents=True, exist_ok=True)


def save_snapshot(
    root: BookmarkFolder,
    name: str | None = None,
    directory: Path = DEFAULT_SNAPSHOT_DIR,
) -> Path:
    """
    Serialize a bookmark tree to a timestamped JSON snapshot file.

    Args:
        root: The root BookmarkFolder to snapshot.
        name: Optional label for the snapshot filename.
        directory: Directory where snapshots are stored.

    Returns:
        Path to the saved snapshot file.
    """
    _ensure_snapshot_dir(directory)
    timestamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    label = f"{name}_" if name else ""
    filename = f"{label}{timestamp}.json"
    filepath = directory / filename

    payload = {
        "snapmark_version": "1.0",
        "created_at": timestamp,
        "label": name,
        "tree": root.to_dict(),
    }

    with open(filepath, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=2, ensure_ascii=False)

    return filepath


def load_snapshot(filepath: Path | str) -> BookmarkFolder:
    """
    Deserialize a bookmark tree from a JSON snapshot file.

    Args:
        filepath: Path to the snapshot JSON file.

    Returns:
        The root BookmarkFolder restored from the snapshot.
    """
    filepath = Path(filepath)
    if not filepath.exists():
        raise FileNotFoundError(f"Snapshot not found: {filepath}")

    with open(filepath, "r", encoding="utf-8") as fh:
        payload = json.load(fh)

    tree_data = payload.get("tree")
    if tree_data is None:
        raise ValueError("Invalid snapshot: missing 'tree' key.")

    return BookmarkFolder.from_dict(tree_data)


def list_snapshots(directory: Path = DEFAULT_SNAPSHOT_DIR) -> list[Path]:
    """Return all snapshot files sorted by modification time (newest first)."""
    if not directory.exists():
        return []
    return sorted(
        directory.glob("*.json"),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
