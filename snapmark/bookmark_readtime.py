from dataclasses import dataclass, field
from typing import List, Optional
from snapmark.models import BookmarkFolder, Bookmark


@dataclass
class ReadTimeResult:
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
            f"Read-time estimation complete: "
            f"{self.updated_count} updated, {self.skipped_count} skipped."
        )


def _estimate_minutes(url: str, title: str) -> int:
    """Heuristic: estimate read time in minutes based on title word count."""
    words = len(title.split())
    # Assume ~200 words/min average reading speed; title is ~5% of content
    estimated_words = words * 20
    minutes = max(1, round(estimated_words / 200))
    return minutes


def _readtime_folder(
    folder: BookmarkFolder,
    url_pattern: Optional[str],
    overwrite: bool,
    result: ReadTimeResult,
) -> BookmarkFolder:
    new_children = []
    for child in folder.children:
        if isinstance(child, Bookmark):
            already_set = "readtime" in (child.metadata or {})
            matches = url_pattern is None or url_pattern in child.url
            if matches and (not already_set or overwrite):
                minutes = _estimate_minutes(child.url, child.title)
                metadata = dict(child.metadata or {})
                metadata["readtime"] = f"{minutes} min"
                updated = Bookmark(
                    title=child.title,
                    url=child.url,
                    tags=list(child.tags),
                    metadata=metadata,
                    added=child.added,
                )
                result.updated.append(updated)
                new_children.append(updated)
            else:
                result.skipped.append(child)
                new_children.append(child)
        elif isinstance(child, BookmarkFolder):
            new_children.append(
                _readtime_folder(child, url_pattern, overwrite, result)
            )
        else:
            new_children.append(child)
    return BookmarkFolder(name=folder.name, children=new_children)


def estimate_readtime(
    root: BookmarkFolder,
    url_pattern: Optional[str] = None,
    overwrite: bool = False,
) -> tuple[BookmarkFolder, ReadTimeResult]:
    result = ReadTimeResult()
    new_root = _readtime_folder(root, url_pattern, overwrite, result)
    return new_root, result
