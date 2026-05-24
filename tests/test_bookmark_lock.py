import pytest
from snapmark.models import Bookmark, BookmarkFolder
from snapmark.bookmark_lock import lock_bookmarks, unlock_bookmarks, LOCK_TAG


@pytest.fixture
def sample_tree():
    return BookmarkFolder(
        name="root",
        children=[
            Bookmark(title="Python", url="https://python.org", tags=["dev"]),
            Bookmark(title="GitHub", url="https://github.com", tags=[]),
            BookmarkFolder(
                name="Work",
                children=[
                    Bookmark(
                        title="Jira",
                        url="https://jira.example.com",
                        tags=["work"],
                    ),
                ],
            ),
        ],
    )


def test_lock_returns_folder_and_result(sample_tree):
    folder, result = lock_bookmarks(sample_tree)
    assert isinstance(folder, BookmarkFolder)
    from snapmark.bookmark_lock import LockResult
    assert isinstance(result, LockResult)


def test_lock_all_bookmarks(sample_tree):
    _, result = lock_bookmarks(sample_tree)
    assert result.locked_count == 3


def test_lock_adds_locked_tag(sample_tree):
    folder, _ = lock_bookmarks(sample_tree)
    python_bm = folder.children[0]
    assert LOCK_TAG in python_bm.tags


def test_lock_preserves_existing_tags(sample_tree):
    folder, _ = lock_bookmarks(sample_tree)
    python_bm = folder.children[0]
    assert "dev" in python_bm.tags


def test_lock_by_url_pattern(sample_tree):
    _, result = lock_bookmarks(sample_tree, url_pattern="github")
    assert result.locked_count == 1
    assert result.locked[0].title == "GitHub"


def test_lock_nested_bookmark(sample_tree):
    folder, result = lock_bookmarks(sample_tree)
    work_folder = folder.children[2]
    jira_bm = work_folder.children[0]
    assert LOCK_TAG in jira_bm.tags


def test_lock_does_not_duplicate_tag(sample_tree):
    folder, _ = lock_bookmarks(sample_tree)
    folder2, result2 = lock_bookmarks(folder)
    assert result2.locked_count == 0


def test_unlock_removes_locked_tag(sample_tree):
    locked_folder, _ = lock_bookmarks(sample_tree)
    unlocked_folder, result = unlock_bookmarks(locked_folder)
    python_bm = unlocked_folder.children[0]
    assert LOCK_TAG not in python_bm.tags
    assert result.unlocked_count == 3


def test_unlock_preserves_other_tags(sample_tree):
    locked_folder, _ = lock_bookmarks(sample_tree)
    unlocked_folder, _ = unlock_bookmarks(locked_folder)
    python_bm = unlocked_folder.children[0]
    assert "dev" in python_bm.tags


def test_summary_locked(sample_tree):
    _, result = lock_bookmarks(sample_tree)
    assert "Locked" in result.summary()
    assert "3" in result.summary()


def test_summary_no_changes(sample_tree):
    locked_folder, _ = lock_bookmarks(sample_tree)
    _, result = lock_bookmarks(locked_folder)
    assert result.summary() == "No bookmarks changed."
