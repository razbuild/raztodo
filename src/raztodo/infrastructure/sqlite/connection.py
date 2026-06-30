import sqlite3
from collections.abc import Callable
from pathlib import Path


def sqlite_connection_factory(
    db_path: Path | None,
) -> Callable[[], sqlite3.Connection]:

    def factory() -> sqlite3.Connection:
        if db_path is None:
            conn = sqlite3.connect(":memory:", check_same_thread=False)
        else:
            conn = sqlite3.connect(str(db_path), check_same_thread=False)

        conn.row_factory = sqlite3.Row
        return conn

    return factory
