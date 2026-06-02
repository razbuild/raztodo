import sys

from raztint import err

from raztodo.infrastructure.container import AppContainer
from raztodo.infrastructure.logger import get_logger
from raztodo.presentation.cli.entrypoint import create_router, run_cli

logger = get_logger("__main__")


class LazyRouterBuilder:
    """Lazily builds the CLI router and manages the application container lifecycle."""

    def __init__(self) -> None:
        self._container: AppContainer | None = None

    def __call__(self):
        if self._container is None:
            self._container = AppContainer()
        return create_router(
            storage=self._container.repo_singleton(),
            connection_factory=self._container.connection_factory(),
        )

    def close_container(self) -> None:
        if self._container is not None:
            try:
                self._container.close_singleton()
            except Exception:
                logger.exception("Error while closing container")
            finally:
                self._container = None


build_router = LazyRouterBuilder()


def main() -> int:
    try:
        return run_cli(router_factory=build_router)
    except Exception as e:
        logger.exception("Unexpected error")
        print(f"{err()} Unexpected error: {e}", file=sys.stderr)
        return 1
    finally:
        build_router.close_container()


if __name__ == "__main__":
    sys.exit(main())
