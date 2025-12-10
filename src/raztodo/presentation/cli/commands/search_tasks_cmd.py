import argparse
import sys
from typing import Any

from raztint import warn

from raztodo.presentation.cli.formatters import CLIHelpFormatter
from raztodo.presentation.cli.helpers import format_tasks_list, output_json, parse_tags


def add_parser(sub: Any) -> None:
    """Add the 'search' subcommand to the CLI parser."""
    search = sub.add_parser(
        "search",
        help="Search tasks by keyword",
        description=(
            "Search for tasks by keyword in title or description, with optional filters.\n\n"
            "Examples:\n"
            "  rt search 'meeting' --pending\n"
            "  rt search 'project' --priority H --project work\n"
            "  rt search 'urgent' --tags important,work"
        ),
        formatter_class=CLIHelpFormatter,
    )
    search.add_argument(
        "keyword",
        metavar="KEYWORD",
        help="Keyword to search for in task title or description (required)",
    )
    search.add_argument(
        "--done",
        action="store_true",
        help="Show only completed tasks in search results",
    )
    search.add_argument(
        "--pending",
        action="store_true",
        help="Show only pending (incomplete) tasks in search results",
    )
    search.add_argument(
        "--priority",
        "-p",
        choices=["L", "M", "H"],
        metavar="LEVEL",
        help="Filter results by priority level: L (Low), M (Medium), H (High)",
    )
    search.add_argument(
        "--project", metavar="NAME", help="Filter results by project or category name"
    )
    search.add_argument(
        "--tags",
        "-t",
        metavar="TAGS",
        help="Filter results by tags (comma-separated, e.g., 'work,urgent')",
    )
    search.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON array instead of human-readable format",
    )


class SearchTasksCMD:
    """Callable class that executes the 'search' command."""

    def __init__(self, uc: Any) -> None:
        self.uc = uc

    def __call__(self, args: argparse.Namespace) -> int:
        tags: list[str] = parse_tags(getattr(args, "tags", None)) or []

        tasks = self.uc.execute(
            args.keyword,
            priority=getattr(args, "priority", None),
            project=getattr(args, "project", None),
            tags=tags,
        )

        if getattr(args, "done", False) and getattr(args, "pending", False):
            print(
                f"{warn()} Both --done and --pending specified; showing all matches",
                file=sys.stderr,
            )
        else:
            if getattr(args, "done", False):
                tasks = [t for t in tasks if getattr(t, "done", False)]
            if getattr(args, "pending", False):
                tasks = [t for t in tasks if not getattr(t, "done", False)]

        if not tasks:
            if getattr(args, "json", False):
                output_json([])
            else:
                print(f"{warn()} No tasks found for '{args.keyword}'")
            return 0

        format_tasks_list(tasks, json_mode=getattr(args, "json", False))
        return 0
