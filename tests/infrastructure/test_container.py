from raztodo.infrastructure.container import AppContainer
from raztodo.presentation.cli.entrypoint import create_router


class TestAppContainer:
    """Test cases for AppContainer."""

    def test_container_initialization(self):
        """Test container initialization."""
        container = AppContainer()

        assert container.config is not None
        assert container.logger is not None
        assert container.repo_singleton() is not None
        assert container.connection_factory() is not None

        # Clean up
        container.close_singleton()

    def test_container_uses_config_db_name(self, monkeypatch):
        monkeypatch.setenv("RAZTODO_DB", "test_container.db")

        container = AppContainer()

        assert container.config.resolve_db_path().name == "test_container.db"

        container.close_singleton()

    def test_container_custom_db_name(self):
        container = AppContainer(db_name="tasks.db")

        assert container.config.resolve_db_path().name == "tasks.db"

        container.close_singleton()

    def test_container_can_create_router(self):
        container = AppContainer()

        repo = container.repo_singleton()
        connection_factory = container.connection_factory()
        router = create_router(repo, connection_factory)

        assert router is not None
        assert hasattr(router, "storage")
        assert router.storage is repo

        container.close_singleton()

    def test_container_repo_singleton(self):
        """Test that repo_singleton returns same instance."""
        container = AppContainer()
        repo1 = container.repo_singleton()
        repo2 = container.repo_singleton()

        assert repo1 is repo2

        # Clean up
        container.close_singleton()

    def test_container_close_singleton(self):
        container = AppContainer()

        repo = container.repo_singleton()
        assert repo is not None

        container.close_singleton()

        new_repo = container.repo_singleton()
        assert new_repo is not repo

        container.close_singleton()
