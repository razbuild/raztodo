from raztodo.infrastructure.sqlite.migrations import (
    create_unique_title_index,
    deduplicate_titles,
)


class TestMigrations:
    """Test cases for migration functions."""

    def test_deduplicate_titles(self, in_memory_db):
        """Test deduplicating titles."""
        conn = in_memory_db()
        try:
            conn.execute(
                """
                CREATE TABLE tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL
                )
            """
            )

            # Create duplicate titles
            conn.execute("INSERT INTO tasks (title) VALUES ('Duplicate')")
            conn.execute("INSERT INTO tasks (title) VALUES ('Duplicate')")
            conn.execute("INSERT INTO tasks (title) VALUES ('Duplicate')")
            conn.execute("INSERT INTO tasks (title) VALUES ('Unique')")

            updated = deduplicate_titles(conn)

            assert updated == 2  # Two duplicates should be renamed

            # Verify titles are now unique
            rows = conn.execute("SELECT title FROM tasks ORDER BY id").fetchall()
            titles = [row[0] for row in rows]

            assert "Duplicate" in titles
            assert "Duplicate (2)" in titles
            assert "Duplicate (3)" in titles
            assert "Unique" in titles
            assert len(set(titles)) == len(titles)  # All unique
        finally:
            conn.close()

    def test_deduplicate_titles_no_duplicates(self, in_memory_db):
        """Test deduplicate with no duplicates."""
        conn = in_memory_db()
        try:
            conn.execute(
                """
                CREATE TABLE tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL
                )
            """
            )

            conn.execute("INSERT INTO tasks (title) VALUES ('Task 1')")
            conn.execute("INSERT INTO tasks (title) VALUES ('Task 2')")

            updated = deduplicate_titles(conn)

            assert updated == 0
        finally:
            conn.close()

    def test_create_unique_title_index(self, in_memory_db):
        """Test creating unique title index."""
        conn = in_memory_db()
        try:
            conn.execute(
                """
                CREATE TABLE tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL
                )
            """
            )

            create_unique_title_index(conn)

            # Verify index exists
            cursor = conn.execute(
                """
                SELECT name FROM sqlite_master 
                WHERE type='index' AND name='idx_tasks_title_unique'
            """
            )
            assert cursor.fetchone() is not None
        finally:
            conn.close()

    def test_create_unique_index_idempotent(self, in_memory_db):
        """Test that creating index multiple times is safe."""
        conn = in_memory_db()
        try:
            conn.execute(
                """
                CREATE TABLE tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL
                )
            """
            )

            create_unique_title_index(conn)
            create_unique_title_index(conn)  # Should not raise error

            # Index should still exist
            cursor = conn.execute(
                """
                SELECT name FROM sqlite_master 
                WHERE type='index' AND name='idx_tasks_title_unique'
            """
            )
            assert cursor.fetchone() is not None
        finally:
            conn.close()
