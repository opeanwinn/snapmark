"""Count bookmarks grouped by tag across a bookmark tree."""

from dataclasses import dataclass, field
from typing import Dict, List
from snapmark.models import BookmarkFolder, Bookmark


@dataclass
class TagCountResult:
    by_tag: Dict[str, int] = field(default_factory=dict)
    untagged: int = 0
    total: int = 0

    def summary(self) -> str:
        lines = [f"Total bookmarks: {self.total}", f"Untagged: {self.untagged}"]
        if self.by_tag:
            lines.append("By tag:")
            for tag, count in sorted(self.by_tag.items()):
                lines.append(f"  {tag}: {count}")
        return "\n".join(lines)


def _count_folder(folder: BookmarkFolder, result: TagCountResult) -> None:
    for child in folder.children:
        if isinstance(child, Bookmark):
            result.total += 1
            tags: List[str] = child.tags if child.tags else []
            if not tags:
                result.untagged += 1
            for tag in tags:
                result.by_tag[tag] = result.by_tag.get(tag, 0) + 1
        elif isinstance(child, BookmarkFolder):
            _count_folder(child, result)


def count_by_tag(root: BookmarkFolder) -> TagCountResult:
    """Return a TagCountResult with bookmark counts grouped by tag."""
    result = TagCountResult()
    _count_folder(root, result)
    return result
