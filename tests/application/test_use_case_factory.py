from unittest.mock import MagicMock

from raztodo.application.use_case_factory import DefaultUseCaseFactory
from raztodo.application.use_cases.clear_tasks import ClearTasksUseCase
from raztodo.application.use_cases.create_task import CreateTaskUseCase
from raztodo.application.use_cases.delete_task import DeleteTaskUseCase
from raztodo.application.use_cases.export_task import ExportTasksUseCase
from raztodo.application.use_cases.import_task import ImportTasksUseCase
from raztodo.application.use_cases.list_tasks import ListTasksUseCase
from raztodo.application.use_cases.mark_task_done import MarkDoneUseCase
from raztodo.application.use_cases.migrate_tasks import MigrateUseCase
from raztodo.application.use_cases.search_tasks import SearchTasksUseCase
from raztodo.application.use_cases.update_task import UpdateTaskUseCase


class TestUseCaseFactory:
    """Tests for DefaultUseCaseFactory."""

    def test_factory_creates_use_cases_with_repo(self, mock_repo):
        """Ensure each repo-based use case is instantiated with the provided repo."""
        factory = DefaultUseCaseFactory()

        use_cases = [
            (factory.create_create_task(mock_repo), CreateTaskUseCase),
            (factory.create_delete_task(mock_repo), DeleteTaskUseCase),
            (factory.create_list_tasks(mock_repo), ListTasksUseCase),
            (factory.create_update_task(mock_repo), UpdateTaskUseCase),
            (factory.create_search_tasks(mock_repo), SearchTasksUseCase),
            (factory.create_export_tasks(mock_repo), ExportTasksUseCase),
            (factory.create_import_tasks(mock_repo), ImportTasksUseCase),
            (factory.create_mark_done(mock_repo), MarkDoneUseCase),
            (factory.create_clear_tasks(mock_repo), ClearTasksUseCase),
        ]

        for instance, expected_cls in use_cases:
            assert isinstance(instance, expected_cls)
            assert instance.repo is mock_repo

    def test_factory_creates_migrate_use_case_with_connection_factory(self):
        """Ensure migrate use case receives the connection factory."""
        factory = DefaultUseCaseFactory()
        connection_factory = MagicMock(name="connection_factory")

        migrate_use_case = factory.create_migrate(connection_factory)

        assert isinstance(migrate_use_case, MigrateUseCase)
        assert migrate_use_case._connection_factory is connection_factory
