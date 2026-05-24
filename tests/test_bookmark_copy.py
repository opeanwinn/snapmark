"""Tests for snapmark.bookmark_copy."""

from __future__ import annotations

import pytest

from snapmark.bookmark_copy import copy_bookmarks, CopyResult
from snapmark.models import Bookmark, BookmarkFolder


@pytest.fixture
def sample_tree() -> BookmarkFolder:
    return BookmarkFolder(
        title="root",
        children=[
            Bookmark(title="GitHub", url="https://github.com", tags=["dev"]),
            Bookmark(title="Google", url="https://google.com", tags=[]),
            BookmarkFolder(
                title="Work",
                children=[
                    Bookmark(title="Jira", url="https://jira.example.com", tags=["work"]),
                    Bookmark(title="Confluence", url="https://confluence.example.com", tags=["work"]),
                ],
            ),
        ],
    )


def test_copy_returns_folder_and_result(sample_tree):
    new_root, result = copy_bookmarks(sample_tree, "Saved", url_pattern="github")
    assert isinstance(new_root, BookmarkFolder)
    assert isinstance(result, CopyResult)


def test_copy_creates_destination_folder_if_missing(sample_tree):
    new_root, result = copy_bookmarks(sample_tree, "NewFolder", url_pattern="github")
    titles = [c.title for c in new_root.children if isinstance(c, BookmarkFolder)]
    assert "NewFolder" in titles


def test_copy_by_url_pattern(sample_tree):
    _, result = copy_bookmarks(sample_tree, "Saved", url_pattern="github")
    assert result.copy_count == 1
    assert result.copied[0].title == "GitHub"


def test_copy_by_title_pattern(sample_tree):
    _, result = copy_bookmarks(sample_tree, "Saved", title_pattern="google")
    assert result.copy_count == 1
    assert result.copied[0].url == "https://google.com"


def test_copy_nested_bookmarks(sample_tree):
    _, result = copy_bookmarks(sample_tree, "Saved", url_pattern="example.com")
    assert result.copy_count == 2


def test_copy_deduplicates_into_destination(sample_tree):
    # Pre-populate destination with GitHub
    existing = Bookmark(title="GitHub", url="https://github.com", tags=[])
    dest = BookmarkFolder(title="Saved", children=[existing])
    sample_tree.children.append(dest)

    _, result = copy_bookmarks(sample_tree, "Saved", url_pattern="github")
    assert result.copy_count == 0


def test_copy_does_not_mutate_original(sample_tree):
    original_child_count = len(sample_tree.children)
    copy_bookmarks(sample_tree, "Saved", url_pattern="github")
    assert len(sample_tree.children) == original_child_count


def test_summary_message(sample_tree):
    _, result = copy_bookmarks(sample_tree, "Saved", url_pattern="github")
    assert "Saved" in result.summary()
    assert "1" in result.summary()


def test_copy_with_both_patterns(sample_tree):
    _, result = copy_bookmarks(
        sample_tree, "Saved", url_pattern="example.com", title_pattern="jira"
    )
    assert result.copy_count == 1
    assert result.copied[0].title == "Jira"
