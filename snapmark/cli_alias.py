import argparse
import sys
from snapmark.snapshot import load_snapshot, save_snapshot
from snapmark.bookmark_alias import set_alias


def cmd_alias(args: argparse.Namespace) -> None:
    try:
        root = load_snapshot(args.snapshot_dir, args.name)
    except FileNotFoundError:
        print(f"Error: snapshot '{args.name}' not found.", file=sys.stderr)
        sys.exit(1)

    new_root, result = set_alias(
        root,
        alias=args.alias,
        url_pattern=args.url_pattern or None,
        overwrite=args.overwrite,
    )

    print(result.summary())

    if args.verbose:
        for bm in result.updated:
            print(f"  [aliased] {bm.title} -> alias='{bm.metadata.get('alias')}'")

    output_name = args.output or args.name
    save_snapshot(args.snapshot_dir, output_name, new_root)
    print(f"Saved as '{output_name}'.")


def add_alias_subparser(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser(
        "alias",
        help="Attach a short alias to bookmarks via metadata.",
    )
    parser.add_argument("name", help="Snapshot name to load.")
    parser.add_argument("alias", help="Alias string to assign.")
    parser.add_argument(
        "--url-pattern",
        dest="url_pattern",
        default="",
        help="Only alias bookmarks whose URL contains this substring.",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing alias if already set.",
    )
    parser.add_argument(
        "--output",
        default="",
        help="Output snapshot name (defaults to overwriting input).",
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Print each aliased bookmark.",
    )
    parser.set_defaults(func=cmd_alias)
