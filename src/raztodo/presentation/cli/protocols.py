from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class Command(Protocol):
    def __init__(self, *args: Any, **kwds: Any) -> None:
        pass

    def __call__(self, *args: Any, **kwds: Any) -> int:
        pass


class HandlerProtocol(Protocol):
    def get_command_class(self, name: str) -> type[Command]:
        pass

    def get_usecase(self, name: str) -> Any:
        pass
