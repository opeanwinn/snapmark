"""Tests for snapmark.bookmark_status."""
import pytest

from snapmark.models import Bookmark, BookmarkFolder
from snapmark.bookmark_status import StatusResult, set_status


@pytest.fixture
def sample_tree() -> BookmarkFolder:
    return BookmarkFolder(
        name="root",
        children=[
            Bookmark(title="Python Docs", url="https://docs.python.org", tags=["python"]),
            Bookmark(title="GitHub", url="https://github.com", tags=[]),
            BookmarkFolder(
                name="Work",
                children=[
                    Bookmark(title="Jira", url="https://jira.example.com", tags=["work"]),
                    Bookmark(title="Already Read", url="https://read.example.com", tags=["read"]),
                ],
            ),
        ],
    )


def test_set_status_returns_folder_and_result(sample_tree):
    folder, result = set_status(sample_tree, status="read")
    assert isinstance(folder, BookmarkFolder)
    assert isinstance(result, StatusResult)


def test_mark_all_as_read(sample_tree):
    folder, result = set_status(sample_tree, status="read")
    # 3 without a read tag should be updated; 1 already has read and is skipped
    assert result.updated_count == 3
    assert result.skipped_count == 1


def test_mark_all_as_unread(sample_tree):
    folder, result = set_status(sample_tree, status="unread")
    # All 4 bookmarks lack 'unread'; the one with 'read' gets 'read' stripped
    assert result.updated_count == 4


def test_read_tag_added_to_bookmark(sample_tree):
    folder, _ = set_status(sample_tree, status="read")
    python_docs = folder.children[0]
    assert "read" in python_docs.tags


def test_unread_tag_replaces_read_tag(sample_tree):
    folder, _ = set_status(sample_tree, status="unread")
    work_folder = folder.children[2]
    already_read = work_folder.children[1]
    assert "unread" in already_read.tags
    assert "read" not in already_read.tags


def test_url_pattern_filters_bookmarks(sample_tree):
    folder, result = set_status(sample_tree, status="read", url_pattern="github")
    assert result.updated_count == 1
    assert result.updated[0].title == "GitHub"


def test_overwrite_false_skips_already_tagged(sample_tree):
    folder, result = set_status(sample_tree, status="read", overwrite=False)
    already_read_titles = [b.title for b in result.skipped]
    assert "Already Read" in already_read_titles


def test_overwrite_true_updates_already_tagged(sample_tree):
    folder, result = set_status(sample_tree, status="read", overwrite=True)
    skipped_titles = [b.title for b in result.skipped]
    assert "Already Read" not in skipped_titles


def test_preserves_existing_tags(sample_tree):
    folder, _ = set_status(sample_tree, status="read")
    python_docs = folder.children[0]
    assert "python" in python_docs.tags
    assert "read" in python_docs.tags


def test_invalid_status_raises_value_error(sample_tree):
    with pytest.raises(ValueError, match="status must be"):
        set_status(sample_tree, status="maybe")


def test_summary_string(sample_tree):
    _, result = set_status(sample_tree, status="read")
    summary = result.summary()
    assert "updated" in summary
    assert "skipped" in summary
