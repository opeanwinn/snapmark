import pytest
from snapmark.models import Bookmark, BookmarkFolder
from snapmark.bookmark_readtime import estimate_readtime, ReadTimeResult


@pytest.fixture
def sample_tree():
    return BookmarkFolder(
        name="root",
        children=[
            Bookmark(title="Python Docs", url="https://docs.python.org", tags=["python"]),
            Bookmark(title="GitHub", url="https://github.com", tags=[]),
            BookmarkFolder(
                name="News",
                children=[
                    Bookmark(
                        title="Hacker News",
                        url="https://news.ycombinator.com",
                        tags=[],
                    ),
                    Bookmark(
                        title="Already Timed",
                        url="https://example.com",
                        tags=[],
                        metadata={"readtime": "3 min"},
                    ),
                ],
            ),
        ],
    )


def test_estimate_readtime_returns_folder_and_result(sample_tree):
    folder, result = estimate_readtime(sample_tree)
    assert isinstance(folder, BookmarkFolder)
    assert isinstance(result, ReadTimeResult)


def test_all_bookmarks_get_readtime_by_default(sample_tree):
    folder, result = estimate_readtime(sample_tree)
    # 3 without existing readtime should be updated; 1 already has readtime => skipped
    assert result.updated_count == 3
    assert result.skipped_count == 1


def test_readtime_stored_in_metadata(sample_tree):
    folder, result = estimate_readtime(sample_tree)
    for bm in result.updated:
        assert "readtime" in bm.metadata
        assert bm.metadata["readtime"].endswith("min")


def test_readtime_value_is_positive(sample_tree):
    folder, result = estimate_readtime(sample_tree)
    for bm in result.updated:
        minutes = int(bm.metadata["readtime"].split()[0])
        assert minutes >= 1


def test_skips_existing_readtime_without_overwrite(sample_tree):
    folder, result = estimate_readtime(sample_tree, overwrite=False)
    skipped_urls = [b.url for b in result.skipped]
    assert "https://example.com" in skipped_urls


def test_overwrite_replaces_existing_readtime(sample_tree):
    folder, result = estimate_readtime(sample_tree, overwrite=True)
    assert result.updated_count == 4
    assert result.skipped_count == 0


def test_url_pattern_filters_bookmarks(sample_tree):
    folder, result = estimate_readtime(sample_tree, url_pattern="github")
    assert result.updated_count == 1
    assert result.updated[0].url == "https://github.com"


def test_summary_string(sample_tree):
    _, result = estimate_readtime(sample_tree)
    s = result.summary()
    assert "updated" in s
    assert "skipped" in s


def test_nested_bookmarks_are_processed(sample_tree):
    folder, result = estimate_readtime(sample_tree)
    news_folder = next(c for c in folder.children if isinstance(c, BookmarkFolder))
    hn = next(b for b in news_folder.children if b.title == "Hacker News")
    assert "readtime" in hn.metadata
