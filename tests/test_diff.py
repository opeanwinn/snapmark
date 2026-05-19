"""Tests for snapmark.diff module."""

import pytest

from snapmark.diff import DiffResult, diff_trees
from snapmark.models import Bookmark, BookmarkFolder


@pytest.fixture
def base_tree():
    return BookmarkFolder(
        title="root",
        children=[
            BookmarkFolder(
                title="Work",
                children=[
                    Bookmark(title="GitHub", url="https://github.com"),
                    Bookmark(title="Jira", url="https://jira.example.com"),
                ],
            ),
            Bookmark(title="News", url="https://news.ycombinator.com"),
        ],
    )


@pytest.fixture
def modified_tree():
    return BookmarkFolder(
        title="root",
        children=[
            BookmarkFolder(
                title="Work",
                children=[
                    Bookmark(title="GitHub", url="https://github.com"),
                    # Jira removed
                    Bookmark(title="Notion", url="https://notion.so"),  # added
                ],
            ),
            Bookmark(title="News", url="https://news.ycombinator.com"),
        ],
    )


def test_identical_trees_no_changes(base_tree):
    result = diff_trees(base_tree, base_tree)
    assert not result.has_changes


def test_detects_added_bookmark(base_tree, modified_tree):
    result = diff_trees(base_tree, modified_tree)
    urls = [b.url for b in result.added]
    assert "https://notion.so" in urls


def test_detects_removed_bookmark(base_tree, modified_tree):
    result = diff_trees(base_tree, modified_tree)
    urls = [b.url for b in result.removed]
    assert "https://jira.example.com" in urls


def test_detects_moved_bookmark():
    old = BookmarkFolder(
        title="root",
        children=[
            BookmarkFolder(
                title="Misc",
                children=[Bookmark(title="Reddit", url="https://reddit.com")],
            )
        ],
    )
    new = BookmarkFolder(
        title="root",
        children=[
            BookmarkFolder(
                title="Social",
                children=[Bookmark(title="Reddit", url="https://reddit.com")],
            )
        ],
    )
    result = diff_trees(old, new)
    assert len(result.moved) == 1
    bookmark, old_path, new_path = result.moved[0]
    assert bookmark.url == "https://reddit.com"
    assert "Misc" in old_path
    assert "Social" in new_path


def test_summary_no_changes():
    result = DiffResult()
    assert result.summary() == "No changes."


def test_summary_with_changes():
    result = DiffResult(
        added=[Bookmark(title="New", url="https://new.example.com")],
        removed=[Bookmark(title="Old", url="https://old.example.com")],
    )
    summary = result.summary()
    assert "Added" in summary
    assert "Removed" in summary
    assert "new.example.com" in summary
    assert "old.example.com" in summary
