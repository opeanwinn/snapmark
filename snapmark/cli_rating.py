"""CLI sub-commands for bookmark rating."""

from __future__ import annotations

import argparse
import sys

from snapmark.snapshot import load_snapshot, save_snapshot
from snapmark.bookmark_rating import rate_bookmarks


def cmd_rate(args: argparse.Namespace) -> None:
    try:
        tree = load_snapshot(args.snapshot_dir, args.name)
    except FileNotFoundError:
        print(f"Snapshot '{args.name}' not found.", file=sys.stderr)
        sys.exit(1)

    try:
        new_tree, result = rate_bookmarks(
            tree,
            rating=args.rating,
            url_pattern=args.url or None,
            overwrite=not args.no_overwrite,
        )
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(1)

    out_name = args.output or args.name
    save_snapshot(args.snapshot_dir, out_name, new_tree)
    print(result.summary())
    if args.verbose:
        for bm in result.rated:
            print(f"  ★{args.rating}  {bm.title}  <{bm.url}>")


def add_rating_subparser(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p = subparsers.add_parser("rate", help="Assign a star rating to bookmarks.")
    p.add_argument("name", help="Snapshot name to operate on.")
    p.add_argument(
        "rating", type=int, choices=range(1, 6), metavar="RATING",
        help="Star rating 1–5.",
    )
    p.add_argument("--url", default="", help="Only rate bookmarks whose URL contains this string.")
    p.add_argument("--output", default="", help="Save result as a new snapshot name.")
    p.add_argument(
        "--no-overwrite", action="store_true",
        help="Skip bookmarks that already have a rating tag.",
    )
    p.add_argument("-v", "--verbose", action="store_true", help="List rated bookmarks.")
    p.add_argument("--snapshot-dir", default="snapshots", help="Snapshot directory.")
    p.set_defaults(func=cmd_rate)
