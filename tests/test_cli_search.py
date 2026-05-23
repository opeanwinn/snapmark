"""Tests for snapmark.cli_search module."""

import argparse
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from snapmark.cli_search import _format_results, add_search_subparser, cmd_search
from snapmark.models import Bookmark, BookmarkFolder
from snapmark.search import SearchResult


@pytest.fixture()
def sample_result() -> SearchResult:
    bm = Bookmark(title="GitHub", url="https://github.com")
    return SearchResult(bookmark=bm, path=["Work"])


def test_format_results_empty():
    assert _format_results([]) == "No bookmarks found."


def test_format_results_single(sample_result):
    output = _format_results([sample_result])
    assert "Found 1 bookmark(s)" in output
    assert "GitHub" in output
    assert "https://github.com" in output
    assert "Work" in output


def test_format_results_multiple():
    bm1 = Bookmark(title="A", url="https://a.com")
    bm2 = Bookmark(title="B", url="https://b.com")
    results = [SearchResult(bookmark=bm1, path=[]), SearchResult(bookmark=bm2, path=["Foo"])]
    output = _format_results(results)
    assert "Found 2 bookmark(s)" in output
    assert "https://a.com" in output
    assert "https://b.com" in output


def test_format_results_nested_path():
    """Ensure deeply nested folder paths are rendered correctly in output."""
    bm = Bookmark(title="Docs", url="https://docs.example.com")
    result = SearchResult(bookmark=bm, path=["Work", "Projects", "Alpha"])
    output = _format_results([result])
    assert "Work" in output
    assert "Projects" in output
    assert "Alpha" in output


def _make_args(**kwargs) -> argparse.Namespace:
    defaults = dict(snapshot="snap1", query="github", case_sensitive=False, snapshot_dir=None)
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


def test_cmd_search_success(tmp_path):
    root = BookmarkFolder(name="root")
    root.children = [Bookmark(title="GitHub", url="https://github.com")]

    with patch("snapmark.cli_search.load_snapshot", return_value=root) as mock_load:
        args = _make_args()
        code = cmd_search(args)

    assert code == 0
    mock_load.assert_called_once_with("snap1", snapshot_dir=None)


def test_cmd_search_snapshot_not_found(capsys):
    with patch("snapmark.cli_search.load_snapshot", side_effect=FileNotFoundError("not found")):
        code = cmd_search(_make_args())

    assert code == 1
    captured = capsys.readouterr()
    assert "Error" in captured.err


def test_cmd_search_custom_snapshot_dir(tmp_path):
    """Verify that a custom snapshot_dir is forwarded to load_snapshot."""
    root = BookmarkFolder(name="root")
    root.children = []

    with patch("snapmark.cli_search.load_snapshot", return_value=root) as mock_load:
        args = _make_args(snapshot_dir=str(tmp_path))
        code = cmd_search(args)

    assert code == 0
    mock_load.assert_called_once_with("snap1", snapshot_dir=str(tmp_path))


def test_add_search_subparser_registers_command():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()
    add_search_subparser(subparsers)
    ns = parser.parse_args(["search", "my_snap", "python"])
    assert ns.snapshot == "my_snap"
    assert ns.query == "python"
    assert ns.case_sensitive is False
    assert ns.func is cmd_search
