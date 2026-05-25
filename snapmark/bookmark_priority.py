from dataclasses import dataclass, field
from typing import List, Optional
from snapmark.models import BookmarkFolder, Bookmark


@dataclass
class PriorityResult:
    updated: List[Bookmark] = field(default_factory=list)
    skipped: List[Bookmark] = field(default_factory=list)

    @property
    def updated_count(self) -> int:
        return len(self.updated)

    @property
    def skipped_count(self) -> int:
        return len(self.skipped)

    def summary(self) -> str:
        return (
            f"Priority set: {self.updated_count} bookmark(s) updated, "
            f"{self.skipped_count} skipped."
        )


def _priority_tag(level: int) -> str:
    return f"priority:{level}"


def _remove_existing_priority_tags(tags: List[str]) -> List[str]:
    return [t for t in tags if not t.startswith("priority:")]


def _priority_folder(
    folder: BookmarkFolder,
    level: int,
    url_pattern: Optional[str],
    overwrite: bool,
    result: PriorityResult,
) -> BookmarkFolder:
    new_children = []
    for child in folder.children:
        if isinstance(child, Bookmark):
            if url_pattern and url_pattern.lower() not in child.url.lower():
                result.skipped.append(child)
                new_children.append(child)
                continue
            existing_priority = [t for t in child.tags if t.startswith("priority:")]
            if existing_priority and not overwrite:
                result.skipped.append(child)
                new_children.append(child)
                continue
            clean_tags = _remove_existing_priority_tags(child.tags)
            updated = Bookmark(
                title=child.title,
                url=child.url,
                tags=clean_tags + [_priority_tag(level)],
                metadata={**child.metadata},
                added=child.added,
                notes=child.notes,
            )
            result.updated.append(updated)
            new_children.append(updated)
        elif isinstance(child, BookmarkFolder):
            new_children.append(
                _priority_folder(child, level, url_pattern, overwrite, result)
            )
        else:
            new_children.append(child)
    return BookmarkFolder(name=folder.name, children=new_children)


def set_priority(
    tree: BookmarkFolder,
    level: int,
    url_pattern: Optional[str] = None,
    overwrite: bool = False,
) -> tuple[BookmarkFolder, PriorityResult]:
    if not 1 <= level <= 5:
        raise ValueError("Priority level must be between 1 and 5.")
    result = PriorityResult()
    updated_tree = _priority_folder(tree, level, url_pattern, overwrite, result)
    return updated_tree, result
