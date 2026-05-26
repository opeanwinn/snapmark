import argparse
import sys
from snapmark.snapshot import load_snapshot, save_snapshot
from snapmark.bookmark_merge_strategy import merge_with_strategy


def cmd_merge_strategy(args: argparse.Namespace) -> None:
    try:
        base = load_snapshot(args.snapshot_dir, args.base)
    except FileNotFoundError:
        print(f"Error: base snapshot '{args.base}' not found.", file=sys.stderr)
        sys.exit(1)

    try:
        incoming = load_snapshot(args.snapshot_dir, args.incoming)
    except FileNotFoundError:
        print(f"Error: incoming snapshot '{args.incoming}' not found.", file=sys.stderr)
        sys.exit(1)

    strategy = args.strategy
    if strategy not in ("keep_base", "keep_incoming", "keep_both"):
        print(f"Error: unknown strategy '{strategy}'.", file=sys.stderr)
        sys.exit(1)

    result = merge_with_strategy(base, incoming, strategy)
    print(result.summary())

    output_name = args.output or f"{args.base}_merged"
    save_snapshot(args.snapshot_dir, output_name, result.root)
    print(f"\nSaved merged snapshot as '{output_name}'.")


def add_merge_strategy_subparser(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser(
        "merge-strategy",
        help="Merge two snapshots using a conflict resolution strategy",
    )
    p.add_argument("base", help="Name of the base snapshot")
    p.add_argument("incoming", help="Name of the incoming snapshot")
    p.add_argument(
        "--strategy",
        choices=["keep_base", "keep_incoming", "keep_both"],
        default="keep_base",
        help="Conflict resolution strategy (default: keep_base)",
    )
    p.add_argument(
        "--output",
        default=None,
        help="Name for the output snapshot (default: <base>_merged)",
    )
    p.add_argument(
        "--snapshot-dir",
        default="snapshots",
        dest="snapshot_dir",
        help="Directory where snapshots are stored",
    )
    p.set_defaults(func=cmd_merge_strategy)
