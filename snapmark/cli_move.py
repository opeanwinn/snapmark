"""CLI subcommand for moving bookmarks between folders."""

import argparse
import sys

from snapmark.snapshot import load_snapshot, save_snapshot
from snapmark.bookmark_move import move_bookmarks


def cmd_move(args: argparse.Namespace) -> None:
    try:
        root = load_snapshot(args.snapshot_dir, args.snapshot)
    except FileNotFoundError:
        print(f"Error: snapshot '{args.snapshot}' not found.", file=sys.stderr)
        sys.exit(1)

    urls = args.urls
    destination = args.destination

    updated_root, result = move_bookmarks(root, urls, destination)

    if result.errors:
        for err in result.errors:
            print(f"Error: {err}", file=sys.stderr)
        sys.exit(1)

    if result.not_found:
        for url in result.not_found:
            print(f"Warning: bookmark not found — {url}")

    output_name = args.output or args.snapshot
    save_snapshot(args.snapshot_dir, output_name, updated_root)
    print(result.summary())
    print(f"Saved to snapshot '{output_name}'.")


def add_move_subparser(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser(
        "move",
        help="Move bookmarks by URL into a destination folder.",
    )
    parser.add_argument("snapshot", help="Name of the snapshot to operate on.")
    parser.add_argument(
        "destination", help="Name of the destination folder."
    )
    parser.add_argument(
        "urls", nargs="+", help="One or more bookmark URLs to move."
    )
    parser.add_argument(
        "--snapshot-dir",
        default=".snapmarks",
        help="Directory where snapshots are stored.",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Output snapshot name (defaults to overwriting the input snapshot).",
    )
    parser.set_defaults(func=cmd_move)
