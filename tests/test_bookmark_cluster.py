"""Tests for snapmark.bookmark_cluster."""

import pytest
from snapmark.models import Bookmark, BookmarkFolder
from snapmark.bookmark_cluster import (
    ClusterResult,
    cluster_by_tag,
    cluster_by_domain,
)


@pytest.fixture
def sample_tree() -> BookmarkFolder:
    return BookmarkFolder(
        title="Root",
        children=[
            Bookmark(title="Python Docs", url="https://docs.python.org", tags=["python", "docs"]),
            Bookmark(title="PyPI", url="https://pypi.org/project/requests", tags=["python", "packages"]),
            Bookmark(title="MDN", url="https://developer.mozilla.org", tags=["web", "docs"]),
            Bookmark(title="GitHub", url="https://github.com", tags=[]),
            BookmarkFolder(
                title="Tools",
                children=[
                    Bookmark(title="Netlify", url="https://netlify.com", tags=["hosting"]),
                    Bookmark(title="Vercel", url="https://vercel.com", tags=["hosting"]),
                ],
            ),
        ],
    )


def test_cluster_returns_cluster_result(sample_tree):
    result = cluster_by_tag(sample_tree)
    assert isinstance(result, ClusterResult)


def test_cluster_by_tag_groups_correctly(sample_tree):
    result = cluster_by_tag(sample_tree)
    assert "docs" in result.clusters or "python" in result.clusters


def test_cluster_by_tag_unclustered_has_no_tags(sample_tree):
    result = cluster_by_tag(sample_tree)
    for bm in result.unclustered:
        assert not bm.tags


def test_cluster_by_tag_github_is_unclustered(sample_tree):
    result = cluster_by_tag(sample_tree)
    urls = [bm.url for bm in result.unclustered]
    assert "https://github.com" in urls


def test_cluster_by_domain_returns_cluster_result(sample_tree):
    result = cluster_by_domain(sample_tree)
    assert isinstance(result, ClusterResult)


def test_cluster_by_domain_groups_pypi(sample_tree):
    result = cluster_by_domain(sample_tree)
    assert "pypi.org" in result.clusters


def test_cluster_by_domain_strips_www(sample_tree):
    folder = BookmarkFolder(
        title="Root",
        children=[
            Bookmark(title="Google", url="https://www.google.com", tags=[]),
        ],
    )
    result = cluster_by_domain(folder)
    assert "google.com" in result.clusters


def test_cluster_count_matches_unique_keys(sample_tree):
    result = cluster_by_tag(sample_tree)
    assert result.cluster_count == len(result.clusters)


def test_total_clustered_sums_all_clusters(sample_tree):
    result = cluster_by_tag(sample_tree)
    expected = sum(len(v) for v in result.clusters.values())
    assert result.total_clustered == expected


def test_summary_contains_cluster_count(sample_tree):
    result = cluster_by_tag(sample_tree)
    summary = result.summary()
    assert "Clusters:" in summary
    assert "Clustered bookmarks:" in summary


def test_nested_bookmarks_included(sample_tree):
    result = cluster_by_tag(sample_tree)
    all_clustered = [bm for bms in result.clusters.values() for bm in bms]
    urls = [bm.url for bm in all_clustered] + [bm.url for bm in result.unclustered]
    assert "https://netlify.com" in urls
    assert "https://vercel.com" in urls
