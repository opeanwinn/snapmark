"""Tests for snapmark.flatten."""

import pytest

from snapmark.models import Bookmark, BookmarkFolder
from snapmark.flatten import FlatBookmark, FlattenResult, flatten_tree


@pytest.fixture
def sample_tree() -> BookmarkFolder:
    return BookmarkFolder(
        title="root",
        children=[
            Bookmark(title="Google", url="https://google.com"),
            BookmarkFolder(
                title="Dev",
                children=[
                    Bookmark(title="GitHub", url="https://github.com"),
                    BookmarkFolder(
                        title="Python",
                        children=[
                            Bookmark(title="PyPI", url="https://pypi.org"),
                        ],
                    ),
                ],
            ),
        ],
    )


def test_flatten_returns_flatten_result(sample_tree):
    result = flatten_tree(sample_tree)
    assert isinstance(result, FlattenResult)


def test_total_count_matches_all_bookmarks(sample_tree):
    result = flatten_tree(sample_tree)
    assert result.total == 3


def test_flat_bookmark_has_correct_type(sample_tree):
    result = flatten_tree(sample_tree)
    for fb in result.bookmarks:
        assert isinstance(fb, FlatBookmark)
        assert isinstance(fb.bookmark, Bookmark)


def test_top_level_bookmark_path(sample_tree):
    result = flatten_tree(sample_tree)
    google = next(fb for fb in result.bookmarks if fb.bookmark.title == "Google")
    assert google.path == ["root"]
    assert google.breadcrumb == "root"


def test_nested_bookmark_path(sample_tree):
    result = flatten_tree(sample_tree)
    github = next(fb for fb in result.bookmarks if fb.bookmark.title == "GitHub")
    assert github.path == ["root", "Dev"]
    assert github.breadcrumb == "root / Dev"


def test_deeply_nested_bookmark_path(sample_tree):
    result = flatten_tree(sample_tree)
    pypi = next(fb for fb in result.bookmarks if fb.bookmark.title == "PyPI")
    assert pypi.path == ["root", "Dev", "Python"]
    assert pypi.breadcrumb == "root / Dev / Python"


def test_empty_tree_returns_zero_bookmarks():
    empty_root = BookmarkFolder(title="root", children=[])
    result = flatten_tree(empty_root)
    assert result.total == 0
    assert result.bookmarks == []


def test_summary_string(sample_tree):
    result = flatten_tree(sample_tree)
    summary = result.summary()
    assert "3" in summary
    assert "bookmark" in summary.lower()


def test_repr_includes_title_and_path(sample_tree):
    result = flatten_tree(sample_tree)
    github = next(fb for fb in result.bookmarks if fb.bookmark.title == "GitHub")
    r = repr(github)
    assert "GitHub" in r
    assert "root / Dev" in r
