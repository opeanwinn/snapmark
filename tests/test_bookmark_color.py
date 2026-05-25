import pytest
from snapmark.models import Bookmark, BookmarkFolder
from snapmark.bookmark_color import color_bookmarks, ColorResult, VALID_COLORS


@pytest.fixture
def sample_tree() -> BookmarkFolder:
    return BookmarkFolder(
        name="root",
        children=[
            Bookmark(title="GitHub", url="https://github.com", tags=["dev"]),
            Bookmark(title="PyPI", url="https://pypi.org", tags=["python", "color:blue"]),
            BookmarkFolder(
                name="News",
                children=[
                    Bookmark(title="HN", url="https://news.ycombinator.com", tags=[]),
                ],
            ),
        ],
    )


def test_color_returns_folder_and_result(sample_tree):
    folder, result = color_bookmarks(sample_tree, color="red")
    assert isinstance(folder, BookmarkFolder)
    assert isinstance(result, ColorResult)


def test_color_all_bookmarks_no_pattern(sample_tree):
    _, result = color_bookmarks(sample_tree, color="green")
    assert result.colored_count == 3


def test_color_tag_added(sample_tree):
    folder, _ = color_bookmarks(sample_tree, color="red")
    github = next(b for b in folder.children if isinstance(b, Bookmark) and b.title == "GitHub")
    assert "color:red" in github.tags


def test_color_preserves_existing_tags(sample_tree):
    folder, _ = color_bookmarks(sample_tree, color="red")
    github = next(b for b in folder.children if isinstance(b, Bookmark) and b.title == "GitHub")
    assert "dev" in github.tags


def test_color_skips_already_colored_without_overwrite(sample_tree):
    _, result = color_bookmarks(sample_tree, color="red", overwrite=False)
    # PyPI already has color:blue — should be skipped
    skipped_titles = [b.title for b in result.skipped]
    assert "PyPI" in skipped_titles


def test_color_overwrites_existing_color_when_flag_set(sample_tree):
    folder, result = color_bookmarks(sample_tree, color="red", overwrite=True)
    pypi = next(b for b in folder.children if isinstance(b, Bookmark) and b.title == "PyPI")
    assert "color:red" in pypi.tags
    assert "color:blue" not in pypi.tags


def test_color_with_url_pattern(sample_tree):
    _, result = color_bookmarks(sample_tree, color="blue", url_pattern="github")
    assert result.colored_count == 1
    assert result.colored[0].title == "GitHub"


def test_color_nested_bookmark(sample_tree):
    folder, result = color_bookmarks(sample_tree, color="yellow")
    news_folder = next(c for c in folder.children if isinstance(c, BookmarkFolder))
    hn = next(b for b in news_folder.children if isinstance(b, Bookmark))
    assert "color:yellow" in hn.tags


def test_invalid_color_raises_value_error(sample_tree):
    with pytest.raises(ValueError, match="Invalid color"):
        color_bookmarks(sample_tree, color="magenta")


def test_summary_string(sample_tree):
    _, result = color_bookmarks(sample_tree, color="green")
    summary = result.summary()
    assert "Colored" in summary
    assert "Skipped" in summary


def test_valid_colors_set_is_not_empty():
    assert len(VALID_COLORS) > 0
    assert "red" in VALID_COLORS
    assert "blue" in VALID_COLORS
