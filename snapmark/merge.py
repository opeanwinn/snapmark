"""Merge two bookmark trees, combining folders and deduplicating bookmarks by URL."""

from typing import List, Optional
from snapmark.models import Bookmark, BookmarkFolder


def _merge_bookmarks(
    base: List[Bookmark], incoming: List[Bookmark]
) -> List[Bookmark]:
    """Merge two lists of bookmarks, deduplicating by URL."""
    seen_urls = {b.url: b for b in base}
    for bookmark in incoming:
        if bookmark.url not in seen_urls:
            seen_urls[bookmark.url] = bookmark
    return list(seen_urls.values())


def _find_folder_by_name(
    folders: List[BookmarkFolder], name: str
) -> Optional[BookmarkFolder]:
    """Find a folder in a list by its name."""
    for folder in folders:
        if folder.name == name:
            return folder
    return None


def merge_trees(
    base: BookmarkFolder, incoming: BookmarkFolder
) -> BookmarkFolder:
    """Recursively merge two bookmark folder trees.

    - Bookmarks are deduplicated by URL (base takes precedence on conflict).
    - Folders with matching names are merged recursively.
    - Folders only in incoming are appended.

    Args:
        base: The base bookmark tree (higher priority).
        incoming: The incoming bookmark tree to merge in.

    Returns:
        A new BookmarkFolder representing the merged tree.
    """
    merged_bookmarks = _merge_bookmarks(
        base.bookmarks, incoming.bookmarks
    )

    merged_folders: List[BookmarkFolder] = []
    visited_names = set()

    for base_folder in base.children:
        incoming_match = _find_folder_by_name(incoming.children, base_folder.name)
        if incoming_match:
            merged_folders.append(merge_trees(base_folder, incoming_match))
        else:
            merged_folders.append(base_folder)
        visited_names.add(base_folder.name)

    for incoming_folder in incoming.children:
        if incoming_folder.name not in visited_names:
            merged_folders.append(incoming_folder)

    return BookmarkFolder(
        name=base.name,
        bookmarks=merged_bookmarks,
        children=merged_folders,
    )
