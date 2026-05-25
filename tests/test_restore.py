"""Tests for snapmark.restore module."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from snapmark.models import Bookmark, BookmarkFolder
from snapmark.restore import RestoreError, export_to_json, restore_snapshot
from snapmark.snapshot import save_snapshot


@pytest.fixture()
def sample_tree() -> BookmarkFolder:
    return BookmarkFolder(
        title="Root",
        children=[
            Bookmark(title="Python", url="https://python.org"),
            BookmarkFolder(
                title="News",
                children=[Bookmark(title="HN", url="https://news.ycombinator.com")],
            ),
        ],
    )


@pytest.fixture()
def snapshot_dir(tmp_path: Path) -> Path:
    return tmp_path / "snaps"


class TestRestoreSnapshot:
    def test_restores_saved_snapshot(self, sample_tree, snapshot_dir):
        save_snapshot(sample_tree, "v1", snapshot_dir=snapshot_dir)
        restored = restore_snapshot("v1", snapshot_dir=snapshot_dir)
        assert isinstance(restored, BookmarkFolder)
        assert restored.title == sample_tree.title

    def test_restored_children_match(self, sample_tree, snapshot_dir):
        save_snapshot(sample_tree, "v1", snapshot_dir=snapshot_dir)
        restored = restore_snapshot("v1", snapshot_dir=snapshot_dir)
        assert len(restored.children) == len(sample_tree.children)

    def test_missing_snapshot_raises_restore_error(self, snapshot_dir):
        with pytest.raises(RestoreError, match="not found"):
            restore_snapshot("nonexistent", snapshot_dir=snapshot_dir)

    def test_invalid_json_raises_restore_error(self, snapshot_dir):
        snapshot_dir.mkdir(parents=True, exist_ok=True)
        bad_file = snapshot_dir / "bad.json"
        bad_file.write_text("{invalid json", encoding="utf-8")
        with pytest.raises(RestoreError, match="invalid JSON"):
            restore_snapshot("bad", snapshot_dir=snapshot_dir)

    def test_wrong_root_type_raises_restore_error(self, snapshot_dir):
        snapshot_dir.mkdir(parents=True, exist_ok=True)
        wrong = snapshot_dir / "wrong.json"
        wrong.write_text(json.dumps({"type": "bookmark", "title": "x", "url": "http://x.com"}), encoding="utf-8")
        with pytest.raises(RestoreError, match="root must be a BookmarkFolder"):
            restore_snapshot("wrong", snapshot_dir=snapshot_dir)


class TestExportToJson:
    def test_creates_output_file(self, sample_tree, tmp_path):
        out = tmp_path / "export" / "tree.json"
        export_to_json(sample_tree, out)
        assert out.exists()

    def test_output_is_valid_json(self, sample_tree, tmp_path):
        out = tmp_path / "tree.json"
        export_to_json(sample_tree, out)
        data = json.loads(out.read_text(encoding="utf-8"))
        assert isinstance(data, dict)

    def test_exported_title_matches(self, sample_tree, tmp_path):
        out = tmp_path / "tree.json"
        export_to_json(sample_tree, out)
        data = json.loads(out.read_text(encoding="utf-8"))
        assert data["title"] == sample_tree.title

    def test_exported_children_count_matches(self, sample_tree, tmp_path):
        """Verify that the exported JSON preserves the number of top-level children."""
        out = tmp_path / "tree.json"
        export_to_json(sample_tree, out)
        data = json.loads(out.read_text(encoding="utf-8"))
        assert len(data["children"]) == len(sample_tree.children)

    def test_creates_parent_directories(self, sample_tree, tmp_path):
        """Verify that export_to_json creates missing parent directories."""
        out = tmp_path / "nested" / "deep" / "tree.json"
        export_to_json(sample_tree, out)
        assert out.exists()
