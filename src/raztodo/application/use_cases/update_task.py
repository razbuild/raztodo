from raztodo.domain.exceptions import RazTodoException
from raztodo.domain.task_repository import TaskRepository


class UpdateTaskUseCase:
    """
    Updates an existing task's attributes via the repository.
    """

    def __init__(self, repo: TaskRepository) -> None:
        self.repo: TaskRepository = repo

    def execute(
        self,
        task_id: int,
        title: str | None = None,
        description: str | None = None,
        priority: str | None = None,
        due_date: str | None = None,
        tags: list[str] | None = None,
        project: str | None = None,
    ) -> bool:
        """
        Update task fields by ID.

        Args:
            task_id: ID of the task to update.
            title: Optional new title.
            description: Optional new description.
            priority: Optional new priority.
            due_date: Optional new due date.
            tags: Optional new list of tags.
            project: Optional new project name.

        Returns:
            True if the update was successful.

        Raises:
            RazTodoException: If the task does not exist or no changes were provided.
        """

        updated: int = self.repo.update_task(
            task_id, title, description, priority, due_date, tags, project
        )
        if not updated:
            raise RazTodoException(
                f"No task found with id {task_id} or no changes provided"
            )
        return True
