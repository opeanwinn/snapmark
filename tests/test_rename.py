"""Tests for snapmark.rename module."""

import pytest
from snapmark.models import Bookmark, BookmarkFolder
from snapmark.rename import rename_tree, RenameResult


@pytest.fixture
def sample_tree() -> BookmarkFolder:
    return BookmarkFolder(
        title="root",
        children=[
            Bookmark(title="Python Docs", url="https://docs.python.org", tags=["python"]),
            Bookmark(title="GitHub", url="https://github.com", tags=[]),
            BookmarkFolder(
                title="Dev Tools",
                children=[
                    Bookmark(title="Python Docs", url="https://docs.python.org/3", tags=[]),
                    Bookmark(title="VS Code", url="https://code.visualstudio.com", tags=[]),
                ],
            ),
        ],
    )


def test_rename_returns_folder_and_result(sample_tree):
    folder, result = rename_tree(sample_tree, "GitHub", "GitHub Mirror")
    assert isinstance(folder, BookmarkFolder)
    assert isinstance(result, RenameResult)


def test_renames_top_level_bookmark(sample_tree):
    folder, result = rename_tree(sample_tree, "GitHub", "GitHub Mirror")
    titles = [c.title for c in folder.children if isinstance(c, Bookmark)]
    assert "GitHub Mirror" in titles
    assert "GitHub" not in titles


def test_renames_all_matching_bookmarks(sample_tree):
    folder, result = rename_tree(sample_tree, "Python Docs", "Python Documentation")
    assert result.renamed_count == 2


def test_renames_nested_bookmark(sample_tree):
    folder, result = rename_tree(sample_tree, "VS Code", "Visual Studio Code")
    dev_tools = next(c for c in folder.children if isinstance(c, BookmarkFolder))
    titles = [c.title for c in dev_tools.children if isinstance(c, Bookmark)]
    assert "Visual Studio Code" in titles
    assert "VS Code" not in titles


def test_renames_folder(sample_tree):
    folder, result = rename_tree(sample_tree, "Dev Tools", "Developer Tools")
    folder_titles = [c.title for c in folder.children if isinstance(c, BookmarkFolder)]
    assert "Developer Tools" in folder_titles
    assert "Dev Tools" not in folder_titles
    assert result.renamed_count == 1


def test_no_match_returns_zero_count(sample_tree):
    folder, result = rename_tree(sample_tree, "Nonexistent", "Something")
    assert result.renamed_count == 0
    assert result.renamed_items == []


def test_summary_no_renames(sample_tree):
    _, result = rename_tree(sample_tree, "Nonexistent", "Something")
    assert result.summary() == "No items renamed."


def test_summary_with_renames(sample_tree):
    _, result = rename_tree(sample_tree, "GitHub", "GitHub Mirror")
    summary = result.summary()
    assert "Renamed 1 item(s)" in summary
    assert "GitHub" in summary
    assert "GitHub Mirror" in summary


def test_original_tree_unchanged(sample_tree):
    original_titles = [c.title for c in sample_tree.children]
    rename_tree(sample_tree, "GitHub", "GitHub Mirror")
    assert [c.title for c in sample_tree.children] == original_titles
