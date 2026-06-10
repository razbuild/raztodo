from raztodo.presentation.cli.router import TaskRouter


class TestTaskRouter:
    def test_resolves_all_command_classes(self):
        router = TaskRouter(storage=None, connection_factory=lambda: None)

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
        ]:
            command_class = router.get_command_class(command_name)
            assert isinstance(command_class, type)
