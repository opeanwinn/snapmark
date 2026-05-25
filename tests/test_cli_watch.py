import argparse
import pytest
from pathlib import Path
from snapmark.models import Bookmark, BookmarkFolder
from snapmark.snapshot import save_snapshot, load_snapshot
from snapmark.cli_watch import cmd_watch


@pytest.fixture
def snapshot_dir(tmp_path: Path) -> Path:
    return tmp_path / "snaps"


@pytest.fixture
def saved_snapshot(snapshot_dir: Path) -> str:
    tree = BookmarkFolder(
        name="root",
        children=[
            Bookmark(title="GitHub", url="https://github.com", tags=["dev"]),
            Bookmark(title="YouTube", url="https://youtube.com", tags=[]),
        ],
    )
    save_snapshot(str(snapshot_dir), "base", tree)
    return "base"


def _make_args(**kwargs) -> argparse.Namespace:
    defaults = {
        "name": "base",
        "snapshot_dir": None,
        "url_pattern": None,
        "unwatch": False,
        "output": None,
        "verbose": False,
    }
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


def test_cmd_watch_creates_output_snapshot(snapshot_dir, saved_snapshot, capsys):
    args = _make_args(
        snapshot_dir=str(snapshot_dir),
        name="base",
        output="watched_out",
    )
    cmd_watch(args)
    result_tree = load_snapshot(str(snapshot_dir), "watched_out")
    bm = next(c for c in result_tree.children if isinstance(c, Bookmark) and c.title == "GitHub")
    assert "watched" in bm.tags


def test_cmd_watch_in_place(snapshot_dir, saved_snapshot, capsys):
    args = _make_args(snapshot_dir=str(snapshot_dir), name="base")
    cmd_watch(args)
    result_tree = load_snapshot(str(snapshot_dir), "base")
    for child in result_tree.children:
        if isinstance(child, Bookmark):
            assert "watched" in child.tags


def test_cmd_watch_prints_summary(snapshot_dir, saved_snapshot, capsys):
    args = _make_args(snapshot_dir=str(snapshot_dir), name="base")
    cmd_watch(args)
    captured = capsys.readouterr()
    assert "Watched" in captured.out


def test_cmd_watch_verbose(snapshot_dir, saved_snapshot, capsys):
    args = _make_args(snapshot_dir=str(snapshot_dir), name="base", verbose=True)
    cmd_watch(args)
    captured = capsys.readouterr()
    assert "GitHub" in captured.out or "YouTube" in captured.out


def test_cmd_watch_missing_snapshot_exits(snapshot_dir, capsys):
    import sys
    args = _make_args(snapshot_dir=str(snapshot_dir), name="nonexistent")
    with pytest.raises(SystemExit):
        cmd_watch(args)
