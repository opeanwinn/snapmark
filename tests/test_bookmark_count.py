"""Tests for snapmark.bookmark_count."""

from __future__ import annotations

import pytest

from snapmark.models import Bookmark, BookmarkFolder
from snapmark.bookmark_count import CountResult, count_bookmarks, _extract_domain


@pytest.fixture()
def sample_tree() -> BookmarkFolder:
    return BookmarkFolder(
        title="root",
        children=[
            Bookmark(title="GitHub", url="https://github.com/user", tags=["dev", "git"]),
            Bookmark(title="PyPI", url="https://pypi.org/project/requests", tags=["python"]),
            BookmarkFolder(
                title="News",
                children=[
                    Bookmark(title="Hacker News", url="https://news.ycombinator.com", tags=["dev"]),
                    Bookmark(title="BBC", url="https://www.bbc.com/news", tags=[]),
                    BookmarkFolder(
                        title="Tech",
                        children=[
                            Bookmark(title="Wired", url="https://www.wired.com", tags=["tech"]),
                        ],
                    ),
                ],
            ),
        ],
    )


def test_count_returns_count_result(sample_tree: BookmarkFolder) -> None:
    result = count_bookmarks(sample_tree)
    assert isinstance(result, CountResult)


def test_total_count(sample_tree: BookmarkFolder) -> None:
    result = count_bookmarks(sample_tree)
    assert result.total == 5


def test_by_domain_keys_present(sample_tree: BookmarkFolder) -> None:
    result = count_bookmarks(sample_tree)
    assert "github.com" in result.by_domain
    assert "pypi.org" in result.by_domain


def test_by_domain_strips_www(sample_tree: BookmarkFolder) -> None:
    result = count_bookmarks(sample_tree)
    # bbc.com and wired.com both had www. prefix
    assert "bbc.com" in result.by_domain
    assert "wired.com" in result.by_domain


def test_by_tag_counts(sample_tree: BookmarkFolder) -> None:
    result = count_bookmarks(sample_tree)
    assert result.by_tag["dev"] == 2
    assert result.by_tag["python"] == 1
    assert result.by_tag["git"] == 1
    assert result.by_tag["tech"] == 1


def test_by_depth_has_entries(sample_tree: BookmarkFolder) -> None:
    result = count_bookmarks(sample_tree)
    # Top-level bookmarks are at depth 0
    assert 0 in result.by_depth
    assert result.by_depth[0] == 2  # GitHub, PyPI
    # Children of News folder are at depth 1
    assert 1 in result.by_depth
    assert result.by_depth[1] == 2  # Hacker News, BBC
    # Wired is nested one level deeper
    assert 2 in result.by_depth
    assert result.by_depth[2] == 1  # Wired


def test_summary_contains_total(sample_tree: BookmarkFolder) -> None:
    result = count_bookmarks(sample_tree)
    assert "Total bookmarks: 5" in result.summary()


def test_summary_contains_domain(sample_tree: BookmarkFolder) -> None:
    result = count_bookmarks(sample_tree)
    assert "github.com" in result.summary()


def test_extract_domain_strips_www() -> None:
    assert _extract_domain("https://www.example.com/path") == "example.com"


def test_extract_domain_no_www() -> None:
    assert _extract_domain("https://example.com/path") == "example.com"


def test_empty_tree_returns_zero_total() -> None:
    root = BookmarkFolder(title="root", children=[])
    result = count_bookmarks(root)
    assert result.total == 0
    assert result.by_domain == {}
    assert result.by_tag == {}
    assert result.by_depth == {}
