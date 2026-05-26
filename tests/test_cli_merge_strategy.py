import argparse
import pytest
from unittest.mock import patch, MagicMock
from snapmark.models import Bookmark, BookmarkFolder
from snapmark.snapshot import save_snapshot
from snapmark.cli_merge_strategy import cmd_merge_strategy, add_merge_strategy_subparser


@pytest.fixture
def snapshot_dir(tmp_path):
    return str(tmp_path)


@pytest.fixture
def saved_snapshots(snapshot_dir):
    base = BookmarkFolder(
        name="root",
        children=[
            Bookmark(title="Python", url="https://python.org", tags=["dev"]),
        ],
    )
    incoming = BookmarkFolder(
        name="root",
        children=[
            Bookmark(title="Python Docs", url="https://python.org", tags=["dev", "docs"]),
            Bookmark(title="GitLab", url="https://gitlab.com", tags=[]),
        ],
    )
    save_snapshot(snapshot_dir, "base", base)
    save_snapshot(snapshot_dir, "incoming", incoming)
    return snapshot_dir


def _make_args(snapshot_dir, base="base", incoming="incoming", strategy="keep_base", output=None):
    return argparse.Namespace(
        snapshot_dir=snapshot_dir,
        base=base,
        incoming=incoming,
        strategy=strategy,
        output=output,
    )


def test_cmd_merge_strategy_creates_output_snapshot(saved_snapshots, capsys):
    args = _make_args(saved_snapshots, output="merged_result")
    cmd_merge_strategy(args)
    from snapmark.snapshot import load_snapshot
    result = load_snapshot(saved_snapshots, "merged_result")
    assert isinstance(result, BookmarkFolder)


def test_cmd_merge_strategy_prints_summary(saved_snapshots, capsys):
    args = _make_args(saved_snapshots)
    cmd_merge_strategy(args)
    captured = capsys.readouterr()
    assert "Merged:" in captured.out


def test_cmd_merge_strategy_missing_base_exits(saved_snapshots):
    args = _make_args(saved_snapshots, base="nonexistent")
    with pytest.raises(SystemExit):
        cmd_merge_strategy(args)


def test_cmd_merge_strategy_missing_incoming_exits(saved_snapshots):
    args = _make_args(saved_snapshots, incoming="nonexistent")
    with pytest.raises(SystemExit):
        cmd_merge_strategy(args)


def test_add_merge_strategy_subparser_registers_command():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()
    add_merge_strategy_subparser(subparsers)
    args = parser.parse_args(
        ["merge-strategy", "base", "incoming", "--strategy", "keep_incoming"]
    )
    assert args.base == "base"
    assert args.incoming == "incoming"
    assert args.strategy == "keep_incoming"
