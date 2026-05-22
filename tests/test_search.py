"""Tests for snapmark.search module."""

import pytest

from snapmark.models import Bookmark, BookmarkFolder
from snapmark.search import SearchResult, search_tree


@pytest.fixture()
def sample_tree() -> BookmarkFolder:
    root = BookmarkFolder(name="root")
    work = BookmarkFolder(name="Work")
    personal = BookmarkFolder(name="Personal")

    work.children = [
        Bookmark(title="GitHub", url="https://github.com"),
        Bookmark(title="Jira Board", url="https://jira.example.com"),
    ]
    personal.children = [
        Bookmark(title="YouTube", url="https://youtube.com"),
        Bookmark(title="GitHub Gists", url="https://gist.github.com"),
    ]
    root.children = [work, personal, Bookmark(title="Root Link", url="https://root.example.com")]
    return root


def test_empty_query_returns_nothing(sample_tree):
    results = search_tree(sample_tree, "")
    assert results == []


def test_finds_bookmark_by_title(sample_tree):
    results = search_tree(sample_tree, "GitHub")
    assert len(results) == 2
    titles = [r.bookmark.title for r in results]
    assert "GitHub" in titles
    assert "GitHub Gists" in titles


def test_finds_bookmark_by_url(sample_tree):
    results = search_tree(sample_tree, "jira.example")
    assert len(results) == 1
    assert results[0].bookmark.title == "Jira Board"


def test_case_insensitive_by_default(sample_tree):
    results = search_tree(sample_tree, "github")
    assert len(results) == 2


def test_case_sensitive_match(sample_tree):
    results = search_tree(sample_tree, "github", case_sensitive=True)
    # lowercase 'github' only matches the URL of GitHub Gists
    assert all("github" in r.bookmark.url for r in results)


def test_breadcrumb_reflects_folder_path(sample_tree):
    results = search_tree(sample_tree, "Jira")
    assert len(results) == 1
    assert results[0].breadcrumb == "Work"


def test_root_level_bookmark_has_root_breadcrumb(sample_tree):
    results = search_tree(sample_tree, "Root Link")
    assert len(results) == 1
    assert results[0].breadcrumb == "(root)"


def test_no_match_returns_empty_list(sample_tree):
    results = search_tree(sample_tree, "nonexistent-bookmark-xyz")
    assert results == []


def test_result_type_is_search_result(sample_tree):
    results = search_tree(sample_tree, "YouTube")
    assert len(results) == 1
    assert isinstance(results[0], SearchResult)
    assert results[0].bookmark.url == "https://youtube.com"
