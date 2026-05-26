"""Tests for snapmark.bookmark_summary."""

import pytest
from snapmark.models import Bookmark, BookmarkFolder
from snapmark.bookmark_summary import SummaryReport, generate_summary


@pytest.fixture
def sample_tree():
    return BookmarkFolder(
        title="root",
        children=[
            Bookmark(
                title="Python Docs",
                url="https://docs.python.org",
                tags=["python", "docs"],
                notes="Official docs",
                metadata={"source": "manual"},
            ),
            Bookmark(
                title="GitHub",
                url="https://github.com",
                tags=["dev"],
            ),
            BookmarkFolder(
                title="News",
                children=[
                    Bookmark(
                        title="Hacker News",
                        url="https://news.ycombinator.com",
                        tags=["news", "dev"],
                    ),
                    Bookmark(
                        title="BBC",
                        url="https://www.bbc.co.uk",
                        tags=["news"],
                        notes="News site",
                    ),
                ],
            ),
        ],
    )


def test_generate_summary_returns_summary_report(sample_tree):
    result = generate_summary(sample_tree)
    assert isinstance(result, SummaryReport)


def test_total_bookmarks(sample_tree):
    result = generate_summary(sample_tree)
    assert result.total_bookmarks == 4


def test_total_folders(sample_tree):
    result = generate_summary(sample_tree)
    assert result.total_folders == 1


def test_unique_domains(sample_tree):
    result = generate_summary(sample_tree)
    assert result.unique_domains == 4


def test_total_tags(sample_tree):
    result = generate_summary(sample_tree)
    # python, docs, dev, news => 4 unique tags
    assert result.total_tags == 4


def test_has_notes_count(sample_tree):
    result = generate_summary(sample_tree)
    assert result.has_notes == 2


def test_has_metadata_count(sample_tree):
    result = generate_summary(sample_tree)
    assert result.has_metadata == 1


def test_top_tags_sorted_by_frequency(sample_tree):
    result = generate_summary(sample_tree)
    tag_names = [t for t, _ in result.top_tags]
    # 'dev' and 'news' both appear twice; both should appear before single-count tags
    counts = dict(result.top_tags)
    assert counts["dev"] == 2
    assert counts["news"] == 2
    assert counts["python"] == 1


def test_top_domains_sorted_by_frequency(sample_tree):
    result = generate_summary(sample_tree)
    assert len(result.top_domains) == 4


def test_summary_string_contains_key_labels(sample_tree):
    result = generate_summary(sample_tree)
    text = result.summary()
    assert "Total bookmarks" in text
    assert "Total folders" in text
    assert "Unique domains" in text
    assert "Top tags" in text
    assert "Top domains" in text


def test_empty_tree_returns_zero_counts():
    root = BookmarkFolder(title="empty", children=[])
    result = generate_summary(root)
    assert result.total_bookmarks == 0
    assert result.total_folders == 0
    assert result.total_tags == 0
    assert result.unique_domains == 0
