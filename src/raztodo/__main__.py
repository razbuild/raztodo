import sys

from raztodo.infrastructure.container import AppContainer
from raztodo.infrastructure.logger import get_logger
from raztodo.presentation.cli.entrypoint import create_router, run_cli

logger = get_logger("__main__")


def main() -> int:
    container = AppContainer()
    handler = create_router(
        storage=container.repo_singleton(),
        connection_factory=container.connection_factory(),
    )

    try:
        return run_cli(handler=handler)
    except Exception as e:
        from raztint import err

        logger.exception(e)
        print(f"{err()} Unexpected error.", file=sys.stderr)
        return 1
    finally:
        container.close_singleton()


if __name__ == "__main__":
    sys.exit(main())
