import json
import os
import sqlite3
from collections.abc import Callable
from pathlib import Path
from sqlite3 import Connection
from types import TracebackType

from raztodo.domain.exceptions import RazTodoException
from raztodo.domain.task_entity import TaskEntity
from raztodo.domain.task_repository import TaskRepository
from raztodo.infrastructure.logger import get_logger
from raztodo.infrastructure.sqlite.task_dao import TaskDAO
from raztodo.infrastructure.sqlite.task_mapper import row_to_task

logger = get_logger("SQLiteTaskRepository")

MAX_TITLE_LENGTH = 60
MAX_DESCRIPTION_LENGTH = 200
VALID_PRIORITIES = {"", "L", "M", "H"}


def validate_length(field_name: str, value: str | None, max_length: int) -> str:
    value = (value or "").strip()
    if not value and field_name == "title":
        logger.warning("Attempt to add empty title")
        raise RazTodoException(f"TaskValidationError: '{field_name}' cannot be empty")
    if len(value) > max_length:
        logger.warning(f"Attempt to add too long {field_name}: {len(value)} characters")
        raise RazTodoException(
            f"TaskValidationError: '{field_name}' too long (max {max_length}, got {len(value)})"
        )
    return value


def normalize_priority(priority: str | None) -> str:
    priority = (priority or "").upper().strip()
    if priority not in VALID_PRIORITIES:
        logger.warning(f"Invalid priority: {priority}, using empty")
        return ""
    return priority


def normalize_tags(tags: list[str] | None) -> list[str]:
    return [t.strip() for t in (tags or []) if t.strip()]


def ensure_writable_path(filepath: str) -> Path:
    file_path = Path(filepath).resolve()
    dir_path = file_path.parent
    if dir_path and not dir_path.exists():
        try:
            dir_path.mkdir(parents=True, exist_ok=True)
        except OSError as e:
            logger.error(f"Failed to create directory {dir_path}: {e}")
            raise RazTodoException(
                f"FileOperationError: Cannot create directory {dir_path}"
            ) from e
    if file_path.exists() and not os.access(filepath, os.W_OK):
        raise RazTodoException(f"FilePermissionError: Cannot write to file {filepath}")
    return file_path


class SQLiteTaskRepository(TaskRepository):
    def __init__(self, connection_factory: Callable[[], Connection]):
        self._connection_factory = connection_factory
        self._conn: Connection | None = self._connection_factory()
        self._dao = TaskDAO(self._conn)

    def __enter__(self) -> TaskRepository:
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        self.close()

    def add_task(
        self,
        title: str,
        description: str = "",
        priority: str = "",
        due_date: str | None = None,
        tags: list[str] | None = None,
        project: str | None = None,
    ) -> int | None:
        title = validate_length("title", title, MAX_TITLE_LENGTH)
        description = validate_length(
            "description", description, MAX_DESCRIPTION_LENGTH
        )
        priority = normalize_priority(priority)
        tags = normalize_tags(tags)

        try:
            task_id = self._dao.insert(
                title, description, priority, due_date, tags, project
            )
            if not task_id:
                raise RazTodoException(
                    f"DuplicateTaskError: Task '{title}' already exists"
                )
            return task_id
        except sqlite3.IntegrityError as e:
            raise RazTodoException(f"DuplicateTaskError: {e}") from e
        except sqlite3.Error as e:
            raise RazTodoException(f"DatabaseError during add_task: {e}") from e

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
        # Pass arguments explicitly to avoid mypy errors with **kwargs unpacking
        rows = self._dao.fetch_all(
            limit=limit,
            offset=offset,
            priority=priority,
            project=project,
            done=done,
            tags=tags,
            due_before=due_before,
            due_after=due_after,
        )
        return [row_to_task(r) for r in rows]

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
        if title is not None:
            title = validate_length("title", title, MAX_TITLE_LENGTH)
        if description is not None:
            description = validate_length(
                "description", description, MAX_DESCRIPTION_LENGTH
            )
        if priority is not None:
            priority = normalize_priority(priority)
        if tags is not None:
            tags = normalize_tags(tags)
        if due_date == "":
            due_date = "__CLEAR__"
        if project == "":
            project = "__CLEAR__"

        try:
            return self._dao.update(
                task_id,
                title=title,
                description=description,
                priority=priority,
                due_date=due_date,
                tags=tags,
                project=project,
            )
        except sqlite3.Error as e:
            raise RazTodoException(
                f"DatabaseError during update_task {task_id}: {e}"
            ) from e

    def remove_task(self, task_id: int) -> int:
        return self._dao.delete(task_id)

    def search_tasks(
        self,
        keyword: str,
        priority: str | None = None,
        project: str | None = None,
        tags: list[str] | None = None,
    ) -> list[TaskEntity]:
        if not keyword or not keyword.strip():
            return []

        logger.info(
            f"Searching for: {keyword} with priority={priority}, project={project}, tags={tags}"
        )

        # Pass arguments explicitly to avoid dict unpacking type errors
        rows = self._dao.search(
            keyword.strip(), priority=priority, project=project, tags=tags
        )
        logger.info(f"Found {len(rows)} rows")
        return [row_to_task(r) for r in rows]

    def mark_done(self, task_id: int, done: bool = True) -> int:
        return self._dao.update(task_id, done=done)

    def export_tasks(self, filepath: str) -> bool:
        file_path = ensure_writable_path(filepath)
        try:
            tasks = self.get_tasks()
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(
                    [
                        {
                            "id": t.id,
                            "title": t.title,
                            "description": t.description,
                            "done": getattr(t, "done", False),
                            "created_at": getattr(t, "created_at", ""),
                            "priority": getattr(t, "priority", ""),
                            "due_date": getattr(t, "due_date", None),
                            "tags": getattr(t, "tags", []),
                            "project": getattr(t, "project", None),
                        }
                        for t in tasks
                    ],
                    f,
                    ensure_ascii=False,
                    indent=2,
                )
            logger.info(f"Exported {len(tasks)} tasks to {filepath}")
            return True
        except Exception as e:
            raise RazTodoException(
                f"FileOperationError during export_tasks: {e}"
            ) from e

    def import_tasks(self, filepath: str) -> int:
        file_path = Path(filepath)
        if not file_path.exists():
            raise RazTodoException(f"TaskFileNotFoundError: {filepath}")
        if not os.access(filepath, os.R_OK):
            raise RazTodoException(f"FilePermissionError: Cannot read {filepath}")

        try:
            data = json.loads(file_path.read_text(encoding="utf-8"))
        except Exception as e:
            raise RazTodoException(f"InvalidFileFormatError: {e}") from e

        if not isinstance(data, list):
            raise RazTodoException(
                f"InvalidFileFormatError: Expected JSON array in {filepath}"
            )

        count, errors = 0, []
        for idx, item in enumerate(data, start=1):
            if not isinstance(item, dict) or "title" not in item:
                logger.warning(f"Skipping invalid item at index {idx}")
                continue
            try:
                new_id = self.add_task(
                    item["title"],
                    item.get("description", ""),
                    item.get("priority", ""),
                    item.get("due_date"),
                    item.get("tags", []),
                    item.get("project"),
                )
                if new_id and "done" in item:
                    try:
                        self._dao.update(new_id, done=bool(item["done"]))
                    except sqlite3.Error as e:
                        logger.warning(
                            f"Failed to set done flag for task {new_id}: {e}"
                        )
                count += 1
            except RazTodoException as e:
                errors.append(f"Item {idx}: {e}")
                continue
            except Exception as e:
                errors.append(f"Item {idx}: {e}")
                continue

        if errors and count == 0:
            raise RazTodoException(
                f"Failed to import any tasks from {filepath}: {errors[:3]}"
            )

        logger.info(f"Imported {count} tasks from {filepath}")
        return count

    def clear_all_tasks(self) -> int:
        try:
            count = self._dao.clear_all()
            logger.info(f"Cleared {count} tasks from repository")
            return count
        except sqlite3.Error as e:
            raise RazTodoException(f"DatabaseError during clear_all_tasks: {e}") from e

    def close(self) -> None:
        if self._conn:
            self._conn.close()
            self._conn = None
