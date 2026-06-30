import os
from pathlib import Path

import pytest

from raztodo.infrastructure.settings import Settings
from raztodo.infrastructure.sqlite.connection import sqlite_connection_factory


@pytest.fixture
def temp_db(tmp_path):
    return tmp_path / "test.db"


class TestConnectionFactory:
    """Test cases for connection factory."""

    def test_in_memory_connection(self):
        """Test creating in-memory connection."""
        factory = sqlite_connection_factory(None)
        conn1 = factory()
        conn2 = factory()

        assert conn1 is not conn2

        conn1.execute("CREATE TABLE test (id INTEGER)")
        conn1.execute("INSERT INTO test VALUES (1)")
        conn1.close()
        conn2.close()

    def test_file_connection(self, temp_db):
        """Test creating file-based connection."""
        factory = sqlite_connection_factory(temp_db)
        conn = factory()

        conn.execute("CREATE TABLE test (id INTEGER)")
        conn.execute("INSERT INTO test VALUES (1)")
        conn.commit()
        conn.close()

        assert os.path.exists(temp_db)

    def test_multiple_connections_same_db(self, temp_db):
        """Test that multiple connections to same DB work."""
        factory = sqlite_connection_factory(temp_db)
        conn1 = factory()
        conn2 = factory()

        conn1.execute("CREATE TABLE test (id INTEGER)")
        conn1.execute("INSERT INTO test VALUES (1)")
        conn1.commit()
        conn1.close()

        cursor = conn2.execute("SELECT COUNT(*) FROM test")
        assert cursor.fetchone()[0] == 1
        conn2.close()

    def test_row_factory_set(self):
        """Test that row factory is set correctly."""
        factory = sqlite_connection_factory(None)
        conn = factory()

        conn.execute("CREATE TABLE test (id INTEGER, name TEXT)")
        conn.execute("INSERT INTO test VALUES (1, 'Test')")

        row = conn.execute("SELECT * FROM test").fetchone()
        assert hasattr(row, "keys")
        assert row["id"] == 1
        assert row["name"] == "Test"
        conn.close()


class TestSettings:
    def test_linux_data_dir(self, monkeypatch):
        monkeypatch.setattr("sys.platform", "linux")

        settings = Settings()

        assert settings.data_dir == Path.home() / ".local/share/raztodo"

    def test_windows_data_dir(self, monkeypatch):
        monkeypatch.setattr("sys.platform", "win32")
        monkeypatch.delenv("GITHUB_ACTIONS", raising=False)
        monkeypatch.setenv("APPDATA", "/tmp/appdata")

        settings = Settings()

        assert settings.data_dir == Path("/tmp/appdata/raztodo")

    def test_macos_data_dir(self, monkeypatch):
        monkeypatch.setattr("sys.platform", "darwin")

        settings = Settings()

        assert settings.data_dir == Path.home() / "Library/Application Support/raztodo"

    def test_resolve_db_path(self, monkeypatch):
        monkeypatch.setattr("sys.platform", "linux")

        settings = Settings()

        assert settings.resolve_db_path("tasks.db") == (
            Path.home() / ".local/share/raztodo/tasks.db"
        )

    def test_absolute_db_path(self):
        settings = Settings()

        path = Path("/tmp/test.db")

        assert settings.resolve_db_path(str(path)) == path
