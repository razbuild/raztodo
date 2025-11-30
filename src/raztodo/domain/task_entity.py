from dataclasses import dataclass


@dataclass
class TaskEntity:
    """
    Represents a task item with metadata including status, priority, deadlines,
    and optional categorization attributes such as tags and project association.

    Attributes:
        id (int): Unique identifier for the task.
        title (str): Short title describing the task.
        description (str): Detailed textual description of the task.
        done (bool): Completion status of the task.
        created_at (str): Timestamp indicating when the task was created.
        priority (str): Priority level (e.g., low, medium, high).
        due_date (Optional[str]): Deadline for task completion, if any.
        tags (Optional[List[str]]): List of associated keywords or labels.
        project (Optional[str]): Name of the related project, if applicable.
    """

    id: int
    title: str
    description: str = ""
    done: bool = False
    created_at: str = ""
    priority: str = ""
    due_date: str | None = None
    tags: list[str] | None = None
    project: str | None = None

    def __post_init__(self) -> None:
        """
        Normalizes optional collection fields after initialization by ensuring
        that tags are always stored as a list.
        """

        self.tags = list(self.tags) if self.tags else []
