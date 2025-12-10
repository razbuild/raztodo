import argparse
from typing import Any

from raztodo.presentation.cli.formatters import CLIHelpFormatter
from raztodo.presentation.cli.helpers import handle_command_error, output_success


def add_parser(sub: Any) -> None:
    """Add the 'done' subcommand to the CLI parser."""
    done = sub.add_parser(
        "done",
        help="Mark a task as done or undone",
        description=(
            "Mark a task as completed or mark it as pending again (using --undo).\n\n"
            "Examples:\n"
            "  rt done 1\n"
            "  rt done 5 --undo\n"
            "  rt done 3 --json"
        ),
        formatter_class=CLIHelpFormatter,
    )
    done.add_argument(
        "id",
        type=int,
        metavar="ID",
        help="ID of the task to mark as done or undone (required)",
    )
    done.add_argument(
        "--undo",
        action="store_true",
        help="Unmark the task (mark as pending/incomplete instead of done)",
    )
    done.add_argument(
        "--json",
        action="store_true",
        help="Output result as JSON instead of human-readable format",
    )


class DoneTaskCMD:
    """Callable class that executes the 'done' command."""

    def __init__(self, uc: Any) -> None:
        self.uc = uc

    def __call__(self, args: argparse.Namespace) -> int:
        try:
            success: bool = self.uc.execute(
                args.id, done=not getattr(args, "undo", False)
            )
            if success:
                action: str = "undone" if getattr(args, "undo", False) else "completed"
                output_success(
                    f"Task marked as {action} (ID: {args.id})",
                    json_mode=getattr(args, "json", False),
                    id=args.id,
                    done=not getattr(args, "undo", False),
                )
                return 0

            from raztodo.domain.exceptions import TaskNotFoundError

            raise TaskNotFoundError(
                task_id=args.id, message="Task not found or no changes provided"
            )
        except Exception as e:
            return handle_command_error(e, args)
