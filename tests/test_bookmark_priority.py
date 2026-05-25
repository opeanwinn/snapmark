import pytest
from snapmark.models import Bookmark, BookmarkFolder
from snapmark.bookmark_priority import set_priority, PriorityResult


@pytest.fixture
def sample_tree():
    return BookmarkFolder(
        name="root",
        children=[
            Bookmark(title="Python Docs", url="https://docs.python.org", tags=["python"]),
            Bookmark(title="GitHub", url="https://github.com", tags=[]),
            BookmarkFolder(
                name="Work",
                children=[
                    Bookmark(title="Jira", url="https://jira.example.com", tags=["work"]),
                    Bookmark(
                        title="Confluence",
                        url="https://confluence.example.com",
                        tags=["priority:3"],
                    ),
                ],
            ),
        ],
    )


def test_set_priority_returns_folder_and_result(sample_tree):
    folder, result = set_priority(sample_tree, level=2)
    assert isinstance(folder, BookmarkFolder)
    assert isinstance(result, PriorityResult)


def test_set_priority_all_bookmarks(sample_tree):
    _, result = set_priority(sample_tree, level=1)
    assert result.updated_count == 3  # Confluence skipped (has priority, no overwrite)
    assert result.skipped_count == 1


def test_priority_tag_added(sample_tree):
    folder, _ = set_priority(sample_tree, level=2)
    python_docs = folder.children[0]
    assert "priority:2" in python_docs.tags


def test_priority_preserves_existing_tags(sample_tree):
    folder, _ = set_priority(sample_tree, level=3)
    python_docs = folder.children[0]
    assert "python" in python_docs.tags
    assert "priority:3" in python_docs.tags


def test_priority_with_url_pattern(sample_tree):
    _, result = set_priority(sample_tree, level=5, url_pattern="github")
    assert result.updated_count == 1
    assert result.updated[0].title == "GitHub"


def test_priority_skips_existing_without_overwrite(sample_tree):
    _, result = set_priority(sample_tree, level=1, overwrite=False)
    skipped_titles = [b.title for b in result.skipped]
    assert "Confluence" in skipped_titles


def test_priority_overwrite_replaces_existing(sample_tree):
    folder, result = set_priority(sample_tree, level=1, overwrite=True)
    work_folder = folder.children[2]
    confluence = work_folder.children[1]
    assert "priority:1" in confluence.tags
    assert "priority:3" not in confluence.tags


def test_invalid_priority_level_raises(sample_tree):
    with pytest.raises(ValueError, match="between 1 and 5"):
        set_priority(sample_tree, level=0)
    with pytest.raises(ValueError, match="between 1 and 5"):
        set_priority(sample_tree, level=6)


def test_summary_message(sample_tree):
    _, result = set_priority(sample_tree, level=2)
    summary = result.summary()
    assert "updated" in summary.lower()
    assert "skipped" in summary.lower()


def test_nested_bookmark_priority(sample_tree):
    folder, result = set_priority(sample_tree, level=4, url_pattern="jira")
    work_folder = folder.children[2]
    jira = work_folder.children[0]
    assert "priority:4" in jira.tags
    assert result.updated_count == 1
