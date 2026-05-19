"""Command-line interface for snapmark."""

import argparse
import sys

from snapmark.diff import diff_trees
from snapmark.snapshot import list_snapshots, load_snapshot, save_snapshot


def cmd_save(args):
    path = save_snapshot(args.tree_file, name=args.name)
    print(f"Snapshot saved: {path}")


def cmd_list(args):
    snapshots = list_snapshots()
    if not snapshots:
        print("No snapshots found.")
        return
    for snap in snapshots:
        print(f"  {snap}")


def cmd_diff(args):
    snap_a = load_snapshot(args.snapshot_a)
    snap_b = load_snapshot(args.snapshot_b)
    result = diff_trees(snap_a, snap_b)
    if not result.has_changes:
        print("Snapshots are identical.")
    else:
        print(f"Diff: {args.snapshot_a} -> {args.snapshot_b}")
        print(result.summary())


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="snapmark",
        description="Snapshot and restore browser bookmark trees.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    save_p = sub.add_parser("save", help="Save a snapshot from a bookmark JSON export.")
    save_p.add_argument("tree_file", help="Path to the bookmark JSON export file.")
    save_p.add_argument("--name", default=None, help="Optional snapshot name.")
    save_p.set_defaults(func=cmd_save)

    list_p = sub.add_parser("list", help="List all saved snapshots.")
    list_p.set_defaults(func=cmd_list)

    diff_p = sub.add_parser("diff", help="Diff two snapshots.")
    diff_p.add_argument("snapshot_a", help="Name of the first snapshot.")
    diff_p.add_argument("snapshot_b", help="Name of the second snapshot.")
    diff_p.set_defaults(func=cmd_diff)

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()
    try:
        args.func(args)
    except Exception as exc:  # noqa: BLE001
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
