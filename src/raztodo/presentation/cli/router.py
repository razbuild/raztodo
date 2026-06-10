import importlib
from typing import Any, ClassVar

from raztodo.application.use_case_factory import DefaultUseCaseFactory, UseCaseFactory
from raztodo.presentation.cli.protocols import Command, HandlerProtocol


class TaskRouter(HandlerProtocol):
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

        module = importlib.import_module(f"raztodo.presentation.cli.commands.{module_name}")

        class_name = "".join(part.capitalize() for part in module_name.split("_"))
        candidates = [
            getattr(module, class_name, None),
            getattr(
                module,
                f"{class_name[:-3]}CMD" if class_name.endswith("Cmd") else f"{class_name}CMD",
                None,
            ),
        ]

        attr = next(
            (
                candidate
                for candidate in candidates
                if isinstance(candidate, type)
                and issubclass(candidate, Command)
                and candidate is not Command
            ),
            None,
        )

        if attr is None:
            attr = next(
                (
                    value
                    for value in vars(module).values()
                    if isinstance(value, type)
                    and issubclass(value, Command)
                    and value is not Command
                ),
                None,
            )

        if attr is None:
            raise ValueError(f"No command class found for command: {command_name}")

        cls: type[Command] = attr
        self._command_cache[command_name] = cls
        return cls

    def get_command_class(self, name: str) -> type[Command]:
        """Get command class for the given command name."""
        return self._get_command_class_lazy(name)

    def get_usecase(self, name: str) -> Any:
        """Get use case instance for the given command name."""

        # Only commands present in USECASE_MAP have a use case; others raise.

        uc_key = self.USECASE_MAP.get(name)
        if uc_key is None:
            raise ValueError(f"No usecase mapping for command: {name}")

        dispatch = {
            "create": lambda: self.use_case_factory.create_create_task(self.storage),
            "remove": lambda: self.use_case_factory.create_delete_task(self.storage),
            "list": lambda: self.use_case_factory.create_list_tasks(self.storage),
            "update": lambda: self.use_case_factory.create_update_task(self.storage),
            "search": lambda: self.use_case_factory.create_search_tasks(self.storage),
            "export": lambda: self.use_case_factory.create_export_tasks(self.storage),
            "import": lambda: self.use_case_factory.create_import_tasks(self.storage),
            "mark_done": lambda: self.use_case_factory.create_mark_done(self.storage),
            "migrate": lambda: self.use_case_factory.create_migrate(self.connection_factory),
            "clear": lambda: self.use_case_factory.create_clear_tasks(self.storage),
        }

        factory = dispatch.get(uc_key)
        if factory is None:
            raise ValueError(f"UseCase factory not found for key: {uc_key}")

        return factory()
