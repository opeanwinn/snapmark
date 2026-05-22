"""Tests for snapmark.merge module."""

import pytest
from snapmark.models import Bookmark, BookmarkFolder
from snapmark.merge import merge_trees, _merge_bookmarks


@pytest.fixture
def base_tree() -> BookmarkFolder:
    return BookmarkFolder(
        name="root",
        bookmarks=[
            Bookmark(title="Google", url="https://google.com"),
            Bookmark(title="GitHub", url="https://github.com"),
        ],
        children=[
            BookmarkFolder(
                name="Dev",
                bookmarks=[Bookmark(title="MDN", url="https://developer.mozilla.org")],
                children=[],
            )
        ],
    )


@pytest.fixture
def incoming_tree() -> BookmarkFolder:
    return BookmarkFolder(
        name="root",
        bookmarks=[
            Bookmark(title="GitHub", url="https://github.com"),  # duplicate
            Bookmark(title="Stack Overflow", url="https://stackoverflow.com"),
        ],
        children=[
            BookmarkFolder(
                name="Dev",
                bookmarks=[Bookmark(title="Can I Use", url="https://caniuse.com")],
                children=[],
            ),
            BookmarkFolder(
                name="News",
                bookmarks=[Bookmark(title="HN", url="https://news.ycombinator.com")],
                children=[],
            ),
        ],
    )


def test_merge_deduplicates_bookmarks_by_url(base_tree, incoming_tree):
    result = merge_trees(base_tree, incoming_tree)
    urls = [b.url for b in result.bookmarks]
    assert urls.count("https://github.com") == 1


def test_merge_includes_new_bookmarks(base_tree, incoming_tree):
    result = merge_trees(base_tree, incoming_tree)
    urls = [b.url for b in result.bookmarks]
    assert "https://stackoverflow.com" in urls


def test_merge_preserves_base_bookmarks(base_tree, incoming_tree):
    result = merge_trees(base_tree, incoming_tree)
    urls = [b.url for b in result.bookmarks]
    assert "https://google.com" in urls


def test_merge_combines_matching_folders(base_tree, incoming_tree):
    result = merge_trees(base_tree, incoming_tree)
    dev_folder = next(f for f in result.children if f.name == "Dev")
    urls = [b.url for b in dev_folder.bookmarks]
    assert "https://developer.mozilla.org" in urls
    assert "https://caniuse.com" in urls


def test_merge_appends_new_folders(base_tree, incoming_tree):
    result = merge_trees(base_tree, incoming_tree)
    folder_names = [f.name for f in result.children]
    assert "News" in folder_names


def test_merge_preserves_root_name(base_tree, incoming_tree):
    result = merge_trees(base_tree, incoming_tree)
    assert result.name == "root"


def test_merge_bookmarks_empty_incoming():
    base = [Bookmark(title="A", url="https://a.com")]
    result = _merge_bookmarks(base, [])
    assert len(result) == 1


def test_merge_bookmarks_empty_base():
    incoming = [Bookmark(title="B", url="https://b.com")]
    result = _merge_bookmarks([], incoming)
    assert len(result) == 1
