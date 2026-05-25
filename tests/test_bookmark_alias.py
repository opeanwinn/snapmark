import pytest
from snapmark.models import Bookmark, BookmarkFolder
from snapmark.bookmark_alias import set_alias, AliasResult


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
                    Bookmark(
                        title="Jira",
                        url="https://jira.example.com",
                        tags=["work"],
                        metadata={"alias": "existing-alias"},
                    ),
                ],
            ),
        ],
    )


def test_set_alias_returns_folder_and_result(sample_tree):
    folder, result = set_alias(sample_tree, alias="py")
    assert isinstance(folder, BookmarkFolder)
    assert isinstance(result, AliasResult)


def test_set_alias_all_bookmarks_no_pattern(sample_tree):
    _, result = set_alias(sample_tree, alias="test-alias")
    # 3 total bookmarks; Jira has existing alias so skipped without overwrite
    assert result.updated_count == 2
    assert result.skipped_count == 1


def test_set_alias_with_url_pattern(sample_tree):
    _, result = set_alias(sample_tree, alias="gh", url_pattern="github.com")
    assert result.updated_count == 1
    assert result.updated[0].title == "GitHub"


def test_alias_stored_in_metadata(sample_tree):
    folder, _ = set_alias(sample_tree, alias="docs", url_pattern="docs.python.org")
    bm = folder.children[0]
    assert isinstance(bm, Bookmark)
    assert bm.metadata.get("alias") == "docs"


def test_skips_existing_alias_without_overwrite(sample_tree):
    _, result = set_alias(sample_tree, alias="new-alias", url_pattern="jira")
    assert result.skipped_count == 1
    assert result.updated_count == 0


def test_overwrites_existing_alias_when_flag_set(sample_tree):
    folder, result = set_alias(
        sample_tree, alias="new-alias", url_pattern="jira", overwrite=True
    )
    assert result.updated_count == 1
    work_folder = folder.children[2]
    assert isinstance(work_folder, BookmarkFolder)
    jira = work_folder.children[0]
    assert jira.metadata.get("alias") == "new-alias"


def test_summary_string(sample_tree):
    _, result = set_alias(sample_tree, alias="x")
    summary = result.summary()
    assert "updated" in summary
    assert "skipped" in summary


def test_original_tags_preserved(sample_tree):
    folder, _ = set_alias(sample_tree, alias="py", url_pattern="docs.python.org")
    bm = folder.children[0]
    assert "python" in bm.tags


def test_nested_bookmark_aliased(sample_tree):
    folder, result = set_alias(
        sample_tree, alias="work-tool", url_pattern="jira", overwrite=True
    )
    work = folder.children[2]
    assert isinstance(work, BookmarkFolder)
    assert work.children[0].metadata.get("alias") == "work-tool"
