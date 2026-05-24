import pytest
from datetime import date, timedelta
from snapmark.models import Bookmark, BookmarkFolder
from snapmark.bookmark_reminder import set_reminders, ReminderResult, _reminder_tag


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
                    ),
                    Bookmark(
                        title="Already Reminded",
                        url="https://reminded.example.com",
                        tags=["remind:2099-01-01"],
                    ),
                ],
            ),
        ],
    )


def test_set_reminders_returns_folder_and_result(sample_tree):
    folder, result = set_reminders(sample_tree)
    assert isinstance(folder, BookmarkFolder)
    assert isinstance(result, ReminderResult)


def test_reminder_tag_format_is_correct():
    tag = _reminder_tag(7)
    expected = f"remind:{(date.today() + timedelta(days=7)).isoformat()}"
    assert tag == expected


def test_all_bookmarks_get_reminder_by_default(sample_tree):
    folder, result = set_reminders(sample_tree, days=3)
    # 3 bookmarks without reminder + 1 skipped (already has remind:)
    assert result.scheduled_count == 3


def test_already_reminded_bookmark_is_skipped(sample_tree):
    _, result = set_reminders(sample_tree)
    skipped_urls = [b.url for b in result.skipped]
    assert "https://reminded.example.com" in skipped_urls


def test_overwrite_replaces_existing_reminder(sample_tree):
    folder, result = set_reminders(sample_tree, overwrite=True)
    assert result.scheduled_count == 4
    assert result.skipped_count == 0


def test_url_pattern_filters_bookmarks(sample_tree):
    _, result = set_reminders(sample_tree, url_pattern="github")
    assert result.scheduled_count == 1
    assert result.scheduled[0].url == "https://github.com"


def test_scheduled_bookmark_has_remind_tag(sample_tree):
    folder, _ = set_reminders(sample_tree, days=5)
    expected_tag = _reminder_tag(5)
    python_bm = folder.children[0]
    assert isinstance(python_bm, Bookmark)
    assert expected_tag in python_bm.tags


def test_nested_bookmark_receives_reminder(sample_tree):
    folder, result = set_reminders(sample_tree, url_pattern="jira")
    assert result.scheduled_count == 1
    assert result.scheduled[0].title == "Jira"


def test_summary_string_contains_counts(sample_tree):
    _, result = set_reminders(sample_tree)
    summary = result.summary()
    assert "3" in summary or str(result.scheduled_count) in summary


def test_existing_tags_are_preserved(sample_tree):
    folder, _ = set_reminders(sample_tree, url_pattern="python")
    python_bm = folder.children[0]
    assert isinstance(python_bm, Bookmark)
    assert "python" in python_bm.tags
