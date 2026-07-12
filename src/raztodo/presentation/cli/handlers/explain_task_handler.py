import argparse
import json
import sys
from typing import Any

from raztodo.presentation.cli.formatters import CLIHelpFormatter
from raztodo.presentation.cli.helpers import handle_command_error


def _loading(label: str) -> None:
    """Print a simple loading line, overwritable with \\r."""
    if sys.stdout.isatty():
        print(f"LLM {label} ...", end="\r", flush=True)


def _clear_loading(label: str) -> None:
    if sys.stdout.isatty():
        print(" " * (len(label) + 10), end="\r", flush=True)


def add_parser(sub: Any) -> None:
    """Add the 'explain' subcommand to the CLI parser."""
    explain = sub.add_parser(
        "explain",
        help="Explain a task using AI (requires Ollama)",
        description=(
            "Use a local LLM via Ollama to analyse or plan a task.\n\n"
            "Modes:\n"
            "  --short   Quick 2 or 3 sentence summary (default)\n"
            "  --deep    In-depth analysis with risks and approach\n"
            "  --plan    Step-by-step action plan with time estimate\n\n"
            "Examples:\n"
            "  rt explain 5\n"
            "  rt explain 5 --short\n"
            "  rt explain 12 --deep\n"
            "  rt explain 3 --plan\n"
            "  rt explain --config\n"
            "  rt explain --config --model mistral\n\n"
            "Config file: ~/.local/share/raztodo/ollama.json\n"
            "Environment variables override config file:\n"
            "  OLLAMA_HOST     Ollama server URL\n"
            "  OLLAMA_MODEL    Model name\n"
            "  OLLAMA_TIMEOUT  Request timeout in seconds"
        ),
        formatter_class=CLIHelpFormatter,
    )

    explain.add_argument(
        "id",
        type=int,
        nargs="?",
        help="ID of the task to explain",
    )

    mode_group = explain.add_mutually_exclusive_group()
    mode_group.add_argument(
        "--short",
        dest="mode",
        action="store_const",
        const="short",
        help="Brief summary (default)",
    )
    mode_group.add_argument(
        "--deep",
        dest="mode",
        action="store_const",
        const="deep",
        help="Deep analysis with risks and approach",
    )
    mode_group.add_argument(
        "--plan",
        dest="mode",
        action="store_const",
        const="plan",
        help="Concrete step-by-step action plan",
    )

    explain.add_argument(
        "--config",
        action="store_true",
        help="View or update Ollama config (no task ID needed)",
    )
    explain.add_argument(
        "--model",
        metavar="NAME",
        help="Set the Ollama model (used with --config)",
    )
    explain.add_argument(
        "--host",
        metavar="URL",
        help="Set the Ollama server URL (used with --config)",
    )
    explain.add_argument(
        "--timeout",
        type=int,
        metavar="SECONDS",
        help="Set the request timeout in seconds (used with --config)",
    )
    explain.add_argument(
        "--system-prompt",
        metavar="TEXT",
        help="Set the system prompt sent to the model (used with --config)",
    )
    explain.add_argument(
        "--json",
        action="store_true",
        help="Output result in JSON format",
    )


class ExplainTaskHandler:
    """Callable class that executes the 'explain' command."""

    def __init__(self, uc: Any) -> None:
        self.uc = uc

    def __call__(self, args: argparse.Namespace) -> int:
        try:
            if getattr(args, "config", False):
                return self._handle_config(args)

            task_id: int | None = getattr(args, "id", None)
            if task_id is None:
                print("task ID is required unless using --config", file=sys.stderr)
                return 1

            mode: str = getattr(args, "mode", None) or "short"
            json_mode: bool = getattr(args, "json", False)

            mode_labels = {"short": "Summary", "deep": "Deep Analysis", "plan": "Action Plan"}
            label = mode_labels.get(mode, mode.capitalize())

            if not json_mode:
                _loading(label)

            result: str = self.uc.execute(task_id, mode=mode)

            if not json_mode:
                _clear_loading(label)

            if json_mode:
                json.dump(
                    {"id": task_id, "mode": mode, "explanation": result},
                    sys.stdout,
                    ensure_ascii=False,
                    indent=2,
                )
                print()
            else:
                print(f"\n{label} for task #{task_id}\n")
                print(result)
                print()

            return 0

        except Exception as e:
            return handle_command_error(e, args)

    def _handle_config(self, args: argparse.Namespace) -> int:
        from raztodo.infrastructure.llm.config import (
            config_path,
            load_config,
            save_config,
        )

        cfg = load_config()
        changed = False

        if model := getattr(args, "model", None):
            cfg.model = model
            changed = True
        if host := getattr(args, "host", None):
            cfg.host = host.rstrip("/")
            changed = True
        if timeout := getattr(args, "timeout", None):
            cfg.timeout = timeout
            changed = True
        if system_prompt := getattr(args, "system_prompt", None):
            cfg.system_prompt = system_prompt
            changed = True

        if changed:
            path = save_config(cfg)
            print(f"Config saved to {path}\n")

        if getattr(args, "json", False):
            data = cfg.to_dict()
            data["_config_file"] = str(config_path())
            json.dump(data, sys.stdout, ensure_ascii=False, indent=2)
            print()
        else:
            path = config_path()
            status = "exists" if path.exists() else "not created yet (using defaults)"
            print(f"Ollama config  [{path}  {status}]\n")
            print(f"  model         {cfg.model}")
            print(f"  host          {cfg.host}")
            print(f"  timeout       {cfg.timeout}s")
            print(
                f"  system_prompt {cfg.system_prompt[:60]}{'…' if len(cfg.system_prompt) > 60 else ''}"
            )
            print()
            print("To update: rt explain --config --model <name> --host <url>")

        return 0
