import os
import sqlite3
from collections.abc import Callable
from pathlib import Path


def default_data_dir(app_name: str = "raztodo") -> Path:
    if os.name == "nt":  # Windows
        path = (
            Path(os.getenv("APPDATA", Path.home() / "AppData" / "Roaming")) / app_name
        )
    else:  # Linux / macOS
        path = (
            Path(os.getenv("XDG_DATA_HOME", Path.home() / ".local" / "share"))
            / app_name
        )
    path.mkdir(parents=True, exist_ok=True)
    return path


def sqlite_connection_factory(
    db_name: str | None = "tasks.db",
) -> Callable[[], sqlite3.Connection]:

    def factory() -> sqlite3.Connection:
        if db_name is None:
            conn = sqlite3.connect(":memory:", check_same_thread=False)
        else:
            db_path = default_data_dir() / db_name
            conn = sqlite3.connect(str(db_path), check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn

    return factory
