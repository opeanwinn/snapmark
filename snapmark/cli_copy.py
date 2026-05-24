"""CLI subcommand: copy bookmarks into a destination folder."""

from __future__ import annotations

import argparse
import sys

from snapmark.bookmark_copy import copy_bookmarks
from snapmark.restore import export_to_json
from snapmark.snapshot import load_snapshot, save_snapshot


def cmd_copy(args: argparse.Namespace) -> None:
    try:
        root = load_snapshot(args.snapshot_dir, args.snapshot)
    except FileNotFoundError:
        print(f"Error: snapshot '{args.snapshot}' not found.", file=sys.stderr)
        sys.exit(1)

    if args.url_pattern is None and args.title_pattern is None:
        print(
            "Error: provide at least --url or --title to match bookmarks.",
            file=sys.stderr,
        )
        sys.exit(1)

    new_root, result = copy_bookmarks(
        root,
        destination=args.destination,
        url_pattern=args.url_pattern,
        title_pattern=args.title_pattern,
    )

    print(result.summary())

    if result.copy_count == 0:
        print("Nothing to save.")
        return

    output_name = args.output or args.snapshot
    if args.export:
        with open(args.export, "w", encoding="utf-8") as fh:
            fh.write(export_to_json(new_root))
        print(f"Exported to {args.export}")
    else:
        save_snapshot(args.snapshot_dir, output_name, new_root)
        print(f"Saved snapshot '{output_name}'.")


def add_copy_subparser(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    parser = subparsers.add_parser(
        "copy",
        help="Copy bookmarks matching a pattern into a destination folder.",
    )
    parser.add_argument("snapshot", help="Source snapshot name.")
    parser.add_argument("destination", help="Target folder title to copy into.")
    parser.add_argument("--url", dest="url_pattern", default=None, help="URL substring to match.")
    parser.add_argument("--title", dest="title_pattern", default=None, help="Title substring to match.")
    parser.add_argument("--output", default=None, help="Output snapshot name (default: overwrite source).")
    parser.add_argument("--export", default=None, help="Write result as JSON to this file path.")
    parser.add_argument(
        "--snapshot-dir",
        default=".snapmarks",
        help="Directory where snapshots are stored.",
    )
    parser.set_defaults(func=cmd_copy)
