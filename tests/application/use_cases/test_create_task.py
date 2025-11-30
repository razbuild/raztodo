import pytest

from raztodo.application.use_cases.create_task import CreateTaskUseCase
from raztodo.domain.exceptions import RazTodoException


class TestCreateTaskUseCase:
    """Test cases for CreateTaskUseCase."""

    def test_create_task_success(self, mock_repo):
        """Test successful task creation."""
        mock_repo.add_task.return_value = 1
        use_case = CreateTaskUseCase(mock_repo)

        result = use_case.execute("Test Task", "Description")

        assert result == 1
        mock_repo.add_task.assert_called_once_with(
            "Test Task", "Description", "", None, None, None
        )

    def test_create_task_with_all_fields(self, mock_repo):
        """Test task creation with all optional fields."""
        mock_repo.add_task.return_value = 1
        use_case = CreateTaskUseCase(mock_repo)

        result = use_case.execute(
            "Test Task",
            "Description",
            priority="H",
            due_date="2025-02-01",
            tags=["tag1", "tag2"],
            project="Project1",
        )

        assert result == 1
        mock_repo.add_task.assert_called_once_with(
            "Test Task", "Description", "H", "2025-02-01", ["tag1", "tag2"], "Project1"
        )

    def test_create_task_empty_title(self, mock_repo):
        """Test creating task with empty title raises error."""
        use_case = CreateTaskUseCase(mock_repo)

        with pytest.raises(RazTodoException) as exc_info:
            use_case.execute("")

        assert (
            "title" in str(exc_info.value).lower()
            or "empty" in str(exc_info.value).lower()
        )

    def test_create_task_whitespace_title(self, mock_repo):
        """Test creating task with whitespace-only title raises error."""
        use_case = CreateTaskUseCase(mock_repo)

        with pytest.raises(RazTodoException) as exc_info:
            use_case.execute("   ")

        assert (
            "title" in str(exc_info.value).lower()
            or "empty" in str(exc_info.value).lower()
        )

    def test_create_task_title_too_long(self, mock_repo):
        """Test creating task with title exceeding max length."""
        use_case = CreateTaskUseCase(mock_repo)
        long_title = "a" * 61

        with pytest.raises(RazTodoException) as exc_info:
            use_case.execute(long_title)

        assert "title" in str(exc_info.value).lower()
        assert "60" in str(exc_info.value)

    def test_create_task_title_stripped(self, mock_repo):
        """Test that title is stripped of whitespace."""
        mock_repo.add_task.return_value = 1
        use_case = CreateTaskUseCase(mock_repo)

        use_case.execute("  Test Task  ")

        mock_repo.add_task.assert_called_once_with(
            "Test Task", "", "", None, None, None
        )

    def test_create_task_duplicate_raises_error(self, mock_repo):
        """Test creating duplicate task raises error."""
        mock_repo.add_task.return_value = None
        use_case = CreateTaskUseCase(mock_repo)

        with pytest.raises(RazTodoException) as exc_info:
            use_case.execute("Existing Task")
        assert (
            "failed" in str(exc_info.value).lower()
            or "duplicate" in str(exc_info.value).lower()
            or "already exists" in str(exc_info.value).lower()
        )
