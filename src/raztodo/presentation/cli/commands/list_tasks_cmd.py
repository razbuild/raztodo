import argparse
import sys
from typing import Any

from raztint import warn

from raztodo.presentation.cli.formatters import CLIHelpFormatter
from raztodo.presentation.cli.helpers import format_tasks_list, parse_tags


def add_parser(sub: Any) -> None:
    """Add the 'list' subcommand to the CLI parser."""
    listp = sub.add_parser(
        "list",
        help="List all tasks",
        description=(
            "List tasks with optional filtering, sorting, and pagination.\n\n"
            "Examples:\n"
            "  rt list --pending --priority H\n"
            "  rt list --project work --sort priority --desc\n"
            "  rt list --tags urgent,important --due-before 2024-12-31\n"
            "  rt list --limit 10 --offset 20"
        ),
        formatter_class=CLIHelpFormatter,
    )
    listp.add_argument("--done", action="store_true", help="Show only completed tasks")
    listp.add_argument(
        "--pending", action="store_true", help="Show only pending (incomplete) tasks"
    )
    listp.add_argument(
        "--priority",
        "-p",
        choices=["L", "M", "H"],
        metavar="LEVEL",
        help="Filter by priority level: L (Low), M (Medium), H (High)",
    )
    listp.add_argument(
        "--project", metavar="NAME", help="Filter by project or category name"
    )
    listp.add_argument(
        "--tags",
        "-t",
        metavar="TAGS",
        help="Filter by tags (comma-separated, e.g., 'work,urgent')",
    )
    listp.add_argument(
        "--due-before",
        metavar="DATE",
        help="Show tasks due before this date (format: YYYY-MM-DD)",
    )
    listp.add_argument(
        "--due-after",
        metavar="DATE",
        help="Show tasks due after this date (format: YYYY-MM-DD)",
    )
    listp.add_argument(
        "--limit",
        type=int,
        metavar="N",
        default=None,
        help="Limit number of tasks to display",
    )
    listp.add_argument(
        "--offset",
        type=int,
        metavar="N",
        default=None,
        help="Offset for pagination (number of tasks to skip)",
    )
    listp.add_argument(
        "--sort",
        choices=["id", "title", "created_at", "done", "priority", "due_date"],
        metavar="FIELD",
        default="id",
        help="Sort by field: id, title, created_at, done, priority, due_date (default: id)",
    )
    listp.add_argument(
        "--desc",
        action="store_true",
        help="Sort in descending order (default: ascending)",
    )
    listp.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON array instead of human-readable format",
    )


class ListTasksCMD:
    """Callable class that executes the 'list' command."""

    def __init__(self, uc: Any) -> None:
        self.uc = uc

    def __call__(self, args: argparse.Namespace) -> int:
        tags: list[str] = parse_tags(getattr(args, "tags", None)) or []

        done: bool | None = None
        if getattr(args, "done", False) and getattr(args, "pending", False):
            print(
                f"{warn()} Both --done and --pending specified; showing all tasks",
                file=sys.stderr,
            )
        elif getattr(args, "done", False):
            done = True
        elif getattr(args, "pending", False):
            done = False

        tasks = self.uc.execute(
            limit=getattr(args, "limit", None),
            offset=getattr(args, "offset", None),
            priority=getattr(args, "priority", None),
            project=getattr(args, "project", None),
            done=done,
            tags=tags,
            due_before=getattr(args, "due_before", None),
            due_after=getattr(args, "due_after", None),
        )

        key: str = getattr(args, "sort", "id")
        reverse: bool = getattr(args, "desc", False)

        def sort_key(t: Any) -> Any:
            if key == "id":
                return getattr(t, "id", 0)
            if key == "title":
                return getattr(t, "title", "").lower()
            if key == "created_at":
                return getattr(t, "created_at", "")
            if key == "done":
                return 1 if getattr(t, "done", False) else 0
            if key == "priority":
                priority = getattr(t, "priority", "") or ""
                priority_map = {"H": 3, "M": 2, "L": 1, "": 0}
                return priority_map.get(priority.upper(), 0)
            if key == "due_date":
                due = getattr(t, "due_date", None) or ""
                return due
            return getattr(t, "id", 0)

        tasks = sorted(tasks, key=sort_key, reverse=reverse)

        if not tasks:
            print(f"{warn()} No tasks found")
            return 0

        format_tasks_list(tasks, json_mode=getattr(args, "json", False))
        return 0
