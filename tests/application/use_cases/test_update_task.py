import pytest

from raztodo.application.use_cases.update_task import UpdateTaskUseCase
from raztodo.domain.exceptions import RazTodoException


class TestUpdateTaskUseCase:
    """Test cases for UpdateTaskUseCase."""

    def test_update_task_success(self, mock_repo):
        """Test successful task update."""
        mock_repo.update_task.return_value = 1
        use_case = UpdateTaskUseCase(mock_repo)

        result = use_case.execute(1, title="New Title")

        assert result is True
        mock_repo.update_task.assert_called_once_with(
            1, "New Title", None, None, None, None, None
        )

    def test_update_task_all_fields(self, mock_repo):
        """Test updating all task fields."""
        mock_repo.update_task.return_value = 1
        use_case = UpdateTaskUseCase(mock_repo)

        result = use_case.execute(
            1,
            title="New Title",
            description="New Description",
            priority="H",
            due_date="2025-02-01",
            tags=["tag1"],
            project="Project1",
        )

        assert result is True
        mock_repo.update_task.assert_called_once_with(
            1, "New Title", "New Description", "H", "2025-02-01", ["tag1"], "Project1"
        )

    def test_update_nonexistent_task(self, mock_repo):
        """Test updating nonexistent task raises error."""
        mock_repo.update_task.return_value = 0
        use_case = UpdateTaskUseCase(mock_repo)

        with pytest.raises(RazTodoException) as exc_info:
            use_case.execute(999, title="New Title")

        assert (
            "999" in str(exc_info.value) or "not found" in str(exc_info.value).lower()
        )
