"""Tests for snapmark.filter module."""
import pytest

from snapmark.models import Bookmark, BookmarkFolder
from snapmark.filter import filter_tree, FilterResult


@pytest.fixture
def sample_tree() -> BookmarkFolder:
    return BookmarkFolder(
        title="Root",
        children=[
            Bookmark(title="GitHub", url="https://github.com", tags="dev,python"),
            Bookmark(title="PyPI", url="https://pypi.org", tags="python,packages"),
            Bookmark(title="Google", url="https://www.google.com", tags="search"),
            BookmarkFolder(
                title="News",
                children=[
                    Bookmark(
                        title="Hacker News",
                        url="https://news.ycombinator.com",
                        tags="tech,news",
                    ),
                    Bookmark(
                        title="BBC",
                        url="https://bbc.co.uk",
                        tags="news",
                    ),
                ],
            ),
        ],
    )


def test_filter_returns_filter_result(sample_tree):
    result = filter_tree(sample_tree, domain="github.com")
    assert isinstance(result, FilterResult)


def test_filter_by_domain_matches_correctly(sample_tree):
    result = filter_tree(sample_tree, domain="github.com")
    assert result.match_count == 1
    assert result.matched[0].title == "GitHub"


def test_filter_by_tag_matches_correctly(sample_tree):
    result = filter_tree(sample_tree, tag="python")
    assert result.match_count == 2
    titles = {b.title for b in result.matched}
    assert titles == {"GitHub", "PyPI"}


def test_filter_by_domain_and_tag(sample_tree):
    result = filter_tree(sample_tree, domain="pypi.org", tag="packages")
    assert result.match_count == 1
    assert result.matched[0].title == "PyPI"


def test_filter_searches_nested_folders(sample_tree):
    result = filter_tree(sample_tree, tag="news")
    assert result.match_count == 2
    titles = {b.title for b in result.matched}
    assert titles == {"Hacker News", "BBC"}


def test_filter_total_scanned(sample_tree):
    result = filter_tree(sample_tree, tag="dev")
    assert result.total_scanned == 5


def test_filter_no_matches_returns_empty(sample_tree):
    result = filter_tree(sample_tree, domain="notexist.xyz")
    assert result.match_count == 0
    assert result.matched == []


def test_filter_raises_if_no_criteria(sample_tree):
    with pytest.raises(ValueError, match="At least one"):
        filter_tree(sample_tree)


def test_filter_summary_string(sample_tree):
    result = filter_tree(sample_tree, tag="python")
    summary = result.summary()
    assert "2" in summary
    assert "5" in summary


def test_filter_case_insensitive_tag(sample_tree):
    result = filter_tree(sample_tree, tag="PYTHON")
    assert result.match_count == 2


def test_filter_case_insensitive_domain(sample_tree):
    result = filter_tree(sample_tree, domain="GITHUB.COM")
    assert result.match_count == 1
