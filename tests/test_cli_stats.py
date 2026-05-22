"""Tests for snapmark.cli_stats."""
from __future__ import annotations

import argparse
import pytest

from snapmark.models import Bookmark, BookmarkFolder
from snapmark.snapshot import save_snapshot
from snapmark.cli_stats import cmd_stats, add_stats_subparser


@pytest.fixture()
def snapshot_dir(tmp_path):
    return tmp_path


@pytest.fixture()
def saved_snapshot(snapshot_dir):
    tree = BookmarkFolder(
        title="root",
        children=[
            Bookmark(title="GitHub", url="https://github.com", tags=["dev"]),
            Bookmark(title="PyPI", url="https://pypi.org", tags=[]),
        ],
    )
    save_snapshot(tree, "mysnap", snapshot_dir=snapshot_dir)
    return "mysnap"


def _make_args(name: str, snapshot_dir, top: int = 5) -> argparse.Namespace:
    return argparse.Namespace(
        name=name,
        snapshot_dir=str(snapshot_dir),
        top=top,
    )


def test_cmd_stats_prints_output(capsys, saved_snapshot, snapshot_dir):
    args = _make_args(saved_snapshot, snapshot_dir)
    cmd_stats(args)
    out = capsys.readouterr().out
    assert "Bookmarks" in out
    assert "mysnap" in out


def test_cmd_stats_missing_snapshot_exits(snapshot_dir):
    args = _make_args("nonexistent", snapshot_dir)
    with pytest.raises(SystemExit) as exc_info:
        cmd_stats(args)
    assert exc_info.value.code == 1


def test_add_stats_subparser_registers_command():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()
    add_stats_subparser(subparsers)
    parsed = parser.parse_args(["stats", "mysnap"])
    assert parsed.name == "mysnap"
    assert parsed.top == 5


def test_add_stats_subparser_top_flag():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()
    add_stats_subparser(subparsers)
    parsed = parser.parse_args(["stats", "mysnap", "--top", "10"])
    assert parsed.top == 10
