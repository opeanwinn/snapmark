"""Toggle visibility (hidden/visible) on bookmarks by URL or title pattern."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from snapmark.models import Bookmark, BookmarkFolder


@dataclass
class VisibilityResult:
    hidden_count: int = 0
    shown_count: int = 0
    affected: List[Bookmark] = field(default_factory=list)

    def summary(self) -> str:
        if self.hidden_count:
            return f"Hidden {self.hidden_count} bookmark(s)."
        if self.shown_count:
            return f"Restored visibility for {self.shown_count} bookmark(s)."
        return "No bookmarks were changed."


def _process_folder(
    folder: BookmarkFolder,
    action: str,
    url_pattern: Optional[str],
    title_pattern: Optional[str],
    result: VisibilityResult,
) -> BookmarkFolder:
    new_children = []
    for child in folder.children:
        if isinstance(child, Bookmark):
            url_match = url_pattern is None or url_pattern.lower() in child.url.lower()
            title_match = title_pattern is None or title_pattern.lower() in child.title.lower()
            if url_match and title_match:
                tags = list(child.tags or [])
                if action == "hide":
                    if "hidden" not in tags:
                        tags.append("hidden")
                        result.hidden_count += 1
                        result.affected.append(child)
                elif action == "show":
                    if "hidden" in tags:
                        tags.remove("hidden")
                        result.shown_count += 1
                        result.affected.append(child)
                child = Bookmark(
                    title=child.title,
                    url=child.url,
                    tags=tags,
                    metadata=child.metadata,
                    created_at=child.created_at,
                )
            new_children.append(child)
        elif isinstance(child, BookmarkFolder):
            new_children.append(
                _process_folder(child, action, url_pattern, title_pattern, result)
            )
        else:
            new_children.append(child)
    return BookmarkFolder(name=folder.name, children=new_children)


def set_visibility(
    root: BookmarkFolder,
    action: str = "hide",
    url_pattern: Optional[str] = None,
    title_pattern: Optional[str] = None,
) -> tuple[BookmarkFolder, VisibilityResult]:
    """Hide or show bookmarks matching the given patterns.

    action: 'hide' or 'show'
    """
    if action not in ("hide", "show"):
        raise ValueError(f"action must be 'hide' or 'show', got {action!r}")
    result = VisibilityResult()
    new_root = _process_folder(root, action, url_pattern, title_pattern, result)
    return new_root, result
