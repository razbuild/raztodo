import json
from collections.abc import Callable
from sqlite3 import Connection, Row
from typing import Any

from raztodo.infrastructure.sqlite.task_schema import ensure_schema


class TaskDAO:
    def __init__(self, conn: Connection):
        self._conn = conn
        ensure_schema(self._conn)

    def insert(
        self,
        title: str,
        description: str = "",
        priority: str = "",
        due_date: str | None = None,
        tags: list[str] | None = None,
        project: str | None = None,
    ) -> int:
        tags_str = json.dumps(tags) if tags else ""
        with self._conn:
            cur = self._conn.execute(
                "INSERT INTO tasks (title, description, priority, due_date, tags, project) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (title, description, priority, due_date, tags_str, project),
            )
            return cur.lastrowid or 0

    def _add_filter(
        self,
        query_parts: list[str],
        params: list[Any],
        field: str,
        value: Any,
        transform: Callable[[Any], Any] = lambda x: x,
    ) -> None:
        if value is not None:
            query_parts.append(f"{field} = ?")
            params.append(transform(value))

    def _add_tags_filter(
        self, query_parts: list[str], params: list[Any], tags: list[str] | None
    ) -> None:
        if tags:
            query_parts.append("(" + " OR ".join("tags LIKE ?" for _ in tags) + ")")
            params.extend(f"%{tag}%" for tag in tags)

    def fetch_all(
        self,
        limit: int | None = None,
        offset: int | None = None,
        priority: str | None = None,
        project: str | None = None,
        done: bool | None = None,
        tags: list[str] | None = None,
        due_before: str | None = None,
        due_after: str | None = None,
    ) -> list[Row]:
        query_parts = [
            "SELECT id, title, description, done, created_at, priority, due_date, tags, project FROM tasks WHERE 1=1"
        ]
        params: list[Any] = []

        self._add_filter(query_parts, params, "priority", priority)
        self._add_filter(query_parts, params, "project", project)
        self._add_filter(query_parts, params, "done", done, lambda x: 1 if x else 0)
        if due_before:
            query_parts.append("due_date IS NOT NULL AND due_date <= ?")
            params.append(due_before)
        if due_after:
            query_parts.append("due_date IS NOT NULL AND due_date >= ?")
            params.append(due_after)
        self._add_tags_filter(query_parts, params, tags)

        query = " AND ".join(query_parts) + " ORDER BY id"

        if limit is not None and offset is not None:
            query += " LIMIT ? OFFSET ?"
            params.extend([limit, offset])
        elif limit is not None:
            query += " LIMIT ?"
            params.append(limit)
        elif offset is not None:
            query += " LIMIT -1 OFFSET ?"
            params.append(offset)

        cur = self._conn.execute(query, params)
        return cur.fetchall()

    def update(
        self,
        task_id: int,
        title: str | None = None,
        description: str | None = None,
        done: bool | None = None,
        priority: str | None = None,
        due_date: str | None = None,
        tags: list[str] | None = None,
        project: str | None = None,
    ) -> int:
        updates: list[str] = []
        params: list[Any] = []

        def add_update(
            field: str,
            value: Any,
            clear_marker: str = "__CLEAR__",
            transform: Callable[[Any], Any] = lambda x: x,
        ) -> None:
            if value is None:
                return
            if value == clear_marker:
                updates.append(f"{field} = NULL")
            else:
                updates.append(f"{field} = ?")
                params.append(transform(value))

        add_update("title", title)
        add_update("description", description)
        add_update("done", done, transform=lambda x: 1 if x else 0)
        add_update("priority", priority)
        add_update("due_date", due_date)
        add_update("tags", json.dumps(tags) if tags is not None else None)
        add_update("project", project)

        if not updates:
            return 0

        params.append(task_id)
        with self._conn:
            cur = self._conn.execute(
                f"UPDATE tasks SET {', '.join(updates)} WHERE id = ?", params
            )
            return cur.rowcount

    def delete(self, task_id: int) -> int:
        with self._conn:
            cur = self._conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
            return cur.rowcount

    def clear_all(self) -> int:
        """Delete all tasks from the database."""
        with self._conn:
            cur = self._conn.execute("DELETE FROM tasks")
            return cur.rowcount

    def search(
        self,
        keyword: str,
        priority: str | None = None,
        project: str | None = None,
        tags: list[str] | None = None,
    ) -> list[Row]:
        # Use FTS5 for O(log n) search performance
        # Escape special FTS5 characters and use phrase search for exact matching
        keyword_escaped = keyword.replace('"', '""')
        fts_query = f'"{keyword_escaped}"*'  # Prefix search for better performance

        # Build query using FTS5 for O(log n) search
        query_parts = [
            """SELECT t.id, t.title, t.description, t.done, t.created_at, 
               t.priority, t.due_date, t.tags, t.project 
               FROM tasks t
               INNER JOIN tasks_fts fts ON t.id = fts.rowid
               WHERE fts MATCH ?"""
        ]
        params: list[Any] = [fts_query]

        # Add additional filters on the main table
        filter_parts: list[str] = []
        if priority is not None:
            filter_parts.append("t.priority = ?")
            params.append(priority)
        if project is not None:
            filter_parts.append("t.project = ?")
            params.append(project)
        if tags:
            tag_filters = " OR ".join("t.tags LIKE ?" for _ in tags)
            filter_parts.append(f"({tag_filters})")
            params.extend(f"%{tag}%" for tag in tags)

        if filter_parts:
            query_parts[0] += " AND " + " AND ".join(filter_parts)

        query = query_parts[0] + " ORDER BY t.id"

        try:
            cur = self._conn.execute(query, params)
            return cur.fetchall()
        except Exception:
            # Fallback to LIKE if FTS5 is not available (backward compatibility)
            pattern = f"%{keyword}%"
            query_parts = [
                "SELECT id, title, description, done, created_at, priority, due_date, tags, project FROM tasks WHERE (title LIKE ? OR description LIKE ?)"
            ]
            params = [pattern, pattern]

            self._add_filter(query_parts, params, "priority", priority)
            self._add_filter(query_parts, params, "project", project)
            self._add_tags_filter(query_parts, params, tags)

            query = " AND ".join(query_parts) + " ORDER BY id"
            cur = self._conn.execute(query, params)
            return cur.fetchall()
