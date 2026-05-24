import argparse
import sys
from snapmark.snapshot import load_snapshot, save_snapshot
from snapmark.bookmark_lock import lock_bookmarks, unlock_bookmarks


def cmd_lock(args: argparse.Namespace) -> None:
    try:
        root = load_snapshot(args.snapshot_dir, args.name)
    except FileNotFoundError:
        print(f"Snapshot '{args.name}' not found.", file=sys.stderr)
        sys.exit(1)

    url_pattern = getattr(args, "url", None)

    if args.unlock:
        new_root, result = unlock_bookmarks(root, url_pattern=url_pattern)
    else:
        new_root, result = lock_bookmarks(root, url_pattern=url_pattern)

    output_name = args.output or args.name
    save_snapshot(args.snapshot_dir, output_name, new_root)
    print(result.summary())


def add_lock_subparser(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser(
        "lock",
        help="Lock or unlock bookmarks by tagging them with 'locked'.",
    )
    parser.add_argument("name", help="Snapshot name to operate on.")
    parser.add_argument(
        "--url",
        default=None,
        help="Only lock/unlock bookmarks whose URL contains this string.",
    )
    parser.add_argument(
        "--unlock",
        action="store_true",
        default=False,
        help="Unlock bookmarks instead of locking them.",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Save result to a different snapshot name (default: overwrite).",
    )
    parser.add_argument(
        "--snapshot-dir",
        default=".snapmarks",
        dest="snapshot_dir",
        help="Directory where snapshots are stored.",
    )
    parser.set_defaults(func=cmd_lock)
