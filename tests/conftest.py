import contextlib
import os
import sqlite3
import tempfile
from unittest.mock import MagicMock

import pytest

from raztodo.infrastructure.sqlite.connection import (
    sqlite_connection_factory,
)
from raztodo.infrastructure.sqlite.task_repository import (
    SQLiteTaskRepository,
)


@pytest.fixture
def temp_db():
    """Create a temporary database file."""
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    yield path
    if os.path.exists(path):
        os.unlink(path)


@pytest.fixture
def in_memory_db():
    """Create an in-memory database connection factory and ensure cleanup."""
    base_factory = sqlite_connection_factory(None)
    connections: list[sqlite3.Connection] = []

    def factory():
        conn = base_factory()
        connections.append(conn)
        return conn

    yield factory

    while connections:
        conn = connections.pop()
        with contextlib.suppress(sqlite3.Error):
            conn.close()


@pytest.fixture
def task_repo(in_memory_db):
    """Create a task repository with in-memory database."""
    repo = SQLiteTaskRepository(connection_factory=in_memory_db)
    yield repo
    repo.close()


@pytest.fixture
def mock_repo():
    """Create a mock task repository."""
    return MagicMock(spec=SQLiteTaskRepository)


@pytest.fixture
def sample_task():
    """Sample task data."""
    from raztodo.domain.task_entity import TaskEntity

    return TaskEntity(
        id=1,
        title="Test Task",
        description="Test Description",
        done=False,
        created_at="2025-01-31 12:00:00",
        priority="M",
        due_date="2025-02-01",
        tags=["test", "sample"],
        project="TestProject",
    )
