"""Tests for snapmark.import_html."""

import pytest

from snapmark.import_html import import_from_html, ImportResult
from snapmark.models import Bookmark, BookmarkFolder


SIMPLE_HTML = """
<!DOCTYPE NETSCAPE-Bookmark-file-1>
<META HTTP-EQUIV="Content-Type" CONTENT="text/html; charset=UTF-8">
<TITLE>Bookmarks</TITLE>
<H1>Bookmarks</H1>
<DL><p>
    <A HREF="https://example.com" TAGS="news,tech">Example</A>
    <A HREF="https://python.org">Python</A>
    <H3>Dev Tools</H3>
    <DL><p>
        <A HREF="https://github.com" TAGS="dev">GitHub</A>
    </DL><p>
</DL><p>
"""

NESTED_HTML = """
<DL><p>
    <H3>Outer</H3>
    <DL><p>
        <H3>Inner</H3>
        <DL><p>
            <A HREF="https://deep.io">Deep Link</A>
        </DL><p>
    </DL><p>
</DL><p>
"""


def test_import_returns_import_result():
    result = import_from_html(SIMPLE_HTML)
    assert isinstance(result, ImportResult)


def test_root_is_bookmark_folder():
    result = import_from_html(SIMPLE_HTML)
    assert isinstance(result.root, BookmarkFolder)


def test_total_bookmarks_count():
    result = import_from_html(SIMPLE_HTML)
    assert result.total_bookmarks == 3


def test_total_folders_count():
    result = import_from_html(SIMPLE_HTML)
    assert result.total_folders == 1


def test_top_level_bookmark_titles():
    result = import_from_html(SIMPLE_HTML)
    top_level = [c for c in result.root.children if isinstance(c, Bookmark)]
    titles = {b.title for b in top_level}
    assert "Example" in titles
    assert "Python" in titles


def test_bookmark_url_is_preserved():
    result = import_from_html(SIMPLE_HTML)
    top_level = [c for c in result.root.children if isinstance(c, Bookmark)]
    urls = {b.url for b in top_level}
    assert "https://example.com" in urls


def test_tags_are_parsed():
    result = import_from_html(SIMPLE_HTML)
    example = next(
        b for b in result.root.children
        if isinstance(b, Bookmark) and b.title == "Example"
    )
    assert "news" in example.tags
    assert "tech" in example.tags


def test_nested_folder_bookmark():
    result = import_from_html(SIMPLE_HTML)
    folder = next(c for c in result.root.children if isinstance(c, BookmarkFolder))
    assert folder.title == "Dev Tools"
    assert len(folder.children) == 1
    assert folder.children[0].url == "https://github.com"


def test_deeply_nested_structure():
    result = import_from_html(NESTED_HTML)
    outer = next(c for c in result.root.children if isinstance(c, BookmarkFolder))
    assert outer.title == "Outer"
    inner = next(c for c in outer.children if isinstance(c, BookmarkFolder))
    assert inner.title == "Inner"
    assert inner.children[0].url == "https://deep.io"


def test_summary_string():
    result = import_from_html(SIMPLE_HTML)
    summary = result.summary()
    assert "3" in summary
    assert "1" in summary


def test_empty_html_returns_empty_tree():
    result = import_from_html("<DL></DL>")
    assert result.total_bookmarks == 0
    assert result.total_folders == 0
