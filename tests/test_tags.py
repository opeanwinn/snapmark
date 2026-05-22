"""Tests for snapmark.tags module."""
from __future__ import annotations
import pytest
from snapmark.models import Bookmark, BookmarkFolder
from snapmark.tags import build_tag_index, filter_by_tag, TagIndex


@pytest.fixture()
def sample_tree() -> BookmarkFolder:
    return BookmarkFolder(
        title="root",
        children=[
            Bookmark(title="Python Docs", url="https://docs.python.org", tags=["python", "docs"]),
            Bookmark(title="Real Python", url="https://realpython.com", tags=["python", "tutorial"]),
            BookmarkFolder(
                title="Tools",
                children=[
                    Bookmark(title="GitHub", url="https://github.com", tags=["dev", "tools"]),
                    Bookmark(title="No Tags", url="https://example.com", tags=[]),
                ],
            ),
        ],
    )


def test_build_tag_index_returns_tag_index(sample_tree: BookmarkFolder) -> None:
    idx = build_tag_index(sample_tree)
    assert isinstance(idx, TagIndex)


def test_index_contains_expected_tags(sample_tree: BookmarkFolder) -> None:
    idx = build_tag_index(sample_tree)
    assert "python" in idx.tags()
    assert "docs" in idx.tags()
    assert "tutorial" in idx.tags()
    assert "dev" in idx.tags()
    assert "tools" in idx.tags()


def test_tags_are_sorted(sample_tree: BookmarkFolder) -> None:
    idx = build_tag_index(sample_tree)
    assert idx.tags() == sorted(idx.tags())


def test_bookmarks_for_python_tag(sample_tree: BookmarkFolder) -> None:
    idx = build_tag_index(sample_tree)
    bms = idx.bookmarks_for("python")
    urls = {b.url for b in bms}
    assert "https://docs.python.org" in urls
    assert "https://realpython.com" in urls


def test_bookmarks_for_unknown_tag_returns_empty(sample_tree: BookmarkFolder) -> None:
    idx = build_tag_index(sample_tree)
    assert idx.bookmarks_for("nonexistent") == []


def test_tag_lookup_is_case_insensitive(sample_tree: BookmarkFolder) -> None:
    idx = build_tag_index(sample_tree)
    assert idx.bookmarks_for("PYTHON") == idx.bookmarks_for("python")


def test_bookmark_without_tags_not_indexed(sample_tree: BookmarkFolder) -> None:
    idx = build_tag_index(sample_tree)
    all_urls = {b.url for bms in idx.index.values() for b in bms}
    assert "https://example.com" not in all_urls


def test_filter_by_tag_convenience(sample_tree: BookmarkFolder) -> None:
    results = filter_by_tag(sample_tree, "dev")
    assert len(results) == 1
    assert results[0].url == "https://github.com"


def test_tag_index_len(sample_tree: BookmarkFolder) -> None:
    idx = build_tag_index(sample_tree)
    assert len(idx) == len(idx.tags())
