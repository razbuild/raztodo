import argparse
from typing import Any

from raztodo.presentation.cli.formatters import CLIHelpFormatter
from raztodo.presentation.cli.helpers import (
    handle_command_error,
    output_json,
    output_success,
)


def add_parser(sub: Any) -> None:
    """Add the 'import' subcommand to the CLI parser."""
    import_ = sub.add_parser(
        "import",
        help="Import tasks from a JSON file",
        description=(
            "Import tasks from a JSON file (exported by the export command).\n\n"
            "Examples:\n"
            "  rt import tasks_backup.json\n"
            "  rt import ~/backups/tasks.json --upsert --json"
        ),
        formatter_class=CLIHelpFormatter,
    )
    import_.add_argument(
        "filepath", metavar="FILE", help="Path to the JSON file to import (required)"
    )
    import_.add_argument(
        "--upsert",
        action="store_true",
        help="Update existing tasks if they match by title (otherwise skip duplicates)",
    )
    import_.add_argument(
        "--json",
        action="store_true",
        help="Output result as JSON instead of human-readable format",
    )


class ImportTasksCMD:
    """Callable class that executes the 'import' command."""

    def __init__(self, uc: Any) -> None:
        self.uc = uc

    def __call__(self, args: argparse.Namespace) -> int:
        try:
            res = self.uc.execute(args.filepath, upsert=getattr(args, "upsert", False))
            json_mode: bool = getattr(args, "json", False)

            if json_mode:
                if isinstance(res, dict):
                    output_json({"ok": True, **res, "filepath": args.filepath})
                else:
                    output_json(
                        {"ok": True, "inserted": int(res), "filepath": args.filepath}
                    )
            else:
                if isinstance(res, dict):
                    inserted = res.get("inserted", 0)
                    updated = res.get("updated", 0)
                    total = inserted + updated
                    if total > 0:
                        msg_parts = []
                        if inserted > 0:
                            msg_parts.append(f"{inserted} new")
                        if updated > 0:
                            msg_parts.append(f"{updated} updated")
                        output_success(
                            f"Imported {', '.join(msg_parts)} task(s) from {args.filepath}",
                            json_mode=False,
                        )
                    else:
                        output_success(
                            "Import completed (no changes made)", json_mode=False
                        )
                else:
                    output_success(
                        f"Imported {res} task(s) successfully from {args.filepath}",
                        json_mode=False,
                    )
            return 0
        except Exception as e:
            return handle_command_error(e, args, filepath=args.filepath)
