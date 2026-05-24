"""Apply URL/title templates to bookmarks (e.g. append UTM params, rewrite domains)."""
from dataclasses import dataclass, field
from typing import List
import re

from snapmark.models import Bookmark, BookmarkFolder


@dataclass
class TemplateResult:
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
            f"Template applied: {self.updated_count} updated, "
            f"{self.skipped_count} skipped."
        )


def _apply_template(
    url: str,
    url_pattern: str | None,
    url_template: str | None,
    title_pattern: str | None,
    title_template: str | None,
    title: str,
) -> tuple[str, str, bool]:
    """Return (new_url, new_title, changed)."""
    new_url = url
    new_title = title
    changed = False

    if url_pattern and url_template:
        replaced = re.sub(url_pattern, url_template, url)
        if replaced != url:
            new_url = replaced
            changed = True

    if title_pattern and title_template:
        replaced = re.sub(title_pattern, title_template, title)
        if replaced != title:
            new_title = replaced
            changed = True

    return new_url, new_title, changed


def _template_folder(
    folder: BookmarkFolder,
    url_pattern: str | None,
    url_template: str | None,
    title_pattern: str | None,
    title_template: str | None,
    result: TemplateResult,
    recursive: bool,
) -> BookmarkFolder:
    new_children = []
    for child in folder.children:
        if isinstance(child, Bookmark):
            new_url, new_title, changed = _apply_template(
                child.url, url_pattern, url_template,
                title_pattern, title_template, child.title,
            )
            if changed:
                updated = Bookmark(
                    title=new_title,
                    url=new_url,
                    tags=list(child.tags),
                    created=child.created,
                    note=child.note,
                )
                result.updated.append(updated)
                new_children.append(updated)
            else:
                result.skipped.append(child)
                new_children.append(child)
        elif isinstance(child, BookmarkFolder) and recursive:
            new_children.append(
                _template_folder(
                    child, url_pattern, url_template,
                    title_pattern, title_template, result, recursive,
                )
            )
        else:
            new_children.append(child)
    return BookmarkFolder(name=folder.name, children=new_children)


def apply_template(
    root: BookmarkFolder,
    *,
    url_pattern: str | None = None,
    url_template: str | None = None,
    title_pattern: str | None = None,
    title_template: str | None = None,
    recursive: bool = True,
) -> tuple[BookmarkFolder, TemplateResult]:
    """Apply regex-based URL/title templates to bookmarks."""
    result = TemplateResult()
    new_root = _template_folder(
        root, url_pattern, url_template,
        title_pattern, title_template, result, recursive,
    )
    return new_root, result
