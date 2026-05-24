"""Annotate bookmarks with notes or descriptions."""
from dataclasses import dataclass, field
from typing import Optional
from snapmark.models import Bookmark, BookmarkFolder


@dataclass
class AnnotateResult:
    annotated: list[Bookmark] = field(default_factory=list)
    skipped: list[Bookmark] = field(default_factory=list)

    def summary(self) -> str:
        return (
            f"Annotated {len(self.annotated)} bookmark(s), "
            f"skipped {len(self.skipped)} (already had note)."
        )


def _annotate_folder(
    folder: BookmarkFolder,
    note: str,
    url_filter: Optional[str],
    overwrite: bool,
    result: AnnotateResult,
) -> BookmarkFolder:
    new_children = []
    for child in folder.children:
        if isinstance(child, Bookmark):
            if url_filter and url_filter not in child.url:
                new_children.append(child)
                continue
            if child.metadata.get("note") and not overwrite:
                result.skipped.append(child)
                new_children.append(child)
            else:
                updated_meta = {**child.metadata, "note": note}
                updated = Bookmark(
                    title=child.title,
                    url=child.url,
                    tags=child.tags,
                    metadata=updated_meta,
                )
                result.annotated.append(updated)
                new_children.append(updated)
        elif isinstance(child, BookmarkFolder):
            new_children.append(
                _annotate_folder(child, note, url_filter, overwrite, result)
            )
        else:
            new_children.append(child)
    return BookmarkFolder(name=folder.name, children=new_children)


def annotate_tree(
    root: BookmarkFolder,
    note: str,
    url_filter: Optional[str] = None,
    overwrite: bool = False,
) -> tuple[BookmarkFolder, AnnotateResult]:
    """Attach a note to bookmarks, optionally filtering by URL substring."""
    result = AnnotateResult()
    new_root = _annotate_folder(root, note, url_filter, overwrite, result)
    return new_root, result
