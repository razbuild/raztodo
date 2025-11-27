import pytest

from raztodo.application.use_cases.delete_task import DeleteTaskUseCase


class TestDeleteTaskUseCase:
    """Test cases for DeleteTaskUseCase."""

    def test_delete_task_success(self, mock_repo):
        """Test successful task deletion."""
        mock_repo.remove_task.return_value = 1
        use_case = DeleteTaskUseCase(mock_repo)

        result = use_case.execute(1)

        assert result is True
        mock_repo.remove_task.assert_called_once_with(1)

    def test_delete_nonexistent_task(self, mock_repo):
        """Test deleting nonexistent task raises error."""
        from raztodo.domain.exceptions import RazTodoException

        mock_repo.remove_task.return_value = 0
        use_case = DeleteTaskUseCase(mock_repo)

        with pytest.raises(RazTodoException) as exc_info:
            use_case.execute(999)

        assert (
            "999" in str(exc_info.value) or "not found" in str(exc_info.value).lower()
        )
