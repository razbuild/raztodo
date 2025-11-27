from sqlite3 import Connection


def deduplicate_titles(conn: Connection) -> int:
    updated: int = 0
    cur = conn.execute("SELECT title FROM tasks GROUP BY title HAVING COUNT(*) > 1")
    duplicate_titles: list[str] = [row[0] for row in cur.fetchall()]

    for title in duplicate_titles:
        rows: list[tuple[int]] = conn.execute(
            "SELECT id FROM tasks WHERE title = ? ORDER BY id",
            (title,),
        ).fetchall()

        for idx, row in enumerate(rows, start=1):
            task_id: int = row[0]
            if idx == 1:
                continue

            new_title: str = f"{title} ({idx})"
            k: int = idx

            while True:
                exists = conn.execute(
                    "SELECT 1 FROM tasks WHERE title = ? LIMIT 1",
                    (new_title,),
                ).fetchone()

                if not exists:
                    break

                k += 1
                new_title = f"{title} ({k})"

            with conn:
                conn.execute(
                    "UPDATE tasks SET title = ? WHERE id = ?",
                    (new_title, task_id),
                )
                updated += 1

    return updated


def create_unique_title_index(conn: Connection) -> None:
    conn.execute(
        """
        CREATE UNIQUE INDEX IF NOT EXISTS idx_tasks_title_unique
        ON tasks(title)
        """
    )
