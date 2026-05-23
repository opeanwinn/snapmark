"""Flatten a bookmark tree into a single list of bookmarks with path info."""

from dataclasses import dataclass, field
from typing import List

from snapmark.models import Bookmark, BookmarkFolder


@dataclass
class FlatBookmark:
    """A bookmark with its full folder path."""
    bookmark: Bookmark
    path: List[str] = field(default_factory=list)

    @property
    def breadcrumb(self) -> str:
        """Return the folder path as a slash-separated string."""
        return " / ".join(self.path) if self.path else "/"

    def __repr__(self) -> str:
        return f"FlatBookmark(title={self.bookmark.title!r}, path={self.breadcrumb!r})"


@dataclass
class FlattenResult:
    """Result of flattening a bookmark tree."""
    bookmarks: List[FlatBookmark] = field(default_factory=list)

    @property
    def total(self) -> int:
        return len(self.bookmarks)

    def summary(self) -> str:
        return f"Flattened {self.total} bookmark(s) across all folders."


def _flatten_folder(
    folder: BookmarkFolder,
    current_path: List[str],
    result: FlattenResult,
) -> None:
    """Recursively walk a folder and append FlatBookmark entries."""
    path = current_path + [folder.title]
    for child in folder.children:
        if isinstance(child, Bookmark):
            result.bookmarks.append(FlatBookmark(bookmark=child, path=path))
        elif isinstance(child, BookmarkFolder):
            _flatten_folder(child, path, result)


def flatten_tree(root: BookmarkFolder) -> FlattenResult:
    """Flatten an entire bookmark tree into a FlattenResult."""
    result = FlattenResult()
    _flatten_folder(root, [], result)
    return result
