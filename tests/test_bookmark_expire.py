import pytest
from datetime import date, timedelta

from snapmark.models import Bookmark, BookmarkFolder
from snapmark.bookmark_expire import ExpireResult, expire_bookmarks


def _days_from_today(delta: int) -> str:
    return (date.today() + timedelta(days=delta)).isoformat()


@pytest.fixture
def sample_tree():
    return BookmarkFolder(
        title="Root",
        children=[
            Bookmark(
                title="Expired Link",
                url="https://expired.example.com",
                metadata={"expires": _days_from_today(-1)},
            ),
            Bookmark(
                title="Future Link",
                url="https://future.example.com",
                metadata={"expires": _days_from_today(10)},
            ),
            Bookmark(
                title="No Expiry",
                url="https://noexpiry.example.com",
            ),
            BookmarkFolder(
                title="Sub",
                children=[
                    Bookmark(
                        title="Nested Expired",
                        url="https://nested-expired.example.com",
                        metadata={"expires": _days_from_today(-5)},
                    ),
                    Bookmark(
                        title="Nested Valid",
                        url="https://nested-valid.example.com",
                        metadata={"expires": _days_from_today(3)},
                    ),
                ],
            ),
        ],
    )


def test_expire_returns_folder_and_result(sample_tree):
    folder, result = expire_bookmarks(sample_tree)
    assert isinstance(folder, BookmarkFolder)
    assert isinstance(result, ExpireResult)


def test_removes_expired_bookmarks(sample_tree):
    folder, result = expire_bookmarks(sample_tree)
    urls = [b.url for b in folder.children if isinstance(b, Bookmark)]
    assert "https://expired.example.com" not in urls


def test_keeps_future_bookmarks(sample_tree):
    folder, result = expire_bookmarks(sample_tree)
    urls = [b.url for b in folder.children if isinstance(b, Bookmark)]
    assert "https://future.example.com" in urls


def test_keeps_bookmarks_without_expiry(sample_tree):
    folder, result = expire_bookmarks(sample_tree)
    urls = [b.url for b in folder.children if isinstance(b, Bookmark)]
    assert "https://noexpiry.example.com" in urls


def test_expired_count_matches(sample_tree):
    _, result = expire_bookmarks(sample_tree)
    assert result.expired_count == 2


def test_kept_count_matches(sample_tree):
    _, result = expire_bookmarks(sample_tree)
    assert result.kept_count == 3


def test_nested_expired_removed(sample_tree):
    folder, _ = expire_bookmarks(sample_tree)
    sub = next(c for c in folder.children if isinstance(c, BookmarkFolder))
    urls = [b.url for b in sub.children]
    assert "https://nested-expired.example.com" not in urls
    assert "https://nested-valid.example.com" in urls


def test_summary_string(sample_tree):
    _, result = expire_bookmarks(sample_tree)
    summary = result.summary()
    assert "Expired" in summary
    assert "Kept" in summary


def test_custom_as_of_date():
    future_date = date.today() + timedelta(days=5)
    tree = BookmarkFolder(
        title="Root",
        children=[
            Bookmark(
                title="Will Expire Soon",
                url="https://soon.example.com",
                metadata={"expires": _days_from_today(3)},
            ),
        ],
    )
    _, result = expire_bookmarks(tree, as_of=future_date)
    assert result.expired_count == 1
