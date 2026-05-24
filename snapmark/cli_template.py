"""CLI subcommand: apply URL/title templates to a snapshot."""
import argparse
import sys

from snapmark.snapshot import load_snapshot, save_snapshot
from snapmark.models import from_dict, to_dict
from snapmark.bookmark_template import apply_template


def cmd_template(args: argparse.Namespace) -> None:
    try:
        data = load_snapshot(args.snapshot_dir, args.name)
    except FileNotFoundError:
        print(f"Snapshot '{args.name}' not found.", file=sys.stderr)
        sys.exit(1)

    root = from_dict(data)

    if not any([args.url_pattern, args.title_pattern]):
        print("Error: at least one of --url-pattern or --title-pattern is required.",
              file=sys.stderr)
        sys.exit(1)

    new_root, result = apply_template(
        root,
        url_pattern=args.url_pattern,
        url_template=args.url_template,
        title_pattern=args.title_pattern,
        title_template=args.title_template,
        recursive=not args.no_recursive,
    )

    print(result.summary())

    if result.updated_count == 0:
        print("No bookmarks matched; snapshot unchanged.")
        return

    output_name = args.output or args.name
    save_snapshot(args.snapshot_dir, output_name, to_dict(new_root))
    print(f"Saved as '{output_name}'.")


def add_template_subparser(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser(
        "template",
        help="Apply URL/title regex templates to bookmarks in a snapshot.",
    )
    p.add_argument("name", help="Snapshot name to process.")
    p.add_argument("--snapshot-dir", default=".snapmarks", help="Snapshot directory.")
    p.add_argument("--url-pattern", default=None, help="Regex pattern to match in URLs.")
    p.add_argument("--url-template", default=None, help="Replacement string for URL pattern.")
    p.add_argument("--title-pattern", default=None, help="Regex pattern to match in titles.")
    p.add_argument("--title-template", default=None, help="Replacement string for title pattern.")
    p.add_argument("--output", default=None, help="Output snapshot name (default: overwrite).")
    p.add_argument("--no-recursive", action="store_true", help="Only process top-level folder.")
    p.set_defaults(func=cmd_template)
