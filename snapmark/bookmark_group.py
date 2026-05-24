"""Group bookmarks by a given attribute (domain, tag, or folder depth)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List
from urllib.parse import urlparse

from snapmark.models import Bookmark, BookmarkFolder


@dataclass
class GroupResult:
    groups: Dict[str, List[Bookmark]] = field(default_factory=dict)
    group_by: str = "domain"

    def summary(self) -> str:
        lines = [f"Grouped by '{self.group_by}': {len(self.groups)} group(s)"]
        for key, bookmarks in sorted(self.groups.items()):
            lines.append(f"  {key}: {len(bookmarks)} bookmark(s)")
        return "\n".join(lines)

    def total(self) -> int:
        return sum(len(v) for v in self.groups.values())


def _extract_domain(url: str) -> str:
    try:
        host = urlparse(url).hostname or ""
        return host.removeprefix("www.") if host else "(unknown)"
    except Exception:
        return "(unknown)"


def _collect_folder(
    folder: BookmarkFolder,
    groups: Dict[str, List[Bookmark]],
    group_by: str,
) -> None:
    for child in folder.children:
        if isinstance(child, Bookmark):
            if group_by == "domain":
                key = _extract_domain(child.url)
            elif group_by == "tag":
                tags = child.tags or []
                for tag in tags:
                    groups.setdefault(tag, []).append(child)
                if not tags:
                    groups.setdefault("(untagged)", []).append(child)
                continue
            else:
                key = "(all)"
            groups.setdefault(key, []).append(child)
        elif isinstance(child, BookmarkFolder):
            _collect_folder(child, groups, group_by)


def group_bookmarks(
    root: BookmarkFolder,
    group_by: str = "domain",
) -> GroupResult:
    """Group all bookmarks in *root* by the specified attribute.

    Args:
        root: The root bookmark folder to traverse.
        group_by: One of ``'domain'``, ``'tag'``.

    Returns:
        A :class:`GroupResult` mapping group keys to bookmark lists.
    """
    if group_by not in ("domain", "tag"):
        raise ValueError(f"Unsupported group_by value: {group_by!r}")

    groups: Dict[str, List[Bookmark]] = {}
    _collect_folder(root, groups, group_by)
    return GroupResult(groups=groups, group_by=group_by)
