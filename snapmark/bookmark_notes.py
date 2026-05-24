from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional
from snapmark.models import Bookmark, BookmarkFolder


@dataclass
class NotesResult:
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
            f"Notes: {self.updated_count} updated, "
            f"{self.skipped_count} skipped."
        )


def _notes_folder(
    folder: BookmarkFolder,
    note: str,
    url_pattern: Optional[str],
    overwrite: bool,
    result: NotesResult,
) -> BookmarkFolder:
    new_children = []
    for child in folder.children:
        if isinstance(child, Bookmark):
            matches = url_pattern is None or url_pattern in child.url
            if matches:
                if child.notes and not overwrite:
                    result.skipped.append(child)
                    new_children.append(child)
                else:
                    updated = Bookmark(
                        title=child.title,
                        url=child.url,
                        tags=child.tags,
                        notes=note,
                        added=child.added,
                    )
                    result.updated.append(updated)
                    new_children.append(updated)
            else:
                new_children.append(child)
        elif isinstance(child, BookmarkFolder):
            new_children.append(
                _notes_folder(child, note, url_pattern, overwrite, result)
            )
        else:
            new_children.append(child)
    return BookmarkFolder(name=folder.name, children=new_children)


def add_notes(
    root: BookmarkFolder,
    note: str,
    url_pattern: Optional[str] = None,
    overwrite: bool = False,
) -> tuple[BookmarkFolder, NotesResult]:
    """Attach a note string to matching bookmarks in the tree."""
    result = NotesResult()
    new_root = _notes_folder(root, note, url_pattern, overwrite, result)
    return new_root, result
