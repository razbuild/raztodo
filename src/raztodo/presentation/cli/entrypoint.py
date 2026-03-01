import sys
from typing import Any, Protocol
import argcomplete  

from raztodo.domain.exceptions import RazTodoException
from raztodo.infrastructure.logger import get_logger
from raztodo.presentation.cli.parser import get_parser
from raztodo.presentation.cli.router import TaskRouter

logger = get_logger("entrypoint")


class HandlerProtocol(Protocol):
    def get_command_class(self, name: str) -> type: ...
    def get_usecase(self, name: str) -> Any: ...


def create_router(storage: Any, connection_factory: Any) -> TaskRouter:
    return TaskRouter(storage, connection_factory)


def run_cli(router_factory, argv: list[str] | None = None) -> int:
    from raztint import err, info
    import os

    argv = argv or sys.argv[1:]
    parser = get_parser()

    # Hook argcomplete BEFORE parsing args
    argcomplete.autocomplete(parser)

    try:
        args = parser.parse_args(argv)

        # ---- COMPLETION SHORT-CIRCUIT ----
        if getattr(args, "command", None) == "completion":
            from raztodo.presentation.cli.commands.completion_cmd import CompletionCMD

            shell = getattr(args, "shell", None)
            return CompletionCMD()(shell)

        if not args.command:
            parser.print_help()
            return 2

        # Normal flow
        handler = router_factory()
        command_class = handler.get_command_class(args.command)
        use_case = handler.get_usecase(args.command)
        command_handler = command_class(use_case)
        return command_handler(args) or 0

    except KeyboardInterrupt:
        logger.info(f"Command '{getattr(args, 'command', None)}' interrupted by user")
        print(f"\n{info()} Operation cancelled", file=sys.stderr)
        return 130

    except SystemExit:
        raise

    except RazTodoException as e:
        logger.exception(f"Domain error: {e}")
        print(f"{err()} {e}", file=sys.stderr)
        return 1

    except Exception as e:
        logger.exception(f"Unexpected error: {e}")
        print(f"{err()} Unexpected error: {e}", file=sys.stderr)
        return 1