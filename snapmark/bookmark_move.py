"""Move bookmarks between folders in a bookmark tree."""

from dataclasses import dataclass, field
from typing import List, Optional
from snapmark.models import Bookmark, BookmarkFolder


@dataclass
class MoveResult:
    moved_count: int = 0
    not_found: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)

    def summary(self) -> str:
        parts = [f"Moved: {self.moved_count}"]
        if self.not_found:
            parts.append(f"Not found: {len(self.not_found)}")
        if self.errors:
            parts.append(f"Errors: {len(self.errors)}")
        return " | ".join(parts)


def _find_folder(root: BookmarkFolder, name: str) -> Optional[BookmarkFolder]:
    """Recursively find a folder by name."""
    if root.title == name:
        return root
    for child in root.children:
        if isinstance(child, BookmarkFolder):
            found = _find_folder(child, name)
            if found:
                return found
    return None


def _remove_bookmark_by_url(
    folder: BookmarkFolder, url: str
) -> Optional[Bookmark]:
    """Remove and return a bookmark by URL from a folder tree."""
    for i, child in enumerate(folder.children):
        if isinstance(child, Bookmark) and child.url == url:
            folder.children.pop(i)
            return child
        if isinstance(child, BookmarkFolder):
            found = _remove_bookmark_by_url(child, url)
            if found:
                return found
    return None


def move_bookmarks(
    root: BookmarkFolder,
    urls: List[str],
    destination_folder: str,
) -> tuple[BookmarkFolder, MoveResult]:
    """Move bookmarks identified by URL into a destination folder by name."""
    result = MoveResult()
    dest = _find_folder(root, destination_folder)

    if dest is None:
        result.errors.append(f"Destination folder '{destination_folder}' not found.")
        return root, result

    for url in urls:
        bookmark = _remove_bookmark_by_url(root, url)
        if bookmark is None:
            result.not_found.append(url)
        else:
            dest.children.append(bookmark)
            result.moved_count += 1

    return root, result
