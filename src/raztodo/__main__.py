import sys

from raztodo.domain.exceptions import RazTodoException
from raztodo.infrastructure.container import AppContainer
from raztodo.infrastructure.logger import get_logger
from raztodo.presentation.cli.entrypoint import run_cli

logger = get_logger("main")


def main() -> int:
    container = AppContainer()
    handler = container.task_handler

    try:
        return run_cli(handler=handler)
    except RazTodoException as e:
        logger.exception(e)
        print(f"[Error] {e}", file=sys.stderr)
        return 1
    except Exception as e:
        logger.exception(e)
        print("[Fatal] Unexpected error.", file=sys.stderr)
        return 1
    finally:
        container.close_singleton()


if __name__ == "__main__":
    sys.exit(main())
