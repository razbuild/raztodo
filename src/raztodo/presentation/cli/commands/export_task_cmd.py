import argparse
from typing import Any

from raztodo.presentation.cli.formatters import CLIHelpFormatter
from raztodo.presentation.cli.helpers import handle_command_error, output_success


def add_parser(sub: Any) -> None:
    """Add the 'export' subcommand to the CLI parser."""
    export = sub.add_parser(
        "export",
        help="Export tasks to a JSON file",
        description=(
            "Export all tasks to a JSON file for backup or transfer.\n\n"
            "Examples:\n"
            "  rt export tasks_backup.json\n"
            "  rt export ~/backups/tasks_2024.json --json"
        ),
        formatter_class=CLIHelpFormatter,
    )
    export.add_argument(
        "filepath", metavar="FILE", help="Path to the output JSON file (required)"
    )
    export.add_argument(
        "--json",
        action="store_true",
        help="Output result as JSON instead of human-readable format",
    )


class ExportTasksCMD:
    """Callable class that executes the 'export' command."""

    def __init__(self, uc: Any) -> None:
        self.uc = uc

    def __call__(self, args: argparse.Namespace) -> int:
        try:
            success: bool = self.uc.execute(args.filepath)
            if success:
                output_success(
                    f"Tasks exported successfully to {args.filepath}",
                    json_mode=getattr(args, "json", False),
                    filepath=args.filepath,
                )
            return 0
        except Exception as e:
            return handle_command_error(e, args, filepath=args.filepath)
