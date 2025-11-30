import os
import sys
from pathlib import Path

from raztodo.infrastructure.settings import Settings


def test_default_data_dir_linux(tmp_path, monkeypatch):
    monkeypatch.setattr(Path, "home", lambda: tmp_path)
    monkeypatch.setattr(sys, "platform", "linux", raising=False)
    monkeypatch.delenv("RAZTODO_DB", raising=False)

    s = Settings()

    expected = tmp_path / ".local" / "share" / "raztodo"
    assert s.data_dir == expected
    assert expected.exists() and expected.is_dir()


def test_default_db_path_relative(tmp_path, monkeypatch):
    monkeypatch.setattr(Path, "home", lambda: tmp_path)
    monkeypatch.setattr(sys, "platform", "linux", raising=False)
    monkeypatch.delenv("RAZTODO_DB", raising=False)

    s = Settings()
    assert s.db_name == "tasks.db"
    assert s.db_path == s.data_dir / "tasks.db"


def test_env_db_absolute(tmp_path, monkeypatch):
    abs_db = tmp_path / "custom.db"
    monkeypatch.setenv("RAZTODO_DB", str(abs_db))
    monkeypatch.setattr(Path, "home", lambda: tmp_path)
    monkeypatch.setattr(sys, "platform", "linux", raising=False)

    s = Settings()
    assert s.db_name == str(abs_db)
    assert s.db_path == abs_db


def test_windows_appdata(monkeypatch, tmp_path):
    appdata = tmp_path / "AppData" / "Roaming"
    monkeypatch.setenv("APPDATA", str(appdata))
    monkeypatch.setattr(sys, "platform", "win32", raising=False)
    monkeypatch.delenv("RAZTODO_DB", raising=False)
    monkeypatch.delenv("GITHUB_ACTIONS", raising=False)

    s = Settings()

    expected = Path(os.getenv("APPDATA")) / "raztodo"
    assert s.data_dir == expected
    assert expected.exists() and expected.is_dir()


def test_darwin_home(monkeypatch, tmp_path):
    monkeypatch.setattr(Path, "home", lambda: tmp_path)
    monkeypatch.setattr(sys, "platform", "darwin", raising=False)
    monkeypatch.delenv("RAZTODO_DB", raising=False)

    s = Settings()

    expected = tmp_path / "Library" / "Application Support" / "raztodo"
    assert s.data_dir == expected
    assert expected.exists() and expected.is_dir()
