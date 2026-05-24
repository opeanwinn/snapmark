"""Copy bookmarks matching a URL or title pattern into a destination folder."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from snapmark.models import Bookmark, BookmarkFolder


@dataclass
class CopyResult:
    copied: List[Bookmark] = field(default_factory=list)
    destination_folder: str = ""

    @property
    def copy_count(self) -> int:
        return len(self.copied)

    def summary(self) -> str:
        return (
            f"Copied {self.copy_count} bookmark(s) into '{self.destination_folder}'."
        )


def _find_folder(root: BookmarkFolder, name: str) -> Optional[BookmarkFolder]:
    if root.title == name:
        return root
    for child in root.children:
        if isinstance(child, BookmarkFolder):
            found = _find_folder(child, name)
            if found:
                return found
    return None


def _collect_matching(
    folder: BookmarkFolder,
    url_pattern: Optional[str],
    title_pattern: Optional[str],
) -> List[Bookmark]:
    matches: List[Bookmark] = []
    for child in folder.children:
        if isinstance(child, Bookmark):
            url_ok = url_pattern is None or url_pattern.lower() in child.url.lower()
            title_ok = (
                title_pattern is None
                or title_pattern.lower() in child.title.lower()
            )
            if url_ok and title_ok:
                matches.append(child)
        elif isinstance(child, BookmarkFolder):
            matches.extend(_collect_matching(child, url_pattern, title_pattern))
    return matches


def copy_bookmarks(
    root: BookmarkFolder,
    destination: str,
    url_pattern: Optional[str] = None,
    title_pattern: Optional[str] = None,
) -> tuple[BookmarkFolder, CopyResult]:
    """Copy bookmarks matching url_pattern and/or title_pattern into destination folder."""
    import copy

    new_root = copy.deepcopy(root)
    dest_folder = _find_folder(new_root, destination)

    if dest_folder is None:
        dest_folder = BookmarkFolder(title=destination, children=[])
        new_root.children.append(dest_folder)

    matched = _collect_matching(new_root, url_pattern, title_pattern)
    existing_urls = {
        b.url for b in dest_folder.children if isinstance(b, Bookmark)
    }

    result = CopyResult(destination_folder=destination)
    for bm in matched:
        if bm.url not in existing_urls:
            dest_folder.children.append(copy.deepcopy(bm))
            existing_urls.add(bm.url)
            result.copied.append(bm)

    return new_root, result
