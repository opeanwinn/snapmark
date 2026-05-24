import pytest
from snapmark.models import BookmarkFolder, Bookmark
from snapmark.bookmark_favorite import (
    favorite_bookmarks,
    unfavorite_bookmarks,
    FavoriteResult,
    FAVORITE_TAG,
)


@pytest.fixture
def sample_tree():
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
                        tags=["reading"],
                    ),
                ],
            ),
        ],
    )


def test_favorite_returns_folder_and_result(sample_tree):
    folder, result = favorite_bookmarks(sample_tree, ["https://python.org"])
    assert isinstance(folder, BookmarkFolder)
    assert isinstance(result, FavoriteResult)


def test_favorite_adds_favorite_tag(sample_tree):
    folder, result = favorite_bookmarks(sample_tree, ["https://python.org"])
    python = next(c for c in folder.children if isinstance(c, Bookmark) and c.url == "https://python.org")
    assert FAVORITE_TAG in python.tags


def test_favorite_preserves_existing_tags(sample_tree):
    folder, result = favorite_bookmarks(sample_tree, ["https://python.org"])
    python = next(c for c in folder.children if isinstance(c, Bookmark) and c.url == "https://python.org")
    assert "dev" in python.tags


def test_favorite_result_count(sample_tree):
    _, result = favorite_bookmarks(
        sample_tree,
        ["https://python.org", "https://github.com"],
    )
    assert result.favorite_count == 2


def test_favorite_nested_bookmark(sample_tree):
    folder, result = favorite_bookmarks(
        sample_tree, ["https://news.ycombinator.com"]
    )
    news_folder = next(c for c in folder.children if isinstance(c, BookmarkFolder))
    hn = news_folder.children[0]
    assert FAVORITE_TAG in hn.tags
    assert result.favorite_count == 1


def test_favorite_does_not_duplicate_tag(sample_tree):
    # Add favorite tag first
    folder, _ = favorite_bookmarks(sample_tree, ["https://python.org"])
    # Favorite again
    folder2, result2 = favorite_bookmarks(folder, ["https://python.org"])
    python = next(c for c in folder2.children if isinstance(c, Bookmark) and c.url == "https://python.org")
    assert python.tags.count(FAVORITE_TAG) == 1
    assert result2.favorite_count == 0


def test_unfavorite_removes_tag(sample_tree):
    folder, _ = favorite_bookmarks(sample_tree, ["https://github.com"])
    folder2, result = unfavorite_bookmarks(folder, ["https://github.com"])
    github = next(c for c in folder2.children if isinstance(c, Bookmark) and c.url == "https://github.com")
    assert FAVORITE_TAG not in github.tags
    assert result.unfavorite_count == 1


def test_unfavorite_noop_if_not_favorited(sample_tree):
    _, result = unfavorite_bookmarks(sample_tree, ["https://python.org"])
    assert result.unfavorite_count == 0


def test_summary_string(sample_tree):
    _, result = favorite_bookmarks(
        sample_tree, ["https://python.org", "https://github.com"]
    )
    summary = result.summary()
    assert "2" in summary
    assert "Favorited" in summary
