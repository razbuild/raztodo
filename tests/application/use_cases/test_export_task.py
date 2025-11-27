import json
import os
import tempfile

import pytest

from raztodo.application.use_cases.export_task import ExportTasksUseCase
from raztodo.domain.exceptions import RazTodoException


class TestExportTasksUseCase:
    """Test cases for ExportTasksUseCase."""

    def test_export_tasks_success(self, task_repo):
        """Test successful task export."""
        task_repo.add_task("Task 1", description="Description 1")
        task_repo.add_task("Task 2", description="Description 2")

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            temp_file = f.name

        try:
            use_case = ExportTasksUseCase(task_repo)
            result = use_case.execute(temp_file)

            assert result is True
            assert os.path.exists(temp_file)

            # Verify file content
            with open(temp_file, encoding="utf-8") as f:
                data = json.load(f)

            assert isinstance(data, list)
            assert len(data) == 2
            assert data[0]["title"] == "Task 1"
        finally:
            if os.path.exists(temp_file):
                os.unlink(temp_file)

    def test_export_empty_tasks(self, task_repo):
        """Test exporting empty task list."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            temp_file = f.name

        try:
            use_case = ExportTasksUseCase(task_repo)
            result = use_case.execute(temp_file)

            assert result is True

            with open(temp_file, encoding="utf-8") as f:
                data = json.load(f)

            assert data == []
        finally:
            if os.path.exists(temp_file):
                os.unlink(temp_file)

    def test_export_tasks_failure(self, mock_repo):
        """Test export failure raises error."""

        mock_repo.export_tasks.return_value = False
        use_case = ExportTasksUseCase(mock_repo)

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            temp_file = f.name

        try:
            with pytest.raises(RazTodoException) as exc_info:
                use_case.execute(temp_file)

            assert "Failed to export" in str(exc_info.value)
            assert temp_file in str(exc_info.value)
        finally:
            if os.path.exists(temp_file):
                os.unlink(temp_file)
