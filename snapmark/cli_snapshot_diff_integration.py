"""Integration helper: register snapdiff subcommand into the main CLI parser."""

from snapmark.cli_snapshot_diff import add_snapdiff_subparser


def register(subparsers) -> None:
    """Register the 'snapdiff' subcommand with the provided subparsers action."""
    add_snapdiff_subparser(subparsers)
