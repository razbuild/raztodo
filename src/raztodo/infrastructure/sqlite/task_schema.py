import sqlite3

from raztodo.infrastructure.logger import get_logger

logger = get_logger("task_schema")

CREATE_TABLE_TASKS = """
CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL CHECK(length(title) <= 60),
    description TEXT,
    done INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    priority TEXT DEFAULT '',
    due_date TEXT,
    tags TEXT DEFAULT '',
    project TEXT
)
"""

CREATE_UNIQUE_INDEX_TITLE = """
CREATE UNIQUE INDEX IF NOT EXISTS idx_tasks_title_unique
ON tasks(title)
"""

TRIGGERS = {
    "desc_len_insert": """
    CREATE TRIGGER IF NOT EXISTS trg_tasks_desc_len_insert
    BEFORE INSERT ON tasks
    FOR EACH ROW
    WHEN NEW.description IS NOT NULL AND length(NEW.description) > 200
    BEGIN
        SELECT RAISE(ABORT, 'description too long');
    END;
    """,
    "desc_len_update": """
    CREATE TRIGGER IF NOT EXISTS trg_tasks_desc_len_update
    BEFORE UPDATE OF description ON tasks
    FOR EACH ROW
    WHEN NEW.description IS NOT NULL AND length(NEW.description) > 200
    BEGIN
        SELECT RAISE(ABORT, 'description too long');
    END;
    """,
    "created_at_insert": """
    CREATE TRIGGER IF NOT EXISTS trg_tasks_created_at_insert
    AFTER INSERT ON tasks
    FOR EACH ROW
    WHEN NEW.created_at IS NULL OR NEW.created_at = ''
    BEGIN
        UPDATE tasks SET created_at = datetime('now') WHERE id = NEW.id;
    END;
    """,
}

INDEXES = [
    "CREATE INDEX IF NOT EXISTS idx_tasks_priority ON tasks(priority)",
    "CREATE INDEX IF NOT EXISTS idx_tasks_due_date ON tasks(due_date)",
    "CREATE INDEX IF NOT EXISTS idx_tasks_project ON tasks(project)",
    "CREATE INDEX IF NOT EXISTS idx_tasks_done ON tasks(done)",
    # Indexes for O(log n) search optimization
    "CREATE INDEX IF NOT EXISTS idx_tasks_title_search ON tasks(title)",
    "CREATE INDEX IF NOT EXISTS idx_tasks_description_search ON tasks(description)",
]

# FTS5 virtual table for full-text search (O(log n))
# When using content='tasks', SQLite automatically maintains the FTS table.
# Manual triggers are NOT needed and can cause database corruption.
CREATE_FTS_TABLE = """
CREATE VIRTUAL TABLE IF NOT EXISTS tasks_fts USING fts5(
    id UNINDEXED,
    title,
    description,
    content='tasks',
    content_rowid='id'
)
"""


def ensure_schema(conn: sqlite3.Connection) -> None:
    """Ensure that the tasks table, indexes, and triggers exist."""
    with conn:
        try:
            conn.execute(CREATE_TABLE_TASKS)
            logger.info("Tasks table ensured.")
        except sqlite3.Error as e:
            logger.error(f"Failed to create tasks table: {e}")
            raise

        # Unique index
        try:
            conn.execute(CREATE_UNIQUE_INDEX_TITLE)
        except sqlite3.Error as e:
            logger.warning(f"Could not create unique index: {e}")

        # Additional indexes
        for idx_sql in INDEXES:
            try:
                conn.execute(idx_sql)
            except sqlite3.Error as e:
                logger.warning(f"Failed to create index: {e}")

        # Triggers
        for name, trigger_sql in TRIGGERS.items():
            try:
                conn.execute(trigger_sql)
            except sqlite3.Error as e:
                logger.warning(f"Failed to create trigger {name}: {e}")

        # FTS5 virtual table for O(log n) search
        # When using content='tasks', SQLite automatically maintains the FTS table.
        # No manual triggers or population needed.
        try:
            conn.execute(CREATE_FTS_TABLE)
            logger.info("FTS5 virtual table ensured.")
        except sqlite3.Error as e:
            logger.warning(f"Failed to create FTS5 table: {e}")

        logger.info("Schema ensured successfully.")
