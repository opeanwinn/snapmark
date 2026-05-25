from dataclasses import dataclass, field
from typing import List, Optional
from snapmark.models import BookmarkFolder, Bookmark


@dataclass
class AliasResult:
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
            f"Alias update complete: {self.updated_count} updated, "
            f"{self.skipped_count} skipped."
        )


def _alias_folder(
    folder: BookmarkFolder,
    url_pattern: Optional[str],
    alias: str,
    overwrite: bool,
    result: AliasResult,
) -> BookmarkFolder:
    new_children = []
    for child in folder.children:
        if isinstance(child, Bookmark):
            matches = url_pattern is None or url_pattern in child.url
            has_alias = bool(child.metadata.get("alias"))
            if matches and (overwrite or not has_alias):
                updated_meta = dict(child.metadata)
                updated_meta["alias"] = alias
                new_bm = Bookmark(
                    title=child.title,
                    url=child.url,
                    tags=list(child.tags),
                    metadata=updated_meta,
                )
                result.updated.append(new_bm)
                new_children.append(new_bm)
            else:
                result.skipped.append(child)
                new_children.append(child)
        elif isinstance(child, BookmarkFolder):
            new_children.append(
                _alias_folder(child, url_pattern, alias, overwrite, result)
            )
        else:
            new_children.append(child)
    return BookmarkFolder(name=folder.name, children=new_children)


def set_alias(
    root: BookmarkFolder,
    alias: str,
    url_pattern: Optional[str] = None,
    overwrite: bool = False,
) -> tuple[BookmarkFolder, AliasResult]:
    """Attach a short alias string to matching bookmarks via metadata."""
    result = AliasResult()
    new_root = _alias_folder(root, url_pattern, alias, overwrite, result)
    return new_root, result
