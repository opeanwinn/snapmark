"""Deduplicate bookmarks within a bookmark tree by URL."""

from dataclasses import dataclass, field
from typing import List

from snapmark.models import Bookmark, BookmarkFolder


@dataclass
class DedupeResult:
    removed: List[Bookmark] = field(default_factory=list)
    kept: List[Bookmark] = field(default_factory=list)

    @property
    def duplicate_count(self) -> int:
        return len(self.removed)

    def summary(self) -> str:
        if self.duplicate_count == 0:
            return "No duplicates found."
        return (
            f"Removed {self.duplicate_count} duplicate(s). "
            f"Kept {len(self.kept)} unique bookmark(s)."
        )


def _dedupe_folder(
    folder: BookmarkFolder,
    seen_urls: set,
    result: DedupeResult,
) -> BookmarkFolder:
    new_children = []
    for child in folder.children:
        if isinstance(child, Bookmark):
            if child.url in seen_urls:
                result.removed.append(child)
            else:
                seen_urls.add(child.url)
                result.kept.append(child)
                new_children.append(child)
        elif isinstance(child, BookmarkFolder):
            deduped_subfolder = _dedupe_folder(child, seen_urls, result)
            new_children.append(deduped_subfolder)
    return BookmarkFolder(name=folder.name, children=new_children)


def dedupe_tree(
    root: BookmarkFolder,
    seen_urls: set | None = None,
) -> tuple[BookmarkFolder, DedupeResult]:
    """Return a new tree with duplicate URLs removed and a DedupeResult report."""
    if seen_urls is None:
        seen_urls = set()
    result = DedupeResult()
    deduped_root = _dedupe_folder(root, seen_urls, result)
    return deduped_root, result
