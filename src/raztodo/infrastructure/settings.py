import os
from pathlib import Path


class Settings:
    def __init__(self) -> None:
        self.db_name = os.getenv("RAZTODO_DB", "tasks.db")
        self.data_dir = self._resolve_data_dir()

    def _resolve_data_dir(self) -> Path:
        if os.name == "nt":
            path = (
                Path(os.getenv("APPDATA", Path.home() / "AppData" / "Roaming"))
                / "raztodo"
            )
        else:
            path = (
                Path(os.getenv("XDG_DATA_HOME", Path.home() / ".local" / "share"))
                / "raztodo"
            )

        path.mkdir(parents=True, exist_ok=True)
        return path

    @property
    def db_path(self) -> Path:
        path = Path(self.db_name)
        return path if path.is_absolute() else self.data_dir / path
