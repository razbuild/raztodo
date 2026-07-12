from collections.abc import Callable
from typing import Any, Protocol

from raztodo.domain.task_repository import TaskRepository


class UseCaseFactory(Protocol):
    """Protocol for creating use case instances."""

    def create_create_task(self, repo: TaskRepository) -> Any:
        pass

    def create_delete_task(self, repo: TaskRepository) -> Any:
        pass

    def create_list_tasks(self, repo: TaskRepository) -> Any:
        pass

    def create_update_task(self, repo: TaskRepository) -> Any:
        pass

    def create_search_tasks(self, repo: TaskRepository) -> Any:
        pass

    def create_export_tasks(self, repo: TaskRepository) -> Any:
        pass

    def create_import_tasks(self, repo: TaskRepository) -> Any:
        pass

    def create_mark_done(self, repo: TaskRepository) -> Any:
        pass

    def create_migrate(self, connection_factory: Callable[..., Any]) -> Any:
        pass

    def create_clear_tasks(self, repo: TaskRepository) -> Any:
        pass

    def create_explain_task(self, repo: TaskRepository) -> Any:
        pass


class DefaultUseCaseFactory:
    """Default implementation of UseCaseFactory with lazy imports."""

    def create_create_task(self, repo: TaskRepository) -> Any:
        from raztodo.application.use_cases.create_task import CreateTaskUseCase

        return CreateTaskUseCase(repo)

    def create_delete_task(self, repo: TaskRepository) -> Any:
        from raztodo.application.use_cases.delete_task import DeleteTaskUseCase

        return DeleteTaskUseCase(repo)

    def create_list_tasks(self, repo: TaskRepository) -> Any:
        from raztodo.application.queries.list_tasks import ListTasksUseCase

        return ListTasksUseCase(repo)

    def create_update_task(self, repo: TaskRepository) -> Any:
        from raztodo.application.use_cases.update_task import UpdateTaskUseCase

        return UpdateTaskUseCase(repo)

    def create_search_tasks(self, repo: TaskRepository) -> Any:
        from raztodo.application.queries.search_tasks import SearchTasksUseCase

        return SearchTasksUseCase(repo)

    def create_export_tasks(self, repo: TaskRepository) -> Any:
        from raztodo.application.queries.export_tasks import ExportTasksUseCase

        return ExportTasksUseCase(repo)

    def create_import_tasks(self, repo: TaskRepository) -> Any:
        from raztodo.application.use_cases.import_tasks import ImportTasksUseCase

        return ImportTasksUseCase(repo)

    def create_mark_done(self, repo: TaskRepository) -> Any:
        from raztodo.application.use_cases.mark_task_done import MarkDoneUseCase

        return MarkDoneUseCase(repo)

    def create_migrate(self, connection_factory: Callable[..., Any]) -> Any:
        from raztodo.application.use_cases.migrate_tasks import MigrateUseCase

        return MigrateUseCase(connection_factory)

    def create_clear_tasks(self, repo: TaskRepository) -> Any:
        from raztodo.application.use_cases.clear_tasks import ClearTasksUseCase

        return ClearTasksUseCase(repo)

    def create_explain_task(self, repo: TaskRepository) -> Any:
        from raztodo.application.queries.explain_task import ExplainTaskUseCase

        return ExplainTaskUseCase(repo)
