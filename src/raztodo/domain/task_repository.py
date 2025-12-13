from abc import ABC, abstractmethod

from raztodo.domain.task_entity import TaskEntity


class TaskRepository(ABC):
    """
    Abstract repository interface defining persistence operations for TaskEntity objects.
    Implementations encapsulate data storage, retrieval, filtering, and mutation logic.
    """

    @abstractmethod
    def add_task(
        self,
        title: str,
        description: str = "",
        priority: str = "",
        due_date: str | None = None,
        tags: list[str] | None = None,
        project: str | None = None,
    ) -> int | None:
        """
        Creates a new task and persists it.

        Args:
            title (str): Title of the task.
            description (str): Optional description text.
            priority (str): Task priority level.
            due_date (str | None): Due date value.
            tags (list[str] | None): Associated tags.
            project (str | None): Project name.

        Returns:
            int | None: The generated task ID, or None if creation fails.
        """
        pass

    @abstractmethod
    def get_tasks(
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
        Retrieves a list of tasks with optional filtering and pagination.

        Args:
            limit (int | None): Maximum number of tasks to return.
            offset (int | None): Number of tasks to skip.
            priority (str | None): Filter by priority.
            project (str | None): Filter by project.
            done (bool | None): Filter by completion status.
            tags (list[str] | None): Filter by associated tags.
            due_before (str | None): Filter tasks with due dates before this value.
            due_after (str | None): Filter tasks with due dates after this value.

        Returns:
            list[TaskEntity]: A list of matching TaskEntity objects.
        """
        pass

    @abstractmethod
    def update_task(
        self,
        task_id: int,
        title: str | None = None,
        description: str | None = None,
        priority: str | None = None,
        due_date: str | None = None,
        tags: list[str] | None = None,
        project: str | None = None,
    ) -> int:
        """
        Updates fields of an existing task.

        Args:
            task_id (int): Unique identifier of the task to update.
            title (str | None): Updated title.
            description (str | None): Updated description.
            priority (str | None): Updated priority.
            due_date (str | None): Updated due date.
            tags (list[str] | None): Updated tags.
            project (str | None): Updated project association.

        Returns:
            int: Number of affected records (typically 1).
        """
        pass

    @abstractmethod
    def remove_task(self, task_id: int) -> int:
        """
        Deletes a task from the repository.

        Args:
            task_id (int): Identifier of the task to remove.

        Returns:
            int: Number of deleted records (typically 1).
        """
        pass

    @abstractmethod
    def mark_done(self, task_id: int, done: bool = True) -> int:
        """
        Updates the completion status of a task.

        Args:
            task_id (int): Identifier of the task.
            done (bool): Completion flag.

        Returns:
            int: Number of updated records.
        """
        pass

    @abstractmethod
    def search_tasks(
        self,
        keyword: str,
        priority: str | None = None,
        project: str | None = None,
        tags: list[str] | None = None,
    ) -> list[TaskEntity]:
        """
        Performs a keyword-based search in task titles and descriptions,
        with optional metadata filtering.

        Args:
            keyword (str): Search term.
            priority (str | None): Filter by priority.
            project (str | None): Filter by project.
            tags (list[str] | None): Filter by tags.

        Returns:
            list[TaskEntity]: Matching tasks.
        """
        pass

    @abstractmethod
    def export_tasks(self, filepath: str) -> bool:
        """
        Exports tasks to an external file.

        Args:
            filepath (str): Path to the output file.

        Returns:
            bool: True if export succeeds; False otherwise.
        """
        pass

    @abstractmethod
    def import_tasks(self, filepath: str) -> int:
        """
        Imports tasks from a file.

        Args:
            filepath (str): Path to the input file.

        Returns:
            int: Count of successfully imported tasks.
        """
        pass

    @abstractmethod
    def clear_all_tasks(self) -> int:
        """
        Deletes all tasks from the repository.

        Returns:
            int: Number of deleted records.
        """
        pass
