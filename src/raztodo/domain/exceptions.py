class RazTodoException(Exception):
    """Base exception class for all RazTodo domain-specific errors."""

    pass


def default_message(base: str, **kwargs: str | None) -> str:
    """
    Builds a formatted message by appending keyword arguments to a base message.

    Args:
        base (str): The base error message.
        **kwargs (Optional[str]): Optional key-value pairs providing context.

    Returns:
        str: The composed error message.
    """

    parts = [f"{k}='{v}'" for k, v in kwargs.items() if v is not None]
    return f"{base}: {', '.join(parts)}" if parts else base


class TaskNotFoundError(RazTodoException):
    """
    Raised when a task with the specified identifier cannot be located.

    Args:
        task_id (int): Identifier of the missing task.
        message (Optional[str]): Custom message override.
    """

    def __init__(self, task_id: int, message: str | None = None) -> None:
        self.task_id = task_id
        super().__init__(message or f"No task found with id {task_id}")


class TaskValidationError(RazTodoException):
    """
    Raised when a task fails validation rules.

    Args:
        field (Optional[str]): Name of the invalid field, if applicable.
        value (Optional[str]): Provided invalid value.
        message (Optional[str]): Custom message override.
    """

    def __init__(
        self,
        field: str | None = None,
        value: str | None = None,
        message: str | None = None,
    ) -> None:
        self.field = field
        self.value = value

        if message is None:
            if field and value is not None:
                message = f"Validation failed for field '{field}': {value}"
            elif field:
                message = f"Validation failed for field '{field}'"
            else:
                message = "Task validation failed"

        super().__init__(message)


class DuplicateTaskError(RazTodoException):
    """
    Raised when attempting to create a task with a title that already exists.

    Args:
        title (str): Title of the conflicting task.
        message (Optional[str]): Custom message override.
    """

    def __init__(self, title: str, message: str | None = None) -> None:
        self.title = title
        super().__init__(message or default_message("Task already exists", title=title))


class FileOperationError(RazTodoException):
    """
    Raised when a file-related operation fails.

    Args:
        filepath (Optional[str]): Path of the involved file.
        message (Optional[str]): Custom message override.
    """

    def __init__(self, filepath: str | None = None, message: str | None = None) -> None:
        self.filepath = filepath
        super().__init__(
            message or default_message("File operation failed", filepath=filepath)
        )


class TaskFileNotFoundError(FileOperationError):
    """
    Raised when the expected task file is not found.

    Args:
        filepath (str): Path of the missing file.
    """

    def __init__(self, filepath: str) -> None:
        super().__init__(filepath=filepath, message=f"File not found: {filepath}")


class FilePermissionError(FileOperationError):
    """
    Raised when the system lacks permissions for a file operation.

    Args:
        filepath (str): Path of the target file.
        operation (str): Operation being attempted (e.g., read, write).
    """

    def __init__(self, filepath: str, operation: str = "access") -> None:
        super().__init__(
            filepath=filepath,
            message=f"Permission denied: Cannot {operation} '{filepath}'",
        )


class InvalidFileFormatError(FileOperationError):
    """
    Raised when a file has an invalid or unsupported format.

    Args:
        filepath (Optional[str]): Path of the problematic file.
        format_type (Optional[str]): File format that failed validation.
        message (Optional[str]): Custom message override.
    """

    def __init__(
        self,
        filepath: str | None = None,
        format_type: str | None = None,
        message: str | None = None,
    ) -> None:

        self.format_type = format_type

        if message is None:
            if filepath and format_type:
                message = f"Invalid {format_type} format in file '{filepath}'"
            elif filepath:
                message = f"Invalid file format: {filepath}"
            elif format_type:
                message = f"Invalid {format_type} format"
            else:
                message = "Invalid file format"

        super().__init__(filepath=filepath, message=message)


class DatabaseError(RazTodoException):
    """
    Raised when a database operation fails.

    Args:
        operation (Optional[str]): Type of operation attempted.
        message (Optional[str]): Custom message override.
    """

    def __init__(
        self, operation: str | None = None, message: str | None = None
    ) -> None:
        self.operation = operation
        super().__init__(
            message or default_message("Database operation failed", operation=operation)
        )


class DatabaseConnectionError(DatabaseError):
    """
    Raised when a connection to the database cannot be established.

    Args:
        message (Optional[str]): Custom message override.
    """

    def __init__(self, message: str | None = None) -> None:
        super().__init__(
            operation="connection",
            message=message or "Failed to connect to database",
        )


ERROR_TYPE_MAP: dict[str, type[RazTodoException]] = {
    """Mapping of string error identifiers to their corresponding exception types."""
    "not_found": TaskNotFoundError,
    "validation": TaskValidationError,
    "duplicate": DuplicateTaskError,
    "permission": FilePermissionError,
    "file_operation": FileOperationError,
    "invalid_format": InvalidFileFormatError,
    "file_not_found": TaskFileNotFoundError,
    "database": DatabaseError,
}
