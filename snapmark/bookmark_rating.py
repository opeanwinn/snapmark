"""Bookmark rating: assign and query star ratings (1–5) on bookmarks."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from snapmark.models import Bookmark, BookmarkFolder


@dataclass
class RatingResult:
    rated: List[Bookmark] = field(default_factory=list)
    skipped: int = 0

    @property
    def rated_count(self) -> int:
        return len(self.rated)

    def summary(self) -> str:
        return (
            f"Rated {self.rated_count} bookmark(s), "
            f"skipped {self.skipped} (already rated or filtered out)."
        )


def _rate_folder(
    folder: BookmarkFolder,
    rating: int,
    url_pattern: Optional[str],
    overwrite: bool,
    result: RatingResult,
) -> BookmarkFolder:
    new_children = []
    for child in folder.children:
        if isinstance(child, Bookmark):
            if url_pattern and url_pattern.lower() not in child.url.lower():
                result.skipped += 1
                new_children.append(child)
                continue
            existing = child.tags or []
            # Remove any previous rating tag
            stripped = [t for t in existing if not t.startswith("rating:")]
            if len(stripped) < len(existing) and not overwrite:
                result.skipped += 1
                new_children.append(child)
                continue
            new_tags = stripped + [f"rating:{rating}"]
            updated = Bookmark(
                title=child.title,
                url=child.url,
                tags=new_tags,
                note=child.note,
                created=child.created,
                metadata=child.metadata,
            )
            result.rated.append(updated)
            new_children.append(updated)
        elif isinstance(child, BookmarkFolder):
            new_children.append(
                _rate_folder(child, rating, url_pattern, overwrite, result)
            )
        else:
            new_children.append(child)
    return BookmarkFolder(name=folder.name, children=new_children)


def rate_bookmarks(
    tree: BookmarkFolder,
    rating: int,
    url_pattern: Optional[str] = None,
    overwrite: bool = True,
) -> tuple[BookmarkFolder, RatingResult]:
    """Assign a star *rating* (1–5) to matching bookmarks."""
    if not 1 <= rating <= 5:
        raise ValueError(f"Rating must be between 1 and 5, got {rating}.")
    result = RatingResult()
    new_tree = _rate_folder(tree, rating, url_pattern, overwrite, result)
    return new_tree, result
