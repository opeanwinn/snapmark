import pytest
from snapmark.models import Bookmark, BookmarkFolder
from snapmark.bookmark_score import score_bookmarks, ScoreResult, _compute_score


@pytest.fixture
def sample_tree():
    return BookmarkFolder(
        name="root",
        children=[
            Bookmark(
                title="Python Docs",
                url="https://docs.python.org",
                metadata={"tags": ["python", "docs"], "note": "official docs"},
            ),
            Bookmark(
                title="Insecure Site",
                url="http://example.com",
                metadata={},
            ),
            BookmarkFolder(
                name="Work",
                children=[
                    Bookmark(
                        title="GitHub",
                        url="https://github.com",
                        metadata={"tags": ["dev"], "alias": "gh"},
                    ),
                ],
            ),
        ],
    )


def test_score_returns_folder_and_result(sample_tree):
    folder, result = score_bookmarks(sample_tree)
    assert isinstance(folder, BookmarkFolder)
    assert isinstance(result, ScoreResult)


def test_score_all_bookmarks_no_pattern(sample_tree):
    _, result = score_bookmarks(sample_tree)
    assert result.scored_count == 3


def test_scored_bookmark_has_score_in_metadata(sample_tree):
    folder, _ = score_bookmarks(sample_tree)
    python_docs = folder.children[0]
    assert isinstance(python_docs, Bookmark)
    assert "score" in python_docs.metadata
    assert isinstance(python_docs.metadata["score"], int)


def test_https_bookmark_scores_higher_than_http(sample_tree):
    folder, _ = score_bookmarks(sample_tree)
    https_score = folder.children[0].metadata["score"]
    http_score = folder.children[1].metadata["score"]
    assert https_score > http_score


def test_score_with_url_pattern_filters(sample_tree):
    _, result = score_bookmarks(sample_tree, url_pattern="github.com")
    assert result.scored_count == 1
    assert result.scored[0].url == "https://github.com"


def test_skips_already_scored_without_overwrite(sample_tree):
    tree_with_score = BookmarkFolder(
        name="root",
        children=[
            Bookmark(
                title="Already Scored",
                url="https://example.com",
                metadata={"score": 42},
            ),
        ],
    )
    _, result = score_bookmarks(tree_with_score, overwrite=False)
    assert result.skipped == 1
    assert result.scored_count == 0


def test_overwrite_rescores_existing(sample_tree):
    folder, _ = score_bookmarks(sample_tree)
    folder2, result2 = score_bookmarks(folder, overwrite=True)
    assert result2.scored_count == 3
    assert result2.skipped == 0


def test_score_nested_bookmark(sample_tree):
    folder, result = score_bookmarks(sample_tree)
    work_folder = folder.children[2]
    assert isinstance(work_folder, BookmarkFolder)
    github = work_folder.children[0]
    assert "score" in github.metadata


def test_compute_score_max_is_100():
    bm = Bookmark(
        title="Full Featured",
        url="https://example.com",
        metadata={
            "tags": ["a", "b", "c", "d"],
            "note": "some note",
            "alias": "fe",
        },
    )
    score = _compute_score(bm)
    assert 0 <= score <= 100


def test_summary_string(sample_tree):
    _, result = score_bookmarks(sample_tree)
    summary = result.summary()
    assert "Scored" in summary
    assert "skipped" in summary
