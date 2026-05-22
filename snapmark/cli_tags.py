"""CLI sub-commands for tag-based bookmark operations."""
from __future__ import annotations
import argparse
import sys
from snapmark.snapshot import load_snapshot
from snapmark.tags import build_tag_index, filter_by_tag


def _format_tag_list(tags: list[str]) -> str:
    if not tags:
        return "(no tags found)"
    return "\n".join(f"  #{t}" for t in tags)


def _format_bookmarks(bookmarks: list) -> str:
    if not bookmarks:
        return "(no bookmarks)"
    lines = []
    for bm in bookmarks:
        lines.append(f"  {bm.title}")
        lines.append(f"    {bm.url}")
    return "\n".join(lines)


def cmd_tags_list(args: argparse.Namespace) -> None:
    """List all tags present in a snapshot."""
    try:
        tree = load_snapshot(args.name, snapshot_dir=args.snapshot_dir)
    except FileNotFoundError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)
    idx = build_tag_index(tree)
    print(f"Tags in '{args.name}':")
    print(_format_tag_list(idx.tags()))


def cmd_tags_filter(args: argparse.Namespace) -> None:
    """List bookmarks matching a specific tag in a snapshot."""
    try:
        tree = load_snapshot(args.name, snapshot_dir=args.snapshot_dir)
    except FileNotFoundError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)
    bookmarks = filter_by_tag(tree, args.tag)
    print(f"Bookmarks tagged '#{args.tag.lower()}' in '{args.name}':")
    print(_format_bookmarks(bookmarks))


def add_tags_subparser(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    tags_parser = subparsers.add_parser("tags", help="Tag-based bookmark operations")
    tags_sub = tags_parser.add_subparsers(dest="tags_cmd", required=True)

    list_p = tags_sub.add_parser("list", help="List all tags in a snapshot")
    list_p.add_argument("name", help="Snapshot name")
    list_p.add_argument("--snapshot-dir", default=None)
    list_p.set_defaults(func=cmd_tags_list)

    filter_p = tags_sub.add_parser("filter", help="Filter bookmarks by tag")
    filter_p.add_argument("name", help="Snapshot name")
    filter_p.add_argument("tag", help="Tag to filter by")
    filter_p.add_argument("--snapshot-dir", default=None)
    filter_p.set_defaults(func=cmd_tags_filter)
