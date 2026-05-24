"""Highlight bookmarks by marking them with a special tag or note prefix.

Provides functionality to add a 'highlighted' tag to bookmarks matching
a given URL pattern, title pattern, or tag filter — useful for surfacing
important bookmarks before export or review.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from snapmark.models import Bookmark, BookmarkFolder


_HIGHLIGHT_TAG = "highlighted"


@dataclass
class HighlightResult:
    """Result of a highlight operation."""

    highlighted: List[Bookmark] = field(default_factory=list)
    already_highlighted: List[Bookmark] = field(default_factory=list)

    @property
    def highlight_count(self) -> int:
        """Number of bookmarks newly highlighted."""
        return len(self.highlighted)

    def summary(self) -> str:
        """Return a human-readable summary of the highlight operation."""
        lines = [
            f"Highlighted : {self.highlight_count}",
            f"Already highlighted: {len(self.already_highlighted)}",
        ]
        return "\n".join(lines)


def _highlight_folder(
    folder: BookmarkFolder,
    *,
    url_pattern: Optional[str],
    title_pattern: Optional[str],
    tag_filter: Optional[str],
    result: HighlightResult,
) -> BookmarkFolder:
    """Recursively walk *folder* and highlight matching bookmarks."""
    new_children = []

    for child in folder.children:
        if isinstance(child, Bookmark):
            if _matches(child, url_pattern=url_pattern, title_pattern=title_pattern, tag_filter=tag_filter):
                if _HIGHLIGHT_TAG in (child.tags or []):
                    result.already_highlighted.append(child)
                    new_children.append(child)
                else:
                    updated_tags = list(child.tags or []) + [_HIGHLIGHT_TAG]
                    highlighted_bm = Bookmark(
                        title=child.title,
                        url=child.url,
                        tags=updated_tags,
                        note=child.note,
                        created=child.created,
                    )
                    result.highlighted.append(highlighted_bm)
                    new_children.append(highlighted_bm)
            else:
                new_children.append(child)
        elif isinstance(child, BookmarkFolder):
            updated_folder = _highlight_folder(
                child,
                url_pattern=url_pattern,
                title_pattern=title_pattern,
                tag_filter=tag_filter,
                result=result,
            )
            new_children.append(updated_folder)
        else:
            new_children.append(child)

    return BookmarkFolder(name=folder.name, children=new_children)


def _matches(
    bookmark: Bookmark,
    *,
    url_pattern: Optional[str],
    title_pattern: Optional[str],
    tag_filter: Optional[str],
) -> bool:
    """Return True if *bookmark* matches all supplied (non-None) criteria."""
    if url_pattern and url_pattern.lower() not in (bookmark.url or "").lower():
        return False
    if title_pattern and title_pattern.lower() not in (bookmark.title or "").lower():
        return False
    if tag_filter and tag_filter.lower() not in [t.lower() for t in (bookmark.tags or [])]:
        return False
    # At least one criterion must be provided to avoid highlighting everything
    if url_pattern is None and title_pattern is None and tag_filter is None:
        return False
    return True


def highlight_tree(
    root: BookmarkFolder,
    *,
    url_pattern: Optional[str] = None,
    title_pattern: Optional[str] = None,
    tag_filter: Optional[str] = None,
) -> tuple[BookmarkFolder, HighlightResult]:
    """Highlight bookmarks in *root* that match the given criteria.

    At least one of *url_pattern*, *title_pattern*, or *tag_filter* must be
    provided; otherwise no bookmarks are modified and an empty result is
    returned.

    Args:
        root: The root :class:`BookmarkFolder` to process.
        url_pattern: Case-insensitive substring to match against bookmark URLs.
        title_pattern: Case-insensitive substring to match against bookmark titles.
        tag_filter: Tag that must be present on the bookmark.

    Returns:
        A ``(new_root, result)`` tuple where *new_root* is the updated tree
        and *result* contains metadata about what was changed.
    """
    result = HighlightResult()
    new_root = _highlight_folder(
        root,
        url_pattern=url_pattern,
        title_pattern=title_pattern,
        tag_filter=tag_filter,
        result=result,
    )
    return new_root, result
