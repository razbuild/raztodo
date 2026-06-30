import os
import sys
import tempfile
from pathlib import Path


def resolve_data_dir() -> Path:
    """
    Resolve platform-specific data directory (no side effects).
    """
    if sys.platform == "win32" and os.getenv("GITHUB_ACTIONS") == "true":
        path = Path(tempfile.gettempdir()) / "raztodo"

    elif sys.platform == "win32":
        path = Path(os.getenv("APPDATA", Path.home() / "AppData" / "Roaming")) / "raztodo"

    elif sys.platform == "darwin":
        path = Path.home() / "Library" / "Application Support" / "raztodo"

    else:
        path = Path.home() / ".local" / "share" / "raztodo"

    return path


class Settings:
    """
    Lightweight environment-based settings holder.
    """

    def __init__(self) -> None:
        self.db_name = os.getenv("RAZTODO_DB", "tasks.db")

    @property
    def data_dir(self) -> Path:
        path = resolve_data_dir()
        path.mkdir(parents=True, exist_ok=True)
        return path

    def resolve_db_path(self, db_name: str | None = None) -> Path:
        db_name = db_name or self.db_name

        path = Path(db_name)
        return path if path.is_absolute() else self.data_dir / path
