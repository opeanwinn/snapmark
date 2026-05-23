"""CLI subcommand for bookmark-count analysis."""

from __future__ import annotations

import argparse
import sys

from snapmark.bookmark_count import count_bookmarks
from snapmark.restore import restore_snapshot


def cmd_count(args: argparse.Namespace) -> None:
    """Handle the `snapmark count` subcommand."""
    try:
        root = restore_snapshot(args.snapshot, snapshot_dir=args.snapshot_dir)
    except FileNotFoundError:
        print(f"Error: snapshot '{args.snapshot}' not found.", file=sys.stderr)
        sys.exit(1)

    result = count_bookmarks(root)

    if args.domain:
        print("Bookmarks by domain:")
        for domain, count in sorted(result.by_domain.items(), key=lambda x: -x[1]):
            print(f"  {domain}: {count}")
        return

    if args.tag:
        print("Bookmarks by tag:")
        for tag, count in sorted(result.by_tag.items()):
            print(f"  #{tag}: {count}")
        return

    if args.depth:
        print("Bookmarks by folder depth:")
        for depth, count in sorted(result.by_depth.items()):
            print(f"  depth {depth}: {count}")
        return

    print(result.summary())


def add_count_subparser(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    parser = subparsers.add_parser(
        "count",
        help="Count bookmarks by domain, tag, or depth.",
    )
    parser.add_argument("snapshot", help="Name of the snapshot to analyse.")
    parser.add_argument(
        "--snapshot-dir",
        default=None,
        help="Directory where snapshots are stored.",
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--domain",
        action="store_true",
        help="Show counts grouped by domain only.",
    )
    group.add_argument(
        "--tag",
        action="store_true",
        help="Show counts grouped by tag only.",
    )
    group.add_argument(
        "--depth",
        action="store_true",
        help="Show counts grouped by folder depth only.",
    )
    parser.set_defaults(func=cmd_count)
