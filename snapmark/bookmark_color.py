from dataclasses import dataclass, field
from typing import List, Optional
from snapmark.models import Bookmark, BookmarkFolder

VALID_COLORS = {"red", "orange", "yellow", "green", "blue", "purple", "pink", "gray"}


@dataclass
class ColorResult:
    colored: List[Bookmark] = field(default_factory=list)
    skipped: List[Bookmark] = field(default_factory=list)

    @property
    def colored_count(self) -> int:
        return len(self.colored)

    @property
    def skipped_count(self) -> int:
        return len(self.skipped)

    def summary(self) -> str:
        return (
            f"Colored: {self.colored_count} bookmark(s), "
            f"Skipped: {self.skipped_count} bookmark(s)."
        )


def _color_folder(
    folder: BookmarkFolder,
    color: str,
    url_pattern: Optional[str],
    overwrite: bool,
    result: ColorResult,
) -> BookmarkFolder:
    new_children = []
    for child in folder.children:
        if isinstance(child, Bookmark):
            already_colored = any(
                t.startswith("color:") for t in (child.tags or [])
            )
            url_match = url_pattern is None or url_pattern in child.url
            if url_match and (not already_colored or overwrite):
                new_tags = [t for t in (child.tags or []) if not t.startswith("color:")]
                new_tags.append(f"color:{color}")
                updated = Bookmark(
                    title=child.title,
                    url=child.url,
                    tags=new_tags,
                    metadata=child.metadata,
                    created_at=child.created_at,
                )
                result.colored.append(updated)
                new_children.append(updated)
            else:
                result.skipped.append(child)
                new_children.append(child)
        elif isinstance(child, BookmarkFolder):
            new_children.append(
                _color_folder(child, color, url_pattern, overwrite, result)
            )
        else:
            new_children.append(child)
    return BookmarkFolder(name=folder.name, children=new_children)


def color_bookmarks(
    root: BookmarkFolder,
    color: str,
    url_pattern: Optional[str] = None,
    overwrite: bool = False,
) -> tuple[BookmarkFolder, ColorResult]:
    if color not in VALID_COLORS:
        raise ValueError(f"Invalid color '{color}'. Choose from: {sorted(VALID_COLORS)}")
    result = ColorResult()
    new_root = _color_folder(root, color, url_pattern, overwrite, result)
    return new_root, result
