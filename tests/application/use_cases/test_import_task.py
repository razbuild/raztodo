import json
from unittest.mock import mock_open

import pytest

from raztodo.application.use_cases.import_task import ImportTasksUseCase
from raztodo.domain.exceptions import RazTodoException
from raztodo.domain.task_entity import TaskEntity


class TestImportTasksUseCase:
    """Test cases for ImportTasksUseCase."""

    def create_json_file(self, tmp_path, data, filename="tasks.json"):
        """Helper to create a json file using pytest's tmp_path."""
        p = tmp_path / filename
        p.write_text(json.dumps(data), encoding="utf-8")
        return str(p)

    def test_import_tasks_success(self, task_repo, tmp_path):
        """Test successful task import."""
        tasks_data = [
            {"title": "Imported Task 1", "description": "Description 1", "done": False},
            {"title": "Imported Task 2", "description": "Description 2", "done": True},
        ]

        file_path = self.create_json_file(tmp_path, tasks_data)

        use_case = ImportTasksUseCase(task_repo)
        count = use_case.execute(file_path)

        assert count == 2
        tasks = task_repo.get_tasks()
        assert len(tasks) == 2
        assert tasks[0].title == "Imported Task 1"
        assert tasks[1].title == "Imported Task 2"

    def test_import_nonexistent_file(self, task_repo):
        """Test importing from nonexistent file raises error."""
        use_case = ImportTasksUseCase(task_repo)

        with pytest.raises(RazTodoException) as exc_info:
            use_case.execute("/nonexistent/file.json")

        assert "not found" in str(exc_info.value).lower()

    def test_import_unreadable_file(self, task_repo, tmp_path, monkeypatch):
        """Test importing an unreadable file raises error before import starts."""
        file_path = self.create_json_file(tmp_path, [])
        monkeypatch.setattr("raztodo.application.use_cases.import_task.os.access", lambda *_: False)

        use_case = ImportTasksUseCase(task_repo)

        with pytest.raises(RazTodoException) as exc_info:
            use_case.execute(file_path)

        assert "permission denied" in str(exc_info.value).lower()

    def test_import_invalid_json_syntax(self, task_repo, tmp_path):
        """Test importing file with invalid JSON syntax raises error."""
        p = tmp_path / "invalid.json"
        p.write_text("invalid json content", encoding="utf-8")

        use_case = ImportTasksUseCase(task_repo)

        with pytest.raises(RazTodoException) as exc_info:
            use_case.execute(str(p))

        error_msg = str(exc_info.value).lower()
        assert "json" in error_msg or "format" in error_msg or "expecting value" in error_msg

    def test_import_not_array(self, task_repo, tmp_path):
        """Test importing valid JSON that is not an array raises error."""
        file_path = self.create_json_file(tmp_path, {"not": "array"})

        use_case = ImportTasksUseCase(task_repo)

        with pytest.raises(RazTodoException) as exc_info:
            use_case.execute(file_path)

        assert "array" in str(exc_info.value).lower()

    def test_import_upsert_not_array(self, task_repo, tmp_path):
        """Test upsert mode rejects valid JSON that is not an array."""
        file_path = self.create_json_file(tmp_path, {"not": "array"})

        use_case = ImportTasksUseCase(task_repo)

        with pytest.raises(RazTodoException) as exc_info:
            use_case.execute(file_path, upsert=True)

        assert "expected json array" in str(exc_info.value).lower()

    def test_import_empty_list(self, task_repo, tmp_path):
        """Test importing an empty JSON list does nothing."""
        file_path = self.create_json_file(tmp_path, [])

        use_case = ImportTasksUseCase(task_repo)
        count = use_case.execute(file_path)

        assert count == 0
        assert len(task_repo.get_tasks()) == 0

    def test_import_with_missing_title(self, task_repo, tmp_path):
        """Test importing tasks with missing title are skipped."""
        tasks_data = [
            {"title": "Valid Task"},
            {"description": "Missing title"},
        ]
        file_path = self.create_json_file(tmp_path, tasks_data)

        use_case = ImportTasksUseCase(task_repo)
        count = use_case.execute(file_path)

        assert count == 1
        tasks = task_repo.get_tasks()
        assert tasks[0].title == "Valid Task"

    def test_import_preserves_done_status(self, task_repo, tmp_path):
        """Test that import preserves done status."""
        tasks_data = [{"title": "Done Task", "done": True}]
        file_path = self.create_json_file(tmp_path, tasks_data)

        use_case = ImportTasksUseCase(task_repo)
        use_case.execute(file_path)

        tasks = task_repo.get_tasks()
        assert tasks[0].done is True

    def test_import_upsert_mode_updates_data(self, task_repo, tmp_path):
        """Test import with upsert mode correctly updates existing tasks."""

        task_repo.add_task("Existing Task", description="Old Description")

        tasks_data = [
            {"title": "Existing Task", "description": "New Description", "done": True},
            {"title": "New Task", "description": "New Task Desc", "done": False},
        ]
        file_path = self.create_json_file(tmp_path, tasks_data)

        use_case = ImportTasksUseCase(task_repo)
        result = use_case.execute(file_path, upsert=True)

        assert result["updated"] == 1
        assert result["inserted"] == 1

        all_tasks = task_repo.get_tasks()
        updated_task = next(t for t in all_tasks if t.title == "Existing Task")

        assert updated_task.description == "New Description"
        assert updated_task.done is True

    def test_import_upsert_skips_invalid_items_and_empty_titles(self, mock_repo, tmp_path):
        """Test upsert mode ignores non-dict items and empty titles."""
        tasks_data = [
            "not a task",
            {"title": "   "},
            {"title": "Valid Task"},
        ]
        file_path = self.create_json_file(tmp_path, tasks_data)
        mock_repo.add_task.return_value = None
        mock_repo.search_tasks.return_value = []

        use_case = ImportTasksUseCase(mock_repo)
        result = use_case.execute(file_path, upsert=True)

        assert result == {"inserted": 0, "updated": 0}
        mock_repo.add_task.assert_called_once_with("Valid Task", "", "", None, [], None)
        mock_repo.search_tasks.assert_called_once_with("Valid Task")

    def test_import_upsert_inserts_without_done_status(self, mock_repo, tmp_path):
        """Test upsert mode does not mark tasks done when done is absent."""
        file_path = self.create_json_file(tmp_path, [{"title": "New Task"}])
        mock_repo.add_task.return_value = 7

        use_case = ImportTasksUseCase(mock_repo)
        result = use_case.execute(file_path, upsert=True)

        assert result == {"inserted": 1, "updated": 0}
        mock_repo.mark_done.assert_not_called()
        mock_repo.search_tasks.assert_not_called()

    def test_import_upsert_updates_when_add_task_fails(self, mock_repo, tmp_path):
        """Test upsert mode updates the first exact title match when insert fails."""
        tasks_data = [
            {
                "title": "Existing Task",
                "description": "New Description",
                "priority": "H",
                "due_date": "2026-07-05",
                "tags": ["work"],
                "project": "Ops",
                "done": False,
            }
        ]
        file_path = self.create_json_file(tmp_path, tasks_data)
        existing_task = TaskEntity(id=42, title="Existing Task")
        mock_repo.add_task.side_effect = RazTodoException("duplicate")
        mock_repo.search_tasks.return_value = [existing_task]

        use_case = ImportTasksUseCase(mock_repo)
        result = use_case.execute(file_path, upsert=True)

        assert result == {"inserted": 0, "updated": 1}
        mock_repo.update_task.assert_called_once_with(
            42,
            title="Existing Task",
            description="New Description",
            priority="H",
            due_date="2026-07-05",
            tags=["work"],
            project="Ops",
        )
        mock_repo.mark_done.assert_called_once_with(42, False)

    def test_import_upsert_updates_without_done_status(self, mock_repo, tmp_path):
        """Test upsert mode does not mark updated tasks done when done is absent."""
        file_path = self.create_json_file(tmp_path, [{"title": "Existing Task"}])
        existing_task = TaskEntity(id=42, title="Existing Task")
        mock_repo.add_task.side_effect = RazTodoException("duplicate")
        mock_repo.search_tasks.return_value = [existing_task]

        use_case = ImportTasksUseCase(mock_repo)
        result = use_case.execute(file_path, upsert=True)

        assert result == {"inserted": 0, "updated": 1}
        mock_repo.update_task.assert_called_once()
        mock_repo.mark_done.assert_not_called()

    def test_import_upsert_invalid_json_syntax(self, task_repo, tmp_path):
        """Test upsert mode wraps JSON decode errors with file context."""
        p = tmp_path / "invalid.json"
        p.write_text("{", encoding="utf-8")

        use_case = ImportTasksUseCase(task_repo)

        with pytest.raises(RazTodoException) as exc_info:
            use_case.execute(str(p), upsert=True)

        error_msg = str(exc_info.value).lower()
        assert "invalid json format" in error_msg
        assert "line" in error_msg

    def test_import_upsert_file_encoding_error(self, task_repo, tmp_path):
        """Test upsert mode wraps unicode decode errors with file context."""
        p = tmp_path / "invalid_encoding.json"
        p.write_bytes(b"\xff")

        use_case = ImportTasksUseCase(task_repo)

        with pytest.raises(RazTodoException) as exc_info:
            use_case.execute(str(p), upsert=True)

        assert "file encoding error" in str(exc_info.value).lower()

    def test_import_upsert_io_error(self, task_repo, tmp_path, monkeypatch):
        """Test upsert mode wraps OS errors raised while opening a readable file."""
        file_path = self.create_json_file(tmp_path, [])
        opener = mock_open()
        opener.side_effect = OSError("disk error")
        monkeypatch.setattr("builtins.open", opener)

        use_case = ImportTasksUseCase(task_repo)

        with pytest.raises(RazTodoException) as exc_info:
            use_case.execute(file_path, upsert=True)

        assert "i/o error" in str(exc_info.value).lower()
