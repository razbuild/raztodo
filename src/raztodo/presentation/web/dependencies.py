from __future__ import annotations

from typing import Annotated, Any

from fastapi import Depends

from raztodo.application.use_case_factory import DefaultUseCaseFactory
from raztodo.infrastructure.container import build_container
from raztodo.infrastructure.sqlite.task_repository import SQLiteTaskRepository

_container = build_container()


def get_storage() -> SQLiteTaskRepository:
    return _container.repo_singleton()


def get_factory() -> DefaultUseCaseFactory:
    return DefaultUseCaseFactory()


StorageDep = Annotated[SQLiteTaskRepository, Depends(get_storage)]
FactoryDep = Annotated[DefaultUseCaseFactory, Depends(get_factory)]


def get_use_case(factory_method: str):
    def _dependency(storage: StorageDep, factory: FactoryDep) -> Any:
        return getattr(factory, factory_method)(storage)

    return _dependency


get_list_uc = get_use_case("create_list_tasks")
get_create_uc = get_use_case("create_create_task")
get_update_uc = get_use_case("create_update_task")
get_delete_uc = get_use_case("create_delete_task")
get_clear_uc = get_use_case("create_clear_tasks")
get_mark_done_uc = get_use_case("create_mark_done")
get_export_uc = get_use_case("create_export_tasks")
get_import_uc = get_use_case("create_import_tasks")
