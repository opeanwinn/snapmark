import argparse
import pytest
from pathlib import Path
from snapmark.models import Bookmark, BookmarkFolder
from snapmark.snapshot import save_snapshot, load_snapshot
from snapmark.cli_category import cmd_category, add_category_subparser


@pytest.fixture
def snapshot_dir(tmp_path):
    return str(tmp_path)


@pytest.fixture
def saved_snapshot(snapshot_dir):
    tree = BookmarkFolder(
        name="root",
        children=[
            Bookmark(title="GitHub", url="https://github.com/foo", tags=[]),
            Bookmark(title="Twitter", url="https://twitter.com/bar", tags=[]),
            Bookmark(title="Unknown", url="https://somerandomblog.io", tags=[]),
        ],
    )
    save_snapshot(snapshot_dir, "test", tree)
    return tree


def _make_args(**kwargs):
    defaults = {
        "snapshot_dir": None,
        "name": "test",
        "output": None,
        "overwrite": False,
    }
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


def test_cmd_category_creates_output_snapshot(snapshot_dir, saved_snapshot):
    args = _make_args(snapshot_dir=snapshot_dir, output="categorized")
    cmd_category(args)
    result = load_snapshot(snapshot_dir, "categorized")
    assert isinstance(result, BookmarkFolder)


def test_cmd_category_in_place(snapshot_dir, saved_snapshot):
    args = _make_args(snapshot_dir=snapshot_dir, output=None)
    cmd_category(args)
    result = load_snapshot(snapshot_dir, "test")
    github = next(c for c in result.children if isinstance(c, Bookmark) and "github" in c.url)
    assert github.metadata.get("category") == "development"


def test_cmd_category_missing_snapshot_exits(snapshot_dir):
    args = _make_args(snapshot_dir=snapshot_dir, name="nonexistent")
    with pytest.raises(SystemExit):
        cmd_category(args)


def test_cmd_category_prints_summary(snapshot_dir, saved_snapshot, capsys):
    args = _make_args(snapshot_dir=snapshot_dir)
    cmd_category(args)
    captured = capsys.readouterr()
    assert "Categorized" in captured.out


def test_add_category_subparser_registers_command():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()
    add_category_subparser(subparsers)
    args = parser.parse_args(["category", "/tmp", "snap"])
    assert args.name == "snap"
    assert args.overwrite is False
