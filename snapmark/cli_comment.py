import argparse
import sys
from snapmark.snapshot import load_snapshot, save_snapshot
from snapmark.bookmark_comment import comment_tree


def cmd_comment(args: argparse.Namespace) -> None:
    try:
        root = load_snapshot(args.snapshot_dir, args.name)
    except FileNotFoundError:
        print(f"Error: snapshot '{args.name}' not found.", file=sys.stderr)
        sys.exit(1)

    url_pattern = getattr(args, "url_pattern", None)
    overwrite = getattr(args, "overwrite", False)

    new_root, result = comment_tree(
        root,
        comment=args.comment,
        url_pattern=url_pattern,
        overwrite=overwrite,
    )

    print(result.summary())

    output_name = getattr(args, "output", None) or args.name
    save_snapshot(args.snapshot_dir, output_name, new_root)
    print(f"Saved snapshot: {output_name}")


def add_comment_subparser(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser(
        "comment",
        help="Attach a comment to bookmarks in a snapshot",
    )
    parser.add_argument("name", help="Snapshot name to operate on")
    parser.add_argument("comment", help="Comment text to attach")
    parser.add_argument(
        "--url-pattern",
        dest="url_pattern",
        default=None,
        help="Only comment bookmarks whose URL contains this substring",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        default=False,
        help="Overwrite existing comments (default: skip)",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Output snapshot name (defaults to in-place update)",
    )
    parser.add_argument(
        "--snapshot-dir",
        dest="snapshot_dir",
        default="snapshots",
        help="Directory where snapshots are stored",
    )
    parser.set_defaults(func=cmd_comment)
