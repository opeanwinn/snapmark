"""Tag-based bookmark filtering and grouping utilities."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List
from snapmark.models import Bookmark, BookmarkFolder


@dataclass
class TagIndex:
    """Maps tags to the bookmarks that carry them."""
    index: Dict[str, List[Bookmark]] = field(default_factory=dict)

    def tags(self) -> List[str]:
        """Return sorted list of all known tags."""
        return sorted(self.index.keys())

    def bookmarks_for(self, tag: str) -> List[Bookmark]:
        """Return bookmarks associated with *tag* (case-insensitive)."""
        return self.index.get(tag.lower(), [])

    def __len__(self) -> int:
        return len(self.index)


def _collect_tagged(node: BookmarkFolder | Bookmark, index: Dict[str, List[Bookmark]]) -> None:
    """Recursively walk *node* and populate *index* with tag -> bookmark mappings."""
    if isinstance(node, Bookmark):
        for raw_tag in (node.tags or []):
            tag = raw_tag.strip().lower()
            if tag:
                index.setdefault(tag, []).append(node)
    elif isinstance(node, BookmarkFolder):
        for child in node.children:
            _collect_tagged(child, index)


def build_tag_index(tree: BookmarkFolder) -> TagIndex:
    """Build a :class:`TagIndex` from the bookmark *tree*."""
    index: Dict[str, List[Bookmark]] = {}
    _collect_tagged(tree, index)
    return TagIndex(index=index)


def filter_by_tag(tree: BookmarkFolder, tag: str) -> List[Bookmark]:
    """Convenience wrapper — return all bookmarks in *tree* that carry *tag*."""
    idx = build_tag_index(tree)
    return idx.bookmarks_for(tag)
