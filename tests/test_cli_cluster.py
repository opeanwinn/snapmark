"""Tests for snapmark.cli_cluster."""

import argparse
import pytest
from snapmark.models import Bookmark, BookmarkFolder
from snapmark.snapshot import save_snapshot
from snapmark.cli_cluster import cmd_cluster, add_cluster_subparser


@pytest.fixture
def snapshot_dir(tmp_path):
    return tmp_path


@pytest.fixture
def saved_snapshot(snapshot_dir):
    tree = BookmarkFolder(
        title="Root",
        children=[
            Bookmark(title="Python", url="https://python.org", tags=["lang"]),
            Bookmark(title="Rust", url="https://rust-lang.org", tags=["lang"]),
            Bookmark(title="GitHub", url="https://github.com", tags=[]),
        ],
    )
    save_snapshot(snapshot_dir, "test", tree)
    return "test"


def _make_args(snapshot_dir, name, mode="tag", verbose=False):
    return argparse.Namespace(
        snapshot_dir=snapshot_dir,
        name=name,
        mode=mode,
        verbose=verbose,
    )


def test_cmd_cluster_prints_summary(snapshot_dir, saved_snapshot, capsys):
    args = _make_args(snapshot_dir, saved_snapshot)
    cmd_cluster(args)
    captured = capsys.readouterr()
    assert "Clusters:" in captured.out


def test_cmd_cluster_by_domain(snapshot_dir, saved_snapshot, capsys):
    args = _make_args(snapshot_dir, saved_snapshot, mode="domain")
    cmd_cluster(args)
    captured = capsys.readouterr()
    assert "python.org" in captured.out or "Clusters:" in captured.out


def test_cmd_cluster_verbose_lists_bookmarks(snapshot_dir, saved_snapshot, capsys):
    args = _make_args(snapshot_dir, saved_snapshot, verbose=True)
    cmd_cluster(args)
    captured = capsys.readouterr()
    assert "Python" in captured.out or "Rust" in captured.out


def test_cmd_cluster_missing_snapshot_exits(snapshot_dir):
    args = _make_args(snapshot_dir, "nonexistent")
    with pytest.raises(SystemExit):
        cmd_cluster(args)


def test_add_cluster_subparser_registers_command():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()
    add_cluster_subparser(subparsers)
    args = parser.parse_args(["cluster", "mysnap"])
    assert args.name == "mysnap"
    assert args.mode == "tag"
