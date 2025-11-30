from raztodo.domain.exceptions import RazTodoException
from raztodo.domain.task_repository import TaskRepository


class DeleteTaskUseCase:
    """
    Handles deletion of a task by ID via the repository.
    """

    def __init__(self, repo: TaskRepository) -> None:
        self.repo: TaskRepository = repo

    def execute(self, task_id: int) -> bool:
        """
        Delete a task by its ID.

        Args:
            task_id: ID of the task to delete.

        Returns:
            True if deletion was successful.

        Raises:
            RazTodoException: If no task with the given ID exists.
        """

        removed: int = self.repo.remove_task(task_id)
        if removed <= 0:
            raise RazTodoException(f"No task found with id {task_id}")
        return True
