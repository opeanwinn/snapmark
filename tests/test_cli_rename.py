"""Tests for snapmark.cli_rename module."""

import argparse
import pytest
from pathlib import Path

from snapmark.models import Bookmark, BookmarkFolder
from snapmark.snapshot import save_snapshot
from snapmark.cli_rename import cmd_rename, add_rename_subparser


@pytest.fixture
def snapshot_dir(tmp_path: Path) -> Path:
    return tmp_path


@pytest.fixture
def saved_snapshot(snapshot_dir: Path) -> str:
    tree = BookmarkFolder(
        title="root",
        children=[
            Bookmark(title="GitHub", url="https://github.com", tags=[]),
            BookmarkFolder(
                title="Work",
                children=[
                    Bookmark(title="Jira", url="https://jira.example.com", tags=[]),
                ],
            ),
        ],
    )
    save_snapshot(snapshot_dir, "test_snap", tree)
    return "test_snap"


def _make_args(**kwargs) -> argparse.Namespace:
    defaults = {
        "snapshot_dir": None,
        "name": "test_snap",
        "old_title": "GitHub",
        "new_title": "GitHub Mirror",
        "in_place": False,
        "output": None,
    }
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


def test_cmd_rename_creates_output_snapshot(snapshot_dir, saved_snapshot, capsys):
    args = _make_args(snapshot_dir=snapshot_dir)
    cmd_rename(args)
    out = capsys.readouterr().out
    assert "test_snap_renamed" in out
    assert (snapshot_dir / "test_snap_renamed.json").exists()


def test_cmd_rename_in_place(snapshot_dir, saved_snapshot, capsys):
    args = _make_args(snapshot_dir=snapshot_dir, in_place=True)
    cmd_rename(args)
    out = capsys.readouterr().out
    assert "updated" in out


def test_cmd_rename_custom_output(snapshot_dir, saved_snapshot, capsys):
    args = _make_args(snapshot_dir=snapshot_dir, output="my_renamed")
    cmd_rename(args)
    assert (snapshot_dir / "my_renamed.json").exists()


def test_cmd_rename_no_match_prints_message(snapshot_dir, saved_snapshot, capsys):
    args = _make_args(snapshot_dir=snapshot_dir, old_title="Nonexistent")
    cmd_rename(args)
    out = capsys.readouterr().out
    assert "Nothing changed" in out


def test_cmd_rename_missing_snapshot_exits(snapshot_dir, capsys):
    args = _make_args(snapshot_dir=snapshot_dir, name="ghost")
    with pytest.raises(SystemExit):
        cmd_rename(args)


def test_cmd_rename_nested_bookmark(snapshot_dir, saved_snapshot, capsys):
    """Renaming a bookmark nested inside a folder should succeed."""
    args = _make_args(snapshot_dir=snapshot_dir, old_title="Jira", new_title="Jira Cloud", output="nested_renamed")
    cmd_rename(args)
    assert (snapshot_dir / "nested_renamed.json").exists()
    out = capsys.readouterr().out
    assert "nested_renamed" in out


def test_add_rename_subparser_registers_command():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()
    add_rename_subparser(subparsers)
    args = parser.parse_args(["rename", "snap", "OldTitle", "NewTitle"])
    assert args.name == "snap"
    assert args.old_title == "OldTitle"
    assert args.new_title == "NewTitle"
    assert args.in_place is False
