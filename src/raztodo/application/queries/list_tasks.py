from raztodo.domain.task_entity import TaskEntity
from raztodo.domain.task_repository import TaskRepository


class ListTasksUseCase:
    """
    Retrieves tasks from the repository with optional filtering and pagination.
    """

    def __init__(self, repo: TaskRepository) -> None:
        self.repo: TaskRepository = repo

    def execute(
        self,
        limit: int | None = None,
        offset: int | None = None,
        priority: str | None = None,
        project: str | None = None,
        done: bool | None = None,
        tags: list[str] | None = None,
        due_before: str | None = None,
        due_after: str | None = None,
    ) -> list[TaskEntity]:
        """
        List tasks with optional filters.

        Args:
            limit: Maximum number of tasks to return.
            offset: Number of tasks to skip.
            priority: Filter by task priority.
            project: Filter by project name.
            done: Filter by completion status.
            tags: Filter by tags.
            due_before: Filter tasks due before this date.
            due_after: Filter tasks due after this date.

        Returns:
            List of TaskEntity objects matching the filters.
        """

        return self.repo.get_tasks(
            limit=limit,
            offset=offset,
            priority=priority,
            project=project,
            done=done,
            tags=tags,
            due_before=due_before,
            due_after=due_after,
        )
