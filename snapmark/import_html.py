"""Parse Netscape-format HTML bookmark files into a BookmarkFolder tree."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from html.parser import HTMLParser
from pathlib import Path
from typing import List, Optional

from snapmark.models import Bookmark, BookmarkFolder


@dataclass
class ImportResult:
    root: BookmarkFolder
    total_bookmarks: int = 0
    total_folders: int = 0

    def summary(self) -> str:
        return (
            f"Imported {self.total_bookmarks} bookmark(s) "
            f"across {self.total_folders} folder(s)."
        )


class _NetscapeParser(HTMLParser):
    """Stateful HTML parser that builds a BookmarkFolder tree."""

    def __init__(self) -> None:
        super().__init__()
        self._root = BookmarkFolder(title="Bookmarks", children=[])
        self._stack: List[BookmarkFolder] = [self._root]
        self._pending_bookmark: Optional[dict] = None
        self._capture_text: bool = False
        self.total_bookmarks: int = 0
        self.total_folders: int = 0

    def handle_starttag(self, tag: str, attrs: list) -> None:
        attr_dict = dict(attrs)
        if tag == "a":
            self._pending_bookmark = {
                "url": attr_dict.get("href", ""),
                "tags": [
                    t.strip()
                    for t in attr_dict.get("tags", "").split(",")
                    if t.strip()
                ],
            }
            self._capture_text = True
        elif tag == "h3":
            self._pending_bookmark = {"is_folder": True}
            self._capture_text = True

    def handle_endtag(self, tag: str) -> None:
        if tag == "dl" and len(self._stack) > 1:
            self._stack.pop()

    def handle_data(self, data: str) -> None:
        text = data.strip()
        if not self._capture_text or not text:
            return
        self._capture_text = False
        if self._pending_bookmark is None:
            return
        info = self._pending_bookmark
        self._pending_bookmark = None
        if info.get("is_folder"):
            folder = BookmarkFolder(title=text, children=[])
            self._stack[-1].children.append(folder)
            self._stack.append(folder)
            self.total_folders += 1
        else:
            bm = Bookmark(
                title=text,
                url=info.get("url", ""),
                tags=info.get("tags", []),
            )
            self._stack[-1].children.append(bm)
            self.total_bookmarks += 1


def import_from_html(source: str | Path) -> ImportResult:
    """Parse a Netscape HTML bookmarks file and return an ImportResult."""
    html = Path(source).read_text(encoding="utf-8") if isinstance(source, Path) else source
    parser = _NetscapeParser()
    parser.feed(html)
    return ImportResult(
        root=parser._root,
        total_bookmarks=parser.total_bookmarks,
        total_folders=parser.total_folders,
    )
