"""CLI subcommand for annotating bookmarks with notes."""
import sys
import argparse
from snapmark.snapshot import load_snapshot, save_snapshot
from snapmark.annotate import annotate_tree


def cmd_annotate(args: argparse.Namespace) -> None:
    try:
        root = load_snapshot(args.snapshot_dir, args.name)
    except FileNotFoundError:
        print(f"Error: snapshot '{args.name}' not found.", file=sys.stderr)
        sys.exit(1)

    new_root, result = annotate_tree(
        root,
        note=args.note,
        url_filter=args.url_filter,
        overwrite=args.overwrite,
    )

    output_name = args.output if args.output else args.name
    save_snapshot(args.snapshot_dir, output_name, new_root)

    print(result.summary())
    if args.verbose and result.annotated:
        print("Annotated:")
        for b in result.annotated:
            print(f"  [{b.title}] {b.url}")


def add_annotate_subparser(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser("annotate", help="Annotate bookmarks with a note")
    p.add_argument("name", help="Snapshot name to annotate")
    p.add_argument("note", help="Note text to attach to matching bookmarks")
    p.add_argument(
        "--url-filter",
        dest="url_filter",
        default=None,
        help="Only annotate bookmarks whose URL contains this substring",
    )
    p.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing notes",
    )
    p.add_argument(
        "--output",
        default=None,
        help="Save result as a new snapshot name (default: overwrite input)",
    )
    p.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Print each annotated bookmark",
    )
    p.set_defaults(func=cmd_annotate)
