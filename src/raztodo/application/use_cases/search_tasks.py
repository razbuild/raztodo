from raztodo.domain.task_entity import TaskEntity
from raztodo.domain.task_repository import TaskRepository


class SearchTasksUseCase:
    """
    Searches tasks in the repository by keyword with optional filters.
    """

    def __init__(self, repo: TaskRepository) -> None:
        self.repo: TaskRepository = repo

    def execute(
        self,
        keyword: str,
        priority: str | None = None,
        project: str | None = None,
        tags: list[str] | None = None,
    ) -> list[TaskEntity]:
        """
        Search tasks matching a keyword and optional filters.

        Args:
            keyword: Text to search in task titles/descriptions.
            priority: Optional filter by task priority.
            project: Optional filter by project name.
            tags: Optional filter by tags.

        Returns:
            List of TaskEntity objects matching the search criteria.
        """

        if not keyword.strip():
            return []
        return self.repo.search_tasks(
            keyword, priority=priority, project=project, tags=tags
        )
