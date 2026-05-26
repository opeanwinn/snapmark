from dataclasses import dataclass, field
from typing import List, Optional
from snapmark.models import BookmarkFolder, Bookmark


@dataclass
class ReorderResult:
    moved_count: int = 0
    skipped_count: int = 0
    messages: List[str] = field(default_factory=list)

    def summary(self) -> str:
        return (
            f"Reordered {self.moved_count} bookmark(s), "
            f"{self.skipped_count} skipped."
        )


def _reorder_folder(
    folder: BookmarkFolder,
    url_order: List[str],
    result: ReorderResult,
    recursive: bool,
) -> BookmarkFolder:
    url_index = {url: i for i, url in enumerate(url_order)}

    targeted = []
    others = []

    for child in folder.children:
        if isinstance(child, Bookmark) and child.url in url_index:
            targeted.append(child)
            result.moved_count += 1
        else:
            others.append(child)

    targeted.sort(key=lambda b: url_index[b.url])

    reordered_children = targeted + others

    if recursive:
        reordered_children = [
            _reorder_folder(child, url_order, result, recursive)
            if isinstance(child, BookmarkFolder)
            else child
            for child in reordered_children
        ]

    return BookmarkFolder(
        title=folder.title,
        children=reordered_children,
        metadata=folder.metadata,
    )


def reorder_tree(
    root: BookmarkFolder,
    url_order: List[str],
    recursive: bool = True,
) -> tuple[BookmarkFolder, ReorderResult]:
    """Reorder bookmarks in the tree to match the given URL order.

    Bookmarks whose URLs appear in url_order are moved to the front of
    their folder, sorted by the position in url_order.  Unrecognised
    bookmarks and sub-folders are left at the end in their original
    relative order.
    """
    if not url_order:
        result = ReorderResult()
        result.messages.append("No URLs provided; nothing to reorder.")
        return root, result

    result = ReorderResult()
    new_root = _reorder_folder(root, url_order, result, recursive)
    return new_root, result
