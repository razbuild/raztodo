import json

import pytest

from raztodo.infrastructure.sqlite.task_dao import TaskDAO


class TestTaskDAO:
    """Test cases for TaskDAO."""

    @pytest.fixture
    def dao(self, in_memory_db):
        """Create a TaskDAO instance with in-memory database."""
        conn = in_memory_db()
        dao = TaskDAO(conn)
        yield dao
        conn.close()

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

    def test_insert_task_tags_json(self, dao):
        """Test that tags are stored as JSON."""
        tags = ["tag1", "tag2", "tag3"]
        dao.insert("Task", tags=tags)

        # Verify tags are stored as JSON
        row = dao._conn.execute("SELECT tags FROM tasks").fetchone()
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
        _task_id2 = dao.insert("Task 2")
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

    def test_update_task_title(self, dao):
        """Test updating task title."""
        task_id = dao.insert("Old Title")
        result = dao.update(task_id, title="New Title")
        assert result > 0

        row = dao._conn.execute(
            "SELECT title FROM tasks WHERE id = ?", (task_id,)
        ).fetchone()
        assert row[0] == "New Title"

    def test_update_task_done(self, dao):
        """Test updating task done status."""
        task_id = dao.insert("Task")
        result = dao.update(task_id, done=True)
        assert result > 0

        row = dao._conn.execute(
            "SELECT done FROM tasks WHERE id = ?", (task_id,)
        ).fetchone()
        assert row[0] == 1

    def test_update_task_clear_due_date(self, dao):
        """Test clearing task due date."""
        task_id = dao.insert("Task", due_date="2025-02-01")
        result = dao.update(task_id, due_date="__CLEAR__")
        assert result > 0

        row = dao._conn.execute(
            "SELECT due_date FROM tasks WHERE id = ?", (task_id,)
        ).fetchone()
        assert row[0] is None

    def test_update_task_clear_project(self, dao):
        """Test clearing task project."""
        task_id = dao.insert("Task", project="Work")
        result = dao.update(task_id, project="__CLEAR__")
        assert result > 0

        row = dao._conn.execute(
            "SELECT project FROM tasks WHERE id = ?", (task_id,)
        ).fetchone()
        assert row[0] is None

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
