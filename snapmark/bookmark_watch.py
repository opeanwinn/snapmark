from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional
from snapmark.models import BookmarkFolder, Bookmark


@dataclass
class WatchResult:
    watched: List[Bookmark] = field(default_factory=list)
    unwatched: List[Bookmark] = field(default_factory=list)

    @property
    def watched_count(self) -> int:
        return len(self.watched)

    @property
    def unwatched_count(self) -> int:
        return len(self.unwatched)

    def summary(self) -> str:
        return (
            f"Watched: {self.watched_count} bookmark(s), "
            f"Unwatched: {self.unwatched_count} bookmark(s)."
        )


def _process_folder(
    folder: BookmarkFolder,
    url_pattern: Optional[str],
    enable: bool,
    result: WatchResult,
) -> BookmarkFolder:
    new_children = []
    for child in folder.children:
        if isinstance(child, Bookmark):
            matches = url_pattern is None or url_pattern.lower() in child.url.lower()
            if matches:
                tags = list(child.tags or [])
                if enable:
                    if "watched" not in tags:
                        tags.append("watched")
                    result.watched.append(child)
                else:
                    tags = [t for t in tags if t != "watched"]
                    result.unwatched.append(child)
                child = Bookmark(
                    title=child.title,
                    url=child.url,
                    tags=tags,
                    metadata=child.metadata,
                    created_at=child.created_at,
                )
            new_children.append(child)
        elif isinstance(child, BookmarkFolder):
            new_children.append(_process_folder(child, url_pattern, enable, result))
        else:
            new_children.append(child)
    return BookmarkFolder(name=folder.name, children=new_children)


def watch_bookmarks(
    tree: BookmarkFolder,
    url_pattern: Optional[str] = None,
    enable: bool = True,
) -> tuple[BookmarkFolder, WatchResult]:
    result = WatchResult()
    new_tree = _process_folder(tree, url_pattern, enable, result)
    return new_tree, result
