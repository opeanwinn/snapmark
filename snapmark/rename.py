"""Rename bookmarks or folders within a bookmark tree."""

from dataclasses import dataclass, field
from typing import List

from snapmark.models import Bookmark, BookmarkFolder


@dataclass
class RenameResult:
    renamed_count: int = 0
    renamed_items: List[str] = field(default_factory=list)

    def summary(self) -> str:
        if self.renamed_count == 0:
            return "No items renamed."
        lines = [f"Renamed {self.renamed_count} item(s):"]
        for item in self.renamed_items:
            lines.append(f"  - {item}")
        return "\n".join(lines)


def _rename_in_folder(
    folder: BookmarkFolder,
    old_title: str,
    new_title: str,
    result: RenameResult,
) -> BookmarkFolder:
    new_children = []
    for child in folder.children:
        if isinstance(child, Bookmark):
            if child.title == old_title:
                renamed = Bookmark(title=new_title, url=child.url, tags=child.tags)
                result.renamed_count += 1
                result.renamed_items.append(
                    f"Bookmark '{old_title}' -> '{new_title}' (url: {child.url})"
                )
                new_children.append(renamed)
            else:
                new_children.append(child)
        elif isinstance(child, BookmarkFolder):
            updated_folder = _rename_in_folder(child, old_title, new_title, result)
            if child.title == old_title:
                updated_folder = BookmarkFolder(
                    title=new_title, children=updated_folder.children
                )
                result.renamed_count += 1
                result.renamed_items.append(
                    f"Folder '{old_title}' -> '{new_title}'"
                )
            new_children.append(updated_folder)
    return BookmarkFolder(title=folder.title, children=new_children)


def rename_tree(
    root: BookmarkFolder, old_title: str, new_title: str
) -> tuple[BookmarkFolder, RenameResult]:
    """Rename all bookmarks/folders matching old_title to new_title."""
    result = RenameResult()
    updated = _rename_in_folder(root, old_title, new_title, result)
    return updated, result
