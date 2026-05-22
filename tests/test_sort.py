"""Tests for snapmark.sort."""
from __future__ import annotations

import pytest

from snapmark.models import Bookmark, BookmarkFolder
from snapmark.sort import sort_tree, SortResult


@pytest.fixture
def sample_tree() -> BookmarkFolder:
    return BookmarkFolder(
        title="root",
        children=[
            BookmarkFolder(
                title="Dev",
                children=[
                    Bookmark(title="Zebra", url="https://zebra.io"),
                    Bookmark(title="Alpha", url="https://alpha.dev"),
                ],
            ),
            Bookmark(title="Mozilla", url="https://mozilla.org"),
            Bookmark(title="GitHub", url="https://github.com"),
        ],
    )


def test_sort_returns_folder_and_result(sample_tree):
    sorted_tree, result = sort_tree(sample_tree)
    assert isinstance(sorted_tree, BookmarkFolder)
    assert isinstance(result, SortResult)


def test_sort_by_title_ascending(sample_tree):
    sorted_tree, _ = sort_tree(sample_tree, key="title")
    top_level_titles = [
        c.title for c in sorted_tree.children
    ]
    # Folders and bookmarks sorted together by title
    assert top_level_titles == sorted(top_level_titles, key=str.lower)


def test_sort_by_title_descending(sample_tree):
    sorted_tree, _ = sort_tree(sample_tree, key="title", reverse=True)
    top_level_titles = [c.title for c in sorted_tree.children]
    assert top_level_titles == sorted(top_level_titles, key=str.lower, reverse=True)


def test_sort_recursive(sample_tree):
    sorted_tree, _ = sort_tree(sample_tree, key="title")
    dev_folder = next(
        c for c in sorted_tree.children if isinstance(c, BookmarkFolder)
    )
    child_titles = [c.title for c in dev_folder.children]
    assert child_titles == ["Alpha", "Zebra"]


def test_sort_counts_bookmarks(sample_tree):
    _, result = sort_tree(sample_tree)
    # 2 in Dev + 2 at root level = 4 total bookmarks
    assert result.total_sorted == 4


def test_sort_counts_folders(sample_tree):
    _, result = sort_tree(sample_tree)
    # root + Dev = 2 folders
    assert result.folders_sorted == 2


def test_invalid_key_raises(sample_tree):
    with pytest.raises(ValueError, match="Invalid sort key"):
        sort_tree(sample_tree, key="date")


def test_sort_by_url(sample_tree):
    sorted_tree, _ = sort_tree(sample_tree, key="url")
    # Should not raise; bookmarks sorted by url, folders by title fallback
    assert isinstance(sorted_tree, BookmarkFolder)


def test_summary_message():
    result = SortResult(total_sorted=10, folders_sorted=3)
    assert "10" in result.summary()
    assert "3" in result.summary()
