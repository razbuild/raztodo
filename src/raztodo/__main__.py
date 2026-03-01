import sys

from raztodo.infrastructure.container import AppContainer
from raztodo.infrastructure.logger import get_logger
from raztodo.presentation.cli.entrypoint import run_cli

logger = get_logger("__main__")


def build_router():
    """
    Lazy application bootstrap.
    This is only executed for real commands like add/list/update.
    NOT for --help, --version, or completion.
    """
    from raztodo.presentation.cli.entrypoint import create_router

    container = AppContainer()

    # store on function so we can close later
    build_router._container = container

    return create_router(
        storage=container.repo_singleton(),
        connection_factory=container.connection_factory(),
    )


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
        container = getattr(build_router, "_container", None)
        if container:
            container.close_singleton()


if __name__ == "__main__":
    sys.exit(main())