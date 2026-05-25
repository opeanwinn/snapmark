"""CLI subcommand: share — export a readable/shareable bookmark list."""

import argparse
import sys
from snapmark.snapshot import load_snapshot
from snapmark.bookmark_share import share_tree


def cmd_share(args: argparse.Namespace) -> None:
    try:
        root = load_snapshot(args.snapshot_dir, args.name)
    except FileNotFoundError:
        print(f"Error: snapshot '{args.name}' not found.", file=sys.stderr)
        sys.exit(1)

    result = share_tree(
        root,
        url_pattern=args.url_pattern,
        tag_filter=args.tag,
    )

    if args.format == "markdown":
        output = result.as_markdown()
    else:
        output = result.as_text()

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(output)
        print(f"Saved to {args.output}")
    else:
        print(output)

    print(result.summary())


def add_share_subparser(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser("share", help="Generate a shareable bookmark list")
    parser.add_argument("name", help="Snapshot name to share")
    parser.add_argument("--snapshot-dir", default=".snapmarks", help="Snapshot directory")
    parser.add_argument("--url-pattern", default=None, help="Filter by URL substring")
    parser.add_argument("--tag", default=None, help="Filter by tag")
    parser.add_argument(
        "--format",
        choices=["text", "markdown"],
        default="text",
        help="Output format (default: text)",
    )
    parser.add_argument("--output", default=None, help="Write output to file instead of stdout")
    parser.set_defaults(func=cmd_share)
