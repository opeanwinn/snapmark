"""Tests for snapmark.bookmark_template."""
import pytest
from snapmark.models import Bookmark, BookmarkFolder
from snapmark.bookmark_template import apply_template, TemplateResult


@pytest.fixture
def sample_tree() -> BookmarkFolder:
    return BookmarkFolder(
        name="root",
        children=[
            Bookmark(title="Python Docs", url="https://docs.python.org/3/", tags=["python"]),
            Bookmark(title="GitHub", url="http://github.com/user/repo", tags=[]),
            BookmarkFolder(
                name="Work",
                children=[
                    Bookmark(title="Jira Board", url="https://company.atlassian.net/jira", tags=[]),
                    Bookmark(title="Old Site", url="http://old.example.com/page", tags=[]),
                ],
            ),
        ],
    )


def test_apply_template_returns_folder_and_result(sample_tree):
    folder, result = apply_template(sample_tree, url_pattern=r"^http://", url_template="https://")
    assert isinstance(folder, BookmarkFolder)
    assert isinstance(result, TemplateResult)


def test_upgrades_http_to_https(sample_tree):
    folder, result = apply_template(sample_tree, url_pattern=r"^http://", url_template="https://")
    urls = [c.url for c in folder.children if isinstance(c, Bookmark)]
    assert all(u.startswith("https://") for u in urls)


def test_updated_count_matches_changed_bookmarks(sample_tree):
    _, result = apply_template(sample_tree, url_pattern=r"^http://", url_template="https://")
    # top-level: GitHub (http) => 1; nested Work folder has Old Site (http) => 1
    assert result.updated_count == 2


def test_skipped_count_matches_unchanged_bookmarks(sample_tree):
    _, result = apply_template(sample_tree, url_pattern=r"^http://", url_template="https://")
    # Python Docs already https => 1; Jira already https => 1
    assert result.skipped_count == 2


def test_no_recursive_only_processes_top_level(sample_tree):
    _, result = apply_template(
        sample_tree,
        url_pattern=r"^http://",
        url_template="https://",
        recursive=False,
    )
    # Only top-level GitHub matches; Old Site is nested and skipped entirely
    assert result.updated_count == 1


def test_title_pattern_renames_matching_titles(sample_tree):
    folder, result = apply_template(
        sample_tree,
        title_pattern=r"Old Site",
        title_template="Legacy Site",
    )
    work = next(c for c in folder.children if isinstance(c, BookmarkFolder))
    titles = [c.title for c in work.children if isinstance(c, Bookmark)]
    assert "Legacy Site" in titles
    assert "Old Site" not in titles


def test_url_and_title_pattern_combined(sample_tree):
    _, result = apply_template(
        sample_tree,
        url_pattern=r"^http://",
        url_template="https://",
        title_pattern=r"Old",
        title_template="New",
    )
    assert result.updated_count >= 2


def test_summary_string_contains_counts(sample_tree):
    _, result = apply_template(sample_tree, url_pattern=r"^http://", url_template="https://")
    summary = result.summary()
    assert str(result.updated_count) in summary
    assert str(result.skipped_count) in summary


def test_no_match_returns_all_skipped(sample_tree):
    _, result = apply_template(sample_tree, url_pattern=r"ftp://", url_template="https://")
    assert result.updated_count == 0
    assert result.skipped_count == 4


def test_original_tree_is_not_mutated(sample_tree):
    original_url = sample_tree.children[1].url  # GitHub http
    apply_template(sample_tree, url_pattern=r"^http://", url_template="https://")
    assert sample_tree.children[1].url == original_url
