"""Compute statistics over a bookmark tree."""
from __future__ import annotations

from dataclasses import dataclass, field
from collections import Counter
from typing import List

from snapmark.models import Bookmark, BookmarkFolder


@dataclass
class BookmarkStats:
    total_bookmarks: int = 0
    total_folders: int = 0
    max_depth: int = 0
    avg_depth: float = 0.0
    top_domains: List[tuple] = field(default_factory=list)
    tagged_count: int = 0
    untagged_count: int = 0

    def summary(self) -> str:
        lines = [
            f"Bookmarks : {self.total_bookmarks}",
            f"Folders   : {self.total_folders}",
            f"Max depth : {self.max_depth}",
            f"Avg depth : {self.avg_depth:.2f}",
            f"Tagged    : {self.tagged_count}",
            f"Untagged  : {self.untagged_count}",
        ]
        if self.top_domains:
            lines.append("Top domains:")
            for domain, count in self.top_domains:
                lines.append(f"  {domain}: {count}")
        return "\n".join(lines)


def _collect(node: BookmarkFolder | Bookmark, depth: int,
             depths: list, domains: Counter, stats: BookmarkStats) -> None:
    if isinstance(node, Bookmark):
        stats.total_bookmarks += 1
        depths.append(depth)
        if node.tags:
            stats.tagged_count += 1
        else:
            stats.untagged_count += 1
        try:
            from urllib.parse import urlparse
            host = urlparse(node.url).netloc
            if host:
                domains[host] += 1
        except Exception:
            pass
    elif isinstance(node, BookmarkFolder):
        stats.total_folders += 1
        for child in node.children:
            _collect(child, depth + 1, depths, domains, stats)


def compute_stats(root: BookmarkFolder, top_n: int = 5) -> BookmarkStats:
    """Return a BookmarkStats for the given bookmark tree."""
    stats = BookmarkStats()
    depths: list = []
    domains: Counter = Counter()

    for child in root.children:
        _collect(child, 1, depths, domains, stats)

    if depths:
        stats.max_depth = max(depths)
        stats.avg_depth = sum(depths) / len(depths)

    stats.top_domains = domains.most_common(top_n)
    return stats
