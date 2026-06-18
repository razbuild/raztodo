import json
import os
from collections.abc import Callable
from pathlib import Path
from sqlite3 import Connection, Error, IntegrityError
from types import TracebackType
from typing import cast

from typing_extensions import Any, override

from raztodo.domain.exceptions import RazTodoException
from raztodo.domain.task_entity import TaskEntity
from raztodo.domain.task_repository import TaskRepository
from raztodo.infrastructure.logger import get_logger
from raztodo.infrastructure.sqlite.task_dao import TaskDAO
from raztodo.infrastructure.sqlite.task_mapper import row_to_task

logger = get_logger(__name__)

MAX_TITLE_LENGTH = 60
MAX_DESCRIPTION_LENGTH = 200
VALID_PRIORITIES = {"", "L", "M", "H"}


def validate_length(field_name: str, value: str | None, max_length: int) -> str:
    value = (value or "").strip()
    if not value and field_name == "title":
        logger.warning("Validation failed: '%s' is empty", field_name)
        raise RazTodoException(f"TaskValidationError: '{field_name}' cannot be empty")
    if len(value) > max_length:
        logger.warning(
            "Validation failed: '%s' too long (%d chars, max %d)",
            field_name,
            len(value),
            max_length,
        )
        raise RazTodoException(
            f"TaskValidationError: '{field_name}' too long (max {max_length}, got {len(value)})"
        )
    return value


def normalize_priority(priority: str | None) -> str:
    priority = (priority or "").upper().strip()
    if priority not in VALID_PRIORITIES:
        logger.warning(
            "Invalid priority %r, expected one of %s — defaulting to empty",
            priority,
            VALID_PRIORITIES,
        )
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
            logger.exception("Failed to create directory %s", dir_path)
            raise RazTodoException(f"FileOperationError: Cannot create directory {dir_path}") from e
    if file_path.exists() and not os.access(str(file_path), os.W_OK):
        raise RazTodoException(f"FilePermissionError: Cannot write to file {file_path}")
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

    @override
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
        description = validate_length("description", description, MAX_DESCRIPTION_LENGTH)
        priority = normalize_priority(priority)
        tags = normalize_tags(tags)

        try:
            task_id = self._dao.insert(title, description, priority, due_date, tags, project)
            if not task_id:
                raise RazTodoException(f"DuplicateTaskError: Task '{title}' already exists")
            logger.info("Task created: id=%d, title=%r", task_id, title)
            return task_id
        except IntegrityError as e:
            raise RazTodoException(f"DuplicateTaskError: {e}") from e
        except Error as e:
            raise RazTodoException(f"DatabaseError during add_task: {e}") from e

    @override
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

    @override
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
            description = validate_length("description", description, MAX_DESCRIPTION_LENGTH)
        if priority is not None:
            priority = normalize_priority(priority)
        if tags is not None:
            tags = normalize_tags(tags)
        if due_date == "":
            due_date = "__CLEAR__"
        if project == "":
            project = "__CLEAR__"

        try:
            affected = self._dao.update(
                task_id,
                title=title,
                description=description,
                priority=priority,
                due_date=due_date,
                tags=tags,
                project=project,
            )
            logger.info("Task updated: id=%d, rows_affected=%d", task_id, affected)
            return affected
        except Error as e:
            raise RazTodoException(f"DatabaseError during update_task {task_id}: {e}") from e

    @override
    def remove_task(self, task_id: int) -> int:
        affected = self._dao.delete(task_id)
        logger.info("Task removed: id=%d, rows_affected=%d", task_id, affected)
        return affected

    @override
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
            "Searching tasks: keyword=%r, priority=%s, project=%s, tags=%s",
            keyword,
            priority,
            project,
            tags,
        )

        rows = self._dao.search(keyword.strip(), priority=priority, project=project, tags=tags)

        logger.info("Search for %r returned %d result(s)", keyword.strip(), len(rows))
        return [row_to_task(r) for r in rows]

    @override
    def mark_done(self, task_id: int, done: bool = True) -> int:
        affected = self._dao.update(task_id, done=done)
        logger.info("Task %d marked as done=%s, rows_affected=%d", task_id, done, affected)
        return affected

    @override
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
            logger.info("Exported %d tasks to %s", len(tasks), filepath)
            return True
        except Exception as e:
            raise RazTodoException(f"FileOperationError during export_tasks: {e}") from e

    @override
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
            raise RazTodoException(f"InvalidFileFormatError: Expected JSON array in {filepath}")

        count, errors = 0, []
        for idx, item in enumerate(data, start=1):
            if not isinstance(item, dict) or "title" not in item:
                logger.warning("Skipping item %d: not a dict or missing 'title' key", idx)
                continue

            task_data = cast(dict[str, Any], item)

            try:
                new_id = self.add_task(
                    task_data["title"],
                    task_data.get("description", ""),
                    task_data.get("priority", ""),
                    task_data.get("due_date"),
                    task_data.get("tags", []),
                    task_data.get("project"),
                )
                if new_id and "done" in task_data:
                    try:
                        self._dao.update(new_id, done=bool(task_data["done"]))
                    except Error as e:
                        logger.warning("Failed to set done flag for task %d: %s", new_id, e)
                count += 1
            except RazTodoException as e:
                errors.append(f"Item {idx}: {e}")
                continue
            except Exception as e:
                errors.append(f"Item {idx}: {e}")
                continue

        if errors and count == 0:
            raise RazTodoException(f"Failed to import any tasks from {filepath}: {errors[:3]}")

        logger.info("Imported %d tasks from %s", count, filepath)
        return count

    @override
    def clear_all_tasks(self) -> int:
        try:
            count = self._dao.clear_all()
            logger.info("Cleared %d tasks from repository", count)
            return count
        except Error as e:
            raise RazTodoException(f"DatabaseError during clear_all_tasks: {e}") from e

    def close(self) -> None:
        if self._conn:
            logger.debug("Closing SQLite connection")
            self._conn.close()
            self._conn = None
