import sys

from raztodo.infrastructure.container import AppContainer
from raztodo.infrastructure.logger import get_logger
from raztodo.presentation.cli.entrypoint import create_router, run_cli

logger = get_logger("__main__")


class LazyRouterBuilder:

    def __init__(self) -> None:
        self._container: AppContainer | None = None

    def __call__(self):
        container = AppContainer()
        self._container = container
        return create_router(
            storage=container.repo_singleton(),
            connection_factory=container.connection_factory(),
        )


build_router = LazyRouterBuilder()


def main() -> int:
    try:
        return run_cli(router_factory=build_router)
    except Exception as e:
        from raztint import err

        logger.exception(e)
        print(f"{err()} Unexpected error.", file=sys.stderr)
        return 1
    finally:
        # Close container ONLY if it was actually created
        container = build_router._container
        if container:
            container.close_singleton()


if __name__ == "__main__":
    sys.exit(main())
