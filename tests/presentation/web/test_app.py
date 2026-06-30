from __future__ import annotations

import importlib
from pathlib import Path
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient
from starlette.routing import BaseRoute, Mount, Route


def _route_path(route: BaseRoute) -> str | None:
    if isinstance(route, (Route, Mount)):
        return route.path
    return None


@pytest.fixture
def client():
    with patch(
        "raztodo.infrastructure.version.get_version",
        return_value="0.0.0-test",
    ):
        import raztodo.presentation.web.app as app_module

        importlib.reload(app_module)

        with TestClient(app_module.app) as c:
            yield c


class TestAppMetadata:
    def test_app_title(self, client):
        from raztodo.presentation.web.app import app

        assert app.title == "RazTodo"

    def test_app_description(self, client):
        from raztodo.presentation.web.app import app

        assert app.description == "Local web interface for RazTodo"

    def test_app_version(self):
        with patch(
            "raztodo.infrastructure.version.get_version",
            return_value="1.2.3",
        ):
            import raztodo.presentation.web.app as app_module

            importlib.reload(app_module)

            assert app_module.app.version == "1.2.3"


class TestIndexRoute:
    def test_index_returns_200(self, client):
        response = client.get("/")
        assert response.status_code == 200

    def test_index_returns_html_content_type(self, client):
        response = client.get("/")
        assert "text/html" in response.headers["content-type"]

    def test_index_serves_index_html_file(self):
        from raztodo.presentation.web.app import _INDEX_FILE

        assert _INDEX_FILE.name == "index.html"

    def test_index_not_in_openapi_schema(self, client):
        schema = client.get("/openapi.json").json()
        assert "/" not in schema["paths"]

    def test_index_missing_file_returns_error(self, client):
        with patch(
            "raztodo.presentation.web.app._INDEX_FILE",
            Path("/nonexistent/index.html"),
        ):
            response = client.get("/")

        assert response.status_code == 500


class TestStaticMount:
    def test_static_mount_path_exists_in_routes(self):
        from raztodo.presentation.web.app import app

        mounts = [_route_path(r) for r in app.routes if _route_path(r) == "/static"]

        assert mounts == ["/static"]

    def test_static_file_not_found_returns_404(self, client):
        response = client.get("/static/does-not-exist.js")
        assert response.status_code == 404


class TestRoutersIncluded:
    def test_tasks_router_included(self, client):
        schema = client.get("/openapi.json").json()
        paths = schema["paths"]

        assert "/api/tasks" in paths
        assert "/api/tasks/{task_id}" in paths
        assert "/api/tasks/{task_id}/done" in paths
        assert "/api/tasks/export" in paths
        assert "/api/tasks/import" in paths
        assert "/api/tasks/clear" in paths

    def test_explain_router_included(self, client):
        schema = client.get("/openapi.json").json()

        assert "/api/tasks/{task_id}/explain" in schema["paths"]

    def test_openapi_schema_generation_succeeds(self, client):
        response = client.get("/openapi.json")

        assert response.status_code == 200
        assert "paths" in response.json()
