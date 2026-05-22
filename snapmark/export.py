"""Export bookmark trees to various formats (HTML, CSV, JSON)."""

from __future__ import annotations

import csv
import io
import json
from typing import List

from snapmark.models import Bookmark, BookmarkFolder


def _collect_all_bookmarks(
    node: BookmarkFolder, path: str = ""
) -> List[tuple[str, Bookmark]]:
    """Recursively collect all bookmarks with their folder path."""
    results: List[tuple[str, Bookmark]] = []
    current_path = f"{path}/{node.name}" if path else node.name
    for child in node.children:
        if isinstance(child, Bookmark):
            results.append((current_path, child))
        elif isinstance(child, BookmarkFolder):
            results.extend(_collect_all_bookmarks(child, current_path))
    return results


def export_to_html(root: BookmarkFolder) -> str:
    """Export bookmark tree to Netscape Bookmark File Format (HTML)."""
    lines = [
        "<!DOCTYPE NETSCAPE-Bookmark-file-1>",
        "<!-- This is an automatically generated file. -->",
        '<META HTTP-EQUIV="Content-Type" CONTENT="text/html; charset=UTF-8">",
        "<TITLE>Bookmarks</TITLE>",
        "<H1>Bookmarks</H1>",
        "<DL><p>",
    ]

    def _render_folder(folder: BookmarkFolder, indent: int = 1) -> None:
        pad = "    " * indent
        lines.append(f"{pad}<DT><H3>{folder.name}</H3>")
        lines.append(f"{pad}<DL><p>")
        for child in folder.children:
            if isinstance(child, Bookmark):
                title = child.title or child.url
                lines.append(f"{pad}    <DT><A HREF=\"{child.url}\">{title}</A>")
            elif isinstance(child, BookmarkFolder):
                _render_folder(child, indent + 1)
        lines.append(f"{pad}</DL><p>")

    for child in root.children:
        if isinstance(child, Bookmark):
            title = child.title or child.url
            lines.append(f"    <DT><A HREF=\"{child.url}\">{title}</A>")
        elif isinstance(child, BookmarkFolder):
            _render_folder(child)

    lines.append("</DL><p>")
    return "\n".join(lines)


def export_to_csv(root: BookmarkFolder) -> str:
    """Export all bookmarks to CSV with columns: folder, title, url."""
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["folder", "title", "url"])
    for folder_path, bookmark in _collect_all_bookmarks(root):
        writer.writerow([folder_path, bookmark.title or "", bookmark.url])
    return output.getvalue()


def export_to_json(root: BookmarkFolder) -> str:
    """Export bookmark tree to pretty-printed JSON."""
    from snapmark.models import to_dict  # avoid circular at module level
    return json.dumps(to_dict(root), indent=2)
