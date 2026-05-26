"""Generate a human-readable summary report for a bookmark tree."""

from dataclasses import dataclass, field
from typing import List

from snapmark.models import BookmarkFolder, Bookmark


@dataclass
class SummaryReport:
    total_bookmarks: int = 0
    total_folders: int = 0
    total_tags: int = 0
    unique_domains: int = 0
    top_tags: List[tuple] = field(default_factory=list)
    top_domains: List[tuple] = field(default_factory=list)
    has_notes: int = 0
    has_metadata: int = 0

    def summary(self) -> str:
        lines = [
            "=== Bookmark Summary Report ===",
            f"Total bookmarks : {self.total_bookmarks}",
            f"Total folders   : {self.total_folders}",
            f"Unique domains  : {self.unique_domains}",
            f"Total tags used : {self.total_tags}",
            f"With notes      : {self.has_notes}",
            f"With metadata   : {self.has_metadata}",
        ]
        if self.top_tags:
            lines.append("Top tags:")
            for tag, count in self.top_tags[:5]:
                lines.append(f"  {tag}: {count}")
        if self.top_domains:
            lines.append("Top domains:")
            for domain, count in self.top_domains[:5]:
                lines.append(f"  {domain}: {count}")
        return "\n".join(lines)


def _extract_domain(url: str) -> str:
    try:
        from urllib.parse import urlparse
        host = urlparse(url).netloc
        return host.lstrip("www.") if host else "unknown"
    except Exception:
        return "unknown"


def _collect(folder: BookmarkFolder, report: SummaryReport,
             tag_counts: dict, domain_counts: dict) -> None:
    for child in folder.children:
        if isinstance(child, Bookmark):
            report.total_bookmarks += 1
            domain = _extract_domain(child.url)
            domain_counts[domain] = domain_counts.get(domain, 0) + 1
            for tag in (child.tags or []):
                tag_counts[tag] = tag_counts.get(tag, 0) + 1
            if child.notes:
                report.has_notes += 1
            if child.metadata:
                report.has_metadata += 1
        elif isinstance(child, BookmarkFolder):
            report.total_folders += 1
            _collect(child, report, tag_counts, domain_counts)


def generate_summary(root: BookmarkFolder) -> SummaryReport:
    report = SummaryReport()
    tag_counts: dict = {}
    domain_counts: dict = {}
    _collect(root, report, tag_counts, domain_counts)
    report.total_tags = len(tag_counts)
    report.unique_domains = len(domain_counts)
    report.top_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)
    report.top_domains = sorted(domain_counts.items(), key=lambda x: x[1], reverse=True)
    return report
