import pytest
from snapmark.models import Bookmark, BookmarkFolder
from snapmark.bookmark_merge_strategy import merge_with_strategy, StrategyMergeResult


@pytest.fixture
def base_tree():
    return BookmarkFolder(
        name="root",
        children=[
            Bookmark(title="Python", url="https://python.org", tags=["dev"]),
            Bookmark(title="GitHub", url="https://github.com", tags=[]),
            BookmarkFolder(
                name="Work",
                children=[
                    Bookmark(title="Jira", url="https://jira.example.com", tags=["work"]),
                ],
            ),
        ],
    )


@pytest.fixture
def incoming_tree():
    return BookmarkFolder(
        name="root",
        children=[
            Bookmark(title="Python Docs", url="https://python.org", tags=["dev", "docs"]),
            Bookmark(title="GitLab", url="https://gitlab.com", tags=[]),
            BookmarkFolder(
                name="Work",
                children=[
                    Bookmark(title="Jira", url="https://jira.example.com", tags=["work"]),
                    Bookmark(title="Confluence", url="https://confluence.example.com", tags=["work"]),
                ],
            ),
        ],
    )


def test_merge_returns_strategy_merge_result(base_tree, incoming_tree):
    result = merge_with_strategy(base_tree, incoming_tree)
    assert isinstance(result, StrategyMergeResult)


def test_merge_root_is_bookmark_folder(base_tree, incoming_tree):
    result = merge_with_strategy(base_tree, incoming_tree)
    assert isinstance(result.root, BookmarkFolder)


def test_keep_base_strategy_preserves_base_on_conflict(base_tree, incoming_tree):
    result = merge_with_strategy(base_tree, incoming_tree, strategy="keep_base")
    urls = {b.url: b for b in result.root.children if isinstance(b, Bookmark)}
    assert urls["https://python.org"].title == "Python"


def test_keep_incoming_strategy_uses_incoming_on_conflict(base_tree, incoming_tree):
    result = merge_with_strategy(base_tree, incoming_tree, strategy="keep_incoming")
    urls = {b.url: b for b in result.root.children if isinstance(b, Bookmark)}
    assert urls["https://python.org"].title == "Python Docs"


def test_keep_both_strategy_adds_duplicate(base_tree, incoming_tree):
    result = merge_with_strategy(base_tree, incoming_tree, strategy="keep_both")
    bm_urls = [b.url for b in result.root.children if isinstance(b, Bookmark)]
    assert "https://python.org#incoming" in bm_urls


def test_conflicts_are_reported(base_tree, incoming_tree):
    result = merge_with_strategy(base_tree, incoming_tree)
    assert "https://python.org" in result.conflicts


def test_new_incoming_bookmark_added(base_tree, incoming_tree):
    result = merge_with_strategy(base_tree, incoming_tree)
    bm_urls = [b.url for b in result.root.children if isinstance(b, Bookmark)]
    assert "https://gitlab.com" in bm_urls


def test_nested_folder_merged(base_tree, incoming_tree):
    result = merge_with_strategy(base_tree, incoming_tree)
    work_folder = next(
        (f for f in result.root.children if isinstance(f, BookmarkFolder) and f.name == "Work"),
        None,
    )
    assert work_folder is not None
    child_urls = [b.url for b in work_folder.children if isinstance(b, Bookmark)]
    assert "https://confluence.example.com" in child_urls


def test_summary_contains_merged_count(base_tree, incoming_tree):
    result = merge_with_strategy(base_tree, incoming_tree)
    summary = result.summary()
    assert "Merged:" in summary
    assert "Skipped:" in summary
