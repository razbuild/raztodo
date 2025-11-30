import os
import sqlite3
import tempfile

from raztodo.application.use_cases.migrate_tasks import MigrateUseCase


class TestMigrateUseCase:
    """Test cases for MigrateUseCase."""

    def test_migrate_execute(self):
        """Test migration execution."""
        # Use a temporary file database so multiple connections can access it
        fd, temp_path = tempfile.mkstemp(suffix=".db")
        os.close(fd)

        try:

            def connection_factory():
                conn = sqlite3.connect(temp_path, check_same_thread=False)
                conn.row_factory = sqlite3.Row
                return conn

            use_case = MigrateUseCase(connection_factory)

            # Create connection and add some duplicate tasks
            conn = connection_factory()
            conn.execute(
                """
                CREATE TABLE tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL
                )
            """
            )
            conn.execute("INSERT INTO tasks (title) VALUES ('Duplicate')")
            conn.execute("INSERT INTO tasks (title) VALUES ('Duplicate')")
            conn.execute("INSERT INTO tasks (title) VALUES ('Unique')")
            conn.commit()
            conn.close()

            result = use_case.execute()

            assert "duplicates_fixed" in result
            assert "unique_index" in result
            assert result["unique_index"] is True
            assert result["duplicates_fixed"] >= 0

        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    def test_migrate_empty_database(self):
        """Test migration on empty database."""
        # Use a temporary file database so multiple connections can access it
        fd, temp_path = tempfile.mkstemp(suffix=".db")
        os.close(fd)

        try:

            def connection_factory():
                conn = sqlite3.connect(temp_path, check_same_thread=False)
                conn.row_factory = sqlite3.Row
                return conn

            use_case = MigrateUseCase(connection_factory)

            # Create empty table
            conn = connection_factory()
            conn.execute(
                """
                CREATE TABLE tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL
                )
            """
            )
            conn.commit()
            conn.close()

            result = use_case.execute()

            assert result["duplicates_fixed"] == 0
            assert result["unique_index"] is True

        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    def test_migrate_with_existing_index(self):
        """Test migration when index already exists."""
        fd, temp_path = tempfile.mkstemp(suffix=".db")
        os.close(fd)

        try:

            def connection_factory():
                conn = sqlite3.connect(temp_path, check_same_thread=False)
                conn.row_factory = sqlite3.Row
                return conn

            use_case = MigrateUseCase(connection_factory)

            # Create table with existing index
            conn = connection_factory()
            conn.execute(
                """
                CREATE TABLE tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL
                )
            """
            )
            conn.execute(
                "CREATE UNIQUE INDEX IF NOT EXISTS idx_tasks_title_unique ON tasks(title)"
            )
            conn.commit()
            conn.close()

            result = use_case.execute()

            assert result["unique_index"] is True
            assert result["duplicates_fixed"] == 0

        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
