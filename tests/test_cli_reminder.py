import argparse
import pytest
from pathlib import Path
from snapmark.models import Bookmark, BookmarkFolder
from snapmark.snapshot import save_snapshot
from snapmark.cli_reminder import cmd_reminder


@pytest.fixture
def snapshot_dir(tmp_path):
    return str(tmp_path)


@pytest.fixture
def saved_snapshot(snapshot_dir):
    tree = BookmarkFolder(
        name="root",
        children=[
            Bookmark(title="OpenAI", url="https://openai.com", tags=["ai"]),
            Bookmark(title="GitHub", url="https://github.com", tags=[]),
        ],
    )
    save_snapshot(tree, snapshot_dir, "base")
    return "base"


def _make_args(snapshot_dir, name, **kwargs):
    defaults = dict(
        snapshot_dir=snapshot_dir,
        name=name,
        days=7,
        url_pattern="",
        overwrite=False,
        output="",
        verbose=False,
    )
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


def test_cmd_reminder_creates_output_snapshot(snapshot_dir, saved_snapshot):
    args = _make_args(snapshot_dir, saved_snapshot, output="reminded")
    cmd_reminder(args)
    assert Path(snapshot_dir, "reminded.json").exists()


def test_cmd_reminder_in_place(snapshot_dir, saved_snapshot):
    args = _make_args(snapshot_dir, saved_snapshot)
    cmd_reminder(args)
    assert Path(snapshot_dir, "base.json").exists()


def test_cmd_reminder_missing_snapshot_exits(snapshot_dir):
    args = _make_args(snapshot_dir, "nonexistent")
    with pytest.raises(SystemExit):
        cmd_reminder(args)


def test_cmd_reminder_prints_summary(snapshot_dir, saved_snapshot, capsys):
    args = _make_args(snapshot_dir, saved_snapshot)
    cmd_reminder(args)
    out = capsys.readouterr().out
    assert "Reminders scheduled" in out


def test_cmd_reminder_verbose_lists_bookmarks(snapshot_dir, saved_snapshot, capsys):
    args = _make_args(snapshot_dir, saved_snapshot, verbose=True)
    cmd_reminder(args)
    out = capsys.readouterr().out
    assert "remind:" in out
