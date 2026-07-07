import json
import os
import sqlite3
import tempfile
from pathlib import Path
from sqlite3 import Error
from unittest.mock import MagicMock, patch

import pytest

from raztodo.domain.exceptions import RazTodoException
from raztodo.infrastructure.sqlite.task_repository import (
    SQLiteTaskRepository,
    ensure_writable_path,
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

    # --- ensure_writable_path ---

    def test_ensure_writable_path_creates_missing_directory(self, tmp_path):
        """Lines 61-62: directory is created when it does not exist."""
        new_dir = tmp_path / "nested" / "sub"
        file_path = new_dir / "tasks.json"
        result = ensure_writable_path(str(file_path))
        assert new_dir.exists()
        assert result == file_path.resolve()

    def test_ensure_writable_path_oserror_raises(self, tmp_path):
        """Lines 63-64: OSError while creating directory raises RazTodoException."""
        target = tmp_path / "new_dir" / "file.json"
        with patch("raztodo.infrastructure.sqlite.task_repository.Path.mkdir", side_effect=OSError("no space")):
            with pytest.raises(RazTodoException, match="FileOperationError"):
                ensure_writable_path(str(target))

    # --- add_task: generic sqlite3.Error ---

    def test_add_task_database_error(self, in_memory_db):
        """Line 110: generic sqlite3.Error (not IntegrityError) wraps as DatabaseError."""
        repo = SQLiteTaskRepository(connection_factory=in_memory_db)
        repo._dao.insert = MagicMock(side_effect=Error("disk full"))
        with pytest.raises(RazTodoException, match="DatabaseError during add_task"):
            repo.add_task("Some Task")
        repo.close()

    # --- get_task: not found ---

    def test_get_task_not_found(self, task_repo):
        """Lines 137-138: get_task returns None when task_id does not exist."""
        result = task_repo.get_task(99999)
        assert result is None

    def test_get_task_found(self, task_repo):
        """Lines 137-138: get_task returns TaskEntity when task exists."""
        task_id = task_repo.add_task("Findable Task")
        result = task_repo.get_task(task_id)
        assert result is not None
        assert result.title == "Findable Task"

    # --- update_task: priority cleared ---

    def test_update_task_clear_priority(self, task_repo):
        """Line 157: passing priority='' converts to __CLEAR__ and NULLs the column."""
        task_id = task_repo.add_task("Task", priority="H")
        task_repo.update_task(task_id, priority="")
        updated = task_repo.get_task(task_id)
        assert updated.priority == "" or updated.priority is None

    # --- update_task: sqlite3.Error ---

    def test_update_task_database_error(self, in_memory_db):
        """Line 177: sqlite3.Error during update wraps as DatabaseError."""
        repo = SQLiteTaskRepository(connection_factory=in_memory_db)
        task_id = repo.add_task("Task to Update")
        repo._dao.update = MagicMock(side_effect=Error("disk full"))
        with pytest.raises(RazTodoException, match="DatabaseError during update_task"):
            repo.update_task(task_id, title="New Title")
        repo.close()

    # --- export_tasks ---

    def test_export_tasks_success(self, task_repo, tmp_path):
        """Lines 214-238: export_tasks writes JSON and returns True."""
        task_repo.add_task("Export Task", description="Exported", priority="H")
        out = tmp_path / "out.json"
        result = task_repo.export_tasks(str(out))
        assert result is True
        data = json.loads(out.read_text(encoding="utf-8"))
        assert len(data) == 1
        assert data[0]["title"] == "Export Task"

    def test_export_tasks_error_raises(self, task_repo, tmp_path):
        """Line 239: any exception during export raises RazTodoException."""
        out = tmp_path / "out.json"
        with patch("builtins.open", side_effect=OSError("disk full")):
            with pytest.raises(RazTodoException, match="FileOperationError during export_tasks"):
                task_repo.export_tasks(str(out))

    # --- import_tasks ---

    def test_import_tasks_success(self, task_repo, tmp_path):
        """Lines 243-291: basic successful import."""
        data = [{"title": "Imported Task", "description": "desc", "done": False}]
        p = tmp_path / "import.json"
        p.write_text(json.dumps(data), encoding="utf-8")
        count = task_repo.import_tasks(str(p))
        assert count == 1
        tasks = task_repo.get_tasks()
        assert tasks[0].title == "Imported Task"

    def test_import_tasks_file_not_found(self, task_repo):
        """Lines 244-245: missing file raises RazTodoException."""
        with pytest.raises(RazTodoException, match="TaskFileNotFoundError"):
            task_repo.import_tasks("/nonexistent/path/file.json")

    def test_import_tasks_unreadable_file(self, task_repo, tmp_path, monkeypatch):
        """Lines 246-247: unreadable file raises RazTodoException."""
        p = tmp_path / "tasks.json"
        p.write_text("[]", encoding="utf-8")
        monkeypatch.setattr(
            "raztodo.infrastructure.sqlite.task_repository.os.access", lambda *_: False
        )
        with pytest.raises(RazTodoException, match="FilePermissionError"):
            task_repo.import_tasks(str(p))

    def test_import_tasks_invalid_json(self, task_repo, tmp_path):
        """Lines 250-252: invalid JSON raises RazTodoException."""
        p = tmp_path / "bad.json"
        p.write_text("not json", encoding="utf-8")
        with pytest.raises(RazTodoException, match="InvalidFileFormatError"):
            task_repo.import_tasks(str(p))

    def test_import_tasks_not_array(self, task_repo, tmp_path):
        """Lines 254-255: JSON object (not array) raises RazTodoException."""
        p = tmp_path / "obj.json"
        p.write_text(json.dumps({"key": "value"}), encoding="utf-8")
        with pytest.raises(RazTodoException, match="InvalidFileFormatError"):
            task_repo.import_tasks(str(p))

    def test_import_tasks_skips_non_dict_items(self, task_repo, tmp_path):
        """Lines 259-261: items that are not dicts or lack 'title' are skipped."""
        data = ["not a dict", {"description": "no title"}, {"title": "Valid"}]
        p = tmp_path / "mixed.json"
        p.write_text(json.dumps(data), encoding="utf-8")
        count = task_repo.import_tasks(str(p))
        assert count == 1
        assert task_repo.get_tasks()[0].title == "Valid"

    def test_import_tasks_done_flag_set(self, task_repo, tmp_path):
        """Lines 274-279: done flag is applied after insert."""
        data = [{"title": "Done Task", "done": True}]
        p = tmp_path / "done.json"
        p.write_text(json.dumps(data), encoding="utf-8")
        task_repo.import_tasks(str(p))
        tasks = task_repo.get_tasks()
        assert tasks[0].done is True

    def test_import_tasks_done_flag_dao_error_is_logged_not_raised(self, task_repo, tmp_path):
        """Lines 277-278: Error setting done flag is logged, not propagated; item still counts."""
        data = [{"title": "Task With Done Error", "done": True}]
        p = tmp_path / "done_err.json"
        p.write_text(json.dumps(data), encoding="utf-8")
        original_update = task_repo._dao.update

        call_count = {"n": 0}

        def flaky_update(*args, **kwargs):
            call_count["n"] += 1
            if call_count["n"] == 1:
                raise Error("simulated done-flag error")
            return original_update(*args, **kwargs)

        task_repo._dao.update = flaky_update
        count = task_repo.import_tasks(str(p))
        # Item was still counted even though done-flag update failed
        assert count == 1

    def test_import_tasks_raztodo_exception_per_item_appended_to_errors(self, task_repo, tmp_path):
        """Lines 280-282: RazTodoException for an item is collected in errors."""
        # Two items with duplicate title → second raises DuplicateTaskError
        data = [{"title": "Dup"}, {"title": "Dup"}]
        p = tmp_path / "dup.json"
        p.write_text(json.dumps(data), encoding="utf-8")
        # First succeeds (count=1), second fails — should still return 1 not raise
        count = task_repo.import_tasks(str(p))
        assert count == 1

    def test_import_tasks_generic_exception_per_item(self, task_repo, tmp_path):
        """Lines 283-285: Generic Exception for an item is collected in errors."""
        data = [{"title": "Boom"}, {"title": "Fine"}]
        p = tmp_path / "boom.json"
        p.write_text(json.dumps(data), encoding="utf-8")
        original_add = task_repo.add_task
        call_count = {"n": 0}

        def explosive_add(title, *args, **kwargs):
            call_count["n"] += 1
            if call_count["n"] == 1:
                raise RuntimeError("unexpected boom")
            return original_add(title, *args, **kwargs)

        task_repo.add_task = explosive_add
        count = task_repo.import_tasks(str(p))
        assert count == 1

    def test_import_tasks_all_fail_raises(self, task_repo, tmp_path):
        """Line 287-288: if all items fail and count==0, raises RazTodoException."""
        data = [{"title": ""}, {"title": ""}]
        p = tmp_path / "allfail.json"
        p.write_text(json.dumps(data), encoding="utf-8")
        with pytest.raises(RazTodoException, match="Failed to import any tasks"):
            task_repo.import_tasks(str(p))

    # --- clear_all_tasks: sqlite3.Error ---

    def test_clear_all_tasks_database_error(self, in_memory_db):
        """Line 298: sqlite3.Error during clear_all wraps as DatabaseError."""
        repo = SQLiteTaskRepository(connection_factory=in_memory_db)
        repo._dao.clear_all = MagicMock(side_effect=Error("disk full"))
        with pytest.raises(RazTodoException, match="DatabaseError during clear_all_tasks"):
            repo.clear_all_tasks()
        repo.close()

    # --- close: idempotent ---

    def test_close_is_idempotent(self, in_memory_db):
        """Line 302->exit: calling close twice does not raise."""
        repo = SQLiteTaskRepository(connection_factory=in_memory_db)
        repo.close()
        repo.close()  # _conn is None — must not raise
