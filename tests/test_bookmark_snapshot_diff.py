"""Tests for snapmark.bookmark_snapshot_diff."""

import pytest

from snapmark.models import Bookmark, BookmarkFolder
from snapmark.snapshot import save_snapshot
from snapmark.bookmark_snapshot_diff import compare_snapshots, SnapshotDiffResult


@pytest.fixture
def snapshot_dir(tmp_path):
    return str(tmp_path)


@pytest.fixture
def base_tree():
    return BookmarkFolder(
        title="root",
        children=[
            Bookmark(title="Python", url="https://python.org"),
            Bookmark(title="GitHub", url="https://github.com"),
        ],
    )


@pytest.fixture
def modified_tree():
    return BookmarkFolder(
        title="root",
        children=[
            Bookmark(title="Python", url="https://python.org"),
            Bookmark(title="GitLab", url="https://gitlab.com"),
        ],
    )


def test_compare_returns_snapshot_diff_result(snapshot_dir, base_tree, modified_tree):
    save_snapshot(base_tree, "snap_a", snapshot_dir=snapshot_dir)
    save_snapshot(modified_tree, "snap_b", snapshot_dir=snapshot_dir)
    result = compare_snapshots("snap_a", "snap_b", snapshot_dir=snapshot_dir)
    assert isinstance(result, SnapshotDiffResult)


def test_identical_snapshots_have_no_changes(snapshot_dir, base_tree):
    save_snapshot(base_tree, "snap_a", snapshot_dir=snapshot_dir)
    save_snapshot(base_tree, "snap_b", snapshot_dir=snapshot_dir)
    result = compare_snapshots("snap_a", "snap_b", snapshot_dir=snapshot_dir)
    assert not result.has_changes()


def test_detects_added_bookmark(snapshot_dir, base_tree, modified_tree):
    save_snapshot(base_tree, "snap_a", snapshot_dir=snapshot_dir)
    save_snapshot(modified_tree, "snap_b", snapshot_dir=snapshot_dir)
    result = compare_snapshots("snap_a", "snap_b", snapshot_dir=snapshot_dir)
    added_urls = [b.url for b in result.diff.added]
    assert "https://gitlab.com" in added_urls


def test_detects_removed_bookmark(snapshot_dir, base_tree, modified_tree):
    save_snapshot(base_tree, "snap_a", snapshot_dir=snapshot_dir)
    save_snapshot(modified_tree, "snap_b", snapshot_dir=snapshot_dir)
    result = compare_snapshots("snap_a", "snap_b", snapshot_dir=snapshot_dir)
    removed_urls = [b.url for b in result.diff.removed]
    assert "https://github.com" in removed_urls


def test_summary_contains_snapshot_names(snapshot_dir, base_tree, modified_tree):
    save_snapshot(base_tree, "snap_a", snapshot_dir=snapshot_dir)
    save_snapshot(modified_tree, "snap_b", snapshot_dir=snapshot_dir)
    result = compare_snapshots("snap_a", "snap_b", snapshot_dir=snapshot_dir)
    summary = result.summary()
    assert "snap_a" in summary
    assert "snap_b" in summary


def test_missing_snapshot_raises_file_not_found(snapshot_dir, base_tree):
    save_snapshot(base_tree, "snap_a", snapshot_dir=snapshot_dir)
    with pytest.raises(FileNotFoundError):
        compare_snapshots("snap_a", "nonexistent", snapshot_dir=snapshot_dir)
