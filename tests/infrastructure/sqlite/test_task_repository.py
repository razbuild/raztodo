import pytest

from raztodo.domain.exceptions import RazTodoException
from raztodo.infrastructure.sqlite.task_repository import (
    SQLiteTaskRepository,
)


class TestSQLiteTaskRepository:
    """Test cases for SQLiteTaskRepository."""

    def test_add_task_success(self, task_repo):
        """Test adding a task successfully."""
        task_id = task_repo.add_task("Test Task", "Description")
        assert task_id is not None
        assert task_id > 0

    def test_add_task_minimal_fields(self, task_repo):
        """Test adding task with minimal fields."""
        task_id = task_repo.add_task("Minimal Task")
        assert task_id > 0

    def test_add_task_all_fields(self, task_repo):
        """Test adding task with all fields."""
        task_id = task_repo.add_task(
            "Full Task",
            description="Full description",
            priority="H",
            due_date="2025-02-01",
            tags=["urgent", "important"],
            project="Work",
        )
        assert task_id > 0

    def test_add_task_empty_title(self, task_repo):
        """Test adding task with empty title raises error."""
        with pytest.raises(RazTodoException) as exc_info:
            task_repo.add_task("")
        assert "title" in str(exc_info.value).lower()

    def test_add_task_title_too_long(self, task_repo):
        """Test adding task with title exceeding max length."""
        long_title = "a" * 61
        with pytest.raises(RazTodoException) as exc_info:
            task_repo.add_task(long_title)
        assert "title" in str(exc_info.value).lower()

    def test_add_task_duplicate_title(self, task_repo):
        """Test adding duplicate task raises error."""
        task_repo.add_task("Unique Task")
        with pytest.raises(RazTodoException) as exc_info:
            task_repo.add_task("Unique Task")
        assert (
            "duplicate" in str(exc_info.value).lower()
            or "already exists" in str(exc_info.value).lower()
        )

    def test_add_task_title_stripped(self, task_repo):
        """Test that title is stripped of whitespace."""
        _task_id = task_repo.add_task("  Test Task  ")
        tasks = task_repo.get_tasks()
        assert len(tasks) == 1
        assert tasks[0].title == "Test Task"

    def test_get_tasks_empty(self, task_repo):
        """Test getting tasks from empty repository."""
        tasks = task_repo.get_tasks()
        assert tasks == []

    def test_get_tasks_all(self, task_repo):
        """Test getting all tasks."""
        task_repo.add_task("Task 1")
        task_repo.add_task("Task 2")
        tasks = task_repo.get_tasks()
        assert len(tasks) == 2

    def test_get_tasks_with_limit(self, task_repo):
        """Test getting tasks with limit."""
        for i in range(5):
            task_repo.add_task(f"Task {i}")
        tasks = task_repo.get_tasks(limit=2)
        assert len(tasks) == 2

    def test_get_tasks_with_offset(self, task_repo):
        """Test getting tasks with offset."""
        for i in range(5):
            task_repo.add_task(f"Task {i}")
        tasks = task_repo.get_tasks(offset=2)
        assert len(tasks) == 3  # Should return remaining tasks

    def test_get_tasks_filter_done(self, task_repo):
        """Test filtering tasks by done status."""
        task_id1 = task_repo.add_task("Task 1")
        _task_id2 = task_repo.add_task("Task 2")
        task_repo.mark_done(task_id1, True)

        done_tasks = task_repo.get_tasks(done=True)
        assert len(done_tasks) == 1
        assert done_tasks[0].done is True

        pending_tasks = task_repo.get_tasks(done=False)
        assert len(pending_tasks) == 1
        assert pending_tasks[0].done is False

    def test_get_tasks_filter_priority(self, task_repo):
        """Test filtering tasks by priority."""
        task_repo.add_task("Task H", priority="H")
        task_repo.add_task("Task M", priority="M")
        task_repo.add_task("Task L", priority="L")

        high_priority = task_repo.get_tasks(priority="H")
        assert len(high_priority) == 1
        assert high_priority[0].priority == "H"

    def test_get_tasks_filter_project(self, task_repo):
        """Test filtering tasks by project."""
        task_repo.add_task("Task 1", project="Work")
        task_repo.add_task("Task 2", project="Personal")

        work_tasks = task_repo.get_tasks(project="Work")
        assert len(work_tasks) == 1
        assert work_tasks[0].project == "Work"

    def test_get_tasks_filter_tags(self, task_repo):
        """Test filtering tasks by tags."""
        task_repo.add_task("Task 1", tags=["urgent"])
        task_repo.add_task("Task 2", tags=["important"])

        urgent_tasks = task_repo.get_tasks(tags=["urgent"])
        assert len(urgent_tasks) == 1

    def test_update_task_title(self, task_repo):
        """Test updating task title."""
        task_id = task_repo.add_task("Old Title")
        result = task_repo.update_task(task_id, title="New Title")
        assert result > 0

        tasks = task_repo.get_tasks()
        assert tasks[0].title == "New Title"

    def test_update_task_all_fields(self, task_repo):
        """Test updating all task fields."""
        task_id = task_repo.add_task("Task")
        result = task_repo.update_task(
            task_id,
            title="New Title",
            description="New Description",
            priority="H",
            due_date="2025-02-01",
            tags=["tag1"],
            project="Project",
        )
        assert result > 0

    def test_update_task_empty_title(self, task_repo):
        """Test updating task with empty title raises error."""
        task_id = task_repo.add_task("Task")
        with pytest.raises(RazTodoException) as exc_info:
            task_repo.update_task(task_id, title="")
        assert "title" in str(exc_info.value).lower()

    def test_update_task_clear_due_date(self, task_repo):
        """Test clearing task due date."""
        task_id = task_repo.add_task("Task", due_date="2025-02-01")
        task_repo.update_task(task_id, due_date="")
        tasks = task_repo.get_tasks()
        assert tasks[0].due_date is None

    def test_update_task_clear_project(self, task_repo):
        """Test clearing task project."""
        task_id = task_repo.add_task("Task", project="Work")
        task_repo.update_task(task_id, project="")
        tasks = task_repo.get_tasks()
        assert tasks[0].project is None

    def test_remove_task(self, task_repo):
        """Test removing a task."""
        task_id = task_repo.add_task("Task")
        result = task_repo.remove_task(task_id)
        assert result > 0

        tasks = task_repo.get_tasks()
        assert len(tasks) == 0

    def test_remove_nonexistent_task(self, task_repo):
        """Test removing nonexistent task returns 0."""
        result = task_repo.remove_task(999)
        assert result == 0

    def test_mark_done(self, task_repo):
        """Test marking task as done."""
        task_id = task_repo.add_task("Task")
        result = task_repo.mark_done(task_id, True)
        assert result > 0

        tasks = task_repo.get_tasks()
        assert tasks[0].done is True

    def test_mark_undone(self, task_repo):
        """Test marking task as undone."""
        task_id = task_repo.add_task("Task")
        task_repo.mark_done(task_id, True)
        task_repo.mark_done(task_id, False)

        tasks = task_repo.get_tasks()
        assert tasks[0].done is False

    def test_search_tasks(self, task_repo):
        """Test searching tasks."""
        task_repo.add_task("Python Task", description="Learn Python")
        task_repo.add_task("Java Task", description="Learn Java")

        results = task_repo.search_tasks("Python")
        assert len(results) == 1
        assert "Python" in results[0].title

    def test_search_tasks_by_description(self, task_repo):
        """Test searching tasks by description."""
        task_repo.add_task("Task 1", description="Python programming")
        task_repo.add_task("Task 2", description="Java programming")

        results = task_repo.search_tasks("programming")
        assert len(results) == 2

    def test_search_tasks_empty_keyword(self, task_repo):
        """Test searching with empty keyword returns empty list."""
        task_repo.add_task("Task")
        results = task_repo.search_tasks("")
        assert results == []

    def test_search_tasks_with_filters(self, task_repo):
        """Test searching tasks with filters."""
        task_repo.add_task("Task H", priority="H", project="Work")
        task_repo.add_task("Task M", priority="M", project="Work")

        results = task_repo.search_tasks("Task", priority="H", project="Work")
        assert len(results) == 1

    def test_context_manager(self, in_memory_db):
        """Test repository as context manager."""
        with SQLiteTaskRepository(connection_factory=in_memory_db) as repo:
            task_id = repo.add_task("Task")
            assert task_id > 0

    def test_priority_validation(self, task_repo):
        """Test that invalid priority is normalized."""
        _task_id = task_repo.add_task("Task", priority="invalid")
        tasks = task_repo.get_tasks()
        assert tasks[0].priority == ""  # Invalid priority becomes empty

    def test_description_max_length(self, task_repo):
        """Test description max length validation."""
        long_desc = "a" * 201
        with pytest.raises(RazTodoException) as exc_info:
            task_repo.add_task("Task", description=long_desc)
        assert "description" in str(exc_info.value).lower()

    def test_clear_all_tasks(self, task_repo):
        """Test clearing all tasks."""
        task_repo.add_task("Task 1")
        task_repo.add_task("Task 2")
        task_repo.add_task("Task 3")

        tasks_before = task_repo.get_tasks()
        assert len(tasks_before) == 3

        count = task_repo.clear_all_tasks()
        assert count == 3

        tasks_after = task_repo.get_tasks()
        assert len(tasks_after) == 0

    def test_clear_all_tasks_empty_repository(self, task_repo):
        """Test clearing when repository is empty."""
        count = task_repo.clear_all_tasks()
        assert count == 0

    def test_clear_all_tasks_removes_all_data(self, task_repo):
        """Test that clear_all_tasks removes all task data."""
        task_repo.add_task("Task 1", priority="H", project="Work")
        task_repo.add_task("Task 2", priority="M", project="Personal")
        task_repo.add_task("Task 3", tags=["urgent"])

        task_repo.clear_all_tasks()

        # Verify all tasks are gone
        tasks = task_repo.get_tasks()
        assert len(tasks) == 0

        # Verify search returns nothing
        search_results = task_repo.search_tasks("Task")
        assert len(search_results) == 0
