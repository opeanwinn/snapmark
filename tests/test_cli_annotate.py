"""Tests for snapmark.cli_annotate."""
import argparse
import pytest
from pathlib import Path
from snapmark.models import Bookmark, BookmarkFolder
from snapmark.snapshot import save_snapshot, load_snapshot
from snapmark.cli_annotate import cmd_annotate


@pytest.fixture
def snapshot_dir(tmp_path: Path) -> Path:
    return tmp_path


@pytest.fixture
def saved_snapshot(snapshot_dir: Path) -> str:
    tree = BookmarkFolder(
        name="Root",
        children=[
            Bookmark(title="Python", url="https://python.org"),
            Bookmark(title="GitHub", url="https://github.com"),
        ],
    )
    save_snapshot(snapshot_dir, "base", tree)
    return "base"


def _make_args(**kwargs) -> argparse.Namespace:
    defaults = {
        "snapshot_dir": None,
        "name": "base",
        "note": "interesting",
        "url_filter": None,
        "overwrite": False,
        "output": None,
        "verbose": False,
    }
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


def test_cmd_annotate_creates_output_snapshot(snapshot_dir, saved_snapshot, capsys):
    args = _make_args(snapshot_dir=snapshot_dir, output="annotated")
    cmd_annotate(args)
    result = load_snapshot(snapshot_dir, "annotated")
    assert result is not None
    bm = result.children[0]
    assert bm.metadata["note"] == "interesting"


def test_cmd_annotate_in_place(snapshot_dir, saved_snapshot, capsys):
    args = _make_args(snapshot_dir=snapshot_dir)
    cmd_annotate(args)
    result = load_snapshot(snapshot_dir, "base")
    assert result.children[0].metadata["note"] == "interesting"


def test_cmd_annotate_with_url_filter(snapshot_dir, saved_snapshot, capsys):
    args = _make_args(snapshot_dir=snapshot_dir, url_filter="github", output="filtered")
    cmd_annotate(args)
    result = load_snapshot(snapshot_dir, "filtered")
    github_bm = next(b for b in result.children if b.title == "GitHub")
    python_bm = next(b for b in result.children if b.title == "Python")
    assert github_bm.metadata.get("note") == "interesting"
    assert python_bm.metadata.get("note") is None


def test_cmd_annotate_missing_snapshot_exits(snapshot_dir, capsys):
    args = _make_args(snapshot_dir=snapshot_dir, name="nonexistent")
    with pytest.raises(SystemExit):
        cmd_annotate(args)


def test_cmd_annotate_verbose_prints_bookmarks(snapshot_dir, saved_snapshot, capsys):
    args = _make_args(snapshot_dir=snapshot_dir, verbose=True)
    cmd_annotate(args)
    captured = capsys.readouterr()
    assert "Annotated:" in captured.out
