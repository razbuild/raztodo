from raztodo.domain.exceptions import RazTodoException
from raztodo.domain.task_repository import TaskRepository


class MarkDoneUseCase:
    """
    Marks a task as done or undone via the repository.
    """

    def __init__(self, repo: TaskRepository) -> None:
        self.repo: TaskRepository = repo

    def execute(self, task_id: int, done: bool = True) -> bool:
        """
        Update a task's completion status.

        Args:
            task_id: ID of the task to update.
            done: True to mark as done, False to mark as not done.

        Returns:
            True if the update was successful.

        Raises:
            RazTodoException: If no task with the given ID exists.
        """

        updated: int = self.repo.mark_done(task_id, done)
        if not updated:
            raise RazTodoException(f"No task found with id {task_id}")
        return True
