from unittest.mock import Mock

import pytest

from raztodo.presentation.cli.router import TaskRouter


class TestTaskRouter:
    @pytest.fixture
    def router(self):
        return TaskRouter(
            storage=Mock(),
            connection_factory=Mock(),
        )

    def test_resolves_all_command_classes(self, router):
        for command_name in [
            "add",
            "remove",
            "list",
            "update",
            "search",
            "export",
            "import",
            "done",
            "migrate",
            "clear",
            "explain",
        ]:
            command_class = router.get_command_class(command_name)
            assert isinstance(command_class, type)

    def test_command_class_is_cached(self, router):
        first = router.get_command_class("add")
        second = router.get_command_class("add")

        assert first is second
        assert "add" in router._command_cache

    def test_unknown_command_raises(self, router):
        with pytest.raises(ValueError, match="Unknown command"):
            router.get_command_class("unknown")

    @pytest.mark.parametrize(
        "command,factory_method",
        [
            ("add", "create_create_task"),
            ("remove", "create_delete_task"),
            ("list", "create_list_tasks"),
            ("update", "create_update_task"),
            ("search", "create_search_tasks"),
            ("export", "create_export_tasks"),
            ("import", "create_import_tasks"),
            ("done", "create_mark_done"),
            ("migrate", "create_migrate"),
            ("clear", "create_clear_tasks"),
            ("explain", "create_explain_task"),
        ],
    )
    def test_get_usecase_dispatch(self, command, factory_method):
        factory = Mock()
        expected = object()

        getattr(factory, factory_method).return_value = expected

        router = TaskRouter(
            storage=Mock(),
            connection_factory=Mock(),
            use_case_factory=factory,
        )

        result = router.get_usecase(command)

        method = getattr(factory, factory_method)

        if command == "migrate":
            method.assert_called_once_with(router.connection_factory)
        else:
            method.assert_called_once_with(router.storage)

        assert result is expected

    def test_unknown_usecase_mapping_raises(self, router):
        with pytest.raises(ValueError, match="No usecase mapping"):
            router.get_usecase("unknown")

    def test_missing_factory_raises(self):
        factory = Mock()

        router = TaskRouter(
            storage=Mock(),
            connection_factory=Mock(),
            use_case_factory=factory,
        )

        router.USECASE_MAP["broken"] = "missing"

        try:
            with pytest.raises(ValueError, match="UseCase factory not found"):
                router.get_usecase("broken")
        finally:
            del router.USECASE_MAP["broken"]
