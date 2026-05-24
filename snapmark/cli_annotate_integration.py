"""Integration helper: register annotate subparser into the main CLI.

This module is imported by cli.py to attach the annotate command.
Kept separate to allow incremental CLI extension without modifying cli.py.
"""
from snapmark.cli_annotate import add_annotate_subparser  # noqa: F401

__all__ = ["add_annotate_subparser"]
