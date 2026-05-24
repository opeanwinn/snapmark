"""Detect bookmarks with potentially broken or suspicious URLs."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List
from urllib.parse import urlparse

from snapmark.models import Bookmark, BookmarkFolder


@dataclass
class BrokenResult:
    broken: List[Bookmark] = field(default_factory=list)
    suspicious: List[Bookmark] = field(default_factory=list)

    @property
    def broken_count(self) -> int:
        return len(self.broken)

    @property
    def suspicious_count(self) -> int:
        return len(self.suspicious)

    def summary(self) -> str:
        lines = [
            f"Broken bookmarks  : {self.broken_count}",
            f"Suspicious URLs   : {self.suspicious_count}",
        ]
        return "\n".join(lines)


_ALLOWED_SCHEMES = {"http", "https"}
_SUSPICIOUS_SCHEMES = {"ftp", "file", "javascript", "data"}


def _is_broken(url: str) -> bool:
    """Return True if the URL is empty or structurally invalid."""
    if not url or not url.strip():
        return True
    try:
        parsed = urlparse(url)
        return not parsed.scheme or not parsed.netloc
    except Exception:
        return True


def _is_suspicious(url: str) -> bool:
    """Return True if the URL uses a non-http/https scheme."""
    try:
        scheme = urlparse(url).scheme.lower()
        return scheme in _SUSPICIOUS_SCHEMES
    except Exception:
        return False


def _scan_folder(folder: BookmarkFolder, result: BrokenResult) -> None:
    for child in folder.children:
        if isinstance(child, Bookmark):
            if _is_broken(child.url):
                result.broken.append(child)
            elif _is_suspicious(child.url):
                result.suspicious.append(child)
        elif isinstance(child, BookmarkFolder):
            _scan_folder(child, result)


def find_broken(root: BookmarkFolder) -> BrokenResult:
    """Scan *root* recursively and return a BrokenResult."""
    result = BrokenResult()
    _scan_folder(root, result)
    return result
