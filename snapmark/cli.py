"""Command-line interface for snapmark."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from snapmark.diff import diff_trees
from snapmark.restore import RestoreError, export_to_json, restore_snapshot
from snapmark.snapshot import list_snapshots, load_snapshot, save_snapshot
from snapmark.models import from_dict


def cmd_save(args: argparse.Namespace) -> None:
    import json

    source = Path(args.file)
    if not source.exists():
        print(f"Error: file '{source}' not found.", file=sys.stderr)
        sys.exit(1)
    with source.open(encoding="utf-8") as fh:
        data = json.load(fh)
    tree = from_dict(data)
    save_snapshot(tree, args.name)
    print(f"Snapshot '{args.name}' saved.")


def cmd_list(args: argparse.Namespace) -> None:
    snapshots = list_snapshots()
    if not snapshots:
        print("No snapshots found.")
    else:
        for name in snapshots:
            print(name)


def cmd_diff(args: argparse.Namespace) -> None:
    import json

    try:
        base_data = load_snapshot(args.base)
        other_data = load_snapshot(args.other)
    except FileNotFoundError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)

    base_tree = from_dict(base_data)
    other_tree = from_dict(other_data)
    result = diff_trees(base_tree, other_tree)
    print(result.summary())


def cmd_restore(args: argparse.Namespace) -> None:
    """Restore a snapshot to a JSON export file."""
    try:
        tree = restore_snapshot(args.name)
    except RestoreError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)

    output = Path(args.output)
    export_to_json(tree, output)
    print(f"Snapshot '{args.name}' restored to '{output}'.")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="snapmark",
        description="Snapshot and restore browser bookmark trees.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_save = sub.add_parser("save", help="Save a snapshot from a JSON bookmark file.")
    p_save.add_argument("file", help="Path to the bookmark JSON file.")
    p_save.add_argument("name", help="Name for the snapshot.")
    p_save.set_defaults(func=cmd_save)

    p_list = sub.add_parser("list", help="List all saved snapshots.")
    p_list.set_defaults(func=cmd_list)

    p_diff = sub.add_parser("diff", help="Diff two snapshots.")
    p_diff.add_argument("base", help="Base snapshot name.")
    p_diff.add_argument("other", help="Other snapshot name.")
    p_diff.set_defaults(func=cmd_diff)

    p_restore = sub.add_parser("restore", help="Restore a snapshot to a JSON file.")
    p_restore.add_argument("name", help="Snapshot name to restore.")
    p_restore.add_argument("output", help="Output JSON file path.")
    p_restore.set_defaults(func=cmd_restore)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
