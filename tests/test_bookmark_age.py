"""Tests for snapmark.bookmark_age."""

import pytest

from snapmark.models import Bookmark, BookmarkFolder
from snapmark.bookmark_age import AgeResult, compute_age


@pytest.fixture
def sample_tree() -> BookmarkFolder:
    return BookmarkFolder(
        title="Root",
        children=[
            Bookmark(
                title="Old Site",
                url="https://old.example.com",
                tags=[],
                metadata={"added_date": "2020-01-15"},
            ),
            Bookmark(
                title="New Site",
                url="https://new.example.com",
                tags=[],
                metadata={"added_date": "2024-06-01"},
            ),
            Bookmark(
                title="No Date",
                url="https://nodate.example.com",
                tags=[],
                metadata={},
            ),
            BookmarkFolder(
                title="Sub",
                children=[
                    Bookmark(
                        title="Mid Site",
                        url="https://mid.example.com",
                        tags=[],
                        metadata={"added_date": "2022-03-10"},
                    )
                ],
            ),
        ],
    )


def test_compute_age_returns_age_result(sample_tree):
    result = compute_age(sample_tree)
    assert isinstance(result, AgeResult)


def test_total_with_date(sample_tree):
    result = compute_age(sample_tree)
    assert result.total_with_date == 3


def test_total_without_date(sample_tree):
    result = compute_age(sample_tree)
    assert result.total_without_date == 1


def test_oldest_bookmark(sample_tree):
    result = compute_age(sample_tree)
    assert result.oldest is not None
    assert result.oldest.title == "Old Site"


def test_newest_bookmark(sample_tree):
    result = compute_age(sample_tree)
    assert result.newest is not None
    assert result.newest.title == "New Site"


def test_average_age_days_is_float(sample_tree):
    result = compute_age(sample_tree)
    assert result.average_age_days is not None
    assert isinstance(result.average_age_days, float)
    assert result.average_age_days > 0


def test_bookmarks_by_age_sorted(sample_tree):
    result = compute_age(sample_tree)
    titles = [bm.title for bm in result.bookmarks_by_age]
    assert titles == ["Old Site", "Mid Site", "New Site"]


def test_empty_tree_no_crash():
    root = BookmarkFolder(title="Empty", children=[])
    result = compute_age(root)
    assert result.total_with_date == 0
    assert result.total_without_date == 0
    assert result.oldest is None
    assert result.newest is None
    assert result.average_age_days is None


def test_summary_contains_counts(sample_tree):
    result = compute_age(sample_tree)
    summary = result.summary()
    assert "3" in summary
    assert "1" in summary
