"""Tests for snapmark.bookmark_share."""

import pytest
from snapmark.models import Bookmark, BookmarkFolder
from snapmark.bookmark_share import share_tree, ShareResult


@pytest.fixture
def sample_tree():
    return BookmarkFolder(
        title="Root",
        children=[
            Bookmark(title="Python Docs", url="https://docs.python.org", tags=["python", "docs"]),
            Bookmark(title="GitHub", url="https://github.com", tags=["dev"]),
            BookmarkFolder(
                title="News",
                children=[
                    Bookmark(title="Hacker News", url="https://news.ycombinator.com", tags=["news"]),
                    Bookmark(title="BBC", url="https://bbc.com", tags=["news"]),
                ],
            ),
        ],
    )


def test_share_returns_share_result(sample_tree):
    result = share_tree(sample_tree)
    assert isinstance(result, ShareResult)


def test_share_all_bookmarks_counted(sample_tree):
    result = share_tree(sample_tree)
    assert result.bookmark_count == 4


def test_share_lines_not_empty(sample_tree):
    result = share_tree(sample_tree)
    assert len(result.lines) > 0


def test_share_url_pattern_filters(sample_tree):
    result = share_tree(sample_tree, url_pattern="github")
    assert result.bookmark_count == 1
    assert any("github" in line for line in result.lines)


def test_share_tag_filter(sample_tree):
    result = share_tree(sample_tree, tag_filter="news")
    assert result.bookmark_count == 2


def test_share_url_and_tag_filter_combined(sample_tree):
    result = share_tree(sample_tree, url_pattern="python", tag_filter="docs")
    assert result.bookmark_count == 1


def test_as_text_returns_string(sample_tree):
    result = share_tree(sample_tree)
    text = result.as_text()
    assert isinstance(text, str)
    assert len(text) > 0


def test_as_markdown_contains_links(sample_tree):
    result = share_tree(sample_tree)
    md = result.as_markdown()
    assert "](" in md or "**" in md


def test_summary_message(sample_tree):
    result = share_tree(sample_tree)
    assert "4" in result.summary()
    assert "bookmark" in result.summary()


def test_no_match_returns_zero_count(sample_tree):
    result = share_tree(sample_tree, url_pattern="nonexistent-xyz")
    assert result.bookmark_count == 0
