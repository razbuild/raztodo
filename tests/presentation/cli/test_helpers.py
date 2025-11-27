"""Tests for helper functions."""

import json
from unittest.mock import MagicMock

from raztodo.domain.task_entity import TaskEntity
from raztodo.presentation.cli.helpers import (
    format_task,
    format_tasks_list,
    handle_command_error,
    output_error,
    output_json,
    output_success,
    parse_tags,
    task_to_dict,
)


class TestParseTags:
    """Test cases for parse_tags function."""

    def test_parse_tags_with_valid_string(self):
        """Test parsing valid tags string."""
        result = parse_tags("tag1, tag2, tag3")
        assert result == ["tag1", "tag2", "tag3"]

    def test_parse_tags_with_spaces(self):
        """Test parsing tags with extra spaces."""
        result = parse_tags("  tag1  ,  tag2  ,  tag3  ")
        assert result == ["tag1", "tag2", "tag3"]

    def test_parse_tags_with_empty_string(self):
        """Test parsing empty string."""
        result = parse_tags("")
        assert result is None

    def test_parse_tags_with_none(self):
        """Test parsing None."""
        result = parse_tags(None)
        assert result is None

    def test_parse_tags_with_only_spaces(self):
        """Test parsing string with only spaces."""
        result = parse_tags("   ,  ,  ")
        assert result is None


class TestTaskToDict:
    """Test cases for task_to_dict function."""

    def test_task_to_dict_minimal(self):
        """Test converting minimal task to dict."""
        task = TaskEntity(id=1, title="Test")
        result = task_to_dict(task)

        assert result["id"] == 1
        assert result["title"] == "Test"
        assert result["description"] == ""
        assert result["done"] is False

    def test_task_to_dict_full(self):
        """Test converting full task to dict."""
        task = TaskEntity(
            id=1,
            title="Test",
            description="Desc",
            done=True,
            created_at="2025-01-01",
            priority="H",
            due_date="2025-02-01",
            tags=["tag1"],
            project="Work",
        )
        result = task_to_dict(task)

        assert result["id"] == 1
        assert result["title"] == "Test"
        assert result["description"] == "Desc"
        assert result["done"] is True
        assert result["priority"] == "H"
        assert result["tags"] == ["tag1"]
        assert result["project"] == "Work"


class TestOutputJson:
    """Test cases for output_json function."""

    def test_output_json(self, capsys):
        """Test JSON output."""
        data = {"key": "value"}
        output_json(data)

        captured = capsys.readouterr()
        assert json.loads(captured.out) == data


class TestOutputSuccess:
    """Test cases for output_success function."""

    def test_output_success_normal_mode(self, capsys):
        """Test success output in normal mode."""
        output_success("Task created")

        captured = capsys.readouterr()
        assert "Task created" in captured.out

    def test_output_success_json_mode(self, capsys):
        """Test success output in JSON mode."""
        output_success("Task created", json_mode=True, task_id=1)

        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert data["ok"] is True
        assert data["task_id"] == 1


class TestOutputError:
    """Test cases for output_error function."""

    def test_output_error_normal_mode(self, capsys):
        """Test error output in normal mode."""
        error = ValueError("Test error")
        output_error(error)

        captured = capsys.readouterr()
        assert "Test error" in captured.out

    def test_output_error_json_mode(self, capsys):
        """Test error output in JSON mode."""
        error = ValueError("Test error")
        output_error(error, json_mode=True, error_type="validation")

        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert data["ok"] is False
        assert data["error"] == "Test error"
        assert data["type"] == "validation"


class TestHandleCommandError:
    """Test cases for handle_command_error function."""

    def test_handle_command_error_with_task_id(self, capsys):
        """Test error handling with task_id."""
        error = ValueError("Error")
        args = MagicMock()
        args.json = False
        args.id = 123

        result = handle_command_error(error, args)

        assert result == 1
        captured = capsys.readouterr()
        assert "Error" in captured.out

    def test_handle_command_error_json_mode(self, capsys):
        """Test error handling in JSON mode."""
        error = ValueError("Error")
        args = MagicMock()
        args.json = True
        args.id = 123
        args.filepath = None  # Ensure filepath is None to avoid MagicMock serialization

        result = handle_command_error(error, args)

        assert result == 1
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert data["ok"] is False
        assert data["id"] == 123


class TestFormatTask:
    """Test cases for format_task function."""

    def test_format_task_minimal(self, capsys):
        """Test formatting minimal task."""
        task = TaskEntity(id=1, title="Test Task")
        format_task(task)

        captured = capsys.readouterr()
        assert "Test Task" in captured.out
        assert "#1" in captured.out

    def test_format_task_with_description(self, capsys):
        """Test formatting task with description."""
        task = TaskEntity(id=1, title="Test", description="Description")
        format_task(task)

        captured = capsys.readouterr()
        assert "Description" in captured.out

    def test_format_task_with_metadata(self, capsys):
        """Test formatting task with metadata."""
        task = TaskEntity(
            id=1,
            title="Test",
            priority="H",
            project="Work",
            tags=["urgent"],
            due_date="2025-02-01",
        )
        format_task(task)

        captured = capsys.readouterr()
        output = captured.out
        assert "Priority" in output or "priority" in output.lower()
        assert "Work" in output
        assert "urgent" in output


class TestFormatTasksList:
    """Test cases for format_tasks_list function."""

    def test_format_tasks_list_normal_mode(self, capsys):
        """Test formatting tasks list in normal mode."""
        tasks = [
            TaskEntity(id=1, title="Task 1"),
            TaskEntity(id=2, title="Task 2"),
        ]
        format_tasks_list(tasks, json_mode=False)

        captured = capsys.readouterr()
        assert "Task 1" in captured.out
        assert "Task 2" in captured.out

    def test_format_tasks_list_json_mode(self, capsys):
        """Test formatting tasks list in JSON mode."""
        tasks = [
            TaskEntity(id=1, title="Task 1"),
            TaskEntity(id=2, title="Task 2"),
        ]
        format_tasks_list(tasks, json_mode=True)

        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert isinstance(data, list)
        assert len(data) == 2
        assert data[0]["title"] == "Task 1"
