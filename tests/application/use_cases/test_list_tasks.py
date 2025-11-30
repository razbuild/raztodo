from raztodo.application.use_cases.list_tasks import ListTasksUseCase
from raztodo.domain.task_entity import TaskEntity


class TestListTasksUseCase:
    """Test cases for ListTasksUseCase."""

    def test_list_all_tasks(self, mock_repo):
        """Test listing all tasks."""
        tasks = [TaskEntity(id=1, title="Task 1"), TaskEntity(id=2, title="Task 2")]
        mock_repo.get_tasks.return_value = tasks
        use_case = ListTasksUseCase(mock_repo)

        result = use_case.execute()

        assert result == tasks
        mock_repo.get_tasks.assert_called_once_with(
            limit=None,
            offset=None,
            priority=None,
            project=None,
            done=None,
            tags=None,
            due_before=None,
            due_after=None,
        )

    def test_list_tasks_with_filters(self, mock_repo):
        """Test listing tasks with filters."""
        tasks = [TaskEntity(id=1, title="Task 1")]
        mock_repo.get_tasks.return_value = tasks
        use_case = ListTasksUseCase(mock_repo)

        result = use_case.execute(
            limit=10,
            offset=5,
            priority="H",
            project="Work",
            done=False,
            tags=["urgent"],
            due_before="2025-12-31",
            due_after="2025-01-01",
        )

        assert result == tasks
        mock_repo.get_tasks.assert_called_once_with(
            limit=10,
            offset=5,
            priority="H",
            project="Work",
            done=False,
            tags=["urgent"],
            due_before="2025-12-31",
            due_after="2025-01-01",
        )
