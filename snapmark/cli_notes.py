import argparse
import sys
from snapmark.snapshot import load_snapshot, save_snapshot
from snapmark.bookmark_notes import add_notes


def cmd_notes(args: argparse.Namespace) -> None:
    try:
        root = load_snapshot(args.snapshot_dir, args.name)
    except FileNotFoundError:
        print(f"Snapshot '{args.name}' not found.", file=sys.stderr)
        sys.exit(1)

    new_root, result = add_notes(
        root,
        note=args.note,
        url_pattern=args.url_pattern or None,
        overwrite=args.overwrite,
    )

    output_name = args.output or args.name
    save_snapshot(args.snapshot_dir, output_name, new_root)

    print(result.summary())
    if args.verbose:
        for bm in result.updated:
            print(f"  [updated] {bm.title} — {bm.url}")
        for bm in result.skipped:
            print(f"  [skipped] {bm.title} — {bm.url}")


def add_notes_subparser(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser(
        "notes", help="Attach notes to bookmarks in a snapshot"
    )
    p.add_argument("name", help="Snapshot name to load")
    p.add_argument("note", help="Note text to attach")
    p.add_argument(
        "--url-pattern",
        default="",
        help="Only annotate bookmarks whose URL contains this string",
    )
    p.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing notes (default: skip)",
    )
    p.add_argument(
        "--output",
        default="",
        help="Output snapshot name (default: overwrite input)",
    )
    p.add_argument(
        "--verbose", "-v", action="store_true", help="List affected bookmarks"
    )
    p.add_argument(
        "--snapshot-dir",
        default="snapshots",
        help="Directory where snapshots are stored",
    )
    p.set_defaults(func=cmd_notes)
