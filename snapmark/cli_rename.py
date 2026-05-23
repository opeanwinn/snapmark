"""CLI subcommand for renaming bookmarks or folders."""

import argparse
import sys

from snapmark.snapshot import load_snapshot, save_snapshot
from snapmark.rename import rename_tree


def cmd_rename(args: argparse.Namespace) -> None:
    try:
        root = load_snapshot(args.snapshot_dir, args.name)
    except FileNotFoundError:
        print(f"Error: snapshot '{args.name}' not found.", file=sys.stderr)
        sys.exit(1)

    updated, result = rename_tree(root, args.old_title, args.new_title)

    if result.renamed_count == 0:
        print(f"No items with title '{args.old_title}' found. Nothing changed.")
        return

    if args.in_place:
        save_snapshot(args.snapshot_dir, args.name, updated)
        print(f"Snapshot '{args.name}' updated.")
    else:
        out_name = args.output or f"{args.name}_renamed"
        save_snapshot(args.snapshot_dir, out_name, updated)
        print(f"Renamed snapshot saved as '{out_name}'.")

    print(result.summary())


def add_rename_subparser(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser(
        "rename", help="Rename bookmarks or folders in a snapshot"
    )
    parser.add_argument("name", help="Snapshot name to operate on")
    parser.add_argument("old_title", help="Current title to search for")
    parser.add_argument("new_title", help="New title to apply")
    parser.add_argument(
        "--in-place",
        action="store_true",
        default=False,
        help="Overwrite the existing snapshot instead of creating a new one",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Name for the output snapshot (default: <name>_renamed)",
    )
    parser.set_defaults(func=cmd_rename)
