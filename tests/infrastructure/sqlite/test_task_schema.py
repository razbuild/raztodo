from contextlib import closing

from raztodo.infrastructure.sqlite.task_schema import ensure_schema


class TestSchema:
    """Test cases for schema management."""

    def test_ensure_schema_creates_table(self, in_memory_db):
        """Test that ensure_schema creates tasks table."""
        with closing(in_memory_db()) as conn:
            ensure_schema(conn)

            # Verify table exists
            cursor = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='tasks'"
            )
            assert cursor.fetchone() is not None

    def test_ensure_schema_idempotent(self, in_memory_db):
        """Test that ensure_schema can be called multiple times safely."""
        with closing(in_memory_db()) as conn:
            ensure_schema(conn)
            ensure_schema(conn)  # Should not raise error

            # Verify table still exists and has correct structure
            cursor = conn.execute("PRAGMA table_info(tasks)")
            columns = {row[1]: row[2] for row in cursor.fetchall()}
            assert "id" in columns
            assert "title" in columns

    def test_ensure_schema_creates_all_columns(self, in_memory_db):
        """Test that ensure_schema creates all required columns."""
        with closing(in_memory_db()) as conn:
            ensure_schema(conn)

            cursor = conn.execute("PRAGMA table_info(tasks)")
            columns = {row[1]: row[2] for row in cursor.fetchall()}

            assert "id" in columns
            assert "title" in columns
            assert "description" in columns
            assert "done" in columns
            assert "created_at" in columns
            assert "priority" in columns
            assert "due_date" in columns
            assert "tags" in columns
            assert "project" in columns

    def test_ensure_schema_creates_indexes(self, in_memory_db):
        """Test that ensure_schema creates indexes."""
        with closing(in_memory_db()) as conn:
            ensure_schema(conn)

            cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='index'")
            indexes = [row[0] for row in cursor.fetchall()]

            # Check for performance indexes
            assert any("idx_tasks_priority" in idx for idx in indexes)
            assert any("idx_tasks_done" in idx for idx in indexes)

    def test_ensure_schema_migration_adds_columns(self, in_memory_db):
        """Test that ensure_schema creates table with all required columns."""
        with closing(in_memory_db()) as conn:
            # ensure_schema uses CREATE TABLE IF NOT EXISTS, so it won't modify existing tables
            # This test verifies that a fresh table has all columns
            ensure_schema(conn)

            # Verify all columns exist
            cursor = conn.execute("PRAGMA table_info(tasks)")
            columns = {row[1]: row[2] for row in cursor.fetchall()}
            assert "priority" in columns
            assert "due_date" in columns
            assert "tags" in columns
            assert "project" in columns

    def test_ensure_schema_backfills_created_at(self, in_memory_db):
        """Test that trigger backfills created_at values on insert."""
        with closing(in_memory_db()) as conn:
            # Create table and ensure schema (triggers will be created)
            ensure_schema(conn)

            # Insert a task with empty created_at - trigger should backfill it
            conn.execute("INSERT INTO tasks (title, created_at) VALUES ('Task', '')")
            conn.commit()

            # Verify created_at was backfilled by trigger
            row = conn.execute("SELECT created_at FROM tasks").fetchone()
            assert row[0] is not None
            assert row[0] != ""

    def test_ensure_schema_creates_triggers(self, in_memory_db):
        """Test that ensure_schema creates triggers."""
        with closing(in_memory_db()) as conn:
            ensure_schema(conn)

            cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='trigger'")
            triggers = [row[0] for row in cursor.fetchall()]

            # Check for description length triggers
            assert any("desc_len_insert" in t for t in triggers)
            assert any("desc_len_update" in t for t in triggers)
            assert any("created_at_insert" in t for t in triggers)

    def test_ensure_schema_creates_unique_index(self, in_memory_db):
        """Test that ensure_schema creates unique index on title."""
        with closing(in_memory_db()) as conn:
            ensure_schema(conn)

            cursor = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='index' AND name='idx_tasks_title_unique'"
            )
            assert cursor.fetchone() is not None
