import json
import os
from typing import Any

from raztodo.domain.exceptions import RazTodoException
from raztodo.domain.task_entity import TaskEntity
from raztodo.domain.task_repository import TaskRepository


class ImportTasksUseCase:
    """
    Handles importing tasks from a JSON file, with optional upsert support.
    """

    def __init__(self, repo: TaskRepository) -> None:
        self.repo: TaskRepository = repo

    def execute(self, filepath: str, upsert: bool = False) -> int | dict[str, int]:
        """
        Import tasks from a file, optionally updating existing tasks.

        Args:
            filepath: Path to the JSON file containing tasks.
            upsert: If True, update existing tasks with matching titles.

        Returns:
            Number of tasks imported, or a dict with counts of inserted and updated tasks if upsert is True.

        Raises:
            RazTodoException: If file is missing, unreadable, JSON is invalid, or import fails.
        """

        try:
            if not os.path.exists(filepath):
                raise RazTodoException(f"File not found: {filepath}")

            if not os.access(filepath, os.R_OK):
                raise RazTodoException(f"Permission denied: Cannot read '{filepath}'")

            if not upsert:
                return self.repo.import_tasks(filepath)

            with open(filepath, encoding="utf-8") as f:
                data: Any = json.load(f)

            if not isinstance(data, list):
                raise RazTodoException(
                    f"Expected JSON array in '{filepath}', got {type(data).__name__}"
                )

            inserted: int = 0
            updated: int = 0
            for item in data:
                if not isinstance(item, dict):
                    continue

                title: str = item.get("title", "").strip()
                if not title:
                    continue

                desc: str = item.get("description", "")
                priority: str = item.get("priority") or ""
                due_date: str | None = item.get("due_date")
                tags: list[str] = item.get("tags") or []
                project: str | None = item.get("project")

                try:
                    inserted_id: int | None = self.repo.add_task(
                        title, desc, priority, due_date, tags, project
                    )
                    if inserted_id:
                        if "done" in item:
                            self.repo.mark_done(inserted_id, bool(item["done"]))
                        inserted += 1
                        continue
                except RazTodoException:
                    pass

                matches: list[TaskEntity] = [
                    t for t in self.repo.search_tasks(title) if t.title == title
                ]
                if matches:
                    task = matches[0]
                    self.repo.update_task(
                        task.id,
                        title=title,
                        description=desc,
                        priority=priority or None,
                        due_date=due_date,
                        tags=tags if tags else None,
                        project=project,
                    )
                    if "done" in item:
                        self.repo.mark_done(task.id, bool(item["done"]))
                    updated += 1

            return {"inserted": inserted, "updated": updated}

        except json.JSONDecodeError as e:
            raise RazTodoException(
                f"Invalid JSON format in '{filepath}': {e.msg} at line {e.lineno}"
            ) from e
        except UnicodeDecodeError as e:
            raise RazTodoException(f"File encoding error in '{filepath}': {e}") from e
        except OSError as e:
            raise RazTodoException(
                f"I/O error while accessing '{filepath}': {e}"
            ) from e
