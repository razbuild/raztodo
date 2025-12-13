import pytest

from raztodo.application.use_cases.clear_tasks import ClearTasksUseCase
from raztodo.domain.exceptions import RazTodoException


class TestClearTasksUseCase:
    """Tests for ClearTasksUseCase."""

    def test_clear_tasks_requires_confirmation(self, mock_repo):
        """Test that clear operation requires explicit confirmation."""
        use_case = ClearTasksUseCase(mock_repo)

        with pytest.raises(ValueError) as exc_info:
            use_case.execute(confirmed=False)

        assert "confirmation" in str(exc_info.value).lower()
        assert "cannot be undone" in str(exc_info.value).lower()
        mock_repo.clear_all_tasks.assert_not_called()

    def test_clear_tasks_with_confirmation(self, mock_repo):
        """Test that clear operation works when confirmed."""
        mock_repo.clear_all_tasks.return_value = 5
        use_case = ClearTasksUseCase(mock_repo)

        result = use_case.execute(confirmed=True)

        assert result == 5
        mock_repo.clear_all_tasks.assert_called_once()

    def test_clear_tasks_returns_count(self, mock_repo):
        """Test that clear operation returns the number of deleted tasks."""
        mock_repo.clear_all_tasks.return_value = 10
        use_case = ClearTasksUseCase(mock_repo)

        result = use_case.execute(confirmed=True)

        assert result == 10

    def test_clear_tasks_handles_database_error(self, mock_repo):
        """Test that database errors are properly handled."""
        mock_repo.clear_all_tasks.side_effect = RazTodoException("Database error")
        use_case = ClearTasksUseCase(mock_repo)

        with pytest.raises(RazTodoException):
            use_case.execute(confirmed=True)

    def test_clear_tasks_with_zero_tasks(self, mock_repo):
        """Test clearing when there are no tasks."""
        mock_repo.clear_all_tasks.return_value = 0
        use_case = ClearTasksUseCase(mock_repo)

        result = use_case.execute(confirmed=True)

        assert result == 0
        mock_repo.clear_all_tasks.assert_called_once()
