"""Tests for snapmark.dedupe."""

import pytest

from snapmark.models import Bookmark, BookmarkFolder
from snapmark.dedupe import dedupe_tree, DedupeResult


@pytest.fixture
def sample_tree() -> BookmarkFolder:
    return BookmarkFolder(
        name="root",
        children=[
            Bookmark(title="Python", url="https://python.org"),
            Bookmark(title="Python Dupe", url="https://python.org"),
            Bookmark(title="GitHub", url="https://github.com"),
            BookmarkFolder(
                name="Sub",
                children=[
                    Bookmark(title="GitHub Again", url="https://github.com"),
                    Bookmark(title="Rust", url="https://rust-lang.org"),
                ],
            ),
        ],
    )


def test_dedupe_returns_folder_and_result(sample_tree):
    result = dedupe_tree(sample_tree)
    assert isinstance(result, tuple)
    assert len(result) == 2
    deduped, report = result
    assert isinstance(deduped, BookmarkFolder)
    assert isinstance(report, DedupeResult)


def test_removes_duplicate_urls(sample_tree):
    deduped, report = dedupe_tree(sample_tree)
    assert report.duplicate_count == 2


def test_keeps_unique_bookmarks(sample_tree):
    deduped, report = dedupe_tree(sample_tree)
    kept_urls = [bm.url for bm in report.kept]
    assert len(kept_urls) == len(set(kept_urls))


def test_removed_bookmarks_listed(sample_tree):
    _, report = dedupe_tree(sample_tree)
    removed_urls = [bm.url for bm in report.removed]
    assert "https://python.org" in removed_urls
    assert "https://github.com" in removed_urls


def test_no_duplicates_tree():
    tree = BookmarkFolder(
        name="root",
        children=[
            Bookmark(title="A", url="https://a.com"),
            Bookmark(title="B", url="https://b.com"),
        ],
    )
    deduped, report = dedupe_tree(tree)
    assert report.duplicate_count == 0
    assert "No duplicates found." in report.summary()


def test_summary_with_duplicates(sample_tree):
    _, report = dedupe_tree(sample_tree)
    summary = report.summary()
    assert "Removed" in summary
    assert "2" in summary


def test_deduped_tree_structure_preserved(sample_tree):
    deduped, _ = dedupe_tree(sample_tree)
    subfolder = next(
        (c for c in deduped.children if isinstance(c, BookmarkFolder)), None
    )
    assert subfolder is not None
    assert subfolder.name == "Sub"


def test_first_occurrence_is_kept(sample_tree):
    deduped, report = dedupe_tree(sample_tree)
    kept_titles = [bm.title for bm in report.kept]
    assert "Python" in kept_titles
    assert "Python Dupe" not in kept_titles
