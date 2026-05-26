import pytest
from snapmark.models import BookmarkFolder, Bookmark
from snapmark.bookmark_reorder import reorder_tree, ReorderResult


@pytest.fixture
def sample_tree():
    return BookmarkFolder(
        title="Root",
        children=[
            Bookmark(title="Alpha", url="https://alpha.com"),
            Bookmark(title="Beta", url="https://beta.com"),
            Bookmark(title="Gamma", url="https://gamma.com"),
            BookmarkFolder(
                title="Sub",
                children=[
                    Bookmark(title="Delta", url="https://delta.com"),
                    Bookmark(title="Epsilon", url="https://epsilon.com"),
                ],
            ),
        ],
    )


def test_reorder_returns_folder_and_result(sample_tree):
    folder, result = reorder_tree(sample_tree, ["https://gamma.com"])
    assert isinstance(folder, BookmarkFolder)
    assert isinstance(result, ReorderResult)


def test_reorder_moves_url_to_front(sample_tree):
    folder, result = reorder_tree(
        sample_tree, ["https://gamma.com", "https://alpha.com"], recursive=False
    )
    bookmarks = [c for c in folder.children if isinstance(c, Bookmark)]
    assert bookmarks[0].url == "https://gamma.com"
    assert bookmarks[1].url == "https://alpha.com"
    assert bookmarks[2].url == "https://beta.com"


def test_moved_count_matches_found_urls(sample_tree):
    _, result = reorder_tree(
        sample_tree,
        ["https://gamma.com", "https://beta.com"],
        recursive=False,
    )
    assert result.moved_count == 2


def test_empty_url_order_returns_unchanged_tree(sample_tree):
    folder, result = reorder_tree(sample_tree, [])
    titles = [c.title for c in folder.children]
    original_titles = [c.title for c in sample_tree.children]
    assert titles == original_titles
    assert result.moved_count == 0
    assert len(result.messages) > 0


def test_unknown_urls_do_not_raise(sample_tree):
    folder, result = reorder_tree(sample_tree, ["https://unknown.com"])
    assert result.moved_count == 0


def test_reorder_recursive_applies_to_subfolders(sample_tree):
    folder, result = reorder_tree(
        sample_tree,
        ["https://epsilon.com", "https://delta.com"],
        recursive=True,
    )
    sub = next(c for c in folder.children if isinstance(c, BookmarkFolder))
    assert sub.children[0].url == "https://epsilon.com"
    assert sub.children[1].url == "https://delta.com"
    assert result.moved_count == 2


def test_reorder_non_recursive_leaves_subfolders_unchanged(sample_tree):
    folder, _ = reorder_tree(
        sample_tree,
        ["https://epsilon.com"],
        recursive=False,
    )
    sub = next(c for c in folder.children if isinstance(c, BookmarkFolder))
    assert sub.children[0].url == "https://delta.com"
    assert sub.children[1].url == "https://epsilon.com"


def test_summary_string_is_human_readable(sample_tree):
    _, result = reorder_tree(sample_tree, ["https://alpha.com"])
    summary = result.summary()
    assert "1" in summary
    assert "bookmark" in summary
