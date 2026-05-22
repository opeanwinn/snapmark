"""CLI subcommand for deduplicating bookmarks in a snapshot."""

import argparse
import sys

from snapmark.snapshot import load_snapshot, save_snapshot
from snapmark.dedupe import dedupe_tree


def cmd_dedupe(args: argparse.Namespace) -> None:
    try:
        root = load_snapshot(args.name, snapshot_dir=args.snapshot_dir)
    except FileNotFoundError:
        print(f"Snapshot '{args.name}' not found.", file=sys.stderr)
        sys.exit(1)

    deduped_root, result = dedupe_tree(root)

    print(result.summary())

    if result.duplicate_count == 0:
        return

    if args.verbose:
        for bm in result.removed:
            print(f"  - Removed duplicate: [{bm.title}] {bm.url}")

    if args.in_place:
        out_name = args.name
    elif args.output:
        out_name = args.output
    else:
        out_name = f"{args.name}-deduped"

    save_snapshot(deduped_root, out_name, snapshot_dir=args.snapshot_dir)
    print(f"Saved deduped snapshot as '{out_name}'.")


def add_dedupe_subparser(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser(
        "dedupe",
        help="Remove duplicate bookmarks (by URL) from a snapshot.",
    )
    parser.add_argument("name", help="Name of the snapshot to deduplicate.")
    parser.add_argument(
        "--in-place",
        action="store_true",
        default=False,
        help="Overwrite the original snapshot.",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Name for the output snapshot (default: <name>-deduped).",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        default=False,
        help="List removed duplicates.",
    )
    parser.set_defaults(func=cmd_dedupe)
