"""CLI subcommand: snapdiff — compare two snapshots."""

import argparse
import sys

from snapmark.bookmark_snapshot_diff import compare_snapshots


def cmd_snapdiff(args: argparse.Namespace) -> None:
    try:
        result = compare_snapshots(
            args.snapshot_a,
            args.snapshot_b,
            snapshot_dir=args.snapshot_dir,
        )
    except FileNotFoundError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)

    print(result.summary())

    if args.verbose and result.has_changes():
        diff = result.diff
        if diff.added:
            print("\nAdded:")
            for b in diff.added:
                print(f"  + [{b.title}] {b.url}")
        if diff.removed:
            print("\nRemoved:")
            for b in diff.removed:
                print(f"  - [{b.title}] {b.url}")
        if diff.modified:
            print("\nModified:")
            for b in diff.modified:
                print(f"  ~ [{b.title}] {b.url}")

    if not result.has_changes():
        print("No differences found.")


def add_snapdiff_subparser(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser(
        "snapdiff",
        help="Compare two snapshots and show bookmark differences.",
    )
    parser.add_argument("snapshot_a", help="Name of the base snapshot.")
    parser.add_argument("snapshot_b", help="Name of the snapshot to compare against.")
    parser.add_argument(
        "--snapshot-dir",
        default=".snapmarks",
        help="Directory where snapshots are stored.",
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="List individual added/removed/modified bookmarks.",
    )
    parser.set_defaults(func=cmd_snapdiff)
