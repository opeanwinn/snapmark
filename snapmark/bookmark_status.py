"""Assign or update a read/unread status tag on bookmarks."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from snapmark.models import Bookmark, BookmarkFolder

_READ_TAG = "read"
_UNREAD_TAG = "unread"


@dataclass
class StatusResult:
    updated: List[Bookmark] = field(default_factory=list)
    skipped: List[Bookmark] = field(default_factory=list)

    @property
    def updated_count(self) -> int:
        return len(self.updated)

    @property
    def skipped_count(self) -> int:
        return len(self.skipped)

    def summary(self) -> str:
        return (
            f"Status update: {self.updated_count} bookmark(s) updated, "
            f"{self.skipped_count} skipped."
        )


def _process_folder(
    folder: BookmarkFolder,
    status: str,
    url_pattern: Optional[str],
    overwrite: bool,
    result: StatusResult,
) -> BookmarkFolder:
    new_children = []
    for child in folder.children:
        if isinstance(child, Bookmark):
            match = url_pattern is None or url_pattern in child.url
            opposite = _UNREAD_TAG if status == _READ_TAG else _READ_TAG
            already_set = status in (child.tags or [])
            if match and (not already_set or overwrite):
                tags = [t for t in (child.tags or []) if t != opposite and t != status]
                tags.append(status)
                updated = Bookmark(
                    title=child.title,
                    url=child.url,
                    tags=tags,
                    metadata=child.metadata,
                    created_at=child.created_at,
                )
                result.updated.append(updated)
                new_children.append(updated)
            else:
                if match and already_set:
                    result.skipped.append(child)
                new_children.append(child)
        elif isinstance(child, BookmarkFolder):
            new_children.append(
                _process_folder(child, status, url_pattern, overwrite, result)
            )
        else:
            new_children.append(child)
    return BookmarkFolder(name=folder.name, children=new_children)


def set_status(
    root: BookmarkFolder,
    status: str = "read",
    url_pattern: Optional[str] = None,
    overwrite: bool = False,
) -> tuple[BookmarkFolder, StatusResult]:
    """Mark bookmarks as 'read' or 'unread'."""
    if status not in (_READ_TAG, _UNREAD_TAG):
        raise ValueError(f"status must be '{_READ_TAG}' or '{_UNREAD_TAG}', got {status!r}")
    result = StatusResult()
    new_root = _process_folder(root, status, url_pattern, overwrite, result)
    return new_root, result
