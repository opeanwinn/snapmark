"""Tests for snapmark.cli_broken."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pytest

from snapmark.cli_broken import cmd_broken
from snapmark.models import Bookmark, BookmarkFolder
from snapmark.snapshot import save_snapshot


@pytest.fixture()
def snapshot_dir(tmp_path: Path) -> Path:
    return tmp_path / "snaps"


@pytest.fixture()
def saved_snapshot(snapshot_dir: Path) -> str:
    root = BookmarkFolder(
        title="Root",
        children=[
            Bookmark(title="Good", url="https://example.com"),
            Bookmark(title="Broken", url=""),
            Bookmark(title="FTP", url="ftp://files.example.com"),
        ],
    )
    save_snapshot(root, "test_snap", str(snapshot_dir))
    return "test_snap"


def _make_args(**kwargs) -> argparse.Namespace:
    defaults = {
        "name": "test_snap",
        "snapshot_dir": ".snapmarks",
        "verbose": False,
        "fail_on_broken": False,
    }
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


def test_cmd_broken_prints_summary(snapshot_dir, saved_snapshot, capsys):
    args = _make_args(snapshot_dir=str(snapshot_dir))
    cmd_broken(args)
    out = capsys.readouterr().out
    assert "Broken" in out
    assert "Suspicious" in out


def test_cmd_broken_verbose_lists_bookmarks(snapshot_dir, saved_snapshot, capsys):
    args = _make_args(snapshot_dir=str(snapshot_dir), verbose=True)
    cmd_broken(args)
    out = capsys.readouterr().out
    assert "Broken" in out
    assert "FTP" in out


def test_cmd_broken_fail_on_broken_exits(snapshot_dir, saved_snapshot):
    args = _make_args(snapshot_dir=str(snapshot_dir), fail_on_broken=True)
    with pytest.raises(SystemExit) as exc_info:
        cmd_broken(args)
    assert exc_info.value.code == 2


def test_cmd_broken_no_fail_when_clean(snapshot_dir):
    root = BookmarkFolder(
        title="Root",
        children=[Bookmark(title="OK", url="https://ok.com")],
    )
    save_snapshot(root, "clean_snap", str(snapshot_dir))
    args = _make_args(
        name="clean_snap",
        snapshot_dir=str(snapshot_dir),
        fail_on_broken=True,
    )
    # Should NOT raise SystemExit
    cmd_broken(args)


def test_cmd_broken_missing_snapshot_exits(snapshot_dir):
    args = _make_args(name="nonexistent", snapshot_dir=str(snapshot_dir))
    with pytest.raises(SystemExit) as exc_info:
        cmd_broken(args)
    assert exc_info.value.code == 1
