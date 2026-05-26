import pytest
from snapmark.models import Bookmark, BookmarkFolder
from snapmark.bookmark_category import (
    CategoryResult,
    categorize_tree,
    _infer_category,
)


@pytest.fixture
def sample_tree():
    return BookmarkFolder(
        name="root",
        children=[
            Bookmark(title="GitHub", url="https://github.com/user/repo", tags=[]),
            Bookmark(title="Twitter", url="https://twitter.com/user", tags=[]),
            Bookmark(title="YouTube", url="https://youtube.com/watch?v=abc", tags=[]),
            Bookmark(title="Unknown", url="https://somerandomblog.io/post", tags=[]),
            BookmarkFolder(
                name="Sub",
                children=[
                    Bookmark(title="Stack Overflow", url="https://stackoverflow.com/q/1", tags=[]),
                ],
            ),
        ],
    )


def test_categorize_returns_folder_and_result(sample_tree):
    folder, result = categorize_tree(sample_tree)
    assert isinstance(folder, BookmarkFolder)
    assert isinstance(result, CategoryResult)


def test_infer_category_github():
    assert _infer_category("https://github.com/foo") == "development"


def test_infer_category_twitter():
    assert _infer_category("https://twitter.com/foo") == "social"


def test_infer_category_youtube():
    assert _infer_category("https://youtube.com/watch") == "video"


def test_infer_category_unknown_returns_none():
    assert _infer_category("https://somerandomblog.io/post") is None


def test_categorized_count_matches_known_domains(sample_tree):
    _, result = categorize_tree(sample_tree)
    # github, twitter, youtube, stackoverflow = 4 known
    assert result.categorized_count == 4


def test_skipped_count_matches_unknown_domains(sample_tree):
    _, result = categorize_tree(sample_tree)
    assert result.skipped_count == 1


def test_category_stored_in_metadata(sample_tree):
    folder, _ = categorize_tree(sample_tree)
    github = next(c for c in folder.children if isinstance(c, Bookmark) and "github" in c.url)
    assert github.metadata.get("category") == "development"


def test_nested_bookmark_is_categorized(sample_tree):
    folder, result = categorize_tree(sample_tree)
    sub = next(c for c in folder.children if isinstance(c, BookmarkFolder))
    so = sub.children[0]
    assert isinstance(so, Bookmark)
    assert so.metadata.get("category") == "development"


def test_categories_assigned_dict_populated(sample_tree):
    _, result = categorize_tree(sample_tree)
    assert "development" in result.categories_assigned
    assert "social" in result.categories_assigned
    assert "video" in result.categories_assigned


def test_no_overwrite_skips_existing_category():
    tree = BookmarkFolder(
        name="root",
        children=[
            Bookmark(
                title="GitHub",
                url="https://github.com/foo",
                tags=[],
                metadata={"category": "custom"},
            )
        ],
    )
    folder, result = categorize_tree(tree, overwrite=False)
    bm = folder.children[0]
    assert bm.metadata["category"] == "custom"
    assert result.skipped_count == 1
    assert result.categorized_count == 0


def test_overwrite_replaces_existing_category():
    tree = BookmarkFolder(
        name="root",
        children=[
            Bookmark(
                title="GitHub",
                url="https://github.com/foo",
                tags=[],
                metadata={"category": "custom"},
            )
        ],
    )
    folder, result = categorize_tree(tree, overwrite=True)
    bm = folder.children[0]
    assert bm.metadata["category"] == "development"
    assert result.categorized_count == 1


def test_summary_contains_counts(sample_tree):
    _, result = categorize_tree(sample_tree)
    s = result.summary()
    assert "Categorized" in s
    assert "Skipped" in s
