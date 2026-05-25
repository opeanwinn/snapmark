import pytest
from snapmark.models import Bookmark, BookmarkFolder
from snapmark.bookmark_comment import comment_tree, CommentResult


@pytest.fixture
def sample_tree() -> BookmarkFolder:
    return BookmarkFolder(
        name="root",
        children=[
            Bookmark(title="Python", url="https://python.org", tags=["dev"]),
            Bookmark(title="GitHub", url="https://github.com", tags=[]),
            BookmarkFolder(
                name="News",
                children=[
                    Bookmark(
                        title="HN",
                        url="https://news.ycombinator.com",
                        tags=[],
                        metadata={"comment": "existing comment"},
                    ),
                ],
            ),
        ],
    )


def test_comment_returns_folder_and_result(sample_tree):
    folder, result = comment_tree(sample_tree, comment="great site")
    assert isinstance(folder, BookmarkFolder)
    assert isinstance(result, CommentResult)


def test_comment_all_bookmarks_no_pattern(sample_tree):
    _, result = comment_tree(sample_tree, comment="nice")
    # Python and GitHub get commented; HN is skipped (already has comment)
    assert result.updated_count == 2
    assert result.skipped_count == 1


def test_commented_bookmark_has_comment(sample_tree):
    folder, _ = comment_tree(sample_tree, comment="my note")
    python_bm = folder.children[0]
    assert isinstance(python_bm, Bookmark)
    assert python_bm.metadata["comment"] == "my note"


def test_comment_with_url_pattern_filters(sample_tree):
    _, result = comment_tree(sample_tree, comment="dev", url_pattern="python.org")
    assert result.updated_count == 1
    assert result.updated[0].title == "Python"


def test_skip_existing_comment_without_overwrite(sample_tree):
    folder, result = comment_tree(sample_tree, comment="new comment")
    hn_bm = folder.children[2].children[0]
    assert hn_bm.metadata["comment"] == "existing comment"
    assert result.skipped_count == 1


def test_overwrite_replaces_existing_comment(sample_tree):
    folder, result = comment_tree(sample_tree, comment="replaced", overwrite=True)
    hn_bm = folder.children[2].children[0]
    assert hn_bm.metadata["comment"] == "replaced"
    assert result.updated_count == 3
    assert result.skipped_count == 0


def test_summary_string(sample_tree):
    _, result = comment_tree(sample_tree, comment="test")
    summary = result.summary()
    assert "Commented" in summary
    assert "skipped" in summary


def test_original_tree_not_mutated(sample_tree):
    original_title = sample_tree.children[0].title
    comment_tree(sample_tree, comment="mutate check")
    assert sample_tree.children[0].title == original_title
    assert sample_tree.children[0].metadata.get("comment") is None
