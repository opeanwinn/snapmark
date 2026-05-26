"""Tests for snapmark.bookmark_batch module."""

import pytest
from snapmark.models import Bookmark, BookmarkFolder
from snapmark.bookmark_batch import BatchResult, batch_update


@pytest.fixture
def sample_tree():
    return BookmarkFolder(
        name="root",
        children=[
            Bookmark(title="GitHub", url="https://github.com", tags=["dev"]),
            Bookmark(title="PyPI", url="https://pypi.org", tags=[]),
            BookmarkFolder(
                name="News",
                children=[
                    Bookmark(title="HN", url="https://news.ycombinator.com", tags=[]),
                ],
            ),
        ],
    )


def test_batch_update_returns_folder_and_result(sample_tree):
    folder, result = batch_update(sample_tree)
    assert isinstance(folder, BookmarkFolder)
    assert isinstance(result, BatchResult)


def test_batch_adds_tag_to_all_bookmarks(sample_tree):
    _, result = batch_update(sample_tree, tag="reviewed")
    assert all("reviewed" in b.tags for b in result.updated)


def test_batch_updated_count_matches(sample_tree):
    _, result = batch_update(sample_tree, tag="bulk")
    assert result.updated_count == 3
    assert result.skipped_count == 0


def test_batch_preserves_existing_tags(sample_tree):
    _, result = batch_update(sample_tree, tag="new-tag")
    github = next(b for b in result.updated if b.title == "GitHub")
    assert "dev" in github.tags
    assert "new-tag" in github.tags


def test_batch_does_not_duplicate_tag(sample_tree):
    # GitHub already has 'dev'
    _, result = batch_update(sample_tree, tag="dev")
    github = next(b for b in result.updated if b.title == "GitHub")
    assert github.tags.count("dev") == 1


def test_batch_adds_note_to_all_bookmarks(sample_tree):
    _, result = batch_update(sample_tree, note="check later")
    assert all(b.metadata.get("note") == "check later" for b in result.updated)


def test_batch_adds_metadata_key(sample_tree):
    _, result = batch_update(sample_tree, metadata_key="source", metadata_value="import")
    assert all(b.metadata.get("source") == "import" for b in result.updated)


def test_batch_url_pattern_filters_bookmarks(sample_tree):
    _, result = batch_update(sample_tree, tag="python", url_pattern="pypi")
    assert result.updated_count == 1
    assert result.updated[0].title == "PyPI"
    assert result.skipped_count == 2


def test_batch_url_pattern_case_insensitive(sample_tree):
    _, result = batch_update(sample_tree, tag="code", url_pattern="GITHUB")
    assert result.updated_count == 1
    assert result.updated[0].title == "GitHub"


def test_batch_summary_string(sample_tree):
    _, result = batch_update(sample_tree, tag="done")
    summary = result.summary()
    assert "3 updated" in summary
    assert "0 skipped" in summary


def test_batch_no_args_marks_all_as_updated(sample_tree):
    _, result = batch_update(sample_tree)
    # No changes applied but bookmarks are still processed
    assert result.updated_count == 3
