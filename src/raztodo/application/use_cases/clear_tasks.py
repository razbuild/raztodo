from raztodo.domain.task_repository import TaskRepository


class ClearTasksUseCase:
    """
    Clears all tasks from the repository with user validation.
    """

    def __init__(self, repo: TaskRepository) -> None:
        self.repo: TaskRepository = repo

    def execute(self, confirmed: bool = False) -> int:
        """
        Clear all tasks from the repository.

        Args:
            confirmed: Whether the user has confirmed the action. Must be True to proceed.

        Returns:
            Number of tasks deleted.

        Raises:
            ValueError: If confirmed is False (user validation failed).
        """
        if not confirmed:
            raise ValueError(
                "Clear operation requires explicit confirmation. "
                "This action cannot be undone. Use --confirm flag to proceed."
            )

        return self.repo.clear_all_tasks()
