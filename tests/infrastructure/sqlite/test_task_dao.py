import json
from unittest.mock import MagicMock

import pytest

from raztodo.infrastructure.sqlite.task_dao import TaskDAO


class TestTaskDAO:
    """Test cases for TaskDAO."""

    @pytest.fixture
    def db_and_dao(self, in_memory_db):
        """Create a TaskDAO instance and connection with in-memory database."""
        conn = in_memory_db()
        dao = TaskDAO(conn)
        yield conn, dao
        conn.close()

    @pytest.fixture
    def dao(self, db_and_dao):
        """Create a TaskDAO instance."""
        _, dao = db_and_dao
        return dao

    def test_insert_task(self, dao):
        """Test inserting a task."""
        task_id = dao.insert("Test Task", "Description")
        assert task_id is not None
        assert task_id > 0

    def test_insert_task_minimal(self, dao):
        """Test inserting task with minimal fields."""
        task_id = dao.insert("Task")
        assert task_id > 0

    def test_insert_task_all_fields(self, dao):
        """Test inserting task with all fields."""
        task_id = dao.insert(
            "Task",
            description="Description",
            priority="H",
            due_date="2025-02-01",
            tags=["tag1", "tag2"],
            project="Project",
        )
        assert task_id > 0

    def test_insert_task_tags_json(self, db_and_dao):
        """Test that tags are stored as JSON."""
        conn, dao = db_and_dao
        tags = ["tag1", "tag2", "tag3"]
        dao.insert("Task", tags=tags)

        # Verify tags are stored as JSON
        row = conn.execute("SELECT tags FROM tasks").fetchone()
        stored_tags = json.loads(row[0])
        assert stored_tags == tags

    def test_fetch_all_empty(self, dao):
        """Test fetching from empty table."""
        rows = list(dao.fetch_all())
        assert rows == []

    def test_fetch_all_tasks(self, dao):
        """Test fetching all tasks."""
        dao.insert("Task 1")
        dao.insert("Task 2")
        rows = list(dao.fetch_all())
        assert len(rows) == 2

    def test_fetch_all_with_limit(self, dao):
        """Test fetching tasks with limit."""
        for i in range(5):
            dao.insert(f"Task {i}")
        rows = list(dao.fetch_all(limit=2))
        assert len(rows) == 2

    def test_fetch_all_with_offset(self, dao):
        """Test fetching tasks with offset."""
        for i in range(5):
            dao.insert(f"Task {i}")
        rows = list(dao.fetch_all(offset=2))
        assert len(rows) == 3

    def test_fetch_all_with_limit_and_offset(self, dao):
        """Test fetching tasks with limit and offset."""
        for i in range(5):
            dao.insert(f"Task {i}")
        rows = list(dao.fetch_all(limit=2, offset=2))
        assert len(rows) == 2

    def test_fetch_all_filter_done(self, dao):
        """Test filtering by done status."""
        task_id1 = dao.insert("Task 1")
        dao.insert("Task 2")
        dao.update(task_id1, done=True)

        done_rows = list(dao.fetch_all(done=True))
        assert len(done_rows) == 1

        pending_rows = list(dao.fetch_all(done=False))
        assert len(pending_rows) == 1

    def test_fetch_all_filter_priority(self, dao):
        """Test filtering by priority."""
        dao.insert("Task H", priority="H")
        dao.insert("Task M", priority="M")

        high_rows = list(dao.fetch_all(priority="H"))
        assert len(high_rows) == 1

    def test_fetch_all_filter_project(self, dao):
        """Test filtering by project."""
        dao.insert("Task 1", project="Work")
        dao.insert("Task 2", project="Personal")

        work_rows = list(dao.fetch_all(project="Work"))
        assert len(work_rows) == 1

    def test_fetch_all_filter_due_dates(self, dao):
        """Test filtering by due_before and due_after dates."""
        dao.insert("Task 1", due_date="2025-01-10")
        dao.insert("Task 2", due_date="2025-01-20")
        dao.insert("Task 3", due_date="2025-01-30")

        before_rows = list(dao.fetch_all(due_before="2025-01-15"))
        assert len(before_rows) == 1
        assert before_rows[0]["title"] == "Task 1"

        after_rows = list(dao.fetch_all(due_after="2025-01-25"))
        assert len(after_rows) == 1
        assert after_rows[0]["title"] == "Task 3"

    def test_fetch_all_filter_tags(self, dao):
        """Test filtering by tags."""
        dao.insert("Task 1", tags=["home", "chores"])
        dao.insert("Task 2", tags=["work"])

        tag_rows = list(dao.fetch_all(tags=["home"]))
        assert len(tag_rows) == 1
        assert tag_rows[0]["title"] == "Task 1"

    def test_update_task_title(self, dao):
        """Test updating task title."""
        task_id = dao.insert("Old Title")
        result = dao.update(task_id, title="New Title")
        assert result > 0

        row = dao.fetch_by_id(task_id)
        assert row is not None
        assert row["title"] == "New Title"

    def test_update_task_done(self, dao):
        """Test updating task done status."""
        task_id = dao.insert("Task")
        result = dao.update(task_id, done=True)
        assert result > 0

        row = dao.fetch_by_id(task_id)
        assert row is not None
        assert row["done"] == 1

    def test_update_task_clear_due_date(self, dao):
        """Test clearing task due date."""
        task_id = dao.insert("Task", due_date="2025-02-01")
        result = dao.update(task_id, due_date="__CLEAR__")
        assert result > 0

        row = dao.fetch_by_id(task_id)
        assert row is not None
        assert row["due_date"] is None

    def test_update_task_clear_project(self, dao):
        """Test clearing task project."""
        task_id = dao.insert("Task", project="Work")
        result = dao.update(task_id, project="__CLEAR__")
        assert result > 0

        row = dao.fetch_by_id(task_id)
        assert row is not None
        assert row["project"] is None

    def test_update_task_tags(self, dao):
        """Test updating and clearing task tags."""
        task_id = dao.insert("Task", tags=["tag1"])
        result = dao.update(task_id, tags=["tag2", "tag3"])
        assert result > 0

        row = dao.fetch_by_id(task_id)
        assert row is not None
        assert json.loads(row["tags"]) == ["tag2", "tag3"]

        # Clear tags
        dao.update(task_id, tags=[])
        row_cleared = dao.fetch_by_id(task_id)
        assert row_cleared is not None
        assert row_cleared["tags"] is None

    def test_update_task_no_changes(self, dao):
        """Test updating task with no changes returns 0."""
        task_id = dao.insert("Task")
        result = dao.update(task_id)
        assert result == 0

    def test_delete_task(self, dao):
        """Test deleting a task."""
        task_id = dao.insert("Task")
        result = dao.delete(task_id)
        assert result > 0

        rows = list(dao.fetch_all())
        assert len(rows) == 0

    def test_delete_nonexistent_task(self, dao):
        """Test deleting nonexistent task returns 0."""
        result = dao.delete(999)
        assert result == 0

    def test_search_tasks(self, dao):
        """Test searching tasks."""
        dao.insert("Python Task", description="Learn Python")
        dao.insert("Java Task", description="Learn Java")

        rows = list(dao.search("Python"))
        assert len(rows) == 1
        assert "Python" in rows[0]["title"]

    def test_search_tasks_by_description(self, dao):
        """Test searching by description."""
        dao.insert("Task 1", description="Python programming")
        dao.insert("Task 2", description="Java programming")

        rows = list(dao.search("programming"))
        assert len(rows) == 2

    def test_search_tasks_with_filters(self, dao):
        """Test searching with filters."""
        dao.insert("Task H", priority="H", project="Work")
        dao.insert("Task M", priority="M", project="Work")

        rows = list(dao.search("Task", priority="H", project="Work"))
        assert len(rows) == 1

    def test_search_tasks_filter_tags(self, dao):
        """Test searching with tag filters."""
        dao.insert("Task 1", tags=["urgent"])
        dao.insert("Task 2", tags=["important"])

        rows = list(dao.search("Task", tags=["urgent"]))
        assert len(rows) == 1

    def test_search_tasks_fts_success_mock(self):
        """Test search successfully returning via FTS5 path (line 211)."""
        mock_conn = MagicMock()
        mock_conn.__enter__.return_value = mock_conn
        mock_conn.__exit__.return_value = None
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [{"id": 1, "title": "Mock Task"}]
        mock_conn.execute.return_value = mock_cursor

        dao = TaskDAO(mock_conn)
        rows = dao.search("Mock")
        assert len(rows) == 1
        assert rows[0]["id"] == 1

    def test_search_tasks_fallback_like(self, db_and_dao):
        """Test searching tasks with fallback LIKE path when FTS5 query fails."""
        conn, dao = db_and_dao
        dao.insert(
            "Fallback Python",
            description="Python query",
            priority="H",
            project="Work",
            tags=["tag1"],
        )

        class ProxyConnection:
            def __init__(self, target):
                self._target = target
                self._first_call = True

            def execute(self, query, params=()):
                if self._first_call and "MATCH" in str(query):
                    self._first_call = False
                    raise RuntimeError("FTS5 table unavailable")
                return self._target.execute(query, params)

            def __enter__(self):
                return self._target.__enter__()

            def __exit__(self, exc_type, exc_val, exc_tb):
                return self._target.__exit__(exc_type, exc_val, exc_tb)

            def __getattr__(self, name):
                return getattr(self._target, name)

        proxy_conn = ProxyConnection(conn)
        fallback_dao = TaskDAO(proxy_conn)
        rows = list(fallback_dao.search("Python", priority="H", project="Work", tags=["tag1"]))
        assert len(rows) == 1
        assert "Fallback Python" in rows[0]["title"]

    def test_clear_all(self, dao):
        """Test clearing all tasks."""
        dao.insert("Task 1")
        dao.insert("Task 2")
        dao.insert("Task 3")

        rows_before = list(dao.fetch_all())
        assert len(rows_before) == 3

        count = dao.clear_all()
        assert count == 3

        rows_after = list(dao.fetch_all())
        assert len(rows_after) == 0

    def test_clear_all_empty(self, dao):
        """Test clearing when database is empty."""
        count = dao.clear_all()
        assert count == 0
