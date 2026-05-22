"""Tests for snapmark.validate."""
import pytest
from snapmark.models import Bookmark, BookmarkFolder
from snapmark.validate import validate_tree, ValidationResult


@pytest.fixture
def valid_tree():
    return BookmarkFolder(
        title="root",
        children=[
            BookmarkFolder(
                title="Work",
                children=[
                    Bookmark(title="GitHub", url="https://github.com"),
                    Bookmark(title="Docs", url="https://docs.python.org"),
                ],
            ),
            Bookmark(title="News", url="https://news.ycombinator.com"),
        ],
    )


def test_valid_tree_passes(valid_tree):
    result = validate_tree(valid_tree)
    assert result.is_valid
    assert result.errors == []


def test_bookmark_with_empty_url_is_error():
    root = BookmarkFolder(
        title="root",
        children=[Bookmark(title="Bad", url="")],
    )
    result = validate_tree(root)
    assert not result.is_valid
    assert any("empty URL" in e for e in result.errors)


def test_bookmark_with_non_http_url_is_warning():
    root = BookmarkFolder(
        title="root",
        children=[Bookmark(title="FTP", url="ftp://files.example.com")],
    )
    result = validate_tree(root)
    assert result.is_valid
    assert any("non-HTTP" in w for w in result.warnings)


def test_bookmark_with_no_title_is_warning():
    root = BookmarkFolder(
        title="root",
        children=[Bookmark(title="", url="https://example.com")],
    )
    result = validate_tree(root)
    assert result.is_valid
    assert any("no title" in w for w in result.warnings)


def test_duplicate_url_in_folder_is_warning():
    root = BookmarkFolder(
        title="root",
        children=[
            Bookmark(title="A", url="https://example.com"),
            Bookmark(title="B", url="https://example.com"),
        ],
    )
    result = validate_tree(root)
    assert result.is_valid
    assert any("Duplicate URL" in w for w in result.warnings)


def test_folder_with_no_title_is_error():
    root = BookmarkFolder(
        title="root",
        children=[BookmarkFolder(title="", children=[])],
    )
    result = validate_tree(root)
    assert not result.is_valid
    assert any("no title" in e for e in result.errors)


def test_summary_contains_passed_when_valid(valid_tree):
    result = validate_tree(valid_tree)
    assert "Validation passed" in result.summary()


def test_summary_contains_failed_when_invalid():
    root = BookmarkFolder(
        title="root",
        children=[Bookmark(title="Bad", url="")],
    )
    result = validate_tree(root)
    assert "Validation failed" in result.summary()


def test_non_folder_root_returns_error():
    result = validate_tree(Bookmark(title="x", url="https://x.com"))  # type: ignore
    assert not result.is_valid
    assert any("Root must be" in e for e in result.errors)
