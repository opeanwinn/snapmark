import pytest
from snapmark.models import Bookmark, BookmarkFolder
from snapmark.bookmark_notes import add_notes, NotesResult


@pytest.fixture
def sample_tree() -> BookmarkFolder:
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
                        notes="existing note",
                    ),
                ],
            ),
        ],
    )


def test_add_notes_returns_folder_and_result(sample_tree):
    folder, result = add_notes(sample_tree, note="interesting")
    assert isinstance(folder, BookmarkFolder)
    assert isinstance(result, NotesResult)


def test_add_notes_to_all_bookmarks(sample_tree):
    folder, result = add_notes(sample_tree, note="my note", overwrite=True)
    assert result.updated_count == 3
    assert result.skipped_count == 0


def test_notes_attached_to_bookmarks(sample_tree):
    folder, result = add_notes(sample_tree, note="hello")
    python_bm = folder.children[0]
    assert isinstance(python_bm, Bookmark)
    assert python_bm.notes == "hello"


def test_skips_existing_note_without_overwrite(sample_tree):
    folder, result = add_notes(sample_tree, note="new note", overwrite=False)
    # Jira already has a note — should be skipped
    assert result.skipped_count == 1
    assert result.skipped[0].title == "Jira"


def test_overwrites_existing_note_when_flag_set(sample_tree):
    folder, result = add_notes(sample_tree, note="new note", overwrite=True)
    work_folder = folder.children[2]
    jira = work_folder.children[0]
    assert jira.notes == "new note"
    assert result.skipped_count == 0


def test_url_pattern_filters_bookmarks(sample_tree):
    folder, result = add_notes(
        sample_tree, note="python site", url_pattern="python.org"
    )
    assert result.updated_count == 1
    assert result.updated[0].title == "Python"


def test_unmatched_url_pattern_updates_nothing(sample_tree):
    folder, result = add_notes(
        sample_tree, note="nope", url_pattern="notarealsite.xyz"
    )
    assert result.updated_count == 0


def test_summary_string(sample_tree):
    _, result = add_notes(sample_tree, note="test")
    summary = result.summary()
    assert "updated" in summary
    assert "skipped" in summary


def test_original_tree_not_mutated(sample_tree):
    original_note = sample_tree.children[0].notes  # type: ignore[union-attr]
    add_notes(sample_tree, note="mutate check")
    assert sample_tree.children[0].notes == original_note  # type: ignore[union-attr]
