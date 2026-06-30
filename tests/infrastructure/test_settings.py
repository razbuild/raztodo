import sys
import tempfile
from pathlib import Path

from raztodo.infrastructure.settings import Settings


def test_linux_data_dir(tmp_path, monkeypatch):
    monkeypatch.setattr(Path, "home", lambda: tmp_path)
    monkeypatch.setattr(sys, "platform", "linux", raising=False)
    monkeypatch.delenv("RAZTODO_DB", raising=False)

    s = Settings()

    expected = tmp_path / ".local" / "share" / "raztodo"

    assert s.data_dir == expected
    assert expected.exists()
    assert expected.is_dir()


def test_windows_github_actions_data_dir(monkeypatch):
    monkeypatch.setattr(sys, "platform", "win32", raising=False)
    monkeypatch.setenv("GITHUB_ACTIONS", "true")
    monkeypatch.setattr(tempfile, "gettempdir", lambda: "/tmp")

    s = Settings()

    expected = Path("/tmp") / "raztodo"

    assert s.data_dir == expected


def test_darwin_home(monkeypatch, tmp_path):
    monkeypatch.setattr(Path, "home", lambda: tmp_path)
    monkeypatch.setattr(sys, "platform", "darwin", raising=False)
    monkeypatch.delenv("RAZTODO_DB", raising=False)

    s = Settings()

    expected = tmp_path / "Library" / "Application Support" / "raztodo"

    assert s.data_dir == expected
    assert expected.exists()
    assert expected.is_dir()


def test_default_db_path_relative(tmp_path, monkeypatch):
    monkeypatch.setattr(Path, "home", lambda: tmp_path)
    monkeypatch.setattr(sys, "platform", "linux", raising=False)
    monkeypatch.delenv("RAZTODO_DB", raising=False)

    s = Settings()

    assert s.db_name == "tasks.db"
    assert s.resolve_db_path() == s.data_dir / "tasks.db"


def test_env_db_absolute(tmp_path, monkeypatch):
    abs_db = tmp_path / "custom.db"

    monkeypatch.setenv("RAZTODO_DB", str(abs_db))
    monkeypatch.setattr(Path, "home", lambda: tmp_path)
    monkeypatch.setattr(sys, "platform", "linux", raising=False)

    s = Settings()

    assert s.db_name == str(abs_db)
    assert s.resolve_db_path() == abs_db


def test_resolve_custom_relative_db(tmp_path, monkeypatch):
    monkeypatch.setattr(Path, "home", lambda: tmp_path)
    monkeypatch.setattr(sys, "platform", "linux", raising=False)

    s = Settings()

    expected = s.data_dir / "other.db"

    assert s.resolve_db_path("other.db") == expected


def test_resolve_custom_absolute_db(tmp_path, monkeypatch):
    monkeypatch.setattr(sys, "platform", "linux", raising=False)
    monkeypatch.setattr(Path, "home", lambda: tmp_path)

    s = Settings()

    db = tmp_path / "absolute.db"

    assert s.resolve_db_path(str(db)) == db


def test_data_dir_is_created(monkeypatch, tmp_path):
    monkeypatch.setattr(sys, "platform", "linux", raising=False)
    monkeypatch.setattr(Path, "home", lambda: tmp_path)

    s = Settings()

    assert s.data_dir.exists()
    assert s.data_dir.is_dir()
