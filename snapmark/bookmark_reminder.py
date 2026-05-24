from __future__ import annotations
from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import List, Optional
from snapmark.models import Bookmark, BookmarkFolder


@dataclass
class ReminderResult:
    scheduled: List[Bookmark] = field(default_factory=list)
    skipped: List[Bookmark] = field(default_factory=list)

    @property
    def scheduled_count(self) -> int:
        return len(self.scheduled)

    @property
    def skipped_count(self) -> int:
        return len(self.skipped)

    def summary(self) -> str:
        return (
            f"Reminders scheduled: {self.scheduled_count}, "
            f"already had reminder: {self.skipped_count}"
        )


def _reminder_tag(days: int) -> str:
    remind_on = date.today() + timedelta(days=days)
    return f"remind:{remind_on.isoformat()}"


def _process_folder(
    folder: BookmarkFolder,
    result: ReminderResult,
    url_pattern: Optional[str],
    days: int,
    overwrite: bool,
) -> BookmarkFolder:
    new_children = []
    for child in folder.children:
        if isinstance(child, Bookmark):
            has_reminder = any(t.startswith("remind:") for t in (child.tags or []))
            matches = url_pattern is None or (url_pattern in child.url)
            if matches and (not has_reminder or overwrite):
                tags = [t for t in (child.tags or []) if not t.startswith("remind:")]
                tags.append(_reminder_tag(days))
                new_children.append(
                    Bookmark(
                        title=child.title,
                        url=child.url,
                        tags=tags,
                        added=child.added,
                        notes=child.notes,
                    )
                )
                result.scheduled.append(child)
            else:
                new_children.append(child)
                if has_reminder:
                    result.skipped.append(child)
        elif isinstance(child, BookmarkFolder):
            new_children.append(
                _process_folder(child, result, url_pattern, days, overwrite)
            )
        else:
            new_children.append(child)
    return BookmarkFolder(name=folder.name, children=new_children)


def set_reminders(
    tree: BookmarkFolder,
    days: int = 7,
    url_pattern: Optional[str] = None,
    overwrite: bool = False,
) -> tuple[BookmarkFolder, ReminderResult]:
    result = ReminderResult()
    new_tree = _process_folder(tree, result, url_pattern, days, overwrite)
    return new_tree, result
