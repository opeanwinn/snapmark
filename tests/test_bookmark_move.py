"""Tests for snapmark.bookmark_move."""

import pytest
from snapmark.models import Bookmark, BookmarkFolder
from snapmark.bookmark_move import move_bookmarks, MoveResult


@pytest.fixture
def sample_tree() -> BookmarkFolder:
    return BookmarkFolder(
        title="root",
        children=[
            Bookmark(title="Python", url="https://python.org", tags=["dev"]),
            Bookmark(title="GitHub", url="https://github.com", tags=[]),
            BookmarkFolder(
                title="Work",
                children=[
                    Bookmark(title="Jira", url="https://jira.example.com", tags=[]),
                ],
            ),
            BookmarkFolder(title="Archive", children=[]),
        ],
    )


def test_move_returns_folder_and_result(sample_tree):
    root, result = move_bookmarks(sample_tree, ["https://python.org"], "Archive")
    assert isinstance(root, BookmarkFolder)
    assert isinstance(result, MoveResult)


def test_move_increases_destination_count(sample_tree):
    root, result = move_bookmarks(sample_tree, ["https://python.org"], "Archive")
    archive = next(c for c in root.children if isinstance(c, BookmarkFolder) and c.title == "Archive")
    assert len(archive.children) == 1
    assert archive.children[0].url == "https://python.org"


def test_move_removes_from_source(sample_tree):
    root, _ = move_bookmarks(sample_tree, ["https://python.org"], "Archive")
    top_level_urls = [c.url for c in root.children if isinstance(c, Bookmark)]
    assert "https://python.org" not in top_level_urls


def test_move_result_count(sample_tree):
    _, result = move_bookmarks(sample_tree, ["https://python.org", "https://github.com"], "Archive")
    assert result.moved_count == 2


def test_move_nested_bookmark(sample_tree):
    root, result = move_bookmarks(sample_tree, ["https://jira.example.com"], "Archive")
    archive = next(c for c in root.children if isinstance(c, BookmarkFolder) and c.title == "Archive")
    assert any(b.url == "https://jira.example.com" for b in archive.children)
    assert result.moved_count == 1


def test_move_url_not_found(sample_tree):
    _, result = move_bookmarks(sample_tree, ["https://notexist.com"], "Archive")
    assert "https://notexist.com" in result.not_found
    assert result.moved_count == 0


def test_move_destination_not_found(sample_tree):
    _, result = move_bookmarks(sample_tree, ["https://python.org"], "NonExistent")
    assert len(result.errors) == 1
    assert "NonExistent" in result.errors[0]


def test_summary_string(sample_tree):
    _, result = move_bookmarks(sample_tree, ["https://python.org"], "Archive")
    summary = result.summary()
    assert "Moved" in summary
