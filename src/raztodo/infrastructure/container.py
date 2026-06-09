from collections.abc import Callable
from typing import Any

from raztodo.infrastructure.logger import get_logger
from raztodo.infrastructure.settings import Settings
from raztodo.infrastructure.sqlite.connection import sqlite_connection_factory
from raztodo.infrastructure.sqlite.task_repository import SQLiteTaskRepository


class AppContainer:
    _repo_singleton: SQLiteTaskRepository | None
    _connection_factory: Callable[..., Any]

    def __init__(self, db_name: str | None = None) -> None:
        self.config = Settings()
        self.logger = get_logger("raztodo")
        self._connection_factory = sqlite_connection_factory(
            db_name or self.config.db_name
        )
        self._repo_singleton = None

    def repo_singleton(self) -> SQLiteTaskRepository:
        if self._repo_singleton is None:
            self._repo_singleton = SQLiteTaskRepository(
                connection_factory=self._connection_factory
            )
        return self._repo_singleton

    def connection_factory(self) -> Callable[..., Any]:
        return self._connection_factory

    def close_singleton(self) -> None:
        if self._repo_singleton:
            self._repo_singleton.close()
            self._repo_singleton = None


def build_container() -> AppContainer:
    return AppContainer()
