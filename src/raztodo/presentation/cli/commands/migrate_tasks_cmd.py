import argparse
from typing import Any

from raztodo.presentation.cli.formatters import CLIHelpFormatter


def add_parser(
    sub: Any,
) -> Any:
    """Add the 'migrate' subcommand to the CLI parser."""
    p = sub.add_parser(
        "migrate",
        help="Run database migration",
        description=(
            "Run database migration to deduplicate task titles and enforce unique index.\n"
            "This command should be run when upgrading from an older version.\n\n"
            "Example:\n"
            "  rt migrate"
        ),
        formatter_class=CLIHelpFormatter,
    )
    p.set_defaults(command="migrate")
    return p


class MigrateCMD:
    """Callable class that executes the 'migrate' command."""

    def __init__(self, uc: Any) -> None:
        self.uc = uc

    def __call__(self, args: argparse.Namespace) -> int:
        result: dict[str, int] = self.uc.execute()
        print(
            f"Migration completed: fixed={result.get('duplicates_fixed', 0)}, "
            f"unique_index={result.get('unique_index', 0)}"
        )
        return 0
