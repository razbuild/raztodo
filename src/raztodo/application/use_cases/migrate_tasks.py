from collections.abc import Callable
from sqlite3 import Connection

from raztodo.infrastructure.sqlite.migrations import (
    create_unique_title_index,
    deduplicate_titles,
)


class MigrateUseCase:
    """
    Handles database migration tasks such as deduplicating titles and creating indexes.
    """

    def __init__(self, connection_factory: Callable[[], Connection]) -> None:
        self._connection_factory: Callable[[], Connection] = connection_factory

    def execute(self) -> dict[str, object]:
        """
        Perform migration: fix duplicate task titles and create unique title index.

        Returns:
            A dictionary with migration results:
                - 'duplicates_fixed': number of duplicate titles corrected
                - 'unique_index': True if the unique index was created

        Raises:
            Any exceptions from database operations are propagated.
        """

        conn: Connection = self._connection_factory()
        try:
            updated: int = deduplicate_titles(conn)
            create_unique_title_index(conn)
            return {"duplicates_fixed": updated, "unique_index": True}
        finally:
            conn.close()
