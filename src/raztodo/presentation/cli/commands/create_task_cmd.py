import argparse
from typing import Any

from raztodo.presentation.cli.formatters import CLIHelpFormatter
from raztodo.presentation.cli.helpers import (
    handle_command_error,
    output_success,
    parse_tags,
)


def add_parser(sub: Any) -> None:
    """Add the 'add' subcommand to the CLI parser."""
    add = sub.add_parser(
        "add",
        help="Create a new task",
        description=(
            "Create a new task with a title and optional metadata.\n\n"
            "Examples:\n"
            "  rt add 'Complete project' --priority H --due 2024-12-31\n"
            "  rt add 'Call client' -p M --desc 'Discuss requirements' --tags work,urgent\n"
            "  rt add 'Buy milk' --project shopping"
        ),
        formatter_class=CLIHelpFormatter,
    )

    add.add_argument("title", help="Title of the task (required)")
    add.add_argument(
        "--desc",
        "--description",
        "-d",
        metavar="TEXT",
        help="Task description (default: empty string)",
        default="",
    )
    add.add_argument(
        "--priority",
        "-p",
        choices=["L", "M", "H"],
        metavar="LEVEL",
        help="Priority level: L (Low), M (Medium), H (High)",
    )
    add.add_argument(
        "--due",
        "--due-date",
        metavar="DATE",
        help="Due date in YYYY-MM-DD format or relative text",
    )
    add.add_argument(
        "--tags",
        "-t",
        metavar="TAGS",
        help="Comma-separated list of tags",
        default="",
    )
    add.add_argument(
        "--project",
        metavar="NAME",
        help="Project or category name",
    )
    add.add_argument(
        "--json",
        action="store_true",
        help="Output result in JSON format",
    )


class CreateTaskCMD:
    """Callable class that executes the 'add' command."""

    def __init__(self, uc: Any) -> None:
        self.uc = uc

    def __call__(self, args: argparse.Namespace) -> int:

        try:
            tags: list[str] = parse_tags(getattr(args, "tags", None)) or []
            due_date: str | None = getattr(args, "due", None)

            task_id: int = self.uc.execute(
                args.title,
                getattr(args, "desc", ""),
                getattr(args, "priority", "") or "",
                due_date,
                tags,
                getattr(args, "project", None),
            )

            output_success(
                f"Task created successfully (ID: {task_id})",
                json_mode=getattr(args, "json", False),
                id=task_id,
            )
            return 0

        except Exception as e:
            return handle_command_error(e, args)
