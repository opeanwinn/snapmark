"""Tests for snapmark.prune."""

from datetime import datetime, timedelta, timezone

import pytest

from snapmark.models import Bookmark, BookmarkFolder
from snapmark.prune import PruneResult, prune_tree


def _days_ago(n: int) -> str:
    dt = datetime.now(tz=timezone.utc) - timedelta(days=n)
    return dt.isoformat()


@pytest.fixture
def sample_tree() -> BookmarkFolder:
    return BookmarkFolder(
        title="root",
        children=[
            Bookmark(
                title="Recent",
                url="https://recent.example.com",
                metadata={"added_date": _days_ago(2)},
            ),
            Bookmark(
                title="Old",
                url="https://old.example.com",
                metadata={"added_date": _days_ago(60)},
            ),
            Bookmark(
                title="No Date",
                url="https://nodate.example.com",
                metadata={},
            ),
            BookmarkFolder(
                title="Sub",
                children=[
                    Bookmark(
                        title="Ancient",
                        url="https://ancient.example.com",
                        metadata={"added_date": _days_ago(365)},
                    ),
                    Bookmark(
                        title="Fresh",
                        url="https://fresh.example.com",
                        metadata={"added_date": _days_ago(1)},
                    ),
                ],
            ),
        ],
    )


def test_prune_returns_folder_and_result(sample_tree):
    folder, result = prune_tree(sample_tree, days=30)
    assert isinstance(folder, BookmarkFolder)
    assert isinstance(result, PruneResult)


def test_prune_removes_old_bookmarks(sample_tree):
    _, result = prune_tree(sample_tree, days=30)
    removed_urls = {b.url for b in result.removed}
    assert "https://old.example.com" in removed_urls
    assert "https://ancient.example.com" in removed_urls


def test_prune_keeps_recent_bookmarks(sample_tree):
    folder, result = prune_tree(sample_tree, days=30)
    removed_urls = {b.url for b in result.removed}
    assert "https://recent.example.com" not in removed_urls
    assert "https://fresh.example.com" not in removed_urls


def test_prune_keeps_bookmarks_without_date(sample_tree):
    folder, result = prune_tree(sample_tree, days=30)
    removed_urls = {b.url for b in result.removed}
    assert "https://nodate.example.com" not in removed_urls


def test_kept_count_is_correct(sample_tree):
    _, result = prune_tree(sample_tree, days=30)
    # Recent + No Date + Fresh = 3 kept
    assert result.kept == 3


def test_removed_count_property(sample_tree):
    _, result = prune_tree(sample_tree, days=30)
    assert result.removed_count == len(result.removed)


def test_summary_string(sample_tree):
    _, result = prune_tree(sample_tree, days=30)
    summary = result.summary()
    assert "Pruned" in summary
    assert "kept" in summary


def test_negative_days_raises(sample_tree):
    with pytest.raises(ValueError):
        prune_tree(sample_tree, days=-1)


def test_zero_days_removes_all_dated(sample_tree):
    _, result = prune_tree(sample_tree, days=0)
    # All bookmarks with any past date should be removed
    removed_urls = {b.url for b in result.removed}
    assert "https://old.example.com" in removed_urls
    assert "https://ancient.example.com" in removed_urls
