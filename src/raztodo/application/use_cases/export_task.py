from raztodo.domain.exceptions import RazTodoException
from raztodo.domain.task_repository import TaskRepository


class ExportTasksUseCase:
    """
    Handles exporting tasks to a specified file via the repository.
    """

    def __init__(self, repo: TaskRepository) -> None:
        """
        Export all tasks to the given file path.

        Args:
            filepath: Destination file path for exported tasks.

        Returns:
            True if export was successful.

        Raises:
            RazTodoException: If export fails (e.g., permission or disk issues).
        """

        self.repo: TaskRepository = repo

    def execute(self, filepath: str) -> bool:
        success: bool = self.repo.export_tasks(filepath)
        if not success:
            raise RazTodoException(
                f"Failed to export tasks to '{filepath}'. "
                "Check file permissions and disk space."
            )
        return True
