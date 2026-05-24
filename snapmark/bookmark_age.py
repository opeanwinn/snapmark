"""Compute age statistics for bookmarks based on their added_date metadata."""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import List, Optional

from snapmark.models import Bookmark, BookmarkFolder


@dataclass
class AgeResult:
    oldest: Optional[Bookmark] = None
    newest: Optional[Bookmark] = None
    total_with_date: int = 0
    total_without_date: int = 0
    average_age_days: Optional[float] = None
    bookmarks_by_age: List[Bookmark] = field(default_factory=list)

    def summary(self) -> str:
        lines = [
            f"Bookmarks with date : {self.total_with_date}",
            f"Bookmarks without date: {self.total_without_date}",
        ]
        if self.oldest:
            lines.append(f"Oldest : {self.oldest.title} ({self.oldest.added_date})")  # type: ignore[attr-defined]
        if self.newest:
            lines.append(f"Newest : {self.newest.title} ({self.newest.added_date})")  # type: ignore[attr-defined]
        if self.average_age_days is not None:
            lines.append(f"Average age (days) : {self.average_age_days:.1f}")
        return "\n".join(lines)


def _collect_folder(folder: BookmarkFolder, out: List[Bookmark]) -> None:
    for child in folder.children:
        if isinstance(child, Bookmark):
            out.append(child)
        elif isinstance(child, BookmarkFolder):
            _collect_folder(child, out)


def _parse_date(value: object) -> Optional[datetime]:
    if not isinstance(value, str) or not value:
        return None
    for fmt in ("%Y-%m-%dT%H:%M:%S", "%Y-%m-%d"):
        try:
            return datetime.strptime(value, fmt).replace(tzinfo=timezone.utc)
        except ValueError:
            continue
    return None


def compute_age(root: BookmarkFolder) -> AgeResult:
    """Analyse bookmark ages using the 'added_date' metadata field."""
    all_bookmarks: List[Bookmark] = []
    _collect_folder(root, all_bookmarks)

    now = datetime.now(tz=timezone.utc)
    dated: List[tuple] = []  # (datetime, Bookmark)

    result = AgeResult()

    for bm in all_bookmarks:
        raw = (bm.metadata or {}).get("added_date") if hasattr(bm, "metadata") else None
        dt = _parse_date(raw)
        if dt is None:
            result.total_without_date += 1
        else:
            result.total_with_date += 1
            dated.append((dt, bm))

    if dated:
        dated.sort(key=lambda x: x[0])
        result.oldest = dated[0][1]
        result.newest = dated[-1][1]
        result.bookmarks_by_age = [bm for _, bm in dated]
        ages = [(now - dt).days for dt, _ in dated]
        result.average_age_days = sum(ages) / len(ages)

    return result
