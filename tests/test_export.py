"""Tests for snapmark.export module."""

import csv
import io
import json

import pytest

from snapmark.models import Bookmark, BookmarkFolder
from snapmark.export import export_to_html, export_to_csv, export_to_json


@pytest.fixture
def sample_tree() -> BookmarkFolder:
    root = BookmarkFolder(name="root")
    toolbar = BookmarkFolder(name="Toolbar")
    toolbar.children.append(Bookmark(url="https://example.com", title="Example"))
    toolbar.children.append(Bookmark(url="https://python.org", title="Python"))
    sub = BookmarkFolder(name="Dev")
    sub.children.append(Bookmark(url="https://github.com", title="GitHub"))
    toolbar.children.append(sub)
    root.children.append(toolbar)
    root.children.append(Bookmark(url="https://top-level.com", title="Top Level"))
    return root


class TestExportToHtml:
    def test_contains_doctype(self, sample_tree):
        html = export_to_html(sample_tree)
        assert "NETSCAPE-Bookmark-file-1" in html

    def test_contains_bookmark_url(self, sample_tree):
        html = export_to_html(sample_tree)
        assert "https://example.com" in html

    def test_contains_bookmark_title(self, sample_tree):
        html = export_to_html(sample_tree)
        assert "Example" in html

    def test_contains_folder_name(self, sample_tree):
        html = export_to_html(sample_tree)
        assert "Toolbar" in html

    def test_nested_folder_rendered(self, sample_tree):
        html = export_to_html(sample_tree)
        assert "Dev" in html
        assert "https://github.com" in html

    def test_top_level_bookmark_rendered(self, sample_tree):
        html = export_to_html(sample_tree)
        assert "https://top-level.com" in html


class TestExportToCsv:
    def test_has_header_row(self, sample_tree):
        csv_text = export_to_csv(sample_tree)
        reader = csv.reader(io.StringIO(csv_text))
        header = next(reader)
        assert header == ["folder", "title", "url"]

    def test_all_bookmarks_present(self, sample_tree):
        csv_text = export_to_csv(sample_tree)
        assert "https://example.com" in csv_text
        assert "https://python.org" in csv_text
        assert "https://github.com" in csv_text

    def test_folder_path_included(self, sample_tree):
        csv_text = export_to_csv(sample_tree)
        assert "Toolbar" in csv_text
        assert "Dev" in csv_text

    def test_nested_path_format(self, sample_tree):
        csv_text = export_to_csv(sample_tree)
        # GitHub is under root/Toolbar/Dev
        assert "Toolbar/Dev" in csv_text


class TestExportToJson:
    def test_returns_valid_json(self, sample_tree):
        result = export_to_json(sample_tree)
        data = json.loads(result)
        assert isinstance(data, dict)

    def test_root_name_present(self, sample_tree):
        data = json.loads(export_to_json(sample_tree))
        assert data.get("name") == "root"

    def test_is_pretty_printed(self, sample_tree):
        result = export_to_json(sample_tree)
        assert "\n" in result
