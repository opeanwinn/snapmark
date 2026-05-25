import argparse
import sys
from snapmark.snapshot import load_snapshot, save_snapshot
from snapmark.bookmark_color import color_bookmarks, VALID_COLORS


def cmd_color(args: argparse.Namespace) -> None:
    try:
        root = load_snapshot(args.snapshot_dir, args.name)
    except FileNotFoundError:
        print(f"Error: snapshot '{args.name}' not found.", file=sys.stderr)
        sys.exit(1)

    try:
        new_root, result = color_bookmarks(
            root,
            color=args.color,
            url_pattern=args.url_pattern or None,
            overwrite=args.overwrite,
        )
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)

    output_name = args.output or args.name
    save_snapshot(args.snapshot_dir, output_name, new_root)

    print(result.summary())
    if args.verbose:
        for bm in result.colored:
            tags = ", ".join(bm.tags or [])
            print(f"  [colored] {bm.title} — {bm.url}  tags=[{tags}]")


def add_color_subparser(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser(
        "color",
        help="Assign a color label to bookmarks via tags.",
    )
    parser.add_argument("snapshot_dir", help="Directory containing snapshots.")
    parser.add_argument("name", help="Snapshot name to load.")
    parser.add_argument(
        "color",
        choices=sorted(VALID_COLORS),
        help="Color label to apply.",
    )
    parser.add_argument(
        "--url-pattern",
        default="",
        help="Only color bookmarks whose URL contains this string.",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Replace existing color tag if present.",
    )
    parser.add_argument(
        "--output",
        default="",
        help="Output snapshot name (defaults to overwriting input).",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="List each colored bookmark.",
    )
    parser.set_defaults(func=cmd_color)
