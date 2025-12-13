from typing import Any, ClassVar, Protocol, runtime_checkable

from raztodo.application.use_case_factory import DefaultUseCaseFactory, UseCaseFactory


@runtime_checkable
class Command(Protocol):
    def __call__(self, *args: Any, **kwargs: Any) -> int: ...


class TaskRouter:
    COMMAND_MAP: ClassVar[dict[str, str]] = {
        "add": "create_task_cmd",
        "remove": "delete_task_cmd",
        "list": "list_tasks_cmd",
        "update": "update_task_cmd",
        "search": "search_tasks_cmd",
        "export": "export_task_cmd",
        "import": "import_task_cmd",
        "done": "mark_task_done_cmd",
        "migrate": "migrate_tasks_cmd",
        "clear": "clear_tasks_cmd",
    }

    USECASE_MAP: ClassVar[dict[str, str]] = {
        "add": "create",
        "remove": "remove",
        "list": "list",
        "update": "update",
        "search": "search",
        "export": "export",
        "import": "import",
        "done": "mark_done",
        "migrate": "migrate",
        "clear": "clear",
    }

    def __init__(
        self,
        storage: Any,
        connection_factory: Any,
        use_case_factory: UseCaseFactory | None = None,
    ) -> None:
        self.storage = storage
        self.connection_factory = connection_factory
        self.use_case_factory = use_case_factory or DefaultUseCaseFactory()
        self._command_cache: dict[str, type[Command]] = {}

    def _get_command_class_lazy(self, command_name: str) -> type[Command]:
        if command_name in self._command_cache:
            return self._command_cache[command_name]

        module_name = self.COMMAND_MAP.get(command_name)
        if not module_name:
            raise ValueError(f"Unknown command: {command_name}")

        cls: type[Command]

        if command_name == "add":
            from raztodo.presentation.cli.commands.create_task_cmd import CreateTaskCMD

            cls = CreateTaskCMD
        elif command_name == "remove":
            from raztodo.presentation.cli.commands.delete_task_cmd import DeleteTaskCMD

            cls = DeleteTaskCMD
        elif command_name == "list":
            from raztodo.presentation.cli.commands.list_tasks_cmd import ListTasksCMD

            cls = ListTasksCMD
        elif command_name == "update":
            from raztodo.presentation.cli.commands.update_task_cmd import UpdateTaskCMD

            cls = UpdateTaskCMD
        elif command_name == "search":
            from raztodo.presentation.cli.commands.search_tasks_cmd import (
                SearchTasksCMD,
            )

            cls = SearchTasksCMD
        elif command_name == "export":
            from raztodo.presentation.cli.commands.export_task_cmd import ExportTasksCMD

            cls = ExportTasksCMD
        elif command_name == "import":
            from raztodo.presentation.cli.commands.import_task_cmd import ImportTasksCMD

            cls = ImportTasksCMD
        elif command_name == "done":
            from raztodo.presentation.cli.commands.mark_task_done_cmd import DoneTaskCMD

            cls = DoneTaskCMD
        elif command_name == "migrate":
            from raztodo.presentation.cli.commands.migrate_tasks_cmd import MigrateCMD

            cls = MigrateCMD
        elif command_name == "clear":
            from raztodo.presentation.cli.commands.clear_tasks_cmd import ClearTasksCMD

            cls = ClearTasksCMD
        else:
            raise ValueError(f"Unknown command: {command_name}")

        self._command_cache[command_name] = cls
        return cls

    def get_command_class(self, command_name: str) -> type[Command]:
        """Get command class for the given command name."""
        return self._get_command_class_lazy(command_name)

    def get_usecase(self, command_name: str) -> Any:
        """Get use case instance for the given command name."""
        uc_key = self.USECASE_MAP.get(command_name)
        if not uc_key:
            raise ValueError(f"No usecase mapping for command: {command_name}")

        if uc_key == "create":
            return self.use_case_factory.create_create_task(self.storage)
        elif uc_key == "remove":
            return self.use_case_factory.create_delete_task(self.storage)
        elif uc_key == "list":
            return self.use_case_factory.create_list_tasks(self.storage)
        elif uc_key == "update":
            return self.use_case_factory.create_update_task(self.storage)
        elif uc_key == "search":
            return self.use_case_factory.create_search_tasks(self.storage)
        elif uc_key == "export":
            return self.use_case_factory.create_export_tasks(self.storage)
        elif uc_key == "import":
            return self.use_case_factory.create_import_tasks(self.storage)
        elif uc_key == "mark_done":
            return self.use_case_factory.create_mark_done(self.storage)
        elif uc_key == "migrate":
            return self.use_case_factory.create_migrate(self.connection_factory)
        elif uc_key == "clear":
            return self.use_case_factory.create_clear_tasks(self.storage)
        else:
            raise ValueError(f"UseCase factory not found for key: {uc_key}")
