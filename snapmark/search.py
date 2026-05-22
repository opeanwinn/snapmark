"""Search functionality for bookmark trees."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from snapmark.models import Bookmark, BookmarkFolder


@dataclass
class SearchResult:
    """Represents a single search hit with its location context."""

    bookmark: Bookmark
    path: List[str] = field(default_factory=list)

    @property
    def breadcrumb(self) -> str:
        """Return a human-readable folder path string."""
        return " / ".join(self.path) if self.path else "(root)"

    def __repr__(self) -> str:  # pragma: no cover
        return f"SearchResult(title={self.bookmark.title!r}, path={self.breadcrumb!r})"


def _search_folder(
    folder: BookmarkFolder,
    query: str,
    path: List[str],
    case_sensitive: bool,
) -> List[SearchResult]:
    """Recursively search a folder for bookmarks matching *query*."""
    results: List[SearchResult] = []
    compare = (lambda s: s) if case_sensitive else str.lower
    needle = compare(query)

    for child in folder.children:
        if isinstance(child, Bookmark):
            if needle in compare(child.title) or needle in compare(child.url):
                results.append(SearchResult(bookmark=child, path=list(path)))
        elif isinstance(child, BookmarkFolder):
            results.extend(
                _search_folder(child, query, path + [child.name], case_sensitive)
            )

    return results


def search_tree(
    root: BookmarkFolder,
    query: str,
    *,
    case_sensitive: bool = False,
) -> List[SearchResult]:
    """Search *root* for bookmarks whose title or URL contains *query*.

    Args:
        root: The top-level bookmark folder to search.
        query: The substring to look for.
        case_sensitive: When *True* the match is case-sensitive.

    Returns:
        A list of :class:`SearchResult` objects ordered by discovery.
    """
    if not query:
        return []
    return _search_folder(root, query, [], case_sensitive)
