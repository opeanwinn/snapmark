import argparse
import sys
from snapmark.snapshot import load_snapshot, save_snapshot
from snapmark.bookmark_category import categorize_tree


def cmd_category(args: argparse.Namespace) -> None:
    try:
        root = load_snapshot(args.snapshot_dir, args.name)
    except FileNotFoundError:
        print(f"Error: snapshot '{args.name}' not found.", file=sys.stderr)
        sys.exit(1)

    new_root, result = categorize_tree(root, overwrite=args.overwrite)

    print(result.summary())

    output_name = args.output or args.name
    save_snapshot(args.snapshot_dir, output_name, new_root)
    print(f"\nSaved categorized snapshot as '{output_name}'.")


def add_category_subparser(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser(
        "category",
        help="Auto-categorize bookmarks based on their URL domain.",
    )
    parser.add_argument("snapshot_dir", help="Path to the snapshots directory.")
    parser.add_argument("name", help="Name of the snapshot to process.")
    parser.add_argument(
        "--output",
        default=None,
        help="Output snapshot name (defaults to overwriting the input).",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing category metadata if present.",
    )
    parser.set_defaults(func=cmd_category)
