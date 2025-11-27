from raztodo.application.use_cases.search_tasks import SearchTasksUseCase
from raztodo.domain.task_entity import TaskEntity


class TestSearchTasksUseCase:
    """Test cases for SearchTasksUseCase."""

    def test_search_tasks_success(self, mock_repo):
        """Test successful task search."""
        tasks = [TaskEntity(id=1, title="Test Task")]
        mock_repo.search_tasks.return_value = tasks
        use_case = SearchTasksUseCase(mock_repo)

        result = use_case.execute("test")

        assert result == tasks
        mock_repo.search_tasks.assert_called_once_with(
            "test", priority=None, project=None, tags=None
        )

    def test_search_tasks_with_filters(self, mock_repo):
        """Test task search with filters."""
        tasks = [TaskEntity(id=1, title="Test Task")]
        mock_repo.search_tasks.return_value = tasks
        use_case = SearchTasksUseCase(mock_repo)

        result = use_case.execute("test", priority="H", project="Work", tags=["urgent"])

        assert result == tasks
        mock_repo.search_tasks.assert_called_once_with(
            "test", priority="H", project="Work", tags=["urgent"]
        )

    def test_search_tasks_empty_keyword(self, mock_repo):
        """Test search with empty keyword returns empty list."""
        use_case = SearchTasksUseCase(mock_repo)

        result = use_case.execute("")

        assert result == []
        mock_repo.search_tasks.assert_not_called()

    def test_search_tasks_whitespace_keyword(self, mock_repo):
        """Test search with whitespace-only keyword returns empty list."""
        use_case = SearchTasksUseCase(mock_repo)

        result = use_case.execute("   ")

        assert result == []
        mock_repo.search_tasks.assert_not_called()
