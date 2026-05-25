from dataclasses import dataclass, field
from typing import List, Optional
import copy

from snapmark.models import Bookmark, BookmarkFolder


@dataclass
class LabelResult:
    labeled_count: int = 0
    skipped_count: int = 0
    labels_applied: List[str] = field(default_factory=list)

    def summary(self) -> str:
        labels = ", ".join(sorted(set(self.labels_applied))) if self.labels_applied else "none"
        return (
            f"Labeled: {self.labeled_count} bookmark(s), "
            f"Skipped: {self.skipped_count}, "
            f"Labels applied: {labels}"
        )


def _label_folder(
    folder: BookmarkFolder,
    labels: List[str],
    url_pattern: Optional[str],
    overwrite: bool,
    result: LabelResult,
) -> BookmarkFolder:
    new_children = []
    for child in folder.children:
        if isinstance(child, Bookmark):
            if url_pattern and url_pattern.lower() not in child.url.lower():
                result.skipped_count += 1
                new_children.append(child)
                continue

            existing_labels = list(child.metadata.get("labels", []))
            if existing_labels and not overwrite:
                result.skipped_count += 1
                new_children.append(child)
                continue

            updated = copy.deepcopy(child)
            updated.metadata["labels"] = labels
            result.labeled_count += 1
            result.labels_applied.extend(labels)
            new_children.append(updated)
        elif isinstance(child, BookmarkFolder):
            new_children.append(
                _label_folder(child, labels, url_pattern, overwrite, result)
            )
        else:
            new_children.append(child)

    updated_folder = copy.deepcopy(folder)
    updated_folder.children = new_children
    return updated_folder


def label_bookmarks(
    tree: BookmarkFolder,
    labels: List[str],
    url_pattern: Optional[str] = None,
    overwrite: bool = False,
) -> tuple[BookmarkFolder, LabelResult]:
    """Attach a list of labels to bookmarks matching the optional url_pattern."""
    result = LabelResult()
    updated_tree = _label_folder(tree, labels, url_pattern, overwrite, result)
    return updated_tree, result
