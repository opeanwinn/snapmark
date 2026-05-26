"""Batch operations: apply a tag, note, or metadata field to multiple bookmarks at once."""

from dataclasses import dataclass, field
from typing import List, Optional
from snapmark.models import Bookmark, BookmarkFolder


@dataclass
class BatchResult:
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
            f"Batch operation complete: {self.updated_count} updated, "
            f"{self.skipped_count} skipped."
        )


def _batch_folder(
    folder: BookmarkFolder,
    tag: Optional[str],
    note: Optional[str],
    metadata_key: Optional[str],
    metadata_value: Optional[str],
    url_pattern: Optional[str],
    result: BatchResult,
) -> BookmarkFolder:
    new_children = []
    for child in folder.children:
        if isinstance(child, BookmarkFolder):
            new_children.append(
                _batch_folder(
                    child, tag, note, metadata_key, metadata_value, url_pattern, result
                )
            )
        elif isinstance(child, Bookmark):
            if url_pattern and url_pattern.lower() not in child.url.lower():
                result.skipped.append(child)
                new_children.append(child)
                continue

            tags = list(child.tags)
            if tag and tag not in tags:
                tags.append(tag)

            metadata = dict(child.metadata) if child.metadata else {}
            if note is not None:
                metadata["note"] = note
            if metadata_key is not None:
                metadata[metadata_key] = metadata_value or ""

            updated = Bookmark(
                title=child.title,
                url=child.url,
                tags=tags,
                metadata=metadata,
                added_at=child.added_at,
            )
            result.updated.append(updated)
            new_children.append(updated)
        else:
            new_children.append(child)

    return BookmarkFolder(name=folder.name, children=new_children)


def batch_update(
    root: BookmarkFolder,
    tag: Optional[str] = None,
    note: Optional[str] = None,
    metadata_key: Optional[str] = None,
    metadata_value: Optional[str] = None,
    url_pattern: Optional[str] = None,
) -> tuple[BookmarkFolder, BatchResult]:
    """Apply tag, note, or metadata to all matching bookmarks."""
    result = BatchResult()
    new_root = _batch_folder(
        root, tag, note, metadata_key, metadata_value, url_pattern, result
    )
    return new_root, result
