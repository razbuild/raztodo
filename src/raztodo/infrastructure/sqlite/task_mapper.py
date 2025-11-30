import json
from typing import Any

from raztodo.domain.task_entity import TaskEntity


def row_to_task(row: Any) -> TaskEntity:
    """Convert a SQLite row to TaskEntity."""
    tags: list[str] = []

    row_keys = row.keys()
    if "tags" in row_keys:
        tags_str = row["tags"]
        if tags_str:
            try:
                tags = json.loads(tags_str)
                if not isinstance(tags, list):
                    tags = []
            except (json.JSONDecodeError, TypeError):
                tags = [t.strip() for t in tags_str.split(",") if t.strip()]

    description = (
        row["description"] if "description" in row_keys and row["description"] else ""
    )
    done = bool(row["done"]) if "done" in row_keys else False
    created_at = (
        row["created_at"] if "created_at" in row_keys and row["created_at"] else ""
    )
    priority = row["priority"] if "priority" in row_keys and row["priority"] else ""
    due_date = row["due_date"] if "due_date" in row_keys and row["due_date"] else None
    project = row["project"] if "project" in row_keys and row["project"] else None

    return TaskEntity(
        id=row["id"],
        title=row["title"],
        description=description,
        done=done,
        created_at=created_at,
        priority=priority,
        due_date=due_date,
        tags=tags,
        project=project,
    )
