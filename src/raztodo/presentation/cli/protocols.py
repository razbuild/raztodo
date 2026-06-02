from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class Command(Protocol):
    def __call__(self, *args: Any, **kwds: Any) -> int: pass


class HandlerProtocol(Protocol):
    def get_command_calss(self, name: str) -> type: ...
    def get_usecase(self, name: str) -> Any: ...
