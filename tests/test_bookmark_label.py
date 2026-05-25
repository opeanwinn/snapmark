import pytest
from snapmark.models import Bookmark, BookmarkFolder
from snapmark.bookmark_label import label_bookmarks, LabelResult


@pytest.fixture
def sample_tree():
    return BookmarkFolder(
        title="Root",
        children=[
            Bookmark(title="GitHub", url="https://github.com", tags=[]),
            Bookmark(title="Python Docs", url="https://docs.python.org", tags=["python"]),
            BookmarkFolder(
                title="Work",
                children=[
                    Bookmark(title="Jira", url="https://jira.example.com", tags=[]),
                ],
            ),
        ],
    )


def test_label_returns_folder_and_result(sample_tree):
    folder, result = label_bookmarks(sample_tree, labels=["important"])
    assert isinstance(folder, BookmarkFolder)
    assert isinstance(result, LabelResult)


def test_label_all_bookmarks_no_pattern(sample_tree):
    _, result = label_bookmarks(sample_tree, labels=["work", "review"])
    assert result.labeled_count == 3
    assert result.skipped_count == 0


def test_labeled_bookmark_has_labels_in_metadata(sample_tree):
    folder, _ = label_bookmarks(sample_tree, labels=["important"])
    github = folder.children[0]
    assert isinstance(github, Bookmark)
    assert github.metadata["labels"] == ["important"]


def test_label_with_url_pattern_filters(sample_tree):
    _, result = label_bookmarks(sample_tree, labels=["dev"], url_pattern="github")
    assert result.labeled_count == 1
    assert result.skipped_count == 2


def test_label_nested_bookmark(sample_tree):
    folder, result = label_bookmarks(sample_tree, labels=["tool"], url_pattern="jira")
    work_folder = folder.children[2]
    assert isinstance(work_folder, BookmarkFolder)
    jira = work_folder.children[0]
    assert jira.metadata["labels"] == ["tool"]
    assert result.labeled_count == 1


def test_label_skips_already_labeled_without_overwrite(sample_tree):
    tree, _ = label_bookmarks(sample_tree, labels=["first"])
    _, result = label_bookmarks(tree, labels=["second"], overwrite=False)
    assert result.skipped_count == 3
    assert result.labeled_count == 0


def test_label_overwrites_existing_labels(sample_tree):
    tree, _ = label_bookmarks(sample_tree, labels=["old"])
    updated_tree, result = label_bookmarks(tree, labels=["new"], overwrite=True)
    assert result.labeled_count == 3
    github = updated_tree.children[0]
    assert github.metadata["labels"] == ["new"]


def test_summary_contains_counts(sample_tree):
    _, result = label_bookmarks(sample_tree, labels=["x"])
    summary = result.summary()
    assert "3" in summary
    assert "x" in summary


def test_original_tree_not_mutated(sample_tree):
    original_meta = dict(sample_tree.children[0].metadata)
    label_bookmarks(sample_tree, labels=["test"])
    assert sample_tree.children[0].metadata == original_meta
