"""Pin and unpin bookmarks by URL for quick access tracking."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from snapmark.models import Bookmark, BookmarkFolder


@dataclass
class PinResult:
    pinned: List[Bookmark] = field(default_factory=list)
    unpinned: List[Bookmark] = field(default_factory=list)
    not_found: List[str] = field(default_factory=list)

    def summary(self) -> str:
        lines = []
        if self.pinned:
            lines.append(f"Pinned {len(self.pinned)} bookmark(s):")
            for b in self.pinned:
                lines.append(f"  + {b.title} <{b.url}>")
        if self.unpinned:
            lines.append(f"Unpinned {len(self.unpinned)} bookmark(s):")
            for b in self.unpinned:
                lines.append(f"  - {b.title} <{b.url}>")
        if self.not_found:
            lines.append(f"Not found ({len(self.not_found)}):")
            for url in self.not_found:
                lines.append(f"  ? {url}")
        if not lines:
            return "No changes made."
        return "\n".join(lines)


PIN_TAG = "pinned"


def _process_folder(
    folder: BookmarkFolder,
    target_urls: set,
    pin: bool,
    result: PinResult,
) -> BookmarkFolder:
    new_children = []
    for child in folder.children:
        if isinstance(child, Bookmark):
            if child.url in target_urls:
                tags = list(child.tags or [])
                if pin and PIN_TAG not in tags:
                    tags.append(PIN_TAG)
                    updated = Bookmark(
                        title=child.title,
                        url=child.url,
                        tags=tags,
                        added=child.added,
                    )
                    result.pinned.append(updated)
                    new_children.append(updated)
                elif not pin and PIN_TAG in tags:
                    tags.remove(PIN_TAG)
                    updated = Bookmark(
                        title=child.title,
                        url=child.url,
                        tags=tags,
                        added=child.added,
                    )
                    result.unpinned.append(updated)
                    new_children.append(updated)
                else:
                    new_children.append(child)
            else:
                new_children.append(child)
        elif isinstance(child, BookmarkFolder):
            new_children.append(_process_folder(child, target_urls, pin, result))
        else:
            new_children.append(child)
    return BookmarkFolder(name=folder.name, children=new_children)


def pin_bookmarks(root: BookmarkFolder, urls: List[str]) -> tuple[BookmarkFolder, PinResult]:
    """Add the 'pinned' tag to bookmarks matching the given URLs."""
    result = PinResult()
    target_urls = set(urls)
    new_root = _process_folder(root, target_urls, pin=True, result=result)
    found_urls = {b.url for b in result.pinned}
    result.not_found = [u for u in urls if u not in found_urls]
    return new_root, result


def unpin_bookmarks(root: BookmarkFolder, urls: List[str]) -> tuple[BookmarkFolder, PinResult]:
    """Remove the 'pinned' tag from bookmarks matching the given URLs."""
    result = PinResult()
    target_urls = set(urls)
    new_root = _process_folder(root, target_urls, pin=False, result=result)
    found_urls = {b.url for b in result.unpinned}
    result.not_found = [u for u in urls if u not in found_urls]
    return new_root, result


def get_pinned(root: BookmarkFolder) -> List[Bookmark]:
    """Return all bookmarks that carry the 'pinned' tag."""
    pinned: List[Bookmark] = []
    _collect_pinned(root, pinned)
    return pinned


def _collect_pinned(folder: BookmarkFolder, acc: List[Bookmark]) -> None:
    for child in folder.children:
        if isinstance(child, Bookmark) and PIN_TAG in (child.tags or []):
            acc.append(child)
        elif isinstance(child, BookmarkFolder):
            _collect_pinned(child, acc)
