import argparse
from typing import Any

from raztodo.presentation.cli.formatters import CLIHelpFormatter
from raztodo.presentation.cli.helpers import handle_command_error, output_success


def add_parser(sub: Any) -> None:
    """Add the 'clear' subcommand to the CLI parser."""
    clear = sub.add_parser(
        "clear",
        help="Delete all tasks",
        description=(
            "Delete all tasks from the database. This action cannot be undone.\n\n"
            "This command requires explicit confirmation using the --confirm flag.\n\n"
            "Examples:\n"
            "  rt clear --confirm\n"
            "  rt clear --confirm --json"
        ),
        formatter_class=CLIHelpFormatter,
    )

    clear.add_argument(
        "--confirm",
        action="store_true",
        required=True,
        help="Confirm that you want to delete all tasks (required)",
    )
    clear.add_argument(
        "--json",
        action="store_true",
        help="Output result as JSON instead of human-readable format",
    )


class ClearTasksCMD:
    """Callable class that executes the 'clear' command."""

    def __init__(self, uc: Any) -> None:
        self.uc = uc

    def __call__(self, args: argparse.Namespace) -> int:
        try:
            count: int = self.uc.execute(confirmed=args.confirm)
            output_success(
                f"Cleared {count} task(s) successfully",
                json_mode=getattr(args, "json", False),
                count=count,
            )
            return 0
        except Exception as e:
            return handle_command_error(e, args)
