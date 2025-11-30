from raztodo.domain.exceptions import RazTodoException
from raztodo.domain.task_repository import TaskRepository

MAX_TITLE_LENGTH = 60


class CreateTaskUseCase:
    """
    Handles creation of a new task with validation and repository interaction.
    """

    def __init__(self, repo: TaskRepository) -> None:
        self.repo: TaskRepository = repo

    def execute(
        self,
        title: str,
        description: str = "",
        priority: str = "",
        due_date: str | None = None,
        tags: list[str] | None = None,
        project: str | None = None,
    ) -> int:
        """
        Create a task after validating title and length.

        Args:
            title: Task title (required, max 60 chars).
            description: Optional task description.
            priority: Optional task priority.
            due_date: Optional due date in string format.
            tags: Optional list of tags.
            project: Optional project name.

        Returns:
            ID of the newly created task.

        Raises:
            RazTodoException: If validation fails or task creation fails.
        """

        title_stripped: str = title.strip() if title else ""
        if not title_stripped:
            raise RazTodoException("Task title cannot be empty")

        if len(title_stripped) > MAX_TITLE_LENGTH:
            raise RazTodoException(
                f"Task title too long. Maximum {MAX_TITLE_LENGTH} characters, "
                f"provided {len(title_stripped)}"
            )

        task_id: int | None = self.repo.add_task(
            title_stripped, description, priority, due_date, tags, project
        )
        if not task_id:
            raise RazTodoException(
                f"Failed to create task. Title '{title_stripped}' might already exist or validation failed"
            )

        return task_id
