"""CLI helpers for the 'search' sub-command."""

from __future__ import annotations

import argparse
import sys
from typing import List

from snapmark.search import SearchResult, search_tree
from snapmark.snapshot import load_snapshot


def _format_results(results: List[SearchResult]) -> str:
    """Format search results for terminal output."""
    if not results:
        return "No bookmarks found."
    lines = []
    for r in results:
        lines.append(f"  [{r.breadcrumb}]  {r.bookmark.title}  <{r.bookmark.url}>")
    header = f"Found {len(results)} bookmark(s):"
    return "\n".join([header] + lines)


def cmd_search(args: argparse.Namespace) -> int:
    """Handle the 'search' CLI sub-command.

    Returns:
        Exit code (0 = success, 1 = error).
    """
    try:
        root = load_snapshot(args.snapshot, snapshot_dir=args.snapshot_dir)
    except FileNotFoundError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    results = search_tree(
        root,
        args.query,
        case_sensitive=args.case_sensitive,
    )
    print(_format_results(results))
    return 0


def add_search_subparser(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    """Register the 'search' sub-command on *subparsers*."""
    parser: argparse.ArgumentParser = subparsers.add_parser(
        "search",
        help="Search bookmarks in a snapshot by title or URL.",
    )
    parser.add_argument("snapshot", help="Name of the snapshot to search.")
    parser.add_argument("query", help="Substring to search for.")
    parser.add_argument(
        "--case-sensitive",
        action="store_true",
        default=False,
        help="Enable case-sensitive matching (default: case-insensitive).",
    )
    parser.add_argument(
        "--snapshot-dir",
        default=None,
        help="Directory where snapshots are stored (overrides default).",
    )
    parser.set_defaults(func=cmd_search)
