"""Restore bookmark trees from snapshots."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from snapmark.models import BookmarkFolder, from_dict
from snapmark.snapshot import load_snapshot, list_snapshots


class RestoreError(Exception):
    """Raised when a restore operation fails."""


def restore_snapshot(name: str, snapshot_dir: Optional[Path] = None) -> BookmarkFolder:
    """Load and return a bookmark tree from a named snapshot.

    Args:
        name: The snapshot name (with or without .json extension).
        snapshot_dir: Optional custom directory to search for snapshots.

    Returns:
        The root BookmarkFolder from the snapshot.

    Raises:
        RestoreError: If the snapshot cannot be found or parsed.
    """
    try:
        data = load_snapshot(name, snapshot_dir=snapshot_dir)
    except FileNotFoundError:
        available = list_snapshots(snapshot_dir=snapshot_dir)
        hint = f" Available snapshots: {available}" if available else " No snapshots found."
        raise RestoreError(f"Snapshot '{name}' not found.{hint}")
    except json.JSONDecodeError as exc:
        raise RestoreError(f"Snapshot '{name}' contains invalid JSON: {exc}") from exc

    try:
        root = from_dict(data)
    except (KeyError, TypeError, ValueError) as exc:
        raise RestoreError(f"Failed to parse snapshot '{name}': {exc}") from exc

    if not isinstance(root, BookmarkFolder):
        raise RestoreError(
            f"Snapshot '{name}' root must be a BookmarkFolder, got {type(root).__name__}."
        )

    return root


def export_to_json(folder: BookmarkFolder, output_path: Path) -> None:
    """Serialize a BookmarkFolder tree to a JSON file.

    Args:
        folder: The root BookmarkFolder to export.
        output_path: Destination file path.
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as fh:
        json.dump(folder.to_dict(), fh, indent=2, ensure_ascii=False)
