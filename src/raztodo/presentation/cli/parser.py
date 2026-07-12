import argparse
import os

from raztodo.infrastructure.version import get_version
from raztodo.presentation.cli.handlers import (
    clear_tasks_handler,
    completion,
    create_task_handler,
    delete_task_handler,
    explain_task_handler,
    export_task_handler,
    import_task_handler,
    list_tasks_handler,
    mark_task_done_handler,
    migrate_tasks_handler,
    search_tasks_handler,
    update_task_handler,
)


def get_parser() -> argparse.ArgumentParser:
    from raztodo.presentation.cli.formatters import CLIHelpFormatter

    parser: argparse.ArgumentParser = argparse.ArgumentParser(
        prog="raztodo",
        description=(
            "A command-line task manager powered by SQLite. "
            "Use one of the commands below to manage your todos."
        ),
        epilog=(
            "Examples:\n"
            "  rt add 'Buy groceries' --priority H --due 2024-12-31\n"
            "  rt list --priority H --pending\n"
            "  rt update 1 --title 'New title'\n"
            "  rt search 'meeting' --project work\n\n"
            "Tips:\n"
            "  • Show command help: rt <command> --help\n"
            "  • Output in JSON mode when available for automation"
        ),
        formatter_class=CLIHelpFormatter,
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {get_version()}",
        help="Show raztodo version information and exit",
    )

    sub_required = os.environ.get("_ARGCOMPLETE") != "1"

    sub = parser.add_subparsers(
        dest="command",
        required=sub_required,
        help="Available commands",
        metavar="COMMAND",
    )

    create_task_handler.add_parser(sub)
    list_tasks_handler.add_parser(sub)
    delete_task_handler.add_parser(sub)
    update_task_handler.add_parser(sub)
    search_tasks_handler.add_parser(sub)
    export_task_handler.add_parser(sub)
    import_task_handler.add_parser(sub)
    mark_task_done_handler.add_parser(sub)
    migrate_tasks_handler.add_parser(sub)
    clear_tasks_handler.add_parser(sub)
    completion.add_parser(sub)
    explain_task_handler.add_parser(sub)

    return parser
