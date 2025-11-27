import json
import sqlite3
from contextlib import closing

from raztodo.infrastructure.sqlite.task_mapper import row_to_task


class TestRowToTask:
    """Test cases for row_to_task mapper."""

    def test_map_row_to_task_minimal(self):
        """Test mapping row with minimal fields."""
        with closing(sqlite3.connect(":memory:")) as conn:
            conn.row_factory = sqlite3.Row
            conn.execute("CREATE TABLE test (id INTEGER, title TEXT, description TEXT)")
            conn.execute("INSERT INTO test VALUES (1, 'Task', 'Description')")
            row = conn.execute("SELECT * FROM test").fetchone()

            task = row_to_task(row)

            assert task.id == 1
            assert task.title == "Task"
            assert task.description == "Description"
            assert task.done is False
            assert task.tags == []

    def test_map_row_with_done_flag(self):
        """Test mapping row with done flag."""
        with closing(sqlite3.connect(":memory:")) as conn:
            conn.row_factory = sqlite3.Row
            conn.execute("CREATE TABLE test (id INTEGER, title TEXT, done INTEGER)")
            conn.execute("INSERT INTO test VALUES (1, 'Task', 1)")
            row = conn.execute("SELECT * FROM test").fetchone()

            task = row_to_task(row)

            assert task.done is True

    def test_map_row_with_json_tags(self):
        """Test mapping row with JSON tags."""
        with closing(sqlite3.connect(":memory:")) as conn:
            conn.row_factory = sqlite3.Row
            tags_json = json.dumps(["tag1", "tag2", "tag3"])
            conn.execute("CREATE TABLE test (id INTEGER, title TEXT, tags TEXT)")
            conn.execute("INSERT INTO test VALUES (1, 'Task', ?)", (tags_json,))
            row = conn.execute("SELECT * FROM test").fetchone()

            task = row_to_task(row)

            assert task.tags == ["tag1", "tag2", "tag3"]

    def test_map_row_with_comma_separated_tags(self):
        """Test mapping row with comma-separated tags."""
        with closing(sqlite3.connect(":memory:")) as conn:
            conn.row_factory = sqlite3.Row
            conn.execute("CREATE TABLE test (id INTEGER, title TEXT, tags TEXT)")
            conn.execute("INSERT INTO test VALUES (1, 'Task', 'tag1, tag2, tag3')")
            row = conn.execute("SELECT * FROM test").fetchone()

            task = row_to_task(row)

            assert task.tags == ["tag1", "tag2", "tag3"]

    def test_map_row_with_all_fields(self):
        """Test mapping row with all fields."""
        with closing(sqlite3.connect(":memory:")) as conn:
            conn.row_factory = sqlite3.Row
            tags_json = json.dumps(["tag1", "tag2"])
            conn.execute(
                """
                CREATE TABLE test (
                    id INTEGER, title TEXT, description TEXT, done INTEGER,
                    created_at TEXT, priority TEXT, due_date TEXT, tags TEXT, project TEXT
                )
            """
            )
            conn.execute(
                """
                INSERT INTO test VALUES (1, 'Task', 'Desc', 1, '2025-01-31 12:00:00', 
                                        'H', '2025-02-01', ?, 'Project')
            """,
                (tags_json,),
            )
            row = conn.execute("SELECT * FROM test").fetchone()

            task = row_to_task(row)

            assert task.id == 1
            assert task.title == "Task"
            assert task.description == "Desc"
            assert task.done is True
            assert task.created_at == "2025-01-31 12:00:00"
            assert task.priority == "H"
            assert task.due_date == "2025-02-01"
            assert task.tags == ["tag1", "tag2"]
            assert task.project == "Project"

    def test_map_row_with_empty_tags(self):
        """Test mapping row with empty tags."""
        with closing(sqlite3.connect(":memory:")) as conn:
            conn.row_factory = sqlite3.Row
            conn.execute("CREATE TABLE test (id INTEGER, title TEXT, tags TEXT)")
            conn.execute("INSERT INTO test VALUES (1, 'Task', '')")
            row = conn.execute("SELECT * FROM test").fetchone()

            task = row_to_task(row)

            assert task.tags == []

    def test_map_row_with_none_tags(self):
        """Test mapping row with None tags."""
        with closing(sqlite3.connect(":memory:")) as conn:
            conn.row_factory = sqlite3.Row
            conn.execute("CREATE TABLE test (id INTEGER, title TEXT, tags TEXT)")
            conn.execute("INSERT INTO test VALUES (1, 'Task', NULL)")
            row = conn.execute("SELECT * FROM test").fetchone()

            task = row_to_task(row)

            assert task.tags == []

    def test_map_row_with_missing_fields(self):
        """Test mapping row with missing optional fields."""
        with closing(sqlite3.connect(":memory:")) as conn:
            conn.row_factory = sqlite3.Row
            conn.execute("CREATE TABLE test (id INTEGER, title TEXT)")
            conn.execute("INSERT INTO test VALUES (1, 'Task')")
            row = conn.execute("SELECT * FROM test").fetchone()

            task = row_to_task(row)

            assert task.id == 1
            assert task.title == "Task"
            assert task.description == ""
            assert task.done is False
            assert task.created_at == ""
            assert task.priority == ""
            assert task.due_date is None
            assert task.tags == []
            assert task.project is None
