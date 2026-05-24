"""Prune bookmarks older than a given number of days based on their added_date metadata."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import List

from snapmark.models import Bookmark, BookmarkFolder


@dataclass
class PruneResult:
    removed: List[Bookmark] = field(default_factory=list)
    kept: int = 0

    @property
    def removed_count(self) -> int:
        return len(self.removed)

    def summary(self) -> str:
        return (
            f"Pruned {self.removed_count} bookmark(s) older than threshold; "
            f"{self.kept} bookmark(s) kept."
        )


def _prune_folder(
    folder: BookmarkFolder,
    cutoff: datetime,
    result: PruneResult,
) -> BookmarkFolder:
    kept_children = []

    for child in folder.children:
        if isinstance(child, Bookmark):
            added = child.metadata.get("added_date")
            if added:
                try:
                    added_dt = datetime.fromisoformat(added)
                    if added_dt.tzinfo is None:
                        added_dt = added_dt.replace(tzinfo=timezone.utc)
                    if added_dt < cutoff:
                        result.removed.append(child)
                        continue
                except ValueError:
                    pass  # unparseable date — keep the bookmark
            result.kept += 1
            kept_children.append(child)
        elif isinstance(child, BookmarkFolder):
            pruned_subfolder = _prune_folder(child, cutoff, result)
            kept_children.append(pruned_subfolder)
        else:
            kept_children.append(child)

    return BookmarkFolder(
        title=folder.title,
        children=kept_children,
        metadata=folder.metadata,
    )


def prune_tree(
    root: BookmarkFolder,
    days: int,
) -> tuple[BookmarkFolder, PruneResult]:
    """Remove bookmarks whose added_date is older than *days* days ago.

    Bookmarks without an added_date are always kept.
    Returns the pruned tree and a PruneResult summary.
    """
    if days < 0:
        raise ValueError("days must be a non-negative integer")

    cutoff = datetime.now(tz=timezone.utc).replace(
        hour=0, minute=0, second=0, microsecond=0
    )
    from datetime import timedelta
    cutoff = cutoff - timedelta(days=days)

    result = PruneResult()
    pruned_root = _prune_folder(root, cutoff, result)
    return pruned_root, result
