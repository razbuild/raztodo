import json

import pytest

from raztodo.application.use_cases.import_task import ImportTasksUseCase
from raztodo.domain.exceptions import RazTodoException


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

    def test_import_invalid_json_syntax(self, task_repo, tmp_path):
        """Test importing file with invalid JSON syntax raises error."""
        p = tmp_path / "invalid.json"
        p.write_text("invalid json content", encoding="utf-8")

        use_case = ImportTasksUseCase(task_repo)

        with pytest.raises(RazTodoException) as exc_info:
            use_case.execute(str(p))

        error_msg = str(exc_info.value).lower()
        assert (
            "json" in error_msg
            or "format" in error_msg
            or "expecting value" in error_msg
        )

    def test_import_not_array(self, task_repo, tmp_path):
        """Test importing valid JSON that is not an array raises error."""
        file_path = self.create_json_file(tmp_path, {"not": "array"})

        use_case = ImportTasksUseCase(task_repo)

        with pytest.raises(RazTodoException) as exc_info:
            use_case.execute(file_path)

        assert "array" in str(exc_info.value).lower()

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
