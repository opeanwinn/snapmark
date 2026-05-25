"""Integration hook to register the watch subcommand with the main CLI parser."""
from snapmark.cli_watch import add_watch_subparser


def register(subparsers):
    """Register the watch subcommand.

    Called by the main CLI builder when assembling all subcommands.
    """
    add_watch_subparser(subparsers)
