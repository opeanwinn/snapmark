"""Utilities for diffing two bookmark trees."""

from dataclasses import dataclass, field
from typing import List, Tuple

from snapmark.models import Bookmark, BookmarkFolder


@dataclass
class DiffResult:
    added: List[Bookmark] = field(default_factory=list)
    removed: List[Bookmark] = field(default_factory=list)
    moved: List[Tuple[Bookmark, str, str]] = field(default_factory=list)  # (bookmark, old_path, new_path)

    @property
    def has_changes(self) -> bool:
        return bool(self.added or self.removed or self.moved)

    def summary(self) -> str:
        lines = []
        if self.added:
            lines.append(f"  Added   ({len(self.added)}):")
            for b in self.added:
                lines.append(f"    + {b.title} <{b.url}>")
        if self.removed:
            lines.append(f"  Removed ({len(self.removed)}):")
            for b in self.removed:
                lines.append(f"    - {b.title} <{b.url}>")
        if self.moved:
            lines.append(f"  Moved   ({len(self.moved)}):")
            for b, old, new in self.moved:
                lines.append(f"    ~ {b.title}: {old} -> {new}")
        if not lines:
            return "No changes."
        return "\n".join(lines)


def _collect_bookmarks(node, path: str = "") -> dict:
    """Recursively collect all bookmarks as {url: (Bookmark, path)}."""
    result = {}
    if isinstance(node, Bookmark):
        result[node.url] = (node, path)
    elif isinstance(node, BookmarkFolder):
        folder_path = f"{path}/{node.title}" if path else node.title
        for child in node.children:
            result.update(_collect_bookmarks(child, folder_path))
    return result


def diff_trees(old_root: BookmarkFolder, new_root: BookmarkFolder) -> DiffResult:
    """Compare two bookmark trees and return a DiffResult."""
    old_map = _collect_bookmarks(old_root)
    new_map = _collect_bookmarks(new_root)

    result = DiffResult()

    for url, (bookmark, new_path) in new_map.items():
        if url not in old_map:
            result.added.append(bookmark)
        else:
            _, old_path = old_map[url]
            if old_path != new_path:
                result.moved.append((bookmark, old_path, new_path))

    for url, (bookmark, _) in old_map.items():
        if url not in new_map:
            result.removed.append(bookmark)

    return result
