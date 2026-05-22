"""CLI sub-command: stats — show statistics for a snapshot."""
from __future__ import annotations

import argparse
import sys

from snapmark.snapshot import load_snapshot
from snapmark.stats import compute_stats


def cmd_stats(args: argparse.Namespace) -> None:
    """Print statistics for a saved snapshot."""
    try:
        tree = load_snapshot(args.name, snapshot_dir=args.snapshot_dir)
    except FileNotFoundError:
        print(f"Error: snapshot '{args.name}' not found.", file=sys.stderr)
        sys.exit(1)

    top_n = getattr(args, "top", 5)
    stats = compute_stats(tree, top_n=top_n)
    print(f"Snapshot : {args.name}")
    print(stats.summary())


def add_stats_subparser(subparsers: argparse._SubParsersAction) -> None:  # noqa: SLF001
    parser = subparsers.add_parser(
        "stats",
        help="Show statistics for a snapshot",
    )
    parser.add_argument("name", help="Snapshot name")
    parser.add_argument(
        "--snapshot-dir",
        default=None,
        help="Directory where snapshots are stored",
    )
    parser.add_argument(
        "--top",
        type=int,
        default=5,
        metavar="N",
        help="Number of top domains to display (default: 5)",
    )
    parser.set_defaults(func=cmd_stats)
