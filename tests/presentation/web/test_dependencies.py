from unittest.mock import MagicMock, Mock

import pytest

import raztodo.presentation.web.dependencies as deps
from raztodo.application.factory import DefaultUseCaseFactory
from raztodo.infrastructure.sqlite.task_repository import SQLiteTaskRepository


def test_get_factory_returns_new_instances():
    f1 = deps.get_factory()
    f2 = deps.get_factory()

    assert isinstance(f1, DefaultUseCaseFactory)
    assert isinstance(f2, DefaultUseCaseFactory)
    assert f1 is not f2


def test_get_storage_uses_container_singleton(monkeypatch):
    fake_repo = object()

    fake_container = Mock()
    fake_container.repo_singleton.return_value = fake_repo

    monkeypatch.setattr(deps, "_container", fake_container)

    result = deps.get_storage()

    fake_container.repo_singleton.assert_called_once()
    assert result is fake_repo


@pytest.fixture
def storage():
    return object()


@pytest.fixture
def factory():
    factory = MagicMock()

    factory.create_list_tasks.return_value = "list_uc"
    factory.create_create_task.return_value = "create_uc"
    factory.create_update_task.return_value = "update_uc"
    factory.create_delete_task.return_value = "delete_uc"
    factory.create_clear_tasks.return_value = "clear_uc"
    factory.create_mark_done.return_value = "mark_done_uc"
    factory.create_export_tasks.return_value = "export_uc"
    factory.create_import_tasks.return_value = "import_uc"

    return factory


@pytest.mark.parametrize(
    "dep, method_name, expected",
    [
        (deps.get_list_uc, "create_list_tasks", "list_uc"),
        (deps.get_create_uc, "create_create_task", "create_uc"),
        (deps.get_update_uc, "create_update_task", "update_uc"),
        (deps.get_delete_uc, "create_delete_task", "delete_uc"),
        (deps.get_clear_uc, "create_clear_tasks", "clear_uc"),
        (deps.get_mark_done_uc, "create_mark_done", "mark_done_uc"),
        (deps.get_export_uc, "create_export_tasks", "export_uc"),
        (deps.get_import_uc, "create_import_tasks", "import_uc"),
    ],
)
def test_use_case_dispatch(dep, method_name, expected, storage, factory):
    result = dep(storage, factory)

    getattr(factory, method_name).assert_called_once_with(storage)
    assert result == expected


def test_invalid_factory_method_raises():
    storage = Mock(spec=SQLiteTaskRepository)

    factory = Mock(spec=[])

    dep = deps.get_use_case("non_existent_method")

    with pytest.raises(AttributeError):
        dep(storage, factory)
