import os

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

    def test_container_uses_config_db_name(self):
        """Test that container uses config db_name."""
        os.environ["RAZTODO_DB"] = "test_container.db"
        try:
            container = AppContainer()
            assert container.config.db_name == "test_container.db"
            # Clean up
            container.close_singleton()
        finally:
            os.environ.pop("RAZTODO_DB", None)

    def test_container_custom_db_name(self):
        """Test container with custom db_name."""
        container = AppContainer(db_name="custom.db")
        # Container should use provided db_name, not config
        assert container.config.db_name == "tasks.db"  # Config default
        # Clean up
        container.close_singleton()

    def test_container_can_create_router(self):
        """Test that container can provide components to create router."""
        container = AppContainer()

        repo = container.repo_singleton()
        connection_factory = container.connection_factory()
        router = create_router(repo, connection_factory)

        assert router is not None
        assert hasattr(router, "storage")
        assert router.storage is repo

        # Clean up
        container.close_singleton()

    def test_container_repo_singleton(self):
        """Test that repo_singleton returns same instance."""
        container = AppContainer()
        repo1 = container.repo_singleton()
        repo2 = container.repo_singleton()

        assert repo1 is repo2

        # Clean up
        container.close_singleton()

    def test_container_repo_singleton_returns_same(self):
        """Test that repo_singleton returns same instance on multiple calls."""
        container = AppContainer()
        repo1 = container.repo_singleton()
        repo2 = container.repo_singleton()

        assert repo1 is repo2

        # Clean up
        container.close_singleton()

    def test_container_close_singleton(self):
        """Test closing singleton repository."""
        container = AppContainer()
        repo = container.repo_singleton()
        assert repo is not None

        container.close_singleton()

        # After close, should get new instance
        new_repo = container.repo_singleton()
        assert new_repo is not repo

        # Clean up the newly created singleton repository
        container.close_singleton()
