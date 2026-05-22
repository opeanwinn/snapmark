"""CLI subcommand for validating a snapshot's bookmark tree."""
import argparse
import sys
from snapmark.snapshot import load_snapshot
from snapmark.validate import validate_tree


def cmd_validate(args: argparse.Namespace) -> None:
    """Load a snapshot and validate its bookmark tree."""
    try:
        root = load_snapshot(args.name, snapshot_dir=args.snapshot_dir)
    except FileNotFoundError:
        print(f"Error: snapshot '{args.name}' not found.", file=sys.stderr)
        sys.exit(1)

    result = validate_tree(root)
    print(result.summary())

    if not result.is_valid:
        sys.exit(2)


def add_validate_subparser(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser(
        "validate",
        help="Validate a bookmark snapshot for structural issues.",
    )
    parser.add_argument("name", help="Name of the snapshot to validate.")
    parser.add_argument(
        "--snapshot-dir",
        default=None,
        dest="snapshot_dir",
        help="Directory where snapshots are stored.",
    )
    parser.set_defaults(func=cmd_validate)
