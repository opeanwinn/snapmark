"""Tests for snapmark.bookmark_broken."""
from __future__ import annotations

import pytest

from snapmark.bookmark_broken import BrokenResult, find_broken
from snapmark.models import Bookmark, BookmarkFolder


@pytest.fixture()
def sample_tree() -> BookmarkFolder:
    return BookmarkFolder(
        title="Root",
        children=[
            Bookmark(title="Good", url="https://example.com"),
            Bookmark(title="Empty URL", url=""),
            Bookmark(title="No scheme", url="example.com"),
            Bookmark(title="FTP link", url="ftp://files.example.com/data"),
            Bookmark(title="JS link", url="javascript:void(0)"),
            BookmarkFolder(
                title="Sub",
                children=[
                    Bookmark(title="Nested good", url="https://nested.io"),
                    Bookmark(title="Nested broken", url=""),
                    Bookmark(title="File link", url="file:///home/user/doc.pdf"),
                ],
            ),
        ],
    )


def test_find_broken_returns_broken_result(sample_tree):
    result = find_broken(sample_tree)
    assert isinstance(result, BrokenResult)


def test_detects_empty_url_as_broken(sample_tree):
    result = find_broken(sample_tree)
    broken_titles = [b.title for b in result.broken]
    assert "Empty URL" in broken_titles


def test_detects_no_scheme_as_broken(sample_tree):
    result = find_broken(sample_tree)
    broken_titles = [b.title for b in result.broken]
    assert "No scheme" in broken_titles


def test_detects_nested_broken(sample_tree):
    result = find_broken(sample_tree)
    broken_titles = [b.title for b in result.broken]
    assert "Nested broken" in broken_titles


def test_good_bookmark_not_broken(sample_tree):
    result = find_broken(sample_tree)
    broken_titles = [b.title for b in result.broken]
    assert "Good" not in broken_titles
    assert "Nested good" not in broken_titles


def test_ftp_is_suspicious(sample_tree):
    result = find_broken(sample_tree)
    suspicious_titles = [b.title for b in result.suspicious]
    assert "FTP link" in suspicious_titles


def test_javascript_is_suspicious(sample_tree):
    result = find_broken(sample_tree)
    suspicious_titles = [b.title for b in result.suspicious]
    assert "JS link" in suspicious_titles


def test_file_scheme_is_suspicious(sample_tree):
    result = find_broken(sample_tree)
    suspicious_titles = [b.title for b in result.suspicious]
    assert "File link" in suspicious_titles


def test_broken_count(sample_tree):
    result = find_broken(sample_tree)
    # Empty URL, No scheme, Nested broken
    assert result.broken_count == 3


def test_suspicious_count(sample_tree):
    result = find_broken(sample_tree)
    # FTP link, JS link, File link
    assert result.suspicious_count == 3


def test_summary_contains_counts(sample_tree):
    result = find_broken(sample_tree)
    s = result.summary()
    assert "3" in s


def test_empty_tree_no_issues():
    root = BookmarkFolder(title="Empty", children=[])
    result = find_broken(root)
    assert result.broken_count == 0
    assert result.suspicious_count == 0
