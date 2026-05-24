import argparse
import sys
from snapmark.snapshot import load_snapshot, save_snapshot
from snapmark.bookmark_reminder import set_reminders


def cmd_reminder(args: argparse.Namespace) -> None:
    try:
        tree = load_snapshot(args.snapshot_dir, args.name)
    except FileNotFoundError:
        print(f"Snapshot '{args.name}' not found.", file=sys.stderr)
        sys.exit(1)

    new_tree, result = set_reminders(
        tree,
        days=args.days,
        url_pattern=args.url_pattern or None,
        overwrite=args.overwrite,
    )

    output_name = args.output or args.name
    save_snapshot(new_tree, args.snapshot_dir, output_name)

    print(result.summary())
    if args.verbose and result.scheduled:
        print("\nScheduled reminders:")
        for bm in result.scheduled:
            remind_tag = next(
                (t for t in (bm.tags or []) if t.startswith("remind:")), "?"
            )
            print(f"  [{remind_tag}] {bm.title} — {bm.url}")


def add_reminder_subparser(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser(
        "reminder", help="Schedule reminders for bookmarks by tagging them"
    )
    p.add_argument("name", help="Snapshot name to process")
    p.add_argument(
        "--days",
        type=int,
        default=7,
        help="Days from today to set the reminder (default: 7)",
    )
    p.add_argument(
        "--url-pattern",
        dest="url_pattern",
        default="",
        help="Only tag bookmarks whose URL contains this pattern",
    )
    p.add_argument(
        "--overwrite",
        action="store_true",
        help="Replace existing remind: tags",
    )
    p.add_argument(
        "--output",
        default="",
        help="Output snapshot name (defaults to overwriting input)",
    )
    p.add_argument(
        "--verbose", "-v", action="store_true", help="List scheduled bookmarks"
    )
    p.add_argument(
        "--snapshot-dir",
        dest="snapshot_dir",
        default="snapshots",
        help="Directory containing snapshots",
    )
    p.set_defaults(func=cmd_reminder)
