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
        task_repo.add_task("  Test Task  ")
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
        task_repo.add_task("Task 2")
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
        task_repo.add_task("Task", priority="invalid")
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

    def test_get_task(self, task_repo):
        """Test get_task returns task entity or None."""
        task_id = task_repo.add_task("Specific Task", description="Desc", priority="H")
        task = task_repo.get_task(task_id)
        assert task is not None
        assert task.id == task_id
        assert task.title == "Specific Task"
        assert task_repo.get_task(99999) is None

    def test_ensure_writable_path_mkdir_failure(self, monkeypatch):
        """Test ensure_writable_path handles directory creation failure."""
        from pathlib import Path

        from raztodo.domain.exceptions import RazTodoException
        from raztodo.infrastructure.sqlite.task_repository import ensure_writable_path

        def fake_mkdir(self, *args, **kwargs):
            raise OSError("Read-only file system")

        monkeypatch.setattr(Path, "mkdir", fake_mkdir)
        with pytest.raises(RazTodoException) as exc_info:
            ensure_writable_path("/nonexistent_forbidden_dir/task.db")
        assert "Cannot create directory" in str(exc_info.value)

    def test_add_task_database_error(self, task_repo, monkeypatch):
        """Test add_task raises DatabaseError on generic SQLite Error."""
        import sqlite3

        def fake_insert(*args, **kwargs):
            raise sqlite3.Error("Disk full")

        monkeypatch.setattr(task_repo._dao, "insert", fake_insert)
        with pytest.raises(RazTodoException) as exc_info:
            task_repo.add_task("Task")
        assert "DatabaseError during add_task" in str(exc_info.value)

    def test_update_task_clear_priority(self, task_repo):
        """Test updating priority to empty string clears it."""
        task_id = task_repo.add_task("Task", priority="H")
        task_repo.update_task(task_id, priority="")
        task = task_repo.get_task(task_id)
        assert task.priority == ""

    def test_update_task_database_error(self, task_repo, monkeypatch):
        """Test update_task raises DatabaseError on generic SQLite Error."""
        import sqlite3

        task_id = task_repo.add_task("Task")

        def fake_update(*args, **kwargs):
            raise sqlite3.Error("Write failed")

        monkeypatch.setattr(task_repo._dao, "update", fake_update)
        with pytest.raises(RazTodoException) as exc_info:
            task_repo.update_task(task_id, title="New Title")
        assert "DatabaseError during update_task" in str(exc_info.value)

    def test_export_tasks_file_error(self, task_repo):
        """Test export_tasks handles file write exceptions."""
        from raztodo.domain.exceptions import RazTodoException

        task_repo.add_task("Task 1")

        with pytest.raises(RazTodoException) as exc_info:
            task_repo.export_tasks("/dev/null/forbidden/path.json")
        assert "FileOperationError" in str(exc_info.value)

    def test_import_tasks_all_errors_raises_exception(self, task_repo, tmp_path):
        """Test importing tasks where all items are invalid raises RazTodoException."""
        import json

        from raztodo.domain.exceptions import RazTodoException

        invalid_file = tmp_path / "invalid_tasks.json"
        invalid_file.write_text(
            json.dumps([{"description": "No title"}, {"title": ""}]), encoding="utf-8"
        )

        with pytest.raises(RazTodoException) as exc_info:
            task_repo.import_tasks(str(invalid_file))
        assert "Failed to import any tasks" in str(exc_info.value)

    def test_import_tasks_done_flag_error_logged(self, task_repo, tmp_path, monkeypatch):
        """Test importing task when setting done flag fails."""
        import json
        import sqlite3

        valid_file = tmp_path / "valid_done.json"
        valid_file.write_text(json.dumps([{"title": "Task Done", "done": True}]), encoding="utf-8")

        original_update = task_repo._dao.update

        def fake_update(task_id, **kwargs):
            if "done" in kwargs:
                raise sqlite3.Error("Mocked done flag failure")
            return original_update(task_id, **kwargs)

        monkeypatch.setattr(task_repo._dao, "update", fake_update)
        count = task_repo.import_tasks(str(valid_file))
        assert count == 1

    def test_clear_all_tasks_database_error(self, task_repo, monkeypatch):
        """Test clear_all_tasks raises DatabaseError on generic SQLite Error."""
        import sqlite3

        def fake_clear(*args, **kwargs):
            raise sqlite3.Error("Locked")

        monkeypatch.setattr(task_repo._dao, "clear_all", fake_clear)
        with pytest.raises(RazTodoException) as exc_info:
            task_repo.clear_all_tasks()
        assert "DatabaseError during clear_all_tasks" in str(exc_info.value)

    def test_close_multiple_times(self, task_repo):
        """Test closing connection multiple times is safe."""
        task_repo.close()
        assert task_repo._conn is None
        task_repo.close()
        assert task_repo._conn is None

    def test_ensure_writable_path_permission_error(self, tmp_path, monkeypatch):
        """Test ensure_writable_path raises FilePermissionError when file is not writable."""
        import os

        from raztodo.domain.exceptions import RazTodoException
        from raztodo.infrastructure.sqlite.task_repository import ensure_writable_path

        existing_file = tmp_path / "readonly.json"
        existing_file.write_text("{}", encoding="utf-8")

        orig_access = os.access

        def fake_access(path, mode):
            if str(path) == str(existing_file) and mode == os.W_OK:
                return False
            return orig_access(path, mode)

        monkeypatch.setattr(os, "access", fake_access)
        with pytest.raises(RazTodoException) as exc_info:
            ensure_writable_path(str(existing_file))
        assert "FilePermissionError" in str(exc_info.value)

    def test_export_tasks_json_dump_error(self, task_repo, tmp_path, monkeypatch):
        """Test export_tasks handles exceptions during JSON serialization (line 239)."""
        import json

        from raztodo.domain.exceptions import RazTodoException

        task_repo.add_task("Task 1")
        export_file = tmp_path / "export.json"

        def fake_dump(*args, **kwargs):
            raise TypeError("Serialization error")

        monkeypatch.setattr(json, "dump", fake_dump)
        with pytest.raises(RazTodoException) as exc_info:
            task_repo.export_tasks(str(export_file))
        assert "FileOperationError during export_tasks" in str(exc_info.value)

    def test_import_tasks_invalid_json_format(self, task_repo, tmp_path):
        """Test import_tasks handles invalid JSON syntax (line 251)."""
        from raztodo.domain.exceptions import RazTodoException

        bad_file = tmp_path / "bad.json"
        bad_file.write_text("{not valid json", encoding="utf-8")
        with pytest.raises(RazTodoException) as exc_info:
            task_repo.import_tasks(str(bad_file))
        assert "InvalidFileFormatError" in str(exc_info.value)

    def test_import_tasks_generic_exception_handled(self, task_repo, tmp_path, monkeypatch):
        """Test import_tasks handles generic non-RazTodoException during item import (lines 283-285)."""
        import json

        from raztodo.domain.exceptions import RazTodoException

        valid_file = tmp_path / "generic_fail.json"
        valid_file.write_text(json.dumps([{"title": "Fail Task"}]), encoding="utf-8")

        def fake_add_task(*args, **kwargs):
            raise RuntimeError("Unexpected error")

        monkeypatch.setattr(task_repo, "add_task", fake_add_task)
        with pytest.raises(RazTodoException) as exc_info:
            task_repo.import_tasks(str(valid_file))
        assert "Failed to import any tasks" in str(exc_info.value)

    def test_export_tasks_success(self, task_repo, tmp_path):
        """Test successful export_tasks returns True (line 238)."""
        task_repo.add_task("Task for export", description="Desc")
        export_file = tmp_path / "success_export.json"
        assert task_repo.export_tasks(str(export_file)) is True

    def test_import_tasks_without_done_key(self, task_repo, tmp_path):
        """Test import_tasks handles item without done key (branch 274->279)."""
        import json

        valid_file = tmp_path / "no_done.json"
        valid_file.write_text(json.dumps([{"title": "Task No Done"}]), encoding="utf-8")
        assert task_repo.import_tasks(str(valid_file)) == 1
