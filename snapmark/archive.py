"""Archive module: mark bookmarks as archived and filter them out of active views."""

from dataclasses import dataclass, field
from typing import List
from snapmark.models import Bookmark, BookmarkFolder


@dataclass
class ArchiveResult:
    archived: List[Bookmark] = field(default_factory=list)
    unarchived: List[Bookmark] = field(default_factory=list)

    @property
    def archived_count(self) -> int:
        return len(self.archived)

    @property
    def unarchived_count(self) -> int:
        return len(self.unarchived)

    def summary(self) -> str:
        return (
            f"Archived: {self.archived_count} bookmark(s), "
            f"Unarchived: {self.unarchived_count} bookmark(s)"
        )


ARCHIVE_TAG = "archived"


def _process_folder(
    folder: BookmarkFolder,
    urls: List[str],
    archive: bool,
    result: ArchiveResult,
) -> BookmarkFolder:
    new_children = []
    for child in folder.children:
        if isinstance(child, Bookmark):
            if child.url in urls:
                tags = list(child.tags or [])
                if archive and ARCHIVE_TAG not in tags:
                    tags.append(ARCHIVE_TAG)
                    child = Bookmark(title=child.title, url=child.url, tags=tags)
                    result.archived.append(child)
                elif not archive and ARCHIVE_TAG in tags:
                    tags.remove(ARCHIVE_TAG)
                    child = Bookmark(title=child.title, url=child.url, tags=tags)
                    result.unarchived.append(child)
            new_children.append(child)
        elif isinstance(child, BookmarkFolder):
            new_children.append(_process_folder(child, urls, archive, result))
        else:
            new_children.append(child)
    return BookmarkFolder(name=folder.name, children=new_children)


def archive_bookmarks(
    root: BookmarkFolder, urls: List[str]
) -> tuple[BookmarkFolder, ArchiveResult]:
    """Tag the given bookmark URLs as archived."""
    result = ArchiveResult()
    new_root = _process_folder(root, urls, archive=True, result=result)
    return new_root, result


def unarchive_bookmarks(
    root: BookmarkFolder, urls: List[str]
) -> tuple[BookmarkFolder, ArchiveResult]:
    """Remove the archived tag from the given bookmark URLs."""
    result = ArchiveResult()
    new_root = _process_folder(root, urls, archive=False, result=result)
    return new_root, result


def filter_archived(root: BookmarkFolder) -> BookmarkFolder:
    """Return a new tree with all archived bookmarks removed."""
    new_children = []
    for child in root.children:
        if isinstance(child, Bookmark):
            if ARCHIVE_TAG not in (child.tags or []):
                new_children.append(child)
        elif isinstance(child, BookmarkFolder):
            new_children.append(filter_archived(child))
        else:
            new_children.append(child)
    return BookmarkFolder(name=root.name, children=new_children)
