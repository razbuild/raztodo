import pytest

from raztodo.domain.exceptions import (
    DuplicateTaskError,
    FileOperationError,
    FilePermissionError,
    InvalidFileFormatError,
    RazTodoException,
    TaskFileNotFoundError,
    TaskNotFoundError,
    TaskValidationError,
)


class TestRazTodoException:
    """Test cases for base RazTodoException."""

    def test_exception_inherits_from_exception(self):
        """Test that RazTodoException inherits from Exception."""
        assert issubclass(RazTodoException, Exception)

    def test_exception_can_be_raised(self):
        """Test that RazTodoException can be raised and caught."""
        with pytest.raises(RazTodoException):
            raise RazTodoException("Test error")


class TestTaskNotFoundError:
    """Test cases for TaskNotFoundError."""

    def test_default_message(self):
        """Test default error message."""
        error = TaskNotFoundError(task_id=5)
        assert str(error) == "No task found with id 5"
        assert error.task_id == 5

    def test_custom_message(self):
        """Test custom error message."""
        error = TaskNotFoundError(task_id=5, message="Custom error")
        assert str(error) == "Custom error"
        assert error.task_id == 5

    def test_inherits_from_raztodo_exception(self):
        """Test that TaskNotFoundError inherits from RazTodoException."""
        assert issubclass(TaskNotFoundError, RazTodoException)


class TestTaskValidationError:
    """Test cases for TaskValidationError."""

    def test_default_message_with_field_and_value(self):
        """Test default message with field and value."""
        error = TaskValidationError(field="title", value="")
        assert "Validation failed for field 'title'" in str(error)
        assert error.field == "title"
        assert error.value == ""

    def test_default_message_with_field_only(self):
        """Test default message with field only."""
        error = TaskValidationError(field="title")
        assert "Validation failed for field 'title'" in str(error)
        assert error.field == "title"
        assert error.value is None

    def test_default_message_no_field(self):
        """Test default message without field."""
        error = TaskValidationError()
        assert str(error) == "Task validation failed"

    def test_custom_message(self):
        """Test custom error message."""
        error = TaskValidationError(message="Custom validation error")
        assert str(error) == "Custom validation error"

    def test_inherits_from_raztodo_exception(self):
        """Test that TaskValidationError inherits from RazTodoException."""
        assert issubclass(TaskValidationError, RazTodoException)


class TestDuplicateTaskError:
    """Test cases for DuplicateTaskError."""

    def test_default_message(self):
        """Test default error message."""
        error = DuplicateTaskError(title="My Task")
        assert "Task already exists" in str(error)
        assert error.title == "My Task"

    def test_custom_message(self):
        """Test custom error message."""
        error = DuplicateTaskError(title="My Task", message="Custom duplicate error")
        assert str(error) == "Custom duplicate error"
        assert error.title == "My Task"

    def test_inherits_from_raztodo_exception(self):
        """Test that DuplicateTaskError inherits from RazTodoException."""
        assert issubclass(DuplicateTaskError, RazTodoException)


class TestFileOperationError:
    """Test cases for FileOperationError."""

    def test_default_message_with_filepath(self):
        """Test default message with filepath."""
        error = FileOperationError(filepath="/path/to/file.json")
        assert "File operation failed" in str(error)
        assert "/path/to/file.json" in str(error)
        assert error.filepath == "/path/to/file.json"

    def test_default_message_no_filepath(self):
        """Test default message without filepath."""
        error = FileOperationError()
        assert str(error) == "File operation failed"

    def test_custom_message(self):
        """Test custom error message."""
        error = FileOperationError(message="Custom file error")
        assert str(error) == "Custom file error"

    def test_inherits_from_raztodo_exception(self):
        """Test that FileOperationError inherits from RazTodoException."""
        assert issubclass(FileOperationError, RazTodoException)


class TestTaskFileNotFoundError:
    """Test cases for TaskFileNotFoundError."""

    def test_default_message(self):
        """Test default error message."""
        error = TaskFileNotFoundError(filepath="/path/to/missing.json")
        assert "File not found: /path/to/missing.json" in str(error)
        assert error.filepath == "/path/to/missing.json"

    def test_inherits_from_file_operation_error(self):
        """Test that TaskFileNotFoundError inherits from FileOperationError."""
        assert issubclass(TaskFileNotFoundError, FileOperationError)


class TestFilePermissionError:
    """Test cases for FilePermissionError."""

    def test_default_message(self):
        """Test default error message with default operation."""
        error = FilePermissionError(filepath="/path/to/file.json")
        assert "Permission denied" in str(error)
        assert "/path/to/file.json" in str(error)
        assert error.filepath == "/path/to/file.json"

    def test_custom_operation(self):
        """Test error message with custom operation."""
        error = FilePermissionError(filepath="/path/to/file.json", operation="write")
        assert "Permission denied" in str(error)
        assert "write" in str(error)
        assert "/path/to/file.json" in str(error)

    def test_inherits_from_file_operation_error(self):
        """Test that FilePermissionError inherits from FileOperationError."""
        assert issubclass(FilePermissionError, FileOperationError)


class TestInvalidFileFormatError:
    """Test cases for InvalidFileFormatError."""

    def test_default_message_with_filepath_and_format(self):
        """Test default message with filepath and format."""
        error = InvalidFileFormatError(
            filepath="/path/to/file.json", format_type="JSON"
        )
        assert "Invalid JSON format in file '/path/to/file.json'" in str(error)
        assert error.format_type == "JSON"
        assert error.filepath == "/path/to/file.json"

    def test_default_message_with_filepath_only(self):
        """Test default message with filepath only."""
        error = InvalidFileFormatError(filepath="/path/to/file.json")
        assert "Invalid file format: /path/to/file.json" in str(error)

    def test_default_message_with_format_only(self):
        """Test default message with format only."""
        error = InvalidFileFormatError(format_type="JSON")
        assert "Invalid JSON format" in str(error)

    def test_default_message_no_args(self):
        """Test default message with no arguments."""
        error = InvalidFileFormatError()
        assert str(error) == "Invalid file format"

    def test_custom_message(self):
        """Test custom error message."""
        error = InvalidFileFormatError(message="Custom format error")
        assert str(error) == "Custom format error"

    def test_inherits_from_file_operation_error(self):
        """Test that InvalidFileFormatError inherits from FileOperationError."""
        assert issubclass(InvalidFileFormatError, FileOperationError)
