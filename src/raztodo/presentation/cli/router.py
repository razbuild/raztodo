from collections.abc import Callable
from typing import Any, ClassVar

from raztodo.application.use_cases.create_task import CreateTaskUseCase
from raztodo.application.use_cases.delete_task import DeleteTaskUseCase
from raztodo.application.use_cases.export_task import ExportTasksUseCase
from raztodo.application.use_cases.import_task import ImportTasksUseCase
from raztodo.application.use_cases.list_tasks import ListTasksUseCase
from raztodo.application.use_cases.mark_task_done import MarkDoneUseCase
from raztodo.application.use_cases.migrate_tasks import MigrateUseCase
from raztodo.application.use_cases.search_tasks import SearchTasksUseCase
from raztodo.application.use_cases.update_task import UpdateTaskUseCase
from raztodo.presentation.cli.commands.create_task_cmd import CreateTaskCMD
from raztodo.presentation.cli.commands.delete_task_cmd import DeleteTaskCMD
from raztodo.presentation.cli.commands.export_task_cmd import ExportTasksCMD
from raztodo.presentation.cli.commands.import_task_cmd import ImportTasksCMD
from raztodo.presentation.cli.commands.list_tasks_cmd import ListTasksCMD
from raztodo.presentation.cli.commands.mark_task_done_cmd import DoneTaskCMD
from raztodo.presentation.cli.commands.migrate_tasks_cmd import MigrateCMD
from raztodo.presentation.cli.commands.search_tasks_cmd import SearchTasksCMD
from raztodo.presentation.cli.commands.update_task_cmd import UpdateTaskCMD


class TaskRouter:

    COMMANDS: ClassVar[dict[str, type[Callable[..., int]]]] = {
        "add": CreateTaskCMD,
        "remove": DeleteTaskCMD,
        "list": ListTasksCMD,
        "update": UpdateTaskCMD,
        "search": SearchTasksCMD,
        "export": ExportTasksCMD,
        "import": ImportTasksCMD,
        "done": DoneTaskCMD,
        "migrate": MigrateCMD,
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
    }

    def __init__(self, storage: Any, connection_factory: Any) -> None:
        self.storage = storage
        self.connection_factory = connection_factory

        self.use_cases: dict[str, Callable[[], Any]] = {
            "create": lambda: CreateTaskUseCase(storage),
            "remove": lambda: DeleteTaskUseCase(storage),
            "list": lambda: ListTasksUseCase(storage),
            "update": lambda: UpdateTaskUseCase(storage),
            "search": lambda: SearchTasksUseCase(storage),
            "export": lambda: ExportTasksUseCase(storage),
            "import": lambda: ImportTasksUseCase(storage),
            "mark_done": lambda: MarkDoneUseCase(storage),
            "migrate": lambda: MigrateUseCase(connection_factory),
        }

    def get_command_class(self, command_name: str) -> type[Callable[..., int]]:
        cls = self.COMMANDS.get(command_name)
        if not cls:
            raise ValueError(f"Unknown command: {command_name}")
        return cls

    def get_usecase(self, command_name: str) -> Any:
        uc_key = self.USECASE_MAP.get(command_name)
        if not uc_key:
            raise ValueError(f"No usecase mapping for command: {command_name}")

        factory = self.use_cases.get(uc_key)
        if not factory:
            raise ValueError(f"UseCase factory not found for key: {uc_key}")

        return factory()
