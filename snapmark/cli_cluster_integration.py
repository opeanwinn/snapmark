"""Integration entry point for the cluster subcommand.

Register this with the main CLI parser in cli.py via::

    from snapmark.cli_cluster import add_cluster_subparser
    add_cluster_subparser(subparsers)

Example usage::

    snapmark cluster my_snapshot --mode domain --verbose
    snapmark cluster my_snapshot --mode tag
"""

from snapmark.cli_cluster import add_cluster_subparser, cmd_cluster

__all__ = ["add_cluster_subparser", "cmd_cluster"]
