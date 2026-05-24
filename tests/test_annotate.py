"""Tests for snapmark.annotate."""
import pytest
from snapmark.models import Bookmark, BookmarkFolder
from snapmark.annotate import annotate_tree, AnnotateResult


@pytest.fixture
def sample_tree() -> BookmarkFolder:
    return BookmarkFolder(
        name="Root",
        children=[
            Bookmark(title="Python", url="https://python.org", tags=["dev"]),
            Bookmark(title="GitHub", url="https://github.com", tags=[]),
            BookmarkFolder(
                name="News",
                children=[
                    Bookmark(title="HN", url="https://news.ycombinator.com", tags=[]),
                ],
            ),
        ],
    )


def test_annotate_returns_folder_and_result(sample_tree):
    folder, result = annotate_tree(sample_tree, note="interesting")
    assert isinstance(folder, BookmarkFolder)
    assert isinstance(result, AnnotateResult)


def test_annotate_all_bookmarks(sample_tree):
    _, result = annotate_tree(sample_tree, note="to read")
    assert len(result.annotated) == 3
    assert len(result.skipped) == 0


def test_annotated_bookmark_has_note(sample_tree):
    folder, _ = annotate_tree(sample_tree, note="my note")
    python_bm = folder.children[0]
    assert isinstance(python_bm, Bookmark)
    assert python_bm.metadata["note"] == "my note"


def test_annotate_with_url_filter(sample_tree):
    _, result = annotate_tree(sample_tree, note="code", url_filter="github")
    assert len(result.annotated) == 1
    assert result.annotated[0].title == "GitHub"


def test_annotate_nested_bookmark(sample_tree):
    folder, result = annotate_tree(sample_tree, note="news site", url_filter="ycombinator")
    assert len(result.annotated) == 1
    news_folder = folder.children[2]
    assert isinstance(news_folder, BookmarkFolder)
    assert news_folder.children[0].metadata["note"] == "news site"


def test_skip_existing_note_without_overwrite():
    tree = BookmarkFolder(
        name="Root",
        children=[
            Bookmark(title="A", url="https://a.com", metadata={"note": "old note"}),
        ],
    )
    _, result = annotate_tree(tree, note="new note", overwrite=False)
    assert len(result.skipped) == 1
    assert len(result.annotated) == 0


def test_overwrite_existing_note():
    tree = BookmarkFolder(
        name="Root",
        children=[
            Bookmark(title="A", url="https://a.com", metadata={"note": "old note"}),
        ],
    )
    folder, result = annotate_tree(tree, note="new note", overwrite=True)
    assert len(result.annotated) == 1
    assert folder.children[0].metadata["note"] == "new note"


def test_summary_string(sample_tree):
    _, result = annotate_tree(sample_tree, note="test")
    summary = result.summary()
    assert "Annotated" in summary
    assert "3" in summary
