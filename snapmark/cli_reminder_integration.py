"""Integration shim: wire the reminder subcommand into the main CLI.

Import and call ``add_reminder_subparser`` from within ``snapmark/cli.py``
to expose the ``reminder`` subcommand via the main entry-point.

Example usage::

    python -m snapmark reminder my_snapshot --days 14 --verbose
    python -m snapmark reminder my_snapshot --url-pattern github --days 3 --output reminded
"""
from snapmark.cli_reminder import add_reminder_subparser  # noqa: F401
