from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import List, Optional

from snapmark.models import Bookmark, BookmarkFolder


@dataclass
class ExpireResult:
    expired: List[Bookmark] = field(default_factory=list)
    kept: List[Bookmark] = field(default_factory=list)

    @property
    def expired_count(self) -> int:
        return len(self.expired)

    @property
    def kept_count(self) -> int:
        return len(self.kept)

    def summary(self) -> str:
        return (
            f"Expired: {self.expired_count} bookmark(s), "
            f"Kept: {self.kept_count} bookmark(s)."
        )


def _parse_expire_date(value: str) -> Optional[date]:
    try:
        return date.fromisoformat(value)
    except (ValueError, TypeError):
        return None


def _expire_folder(
    folder: BookmarkFolder,
    cutoff: date,
    result: ExpireResult,
) -> BookmarkFolder:
    new_children = []
    for child in folder.children:
        if isinstance(child, Bookmark):
            raw = (child.metadata or {}).get("expires")
            expire_date = _parse_expire_date(raw) if raw else None
            if expire_date is not None and expire_date <= cutoff:
                result.expired.append(child)
            else:
                result.kept.append(child)
                new_children.append(child)
        elif isinstance(child, BookmarkFolder):
            new_children.append(_expire_folder(child, cutoff, result))
        else:
            new_children.append(child)
    return BookmarkFolder(
        title=folder.title,
        children=new_children,
        metadata=folder.metadata,
    )


def expire_bookmarks(
    root: BookmarkFolder,
    as_of: Optional[date] = None,
) -> tuple[BookmarkFolder, ExpireResult]:
    """Remove bookmarks whose 'expires' metadata date is on or before `as_of`."""
    cutoff = as_of or date.today()
    result = ExpireResult()
    new_root = _expire_folder(root, cutoff, result)
    return new_root, result
