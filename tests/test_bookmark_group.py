"""Tests for snapmark.bookmark_group."""

import pytest

from snapmark.bookmark_group import GroupResult, group_bookmarks
from snapmark.models import Bookmark, BookmarkFolder


@pytest.fixture
def sample_tree() -> BookmarkFolder:
    return BookmarkFolder(
        title="Root",
        children=[
            Bookmark(title="GitHub", url="https://github.com/user", tags=["dev", "python"]),
            Bookmark(title="PyPI", url="https://pypi.org/project/foo", tags=["python"]),
            Bookmark(title="Google", url="https://www.google.com", tags=[]),
            BookmarkFolder(
                title="News",
                children=[
                    Bookmark(title="HN", url="https://news.ycombinator.com", tags=["dev"]),
                    Bookmark(title="BBC", url="https://www.bbc.co.uk", tags=[]),
                ],
            ),
        ],
    )


def test_group_returns_group_result(sample_tree):
    result = group_bookmarks(sample_tree)
    assert isinstance(result, GroupResult)


def test_group_by_domain_default(sample_tree):
    result = group_bookmarks(sample_tree)
    assert result.group_by == "domain"


def test_group_by_domain_keys(sample_tree):
    result = group_bookmarks(sample_tree)
    assert "github.com" in result.groups
    assert "pypi.org" in result.groups
    assert "google.com" in result.groups


def test_group_by_domain_strips_www(sample_tree):
    result = group_bookmarks(sample_tree)
    assert "bbc.co.uk" in result.groups
    assert "www.bbc.co.uk" not in result.groups


def test_group_by_domain_total(sample_tree):
    result = group_bookmarks(sample_tree)
    assert result.total() == 5


def test_group_by_tag_keys(sample_tree):
    result = group_bookmarks(sample_tree, group_by="tag")
    assert "python" in result.groups
    assert "dev" in result.groups
    assert "(untagged)" in result.groups


def test_group_by_tag_python_count(sample_tree):
    result = group_bookmarks(sample_tree, group_by="tag")
    assert len(result.groups["python"]) == 2


def test_group_by_tag_dev_count(sample_tree):
    result = group_bookmarks(sample_tree, group_by="tag")
    assert len(result.groups["dev"]) == 2


def test_group_by_tag_untagged_count(sample_tree):
    result = group_bookmarks(sample_tree, group_by="tag")
    assert len(result.groups["(untagged)"]) == 2


def test_invalid_group_by_raises(sample_tree):
    with pytest.raises(ValueError, match="Unsupported group_by"):
        group_bookmarks(sample_tree, group_by="color")


def test_summary_contains_group_by(sample_tree):
    result = group_bookmarks(sample_tree, group_by="domain")
    assert "domain" in result.summary()


def test_summary_contains_group_count(sample_tree):
    result = group_bookmarks(sample_tree, group_by="domain")
    summary = result.summary()
    assert str(len(result.groups)) in summary
