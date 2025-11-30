import os
from pathlib import Path

import pytest

from raztodo.infrastructure.sqlite.connection import (
    default_data_dir,
    sqlite_connection_factory,
)


@pytest.fixture
def temp_db(tmp_path):
    """Fixture to provide a temporary database path."""
    return str(tmp_path / "test.db")


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


class TestDefaultDataDir:
    """Test cases for default_data_dir function."""

    def test_default_data_dir_linux(self, monkeypatch):
        """Test default data dir on Linux."""
        monkeypatch.setattr("sys.platform", "linux")
        path = default_data_dir()
        expected = Path.home() / ".local/share/raztodo"
        assert path == expected

    def test_default_data_dir_custom_app_name(self, monkeypatch):
        """Test default data dir with custom app name."""
        monkeypatch.setattr("sys.platform", "linux")
        path = default_data_dir("myapp")
        expected = Path.home() / ".local/share/myapp"
        assert path == expected

    def test_default_data_dir_windows(self, monkeypatch):
        """Test default data dir on Windows."""
        monkeypatch.setattr("sys.platform", "win32")
        monkeypatch.delenv("GITHUB_ACTIONS", raising=False)
        monkeypatch.setenv("APPDATA", "/tmp/appdata")

        path = default_data_dir("myapp")
        assert path == Path("/tmp/appdata/myapp")

    def test_default_data_dir_macos(self, monkeypatch):
        """Test default data dir on macOS."""
        monkeypatch.setattr("sys.platform", "darwin")
        path = default_data_dir("myapp")
        expected = Path.home() / "Library/Application Support/myapp"
        assert path == expected
