"""Tests for connection factory."""

import os
import tempfile
from pathlib import Path

from raztodo.infrastructure.sqlite.connection import (
    default_data_dir,
    sqlite_connection_factory,
)


class TestConnectionFactory:
    """Test cases for connection factory."""

    def test_in_memory_connection(self):
        """Test creating in-memory connection."""
        factory = sqlite_connection_factory(None)
        conn1 = factory()
        conn2 = factory()

        # Each call should return a new connection
        assert conn1 is not conn2

        # Connections should work
        conn1.execute("CREATE TABLE test (id INTEGER)")
        conn1.execute("INSERT INTO test VALUES (1)")
        conn1.close()
        conn2.close()

    def test_file_connection(self, temp_db):
        """Test creating file-based connection."""
        factory = sqlite_connection_factory(temp_db)
        conn = factory()

        # Connection should work
        conn.execute("CREATE TABLE test (id INTEGER)")
        conn.execute("INSERT INTO test VALUES (1)")
        conn.close()

        # Verify file exists
        assert os.path.exists(temp_db)

    def test_multiple_connections_same_db(self, temp_db):
        """Test that multiple connections to same DB work."""
        factory = sqlite_connection_factory(temp_db)
        conn1 = factory()
        conn2 = factory()

        # Both should be able to use the database
        conn1.execute("CREATE TABLE test (id INTEGER)")
        conn1.execute("INSERT INTO test VALUES (1)")
        conn1.commit()
        conn1.close()

        # Second connection should see the table
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

    def test_default_data_dir_no_xdg(self):
        """Test default data dir without XDG_DATA_HOME."""
        os.environ.pop("XDG_DATA_HOME", None)
        path = default_data_dir()

        expected = Path.home() / ".local/share/raztodo"
        assert path == expected

    def test_default_data_dir_with_xdg(self):
        """Test default data dir with XDG_DATA_HOME."""
        with tempfile.TemporaryDirectory() as tmpdir:
            os.environ["XDG_DATA_HOME"] = tmpdir
            try:
                path = default_data_dir()
                expected = Path(tmpdir) / "raztodo"
                assert path == expected
            finally:
                os.environ.pop("XDG_DATA_HOME", None)

    def test_default_data_dir_custom_app_name(self):
        """Test default data dir with custom app name."""
        path = default_data_dir("myapp")

        expected = Path.home() / ".local/share/myapp"
        assert path == expected
