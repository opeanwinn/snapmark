"""Generate shareable text representations of bookmark trees or subsets."""

from dataclasses import dataclass, field
from typing import List, Optional
from snapmark.models import Bookmark, BookmarkFolder


@dataclass
class ShareResult:
    lines: List[str] = field(default_factory=list)
    bookmark_count: int = 0

    def summary(self) -> str:
        return f"Shared {self.bookmark_count} bookmark(s)."

    def as_text(self) -> str:
        return "\n".join(self.lines)

    def as_markdown(self) -> str:
        return "\n".join(
            f"- [{line.split(' ', 1)[-1]}]({line.split(' ', 1)[0]})" if line.startswith("http")
            else f"**{line}**"
            for line in self.lines
        )


def _share_folder(
    folder: BookmarkFolder,
    result: ShareResult,
    url_pattern: Optional[str],
    tag_filter: Optional[str],
    depth: int,
) -> None:
    indent = "  " * depth
    result.lines.append(f"{indent}[{folder.title}]")
    for child in folder.children:
        if isinstance(child, Bookmark):
            if url_pattern and url_pattern.lower() not in child.url.lower():
                continue
            if tag_filter and tag_filter.lower() not in [t.lower() for t in (child.tags or [])]:
                continue
            result.lines.append(f"{indent}  {child.url}  {child.title}")
            result.bookmark_count += 1
        elif isinstance(child, BookmarkFolder):
            _share_folder(child, result, url_pattern, tag_filter, depth + 1)


def share_tree(
    root: BookmarkFolder,
    url_pattern: Optional[str] = None,
    tag_filter: Optional[str] = None,
) -> ShareResult:
    """Produce a ShareResult with a human-readable listing of matching bookmarks."""
    result = ShareResult()
    _share_folder(root, result, url_pattern, tag_filter, depth=0)
    return result
