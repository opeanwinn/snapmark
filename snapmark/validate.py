"""Validation utilities for bookmark trees."""
from dataclasses import dataclass, field
from typing import List
from snapmark.models import Bookmark, BookmarkFolder


@dataclass
class ValidationResult:
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    @property
    def is_valid(self) -> bool:
        return len(self.errors) == 0

    def summary(self) -> str:
        lines = []
        if self.is_valid:
            lines.append("Validation passed.")
        else:
            lines.append(f"Validation failed with {len(self.errors)} error(s).")
        if self.errors:
            lines.append("Errors:")
            for e in self.errors:
                lines.append(f"  - {e}")
        if self.warnings:
            lines.append("Warnings:")
            for w in self.warnings:
                lines.append(f"  - {w}")
        return "\n".join(lines)


def _validate_folder(
    folder: BookmarkFolder,
    result: ValidationResult,
    path: str = "",
) -> None:
    current_path = f"{path}/{folder.title}" if path else folder.title
    seen_urls: set = set()

    for child in folder.children:
        if isinstance(child, Bookmark):
            if not child.url:
                result.errors.append(
                    f"Bookmark '{child.title}' at '{current_path}' has an empty URL."
                )
            elif not (child.url.startswith("http://") or child.url.startswith("https://")):
                result.warnings.append(
                    f"Bookmark '{child.title}' at '{current_path}' has a non-HTTP URL: {child.url}"
                )
            if not child.title:
                result.warnings.append(
                    f"A bookmark at '{current_path}' has no title (url={child.url})."
                )
            if child.url in seen_urls:
                result.warnings.append(
                    f"Duplicate URL '{child.url}' found in folder '{current_path}'."
                )
            seen_urls.add(child.url)
        elif isinstance(child, BookmarkFolder):
            if not child.title:
                result.errors.append(
                    f"A folder inside '{current_path}' has no title."
                )
            _validate_folder(child, result, current_path)


def validate_tree(root: BookmarkFolder) -> ValidationResult:
    """Validate a bookmark tree, returning a ValidationResult."""
    result = ValidationResult()
    if not isinstance(root, BookmarkFolder):
        result.errors.append("Root must be a BookmarkFolder.")
        return result
    _validate_folder(root, result)
    return result
