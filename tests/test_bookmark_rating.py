"""Tests for snapmark.bookmark_rating."""

from __future__ import annotations

import pytest

from snapmark.models import Bookmark, BookmarkFolder
from snapmark.bookmark_rating import rate_bookmarks, RatingResult


@pytest.fixture()
def sample_tree() -> BookmarkFolder:
    return BookmarkFolder(
        name="root",
        children=[
            Bookmark(title="Python", url="https://python.org", tags=["dev"]),
            Bookmark(title="GitHub", url="https://github.com", tags=[]),
            BookmarkFolder(
                name="News",
                children=[
                    Bookmark(title="HN", url="https://news.ycombinator.com", tags=[]),
                ],
            ),
        ],
    )


def test_rate_returns_folder_and_result(sample_tree):
    folder, result = rate_bookmarks(sample_tree, rating=4)
    assert isinstance(folder, BookmarkFolder)
    assert isinstance(result, RatingResult)


def test_rate_all_bookmarks(sample_tree):
    _, result = rate_bookmarks(sample_tree, rating=5)
    assert result.rated_count == 3


def test_rated_bookmark_has_tag(sample_tree):
    folder, _ = rate_bookmarks(sample_tree, rating=3)
    python_bm = folder.children[0]
    assert "rating:3" in python_bm.tags


def test_rate_preserves_existing_tags(sample_tree):
    folder, _ = rate_bookmarks(sample_tree, rating=2)
    python_bm = folder.children[0]
    assert "dev" in python_bm.tags
    assert "rating:2" in python_bm.tags


def test_rate_with_url_filter(sample_tree):
    _, result = rate_bookmarks(sample_tree, rating=5, url_pattern="python")
    assert result.rated_count == 1
    assert result.skipped == 2


def test_rate_nested_bookmark(sample_tree):
    folder, result = rate_bookmarks(sample_tree, rating=1)
    news_folder = folder.children[2]
    hn = news_folder.children[0]
    assert "rating:1" in hn.tags


def test_no_overwrite_skips_already_rated(sample_tree):
    tree, _ = rate_bookmarks(sample_tree, rating=4)
    _, result2 = rate_bookmarks(tree, rating=5, overwrite=False)
    # All three already have a rating tag, so all should be skipped
    assert result2.skipped == 3
    assert result2.rated_count == 0


def test_overwrite_replaces_rating(sample_tree):
    tree, _ = rate_bookmarks(sample_tree, rating=2)
    folder2, result2 = rate_bookmarks(tree, rating=5, overwrite=True)
    for child in folder2.children:
        if isinstance(child, Bookmark):
            assert "rating:5" in child.tags
            assert "rating:2" not in child.tags
    assert result2.rated_count == 2  # top-level bookmarks only (nested handled recursively)


def test_invalid_rating_raises(sample_tree):
    with pytest.raises(ValueError, match="Rating must be between 1 and 5"):
        rate_bookmarks(sample_tree, rating=6)


def test_summary_string(sample_tree):
    _, result = rate_bookmarks(sample_tree, rating=3)
    s = result.summary()
    assert "Rated" in s
    assert "skipped" in s
