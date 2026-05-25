"""Tests for snapmark.cli_snapshot_diff."""

import argparse
import pytest

from snapmark.models import Bookmark, BookmarkFolder
from snapmark.snapshot import save_snapshot
from snapmark.cli_snapshot_diff import cmd_snapdiff, add_snapdiff_subparser


@pytest.fixture
def snapshot_dir(tmp_path):
    return str(tmp_path)


@pytest.fixture
def saved_snapshots(snapshot_dir):
    tree_a = BookmarkFolder(
        title="root",
        children=[Bookmark(title="Python", url="https://python.org")],
    )
    tree_b = BookmarkFolder(
        title="root",
        children=[
            Bookmark(title="Python", url="https://python.org"),
            Bookmark(title="Rust", url="https://rust-lang.org"),
        ],
    )
    save_snapshot(tree_a, "snap_a", snapshot_dir=snapshot_dir)
    save_snapshot(tree_b, "snap_b", snapshot_dir=snapshot_dir)
    return snapshot_dir


def _make_args(snapshot_dir, snap_a, snap_b, verbose=False):
    return argparse.Namespace(
        snapshot_a=snap_a,
        snapshot_b=snap_b,
        snapshot_dir=snapshot_dir,
        verbose=verbose,
    )


def test_cmd_snapdiff_prints_summary(capsys, saved_snapshots):
    args = _make_args(saved_snapshots, "snap_a", "snap_b")
    cmd_snapdiff(args)
    out = capsys.readouterr().out
    assert "snap_a" in out
    assert "snap_b" in out


def test_cmd_snapdiff_verbose_lists_added(capsys, saved_snapshots):
    args = _make_args(saved_snapshots, "snap_a", "snap_b", verbose=True)
    cmd_snapdiff(args)
    out = capsys.readouterr().out
    assert "rust-lang.org" in out


def test_cmd_snapdiff_no_changes_message(capsys, saved_snapshots):
    args = _make_args(saved_snapshots, "snap_a", "snap_a")
    cmd_snapdiff(args)
    out = capsys.readouterr().out
    assert "No differences" in out


def test_cmd_snapdiff_missing_snapshot_exits(saved_snapshots):
    args = _make_args(saved_snapshots, "snap_a", "does_not_exist")
    with pytest.raises(SystemExit):
        cmd_snapdiff(args)


def test_add_snapdiff_subparser_registers_command():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()
    add_snapdiff_subparser(subparsers)
    parsed = parser.parse_args(["snapdiff", "a", "b"])
    assert parsed.snapshot_a == "a"
    assert parsed.snapshot_b == "b"
