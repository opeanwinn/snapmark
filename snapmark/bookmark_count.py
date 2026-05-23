"""Bookmark count utilities — count bookmarks by domain, tag, or folder depth."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from typing import Dict, List

from snapmark.models import Bookmark, BookmarkFolder


@dataclass
class CountResult:
    by_domain: Dict[str, int] = field(default_factory=dict)
    by_tag: Dict[str, int] = field(default_factory=dict)
    by_depth: Dict[int, int] = field(default_factory=dict)
    total: int = 0

    def summary(self) -> str:
        lines = [f"Total bookmarks: {self.total}"]
        if self.by_domain:
            top = sorted(self.by_domain.items(), key=lambda x: -x[1])[:5]
            lines.append("Top domains:")
            for domain, count in top:
                lines.append(f"  {domain}: {count}")
        if self.by_tag:
            lines.append("By tag:")
            for tag, count in sorted(self.by_tag.items()):
                lines.append(f"  #{tag}: {count}")
        if self.by_depth:
            lines.append("By depth:")
            for depth, count in sorted(self.by_depth.items()):
                lines.append(f"  depth {depth}: {count}")
        return "\n".join(lines)


def _extract_domain(url: str) -> str:
    """Return the netloc portion of a URL, stripping www."""
    try:
        from urllib.parse import urlparse
        netloc = urlparse(url).netloc
        return netloc.lstrip("www.") if netloc else url
    except Exception:
        return url


def _count_folder(
    folder: BookmarkFolder,
    depth: int,
    by_domain: Dict[str, int],
    by_tag: Dict[str, int],
    by_depth: Dict[int, int],
) -> int:
    total = 0
    for child in folder.children:
        if isinstance(child, Bookmark):
            total += 1
            domain = _extract_domain(child.url)
            by_domain[domain] = by_domain.get(domain, 0) + 1
            by_depth[depth] = by_depth.get(depth, 0) + 1
            for tag in child.tags:
                by_tag[tag] = by_tag.get(tag, 0) + 1
        elif isinstance(child, BookmarkFolder):
            total += _count_folder(child, depth + 1, by_domain, by_tag, by_depth)
    return total


def count_bookmarks(root: BookmarkFolder) -> CountResult:
    """Analyse a bookmark tree and return counts by domain, tag, and depth."""
    by_domain: Dict[str, int] = defaultdict(int)
    by_tag: Dict[str, int] = defaultdict(int)
    by_depth: Dict[int, int] = defaultdict(int)

    total = _count_folder(root, 0, by_domain, by_tag, by_depth)

    return CountResult(
        by_domain=dict(by_domain),
        by_tag=dict(by_tag),
        by_depth=dict(by_depth),
        total=total,
    )
