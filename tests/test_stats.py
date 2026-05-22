"""Tests for snapmark.stats."""
from __future__ import annotations

import pytest

from snapmark.models import Bookmark, BookmarkFolder
from snapmark.stats import compute_stats, BookmarkStats


@pytest.fixture()
def sample_tree() -> BookmarkFolder:
    return BookmarkFolder(
        title="root",
        children=[
            BookmarkFolder(
                title="Dev",
                children=[
                    Bookmark(title="GitHub", url="https://github.com", tags=["dev", "git"]),
                    Bookmark(title="GitLab", url="https://gitlab.com", tags=["dev"]),
                    BookmarkFolder(
                        title="Python",
                        children=[
                            Bookmark(title="PyPI", url="https://pypi.org", tags=[]),
                        ],
                    ),
                ],
            ),
            BookmarkFolder(
                title="News",
                children=[
                    Bookmark(title="HN", url="https://news.ycombinator.com", tags=["news"]),
                    Bookmark(title="Lobsters", url="https://lobste.rs", tags=[]),
                ],
            ),
        ],
    )


def test_returns_bookmark_stats_instance(sample_tree):
    result = compute_stats(sample_tree)
    assert isinstance(result, BookmarkStats)


def test_total_bookmarks(sample_tree):
    stats = compute_stats(sample_tree)
    assert stats.total_bookmarks == 5


def test_total_folders(sample_tree):
    # Dev, Python, News — root itself is not counted
    stats = compute_stats(sample_tree)
    assert stats.total_folders == 3


def test_max_depth(sample_tree):
    # PyPI is at depth 2 inside Dev > Python
    stats = compute_stats(sample_tree)
    assert stats.max_depth == 2


def test_tagged_and_untagged(sample_tree):
    stats = compute_stats(sample_tree)
    assert stats.tagged_count == 3   # GitHub, GitLab, HN
    assert stats.untagged_count == 2  # PyPI, Lobsters


def test_top_domains(sample_tree):
    stats = compute_stats(sample_tree, top_n=3)
    domain_names = [d for d, _ in stats.top_domains]
    assert "github.com" in domain_names


def test_summary_contains_key_labels(sample_tree):
    stats = compute_stats(sample_tree)
    summary = stats.summary()
    assert "Bookmarks" in summary
    assert "Folders" in summary
    assert "Tagged" in summary


def test_empty_tree():
    root = BookmarkFolder(title="root", children=[])
    stats = compute_stats(root)
    assert stats.total_bookmarks == 0
    assert stats.total_folders == 0
    assert stats.max_depth == 0
    assert stats.avg_depth == 0.0
