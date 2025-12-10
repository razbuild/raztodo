import argparse
from typing import Any

from raztodo.presentation.cli.formatters import CLIHelpFormatter
from raztodo.presentation.cli.helpers import handle_command_error, output_success


def add_parser(sub: Any) -> None:
    """Add the 'remove' subcommand to the CLI parser."""
    remove = sub.add_parser(
        "remove",
        help="Delete a task",
        description=(
            "Delete a task by its ID. This action cannot be undone.\n\n"
            "Examples:\n"
            "  rt remove 1\n"
            "  rt remove 5 --json"
        ),
        formatter_class=CLIHelpFormatter,
    )

    remove.add_argument(
        "id",
        type=int,
        metavar="ID",
        help="ID of the task to delete (required)",
    )
    remove.add_argument(
        "--json",
        action="store_true",
        help="Output result as JSON instead of human-readable format",
    )


class DeleteTaskCMD:
    """Callable class that executes the 'remove' command."""

    def __init__(self, uc: Any) -> None:
        self.uc = uc

    def __call__(self, args: argparse.Namespace) -> int:
        try:
            success: bool = self.uc.execute(args.id)
            if success:
                output_success(
                    f"Task deleted successfully (ID: {args.id})",
                    json_mode=getattr(args, "json", False),
                    id=args.id,
                )
            return 0
        except Exception as e:
            return handle_command_error(e, args)
