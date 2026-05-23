"""Tests for snapmark.pin module."""

import pytest

from snapmark.models import Bookmark, BookmarkFolder
from snapmark.pin import (
    PIN_TAG,
    PinResult,
    get_pinned,
    pin_bookmarks,
    unpin_bookmarks,
)


@pytest.fixture
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
                    Bookmark(title="Lobsters", url="https://lobste.rs", tags=["community"]),
                ],
            ),
        ],
    )


def test_pin_returns_folder_and_result(sample_tree):
    folder, result = pin_bookmarks(sample_tree, ["https://python.org"])
    assert isinstance(folder, BookmarkFolder)
    assert isinstance(result, PinResult)


def test_pin_adds_pinned_tag(sample_tree):
    folder, result = pin_bookmarks(sample_tree, ["https://python.org"])
    assert len(result.pinned) == 1
    assert result.pinned[0].url == "https://python.org"
    assert PIN_TAG in result.pinned[0].tags


def test_pin_preserves_existing_tags(sample_tree):
    folder, result = pin_bookmarks(sample_tree, ["https://python.org"])
    pinned_bm = result.pinned[0]
    assert "dev" in pinned_bm.tags
    assert PIN_TAG in pinned_bm.tags


def test_pin_nested_bookmark(sample_tree):
    folder, result = pin_bookmarks(sample_tree, ["https://news.ycombinator.com"])
    assert len(result.pinned) == 1
    assert result.pinned[0].title == "HN"


def test_pin_not_found_url(sample_tree):
    _, result = pin_bookmarks(sample_tree, ["https://nothere.example.com"])
    assert "https://nothere.example.com" in result.not_found
    assert len(result.pinned) == 0


def test_pin_already_pinned_is_idempotent(sample_tree):
    folder, _ = pin_bookmarks(sample_tree, ["https://python.org"])
    folder2, result2 = pin_bookmarks(folder, ["https://python.org"])
    # Already pinned — no change recorded
    assert len(result2.pinned) == 0


def test_unpin_removes_pinned_tag(sample_tree):
    folder, _ = pin_bookmarks(sample_tree, ["https://github.com"])
    folder2, result = unpin_bookmarks(folder, ["https://github.com"])
    assert len(result.unpinned) == 1
    assert PIN_TAG not in result.unpinned[0].tags


def test_unpin_not_found(sample_tree):
    _, result = unpin_bookmarks(sample_tree, ["https://missing.example.com"])
    assert "https://missing.example.com" in result.not_found


def test_get_pinned_returns_only_pinned(sample_tree):
    folder, _ = pin_bookmarks(sample_tree, ["https://python.org", "https://lobste.rs"])
    pinned = get_pinned(folder)
    urls = [b.url for b in pinned]
    assert "https://python.org" in urls
    assert "https://lobste.rs" in urls
    assert "https://github.com" not in urls


def test_summary_contains_pinned_title(sample_tree):
    _, result = pin_bookmarks(sample_tree, ["https://python.org"])
    summary = result.summary()
    assert "Python" in summary
    assert "pinned" in summary.lower() or "+" in summary


def test_summary_no_changes_message():
    result = PinResult()
    assert result.summary() == "No changes made."
