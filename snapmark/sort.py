"""Sorting utilities for bookmark trees."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from snapmark.models import Bookmark, BookmarkFolder


@dataclass
class SortResult:
    total_sorted: int = 0
    folders_sorted: int = 0

    def summary(self) -> str:
        return (
            f"Sorted {self.total_sorted} bookmark(s) across "
            f"{self.folders_sorted} folder(s)."
        )


def _sort_folder(
    folder: BookmarkFolder,
    key: str = "title",
    reverse: bool = False,
    result: SortResult | None = None,
) -> BookmarkFolder:
    """Recursively sort a folder's children by key ('title' or 'url')."""
    if result is None:
        result = SortResult()

    def _sort_key(item: Bookmark | BookmarkFolder) -> str:
        if isinstance(item, Bookmark):
            return (getattr(item, key, item.title) or "").lower()
        return item.title.lower()

    sorted_children: List[Bookmark | BookmarkFolder] = sorted(
        folder.children, key=_sort_key, reverse=reverse
    )

    new_children: List[Bookmark | BookmarkFolder] = []
    for child in sorted_children:
        if isinstance(child, BookmarkFolder):
            new_children.append(
                _sort_folder(child, key=key, reverse=reverse, result=result)
            )
        else:
            new_children.append(child)
            result.total_sorted += 1

    result.folders_sorted += 1

    return BookmarkFolder(
        title=folder.title,
        children=new_children,
    )


def sort_tree(
    root: BookmarkFolder,
    key: str = "title",
    reverse: bool = False,
) -> tuple[BookmarkFolder, SortResult]:
    """Sort an entire bookmark tree and return the sorted tree with stats."""
    if key not in ("title", "url"):
        raise ValueError(f"Invalid sort key '{key}'. Must be 'title' or 'url'.")
    result = SortResult()
    sorted_root = _sort_folder(root, key=key, reverse=reverse, result=result)
    return sorted_root, result
