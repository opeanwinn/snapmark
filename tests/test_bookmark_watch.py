import pytest
from snapmark.models import Bookmark, BookmarkFolder
from snapmark.bookmark_watch import watch_bookmarks, WatchResult


@pytest.fixture
def sample_tree() -> BookmarkFolder:
    return BookmarkFolder(
        name="root",
        children=[
            Bookmark(title="GitHub", url="https://github.com", tags=["dev"]),
            Bookmark(title="YouTube", url="https://youtube.com", tags=[]),
            BookmarkFolder(
                name="News",
                children=[
                    Bookmark(title="HN", url="https://news.ycombinator.com", tags=["tech"]),
                ],
            ),
        ],
    )


def test_watch_returns_folder_and_result(sample_tree):
    folder, result = watch_bookmarks(sample_tree)
    assert isinstance(folder, BookmarkFolder)
    assert isinstance(result, WatchResult)


def test_watch_all_bookmarks_no_pattern(sample_tree):
    _, result = watch_bookmarks(sample_tree, url_pattern=None)
    assert result.watched_count == 3


def test_watch_adds_watched_tag(sample_tree):
    folder, _ = watch_bookmarks(sample_tree, url_pattern=None)
    github = next(c for c in folder.children if isinstance(c, Bookmark) and c.title == "GitHub")
    assert "watched" in github.tags


def test_watch_preserves_existing_tags(sample_tree):
    folder, _ = watch_bookmarks(sample_tree, url_pattern=None)
    github = next(c for c in folder.children if isinstance(c, Bookmark) and c.title == "GitHub")
    assert "dev" in github.tags


def test_watch_with_url_pattern(sample_tree):
    _, result = watch_bookmarks(sample_tree, url_pattern="github")
    assert result.watched_count == 1
    assert result.watched[0].title == "GitHub"


def test_watch_nested_bookmark(sample_tree):
    folder, result = watch_bookmarks(sample_tree, url_pattern="ycombinator")
    assert result.watched_count == 1
    news = next(c for c in folder.children if isinstance(c, BookmarkFolder))
    hn = next(c for c in news.children if isinstance(c, Bookmark))
    assert "watched" in hn.tags


def test_unwatch_removes_watched_tag():
    tree = BookmarkFolder(
        name="root",
        children=[
            Bookmark(title="GitHub", url="https://github.com", tags=["watched", "dev"]),
        ],
    )
    folder, result = watch_bookmarks(tree, enable=False)
    bm = next(c for c in folder.children if isinstance(c, Bookmark))
    assert "watched" not in bm.tags
    assert result.unwatched_count == 1


def test_unwatch_preserves_other_tags():
    tree = BookmarkFolder(
        name="root",
        children=[
            Bookmark(title="GitHub", url="https://github.com", tags=["watched", "dev"]),
        ],
    )
    folder, _ = watch_bookmarks(tree, enable=False)
    bm = next(c for c in folder.children if isinstance(c, Bookmark))
    assert "dev" in bm.tags


def test_watch_does_not_duplicate_tag():
    tree = BookmarkFolder(
        name="root",
        children=[
            Bookmark(title="GitHub", url="https://github.com", tags=["watched"]),
        ],
    )
    folder, result = watch_bookmarks(tree)
    bm = next(c for c in folder.children if isinstance(c, Bookmark))
    assert bm.tags.count("watched") == 1
    assert result.watched_count == 1


def test_summary_string(sample_tree):
    _, result = watch_bookmarks(sample_tree)
    s = result.summary()
    assert "Watched" in s
    assert "3" in s
