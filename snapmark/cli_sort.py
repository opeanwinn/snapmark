"""CLI subcommand for sorting bookmark snapshots."""
from __future__ import annotations

import argparse
import sys

from snapmark.snapshot import load_snapshot, save_snapshot
from snapmark.sort import sort_tree


def cmd_sort(args: argparse.Namespace) -> None:
    """Sort a snapshot and either overwrite it or save as a new snapshot."""
    try:
        root = load_snapshot(args.snapshot_dir, args.name)
    except FileNotFoundError:
        print(f"Error: snapshot '{args.name}' not found.", file=sys.stderr)
        sys.exit(1)

    sorted_root, result = sort_tree(
        root,
        key=args.key,
        reverse=args.reverse,
    )

    output_name = args.output if args.output else args.name
    save_snapshot(args.snapshot_dir, output_name, sorted_root)

    print(result.summary())
    if args.output:
        print(f"Saved sorted snapshot as '{output_name}'.")
    else:
        print(f"Snapshot '{output_name}' updated in place.")


def add_sort_subparser(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    parser = subparsers.add_parser(
        "sort",
        help="Sort bookmarks in a snapshot alphabetically.",
    )
    parser.add_argument("name", help="Name of the snapshot to sort.")
    parser.add_argument(
        "--key",
        choices=["title", "url"],
        default="title",
        help="Field to sort by (default: title).",
    )
    parser.add_argument(
        "--reverse",
        action="store_true",
        default=False,
        help="Sort in descending order.",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Save sorted result as a new snapshot name instead of overwriting.",
    )
    parser.set_defaults(func=cmd_sort)
