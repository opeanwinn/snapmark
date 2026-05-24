"""Tests for snapmark.bookmark_count_by_tag."""

import pytest
from snapmark.models import Bookmark, BookmarkFolder
from snapmark.bookmark_count_by_tag import count_by_tag, TagCountResult


@pytest.fixture
def sample_tree() -> BookmarkFolder:
    return BookmarkFolder(
        title="root",
        children=[
            Bookmark(title="Python Docs", url="https://docs.python.org", tags=["python", "docs"]),
            Bookmark(title="PyPI", url="https://pypi.org", tags=["python"]),
            Bookmark(title="GitHub", url="https://github.com", tags=["dev"]),
            Bookmark(title="No Tags", url="https://example.com", tags=[]),
            BookmarkFolder(
                title="Work",
                children=[
                    Bookmark(title="Jira", url="https://jira.example.com", tags=["work", "dev"]),
                    Bookmark(title="Internal", url="https://internal.example.com", tags=[]),
                ],
            ),
        ],
    )


def test_count_by_tag_returns_tag_count_result(sample_tree):
    result = count_by_tag(sample_tree)
    assert isinstance(result, TagCountResult)


def test_total_count_includes_all_bookmarks(sample_tree):
    result = count_by_tag(sample_tree)
    assert result.total == 6


def test_untagged_count(sample_tree):
    result = count_by_tag(sample_tree)
    assert result.untagged == 2


def test_python_tag_count(sample_tree):
    result = count_by_tag(sample_tree)
    assert result.by_tag["python"] == 2


def test_dev_tag_count(sample_tree):
    result = count_by_tag(sample_tree)
    assert result.by_tag["dev"] == 2


def test_docs_tag_count(sample_tree):
    result = count_by_tag(sample_tree)
    assert result.by_tag["docs"] == 1


def test_work_tag_count(sample_tree):
    result = count_by_tag(sample_tree)
    assert result.by_tag["work"] == 1


def test_summary_contains_total(sample_tree):
    result = count_by_tag(sample_tree)
    summary = result.summary()
    assert "Total bookmarks: 6" in summary


def test_summary_contains_untagged(sample_tree):
    result = count_by_tag(sample_tree)
    summary = result.summary()
    assert "Untagged: 2" in summary


def test_summary_lists_tags(sample_tree):
    result = count_by_tag(sample_tree)
    summary = result.summary()
    assert "python: 2" in summary
    assert "dev: 2" in summary


def test_empty_tree_returns_zeros():
    empty = BookmarkFolder(title="root", children=[])
    result = count_by_tag(empty)
    assert result.total == 0
    assert result.untagged == 0
    assert result.by_tag == {}
