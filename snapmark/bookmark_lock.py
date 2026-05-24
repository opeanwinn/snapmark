from dataclasses import dataclass, field
from typing import List
from snapmark.models import BookmarkFolder, Bookmark


@dataclass
class LockResult:
    locked: List[Bookmark] = field(default_factory=list)
    unlocked: List[Bookmark] = field(default_factory=list)

    @property
    def locked_count(self) -> int:
        return len(self.locked)

    @property
    def unlocked_count(self) -> int:
        return len(self.unlocked)

    def summary(self) -> str:
        if self.locked:
            return f"Locked {self.locked_count} bookmark(s)."
        if self.unlocked:
            return f"Unlocked {self.unlocked_count} bookmark(s)."
        return "No bookmarks changed."


LOCK_TAG = "locked"


def _process_folder(
    folder: BookmarkFolder,
    action: str,
    url_pattern: str,
    result: LockResult,
) -> BookmarkFolder:
    new_children = []
    for child in folder.children:
        if isinstance(child, Bookmark):
            matches = url_pattern is None or url_pattern in child.url
            tags = list(child.tags or [])
            if action == "lock" and matches and LOCK_TAG not in tags:
                tags.append(LOCK_TAG)
                child = Bookmark(
                    title=child.title,
                    url=child.url,
                    tags=tags,
                    added=child.added,
                    notes=child.notes,
                )
                result.locked.append(child)
            elif action == "unlock" and matches and LOCK_TAG in tags:
                tags.remove(LOCK_TAG)
                child = Bookmark(
                    title=child.title,
                    url=child.url,
                    tags=tags,
                    added=child.added,
                    notes=child.notes,
                )
                result.unlocked.append(child)
            new_children.append(child)
        elif isinstance(child, BookmarkFolder):
            new_children.append(
                _process_folder(child, action, url_pattern, result)
            )
    return BookmarkFolder(name=folder.name, children=new_children)


def lock_bookmarks(
    root: BookmarkFolder,
    url_pattern: str = None,
) -> tuple[BookmarkFolder, LockResult]:
    result = LockResult()
    new_root = _process_folder(root, "lock", url_pattern, result)
    return new_root, result


def unlock_bookmarks(
    root: BookmarkFolder,
    url_pattern: str = None,
) -> tuple[BookmarkFolder, LockResult]:
    result = LockResult()
    new_root = _process_folder(root, "unlock", url_pattern, result)
    return new_root, result
