"""Filter bookmarks by domain, tag, or date added."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional
from urllib.parse import urlparse

from snapmark.models import Bookmark, BookmarkFolder


@dataclass
class FilterResult:
    matched: List[Bookmark] = field(default_factory=list)
    total_scanned: int = 0

    @property
    def match_count(self) -> int:
        return len(self.matched)

    def summary(self) -> str:
        return (
            f"Matched {self.match_count} bookmark(s) "
            f"out of {self.total_scanned} scanned."
        )


def _filter_folder(
    folder: BookmarkFolder,
    domain: Optional[str],
    tag: Optional[str],
    result: FilterResult,
) -> None:
    for child in folder.children:
        if isinstance(child, Bookmark):
            result.total_scanned += 1
            domain_match = True
            tag_match = True

            if domain is not None:
                try:
                    parsed = urlparse(child.url)
                    host = parsed.netloc.lower().lstrip("www.")
                    domain_match = domain.lower() in host
                except Exception:
                    domain_match = False

            if tag is not None:
                bookmark_tags = [
                    t.strip().lower()
                    for t in (child.tags or "").split(",")
                    if t.strip()
                ]
                tag_match = tag.lower() in bookmark_tags

            if domain_match and tag_match:
                result.matched.append(child)

        elif isinstance(child, BookmarkFolder):
            _filter_folder(child, domain, tag, result)


def filter_tree(
    root: BookmarkFolder,
    domain: Optional[str] = None,
    tag: Optional[str] = None,
) -> FilterResult:
    """Return bookmarks matching the given domain and/or tag filters."""
    if domain is None and tag is None:
        raise ValueError("At least one of 'domain' or 'tag' must be provided.")

    result = FilterResult()
    _filter_folder(root, domain, tag, result)
    return result
