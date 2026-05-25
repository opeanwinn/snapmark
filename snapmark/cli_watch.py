import argparse
import sys
from snapmark.snapshot import load_snapshot, save_snapshot
from snapmark.bookmark_watch import watch_bookmarks


def cmd_watch(args: argparse.Namespace) -> None:
    try:
        tree = load_snapshot(args.snapshot_dir, args.name)
    except FileNotFoundError:
        print(f"Snapshot '{args.name}' not found.", file=sys.stderr)
        sys.exit(1)

    enable = not args.unwatch
    new_tree, result = watch_bookmarks(
        tree,
        url_pattern=args.url_pattern,
        enable=enable,
    )

    output_name = args.output or args.name
    save_snapshot(args.snapshot_dir, output_name, new_tree)

    print(result.summary())
    if args.verbose:
        if enable and result.watched:
            print("\nNow watching:")
            for b in result.watched:
                print(f"  [{b.title}] {b.url}")
        elif not enable and result.unwatched:
            print("\nUnwatched:")
            for b in result.unwatched:
                print(f"  [{b.title}] {b.url}")


def add_watch_subparser(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser("watch", help="Mark bookmarks as watched/unwatched")
    p.add_argument("name", help="Snapshot name to load")
    p.add_argument("--snapshot-dir", default=".snapmarks", help="Snapshot directory")
    p.add_argument("--url-pattern", default=None, help="Filter bookmarks by URL substring")
    p.add_argument("--unwatch", action="store_true", help="Remove watched tag instead of adding")
    p.add_argument("--output", default=None, help="Output snapshot name (default: overwrite)")
    p.add_argument("--verbose", "-v", action="store_true", help="List affected bookmarks")
    p.set_defaults(func=cmd_watch)
