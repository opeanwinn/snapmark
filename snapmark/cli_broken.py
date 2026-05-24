"""CLI sub-command: broken — report broken/suspicious bookmarks."""
from __future__ import annotations

import argparse
import sys

from snapmark.bookmark_broken import find_broken
from snapmark.restore import restore_snapshot


def cmd_broken(args: argparse.Namespace) -> None:
    try:
        root = restore_snapshot(args.snapshot_dir, args.name)
    except Exception as exc:  # noqa: BLE001
        print(f"Error loading snapshot: {exc}", file=sys.stderr)
        sys.exit(1)

    result = find_broken(root)

    print(result.summary())

    if result.broken and args.verbose:
        print("\n--- Broken ---")
        for bm in result.broken:
            print(f"  [{bm.title}] url={bm.url!r}")

    if result.suspicious and args.verbose:
        print("\n--- Suspicious ---")
        for bm in result.suspicious:
            print(f"  [{bm.title}] url={bm.url!r}")

    if args.fail_on_broken and result.broken_count > 0:
        sys.exit(2)


def add_broken_subparser(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p = subparsers.add_parser(
        "broken",
        help="Find bookmarks with broken or suspicious URLs.",
    )
    p.add_argument("name", help="Snapshot name to inspect.")
    p.add_argument(
        "--snapshot-dir",
        default=".snapmarks",
        help="Directory where snapshots are stored (default: .snapmarks).",
    )
    p.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Print each broken/suspicious bookmark.",
    )
    p.add_argument(
        "--fail-on-broken",
        action="store_true",
        help="Exit with code 2 if any broken bookmarks are found.",
    )
    p.set_defaults(func=cmd_broken)
