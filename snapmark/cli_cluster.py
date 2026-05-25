"""CLI subcommand for clustering bookmarks."""

import argparse
import sys
from snapmark.snapshot import load_snapshot
from snapmark.bookmark_cluster import cluster_by_tag, cluster_by_domain


def cmd_cluster(args: argparse.Namespace) -> None:
    try:
        tree = load_snapshot(args.snapshot_dir, args.name)
    except FileNotFoundError:
        print(f"Snapshot '{args.name}' not found.", file=sys.stderr)
        sys.exit(1)

    mode = getattr(args, "mode", "tag")

    if mode == "domain":
        result = cluster_by_domain(tree)
    else:
        result = cluster_by_tag(tree)

    print(result.summary())

    if args.verbose:
        for cluster_name, bookmarks in sorted(result.clusters.items()):
            print(f"\n=== {cluster_name} ===")
            for bm in bookmarks:
                print(f"  {bm.title} — {bm.url}")
        if result.unclustered:
            print("\n=== (unclustered) ===")
            for bm in result.unclustered:
                print(f"  {bm.title} — {bm.url}")


def add_cluster_subparser(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser(
        "cluster",
        help="Cluster bookmarks by tag or domain",
    )
    parser.add_argument("name", help="Snapshot name to load")
    parser.add_argument(
        "--mode",
        choices=["tag", "domain"],
        default="tag",
        help="Clustering strategy (default: tag)",
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="List bookmarks in each cluster",
    )
    parser.set_defaults(func=cmd_cluster)
