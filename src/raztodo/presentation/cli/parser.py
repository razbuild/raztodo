import argparse
from importlib import metadata

from raztodo.presentation.cli.commands import (
    create_task_cmd,
    delete_task_cmd,
    export_task_cmd,
    import_task_cmd,
    list_tasks_cmd,
    mark_task_done_cmd,
    migrate_tasks_cmd,
    search_tasks_cmd,
    update_task_cmd,
)
from raztodo.presentation.cli.formatters import CLIHelpFormatter


def _get_version() -> str:
    try:
        return metadata.version("raztodo")
    except metadata.PackageNotFoundError:
        return "unknown"


def get_parser() -> argparse.ArgumentParser:
    parser: argparse.ArgumentParser = argparse.ArgumentParser(
        prog="raztodo",
        description=(
            "A command-line task manager powered by SQLite. "
            "Use one of the commands below to manage your todos."
        ),
        epilog=(
            "Examples:\n"
            "  raztodo add 'Buy groceries' --priority H --due tomorrow\n"
            "  raztodo list --priority H --pending\n"
            "  raztodo update 1 --title 'New title' --done\n"
            "  raztodo search 'meeting' --project work\n\n"
            "Tips:\n"
            "  • Show command help: raztodo <command> --help\n"
            "  • Output in JSON mode when available for automation"
        ),
        formatter_class=CLIHelpFormatter,
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {_get_version()}",
        help="Show raztodo version information and exit",
    )

    sub = parser.add_subparsers(
        dest="command",
        required=True,
        help="Available commands",
        metavar="COMMAND",
    )

    create_task_cmd.add_parser(sub)
    list_tasks_cmd.add_parser(sub)
    delete_task_cmd.add_parser(sub)
    update_task_cmd.add_parser(sub)
    search_tasks_cmd.add_parser(sub)
    export_task_cmd.add_parser(sub)
    import_task_cmd.add_parser(sub)
    mark_task_done_cmd.add_parser(sub)
    migrate_tasks_cmd.add_parser(sub)

    return parser
