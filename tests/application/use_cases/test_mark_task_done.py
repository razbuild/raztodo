import pytest

from raztodo.application.use_cases.mark_task_done import MarkDoneUseCase


class TestMarkDoneUseCase:
    """Test cases for MarkDoneUseCase."""

    def test_mark_task_done(self, mock_repo):
        """Test marking task as done."""
        mock_repo.mark_done.return_value = 1
        use_case = MarkDoneUseCase(mock_repo)

        result = use_case.execute(1, done=True)

        assert result is True
        mock_repo.mark_done.assert_called_once_with(1, True)

    def test_mark_task_undone(self, mock_repo):
        """Test marking task as undone."""
        mock_repo.mark_done.return_value = 1
        use_case = MarkDoneUseCase(mock_repo)

        result = use_case.execute(1, done=False)

        assert result is True
        mock_repo.mark_done.assert_called_once_with(1, False)

    def test_mark_nonexistent_task_done(self, mock_repo):
        """Test marking nonexistent task raises error."""
        mock_repo.mark_done.return_value = 0
        use_case = MarkDoneUseCase(mock_repo)

        from raztodo.domain.exceptions import RazTodoException

        with pytest.raises(RazTodoException) as exc_info:
            use_case.execute(999)

        assert (
            "999" in str(exc_info.value) or "not found" in str(exc_info.value).lower()
        )
