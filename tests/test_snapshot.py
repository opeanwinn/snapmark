"""Tests for snapmark snapshot save/load functionality."""

import json
from pathlib import Path

import pytest

from snapmark.models import Bookmark, BookmarkFolder
from snapmark.snapshot import list_snapshots, load_snapshot, save_snapshot


@pytest.fixture()
def sample_tree() -> BookmarkFolder:
    root = BookmarkFolder(title="Bookmarks Bar")
    root.children.append(Bookmark(title="GitHub", url="https://github.com"))
    sub = BookmarkFolder(title="Dev Tools")
    sub.children.append(Bookmark(title="MDN", url="https://developer.mozilla.org"))
    root.children.append(sub)
    return root


@pytest.fixture()
def snapshot_dir(tmp_path: Path) -> Path:
    return tmp_path / "snapshots"


class TestSaveSnapshot:
    def test_creates_file(self, sample_tree, snapshot_dir):
        path = save_snapshot(sample_tree, directory=snapshot_dir)
        assert path.exists()

    def test_file_is_valid_json(self, sample_tree, snapshot_dir):
        path = save_snapshot(sample_tree, directory=snapshot_dir)
        data = json.loads(path.read_text())
        assert "tree" in data
        assert data["snapmark_version"] == "1.0"

    def test_label_in_filename(self, sample_tree, snapshot_dir):
        path = save_snapshot(sample_tree, name="work", directory=snapshot_dir)
        assert path.name.startswith("work_")

    def test_no_label_filename(self, sample_tree, snapshot_dir):
        path = save_snapshot(sample_tree, directory=snapshot_dir)
        assert not path.name.startswith("_")


class TestLoadSnapshot:
    def test_round_trip(self, sample_tree, snapshot_dir):
        path = save_snapshot(sample_tree, directory=snapshot_dir)
        restored = load_snapshot(path)
        assert restored.title == sample_tree.title
        assert len(restored.children) == len(sample_tree.children)

    def test_nested_folder_preserved(self, sample_tree, snapshot_dir):
        path = save_snapshot(sample_tree, directory=snapshot_dir)
        restored = load_snapshot(path)
        sub = next(c for c in restored.children if isinstance(c, BookmarkFolder))
        assert sub.title == "Dev Tools"
        assert sub.children[0].url == "https://developer.mozilla.org"

    def test_missing_file_raises(self, snapshot_dir):
        with pytest.raises(FileNotFoundError):
            load_snapshot(snapshot_dir / "nonexistent.json")

    def test_invalid_json_raises(self, tmp_path):
        bad_file = tmp_path / "bad.json"
        bad_file.write_text(json.dumps({"snapmark_version": "1.0"}))
        with pytest.raises(ValueError, match="missing 'tree' key"):
            load_snapshot(bad_file)


class TestListSnapshots:
    def test_empty_dir_returns_empty(self, snapshot_dir):
        assert list_snapshots(snapshot_dir) == []

    def test_returns_all_snapshots(self, sample_tree, snapshot_dir):
        save_snapshot(sample_tree, name="a", directory=snapshot_dir)
        save_snapshot(sample_tree, name="b", directory=snapshot_dir)
        snapshots = list_snapshots(snapshot_dir)
        assert len(snapshots) == 2

    def test_sorted_newest_first(self, sample_tree, snapshot_dir):
        p1 = save_snapshot(sample_tree, name="first", directory=snapshot_dir)
        p2 = save_snapshot(sample_tree, name="second", directory=snapshot_dir)
        snapshots = list_snapshots(snapshot_dir)
        assert snapshots[0].stat().st_mtime >= snapshots[1].stat().st_mtime
