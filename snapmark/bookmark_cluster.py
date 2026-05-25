"""Cluster bookmarks into groups based on shared tags or domain patterns."""

from dataclasses import dataclass, field
from collections import defaultdict
from typing import Dict, List
from snapmark.models import Bookmark, BookmarkFolder


@dataclass
class ClusterResult:
    clusters: Dict[str, List[Bookmark]] = field(default_factory=dict)
    unclustered: List[Bookmark] = field(default_factory=list)

    @property
    def cluster_count(self) -> int:
        return len(self.clusters)

    @property
    def total_clustered(self) -> int:
        return sum(len(v) for v in self.clusters.values())

    def summary(self) -> str:
        lines = [
            f"Clusters: {self.cluster_count}",
            f"Clustered bookmarks: {self.total_clustered}",
            f"Unclustered bookmarks: {len(self.unclustered)}",
        ]
        for name, bookmarks in sorted(self.clusters.items()):
            lines.append(f"  [{name}] {len(bookmarks)} bookmark(s)")
        return "\n".join(lines)


def _collect_folder(folder: BookmarkFolder, bookmarks: List[Bookmark]) -> None:
    for child in folder.children:
        if isinstance(child, Bookmark):
            bookmarks.append(child)
        elif isinstance(child, BookmarkFolder):
            _collect_folder(child, bookmarks)


def cluster_by_tag(folder: BookmarkFolder) -> ClusterResult:
    """Cluster bookmarks by their first tag alphabetically."""
    all_bookmarks: List[Bookmark] = []
    _collect_folder(folder, all_bookmarks)

    result = ClusterResult()
    grouped: Dict[str, List[Bookmark]] = defaultdict(list)

    for bm in all_bookmarks:
        tags = sorted(bm.tags) if bm.tags else []
        if tags:
            grouped[tags[0]].append(bm)
        else:
            result.unclustered.append(bm)

    result.clusters = dict(grouped)
    return result


def cluster_by_domain(folder: BookmarkFolder) -> ClusterResult:
    """Cluster bookmarks by their domain."""
    import re

    all_bookmarks: List[Bookmark] = []
    _collect_folder(folder, all_bookmarks)

    result = ClusterResult()
    grouped: Dict[str, List[Bookmark]] = defaultdict(list)

    for bm in all_bookmarks:
        match = re.search(r"https?://(?:www\.)?([^/]+)", bm.url or "")
        if match:
            domain = match.group(1)
            grouped[domain].append(bm)
        else:
            result.unclustered.append(bm)

    result.clusters = dict(grouped)
    return result
