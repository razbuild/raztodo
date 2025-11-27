from raztodo.domain.task_entity import TaskEntity


class TestTaskEntity:
    """Test cases for TaskEntity."""

    def test_task_creation_with_minimal_fields(self):
        """Test creating a task with minimal required fields."""
        task = TaskEntity(id=1, title="My Task")
        assert task.id == 1
        assert task.title == "My Task"
        assert task.description == ""
        assert task.done is False
        assert task.created_at == ""
        assert task.priority == ""
        assert task.due_date is None
        assert task.tags == []
        assert task.project is None

    def test_task_creation_with_all_fields(self):
        """Test creating a task with all fields."""
        task = TaskEntity(
            id=1,
            title="My Task",
            description="Task description",
            done=True,
            created_at="2025-01-31 12:00:00",
            priority="H",
            due_date="2025-02-01",
            tags=["urgent", "important"],
            project="Work",
        )
        assert task.id == 1
        assert task.title == "My Task"
        assert task.description == "Task description"
        assert task.done is True
        assert task.created_at == "2025-01-31 12:00:00"
        assert task.priority == "H"
        assert task.due_date == "2025-02-01"
        assert task.tags == ["urgent", "important"]
        assert task.project == "Work"

    def test_task_tags_default_to_empty_list(self):
        """Test that tags default to empty list when None."""
        task = TaskEntity(id=1, title="Task", tags=None)
        assert task.tags == []

    def test_task_tags_are_preserved(self):
        """Test that provided tags are preserved."""
        tags = ["tag1", "tag2", "tag3"]
        task = TaskEntity(id=1, title="Task", tags=tags)
        assert task.tags == tags
        assert task.tags is not tags  # Should be a copy/new list

    def test_task_default_values(self):
        """Test default values for optional fields."""
        task = TaskEntity(id=1, title="Task")
        assert task.description == ""
        assert task.done is False
        assert task.created_at == ""
        assert task.priority == ""
        assert task.due_date is None
        assert task.tags == []
        assert task.project is None

    def test_task_equality(self):
        """Test task equality comparison."""
        task1 = TaskEntity(id=1, title="Task", description="Desc")
        task2 = TaskEntity(id=1, title="Task", description="Desc")
        assert task1 == task2

    def test_task_inequality_different_id(self):
        """Test that tasks with different IDs are not equal."""
        task1 = TaskEntity(id=1, title="Task")
        task2 = TaskEntity(id=2, title="Task")
        assert task1 != task2
