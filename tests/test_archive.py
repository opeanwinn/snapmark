"""Tests for snapmark.archive module."""

import pytest
from snapmark.models import Bookmark, BookmarkFolder
from snapmark.archive import (
    archive_bookmarks,
    unarchive_bookmarks,
    filter_archived,
    ArchiveResult,
    ARCHIVE_TAG,
)


@pytest.fixture
def sample_tree():
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


def test_archive_returns_folder_and_result(sample_tree):
    folder, result = archive_bookmarks(sample_tree, ["https://python.org"])
    assert isinstance(folder, BookmarkFolder)
    assert isinstance(result, ArchiveResult)


def test_archive_adds_archived_tag(sample_tree):
    folder, result = archive_bookmarks(sample_tree, ["https://python.org"])
    python = next(c for c in folder.children if isinstance(c, Bookmark) and c.url == "https://python.org")
    assert ARCHIVE_TAG in python.tags


def test_archive_preserves_existing_tags(sample_tree):
    folder, result = archive_bookmarks(sample_tree, ["https://python.org"])
    python = next(c for c in folder.children if isinstance(c, Bookmark) and c.url == "https://python.org")
    assert "dev" in python.tags


def test_archive_result_count(sample_tree):
    _, result = archive_bookmarks(sample_tree, ["https://python.org", "https://github.com"])
    assert result.archived_count == 2


def test_archive_nested_bookmark(sample_tree):
    folder, result = archive_bookmarks(sample_tree, ["https://news.ycombinator.com"])
    news_folder = next(c for c in folder.children if isinstance(c, BookmarkFolder))
    hn = news_folder.children[0]
    assert ARCHIVE_TAG in hn.tags
    assert result.archived_count == 1


def test_archive_does_not_duplicate_tag(sample_tree):
    folder, _ = archive_bookmarks(sample_tree, ["https://python.org"])
    folder2, result = archive_bookmarks(folder, ["https://python.org"])
    python = next(c for c in folder2.children if isinstance(c, Bookmark) and c.url == "https://python.org")
    assert python.tags.count(ARCHIVE_TAG) == 1
    assert result.archived_count == 0


def test_unarchive_removes_archived_tag(sample_tree):
    folder, _ = archive_bookmarks(sample_tree, ["https://github.com"])
    folder2, result = unarchive_bookmarks(folder, ["https://github.com"])
    github = next(c for c in folder2.children if isinstance(c, Bookmark) and c.url == "https://github.com")
    assert ARCHIVE_TAG not in github.tags
    assert result.unarchived_count == 1


def test_filter_archived_removes_archived_bookmarks(sample_tree):
    folder, _ = archive_bookmarks(sample_tree, ["https://python.org"])
    filtered = filter_archived(folder)
    urls = [c.url for c in filtered.children if isinstance(c, Bookmark)]
    assert "https://python.org" not in urls
    assert "https://github.com" in urls


def test_filter_archived_keeps_non_archived(sample_tree):
    filtered = filter_archived(sample_tree)
    urls = [c.url for c in filtered.children if isinstance(c, Bookmark)]
    assert "https://python.org" in urls
    assert "https://github.com" in urls


def test_summary_string(sample_tree):
    _, result = archive_bookmarks(sample_tree, ["https://python.org"])
    assert "Archived: 1" in result.summary()
    assert "Unarchived: 0" in result.summary()
