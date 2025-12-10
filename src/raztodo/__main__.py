import sys

from raztodo.infrastructure.container import AppContainer
from raztodo.infrastructure.logger import get_logger
from raztodo.presentation.cli.entrypoint import run_cli

logger = get_logger("__main__")


def main() -> int:
    container = AppContainer()
    handler = container.task_handler

    try:
        return run_cli(handler=handler)
    except Exception as e:
        logger.exception(e)
        print("[Fatal] Unexpected error.", file=sys.stderr)
        return 1
    finally:
        container.close_singleton()


if __name__ == "__main__":
    sys.exit(main())
