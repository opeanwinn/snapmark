"""Tests for snapmark.bookmark_visibility."""

import pytest

from snapmark.models import Bookmark, BookmarkFolder
from snapmark.bookmark_visibility import VisibilityResult, set_visibility


@pytest.fixture
def sample_tree() -> BookmarkFolder:
    return BookmarkFolder(
        name="root",
        children=[
            Bookmark(title="GitHub", url="https://github.com", tags=[]),
            Bookmark(title="Python Docs", url="https://docs.python.org", tags=["python"]),
            Bookmark(title="Hidden Already", url="https://example.com", tags=["hidden"]),
            BookmarkFolder(
                name="Work",
                children=[
                    Bookmark(title="Jira", url="https://jira.example.com", tags=[]),
                ],
            ),
        ],
    )


def test_hide_returns_folder_and_result(sample_tree):
    folder, result = set_visibility(sample_tree, action="hide")
    assert isinstance(folder, BookmarkFolder)
    assert isinstance(result, VisibilityResult)


def test_hide_all_bookmarks_no_pattern(sample_tree):
    _, result = set_visibility(sample_tree, action="hide")
    # "Hidden Already" already has the tag, so only 3 new ones get hidden
    assert result.hidden_count == 3


def test_hide_adds_hidden_tag(sample_tree):
    folder, _ = set_visibility(sample_tree, action="hide")
    github = next(c for c in folder.children if isinstance(c, Bookmark) and c.title == "GitHub")
    assert "hidden" in github.tags


def test_hide_preserves_existing_tags(sample_tree):
    folder, _ = set_visibility(sample_tree, action="hide")
    python_bm = next(
        c for c in folder.children if isinstance(c, Bookmark) and c.title == "Python Docs"
    )
    assert "python" in python_bm.tags
    assert "hidden" in python_bm.tags


def test_hide_does_not_duplicate_hidden_tag(sample_tree):
    folder, result = set_visibility(sample_tree, action="hide")
    already_hidden = next(
        c for c in folder.children if isinstance(c, Bookmark) and c.title == "Hidden Already"
    )
    assert already_hidden.tags.count("hidden") == 1
    # It was already hidden, so not counted
    assert all(b.title != "Hidden Already" for b in result.affected)


def test_hide_by_url_pattern(sample_tree):
    _, result = set_visibility(sample_tree, action="hide", url_pattern="github")
    assert result.hidden_count == 1
    assert result.affected[0].title == "GitHub"


def test_hide_by_title_pattern(sample_tree):
    _, result = set_visibility(sample_tree, action="hide", title_pattern="python")
    assert result.hidden_count == 1
    assert result.affected[0].title == "Python Docs"


def test_show_removes_hidden_tag(sample_tree):
    folder, result = set_visibility(sample_tree, action="show")
    assert result.shown_count == 1
    restored = next(
        c for c in folder.children if isinstance(c, Bookmark) and c.title == "Hidden Already"
    )
    assert "hidden" not in restored.tags


def test_hide_nested_bookmark(sample_tree):
    folder, result = set_visibility(sample_tree, action="hide", url_pattern="jira")
    work_folder = next(c for c in folder.children if isinstance(c, BookmarkFolder))
    jira = work_folder.children[0]
    assert "hidden" in jira.tags
    assert result.hidden_count == 1


def test_invalid_action_raises(sample_tree):
    with pytest.raises(ValueError, match="action must be"):
        set_visibility(sample_tree, action="toggle")


def test_summary_hide(sample_tree):
    _, result = set_visibility(sample_tree, action="hide", url_pattern="github")
    assert "Hidden 1" in result.summary()


def test_summary_show(sample_tree):
    _, result = set_visibility(sample_tree, action="show")
    assert "Restored visibility" in result.summary()


def test_summary_no_changes():
    result = VisibilityResult()
    assert result.summary() == "No bookmarks were changed."
