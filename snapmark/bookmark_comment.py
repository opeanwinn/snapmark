from dataclasses import dataclass, field
from typing import List, Optional
from snapmark.models import BookmarkFolder, Bookmark


@dataclass
class CommentResult:
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
            f"Commented: {self.updated_count} bookmark(s), "
            f"skipped: {self.skipped_count} (already had comment)"
        )


def _comment_folder(
    folder: BookmarkFolder,
    comment: str,
    url_pattern: Optional[str],
    overwrite: bool,
    result: CommentResult,
) -> BookmarkFolder:
    new_children = []
    for child in folder.children:
        if isinstance(child, Bookmark):
            matches = url_pattern is None or url_pattern in child.url
            existing = child.metadata.get("comment", "") if child.metadata else ""
            if matches and (overwrite or not existing):
                meta = dict(child.metadata) if child.metadata else {}
                meta["comment"] = comment
                updated = Bookmark(
                    title=child.title,
                    url=child.url,
                    tags=list(child.tags),
                    metadata=meta,
                )
                result.updated.append(updated)
                new_children.append(updated)
            else:
                if matches and existing:
                    result.skipped.append(child)
                new_children.append(child)
        elif isinstance(child, BookmarkFolder):
            new_children.append(
                _comment_folder(child, comment, url_pattern, overwrite, result)
            )
        else:
            new_children.append(child)
    return BookmarkFolder(name=folder.name, children=new_children)


def comment_tree(
    root: BookmarkFolder,
    comment: str,
    url_pattern: Optional[str] = None,
    overwrite: bool = False,
) -> tuple[BookmarkFolder, CommentResult]:
    result = CommentResult()
    new_root = _comment_folder(root, comment, url_pattern, overwrite, result)
    return new_root, result
