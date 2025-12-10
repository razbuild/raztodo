import argparse
from typing import Any

from raztodo.presentation.cli.formatters import CLIHelpFormatter
from raztodo.presentation.cli.helpers import (
    handle_command_error,
    output_success,
    parse_tags,
)


def add_parser(sub: Any) -> None:
    """Add the 'update' subcommand to the CLI parser."""
    update = sub.add_parser(
        "update",
        help="Update an existing task",
        description=(
            "Update one or more fields of an existing task by ID.\n\n"
            "Examples:\n"
            "  rt update 1 --title 'Updated title'\n"
            "  rt update 5 --priority H --due 2024-12-31\n"
            "  rt update 3 --tags work,urgent --project client"
        ),
        formatter_class=CLIHelpFormatter,
    )
    update.add_argument(
        "id", type=int, metavar="ID", help="ID of the task to update (required)"
    )
    update.add_argument(
        "--title", metavar="TEXT", help="New title for the task", default=None
    )
    update.add_argument(
        "--desc",
        "--description",
        metavar="TEXT",
        help="New description for the task",
        default=None,
    )
    update.add_argument(
        "--priority",
        "-p",
        choices=["L", "M", "H"],
        metavar="LEVEL",
        help="New priority level: L (Low), M (Medium), H (High)",
    )
    update.add_argument(
        "--due", "--due-date", metavar="DATE", help="New due date (format: YYYY-MM-DD)"
    )
    update.add_argument(
        "--tags",
        "-t",
        metavar="TAGS",
        help="New tags (comma-separated, e.g., 'work,urgent')",
    )
    update.add_argument(
        "--project", metavar="NAME", help="New project or category name"
    )
    update.add_argument(
        "--json",
        action="store_true",
        help="Output result as JSON instead of human-readable format",
    )


class UpdateTaskCMD:
    """Callable class that executes the 'update' command."""

    def __init__(self, uc: Any) -> None:
        self.uc = uc

    def __call__(self, args: argparse.Namespace) -> int:
        try:
            tags: list[str] = parse_tags(getattr(args, "tags", None)) or []
            due_date: str | None = getattr(args, "due", None)
            project: str | None = getattr(args, "project", None)

            success: bool = self.uc.execute(
                args.id,
                getattr(args, "title", None),
                getattr(args, "desc", None),
                getattr(args, "priority", None),
                due_date,
                tags,
                project,
            )
            if success:
                output_success(
                    f"Task updated successfully (ID: {args.id})",
                    json_mode=getattr(args, "json", False),
                    id=args.id,
                )
                return 0

            from raztodo.domain.exceptions import TaskNotFoundError

            raise TaskNotFoundError(
                task_id=args.id, message="Task not found or no changes provided"
            )
        except Exception as e:
            return handle_command_error(e, args)
