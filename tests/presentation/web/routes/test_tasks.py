from __future__ import annotations

from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

from raztodo.domain.exceptions import RazTodoException
from raztodo.domain.task_entity import TaskEntity
from raztodo.presentation.web.app import app


def make_task(
    id: int = 1,
    title: str = "Test task",
    description: str = "",
    done: bool = False,
    priority: str = "",
    due_date: str | None = None,
    tags: list[str] | None = None,
    project: str | None = None,
    created_at: str = "2026-01-01 00:00:00",
) -> TaskEntity:
    return TaskEntity(
        id=id,
        title=title,
        description=description,
        done=done,
        created_at=created_at,
        priority=priority,
        due_date=due_date,
        tags=tags or [],
        project=project,
    )


def mock_use_cases(
    list_tasks=None,
    create_task=None,
    update_task=None,
    delete_task=None,
    clear_tasks=None,
    mark_done=None,
    export_tasks=None,
    import_tasks=None,
):
    """Return a dict of mock use case instances."""
    list_uc = MagicMock()
    list_uc.execute.return_value = list_tasks or []
    create_uc = MagicMock()
    create_uc.execute.return_value = create_task or 1
    update_uc = MagicMock()
    update_uc.execute.return_value = True
    delete_uc = MagicMock()
    delete_uc.execute.return_value = True
    clear_uc = MagicMock()
    clear_uc.execute.return_value = clear_tasks or 0
    mark_uc = MagicMock()
    mark_uc.execute.return_value = True
    export_uc = MagicMock()
    export_uc.execute.return_value = True
    import_uc = MagicMock()
    import_uc.execute.return_value = import_tasks or {"inserted": 0, "updated": 0}
    return {
        "list": list_uc,
        "create": create_uc,
        "update": update_uc,
        "delete": delete_uc,
        "clear": clear_uc,
        "mark": mark_uc,
        "export": export_uc,
        "import": import_uc,
    }


@pytest.fixture
def client():
    """TestClient with all use cases mocked via dependency overrides."""
    from raztodo.presentation.web import dependencies as deps

    tasks = [make_task(1, "Buy milk"), make_task(2, "Write tests", done=True)]
    uc = mock_use_cases(list_tasks=tasks)

    app.dependency_overrides = {
        deps.get_list_uc: lambda: uc["list"],
        deps.get_create_uc: lambda: uc["create"],
        deps.get_update_uc: lambda: uc["update"],
        deps.get_delete_uc: lambda: uc["delete"],
        deps.get_clear_uc: lambda: uc["clear"],
        deps.get_mark_done_uc: lambda: uc["mark"],
        deps.get_export_uc: lambda: uc["export"],
        deps.get_import_uc: lambda: uc["import"],
    }
    yield TestClient(app), uc
    app.dependency_overrides = {}


# ---------------------------------------------------------------------------
# GET /api/tasks
# ---------------------------------------------------------------------------


class TestListTasks:
    def test_returns_task_list(self, client):
        c, _ = client
        res = c.get("/api/tasks")
        assert res.status_code == 200
        data = res.json()
        assert len(data) == 2
        assert data[0]["title"] == "Buy milk"
        assert data[1]["done"] is True

    def test_filters_by_q_param(self, client):
        c, uc = client
        uc["list"].execute.return_value = [
            make_task(1, "Buy milk"),
            make_task(2, "Write tests"),
        ]
        res = c.get("/api/tasks?q=milk")
        assert res.status_code == 200
        data = res.json()
        assert len(data) == 1
        assert data[0]["title"] == "Buy milk"

    def test_empty_list_returns_empty_array(self, client):
        c, uc = client
        uc["list"].execute.return_value = []
        res = c.get("/api/tasks")
        assert res.status_code == 200
        assert res.json() == []

    def test_domain_error_returns_400(self, client):
        c, uc = client
        uc["list"].execute.side_effect = RazTodoException("db error")
        res = c.get("/api/tasks")
        assert res.status_code == 400


# ---------------------------------------------------------------------------
# POST /api/tasks
# ---------------------------------------------------------------------------


class TestCreateTask:
    def test_creates_task_and_returns_201(self, client):
        c, uc = client
        new_task = make_task(3, "New task")
        uc["create"].execute.return_value = 3
        uc["list"].execute.return_value = [new_task]
        res = c.post("/api/tasks", json={"title": "New task"})
        assert res.status_code == 201
        assert res.json()["title"] == "New task"

    def test_passes_all_fields_to_use_case(self, client):
        c, uc = client
        uc["create"].execute.return_value = 5
        uc["list"].execute.return_value = [make_task(5, "Full task")]
        c.post(
            "/api/tasks",
            json={
                "title": "Full task",
                "description": "desc",
                "priority": "H",
                "due_date": "2025-12-31",
                "tags": ["work"],
                "project": "proj",
            },
        )
        uc["create"].execute.assert_called_once_with(
            title="Full task",
            description="desc",
            priority="H",
            due_date="2025-12-31",
            tags=["work"],
            project="proj",
        )

    def test_empty_title_returns_422(self, client):
        c, _ = client
        res = c.post("/api/tasks", json={"title": ""})
        assert res.status_code == 422

    def test_missing_title_returns_422(self, client):
        c, _ = client
        res = c.post("/api/tasks", json={})
        assert res.status_code == 422

    def test_invalid_priority_returns_422(self, client):
        c, _ = client
        res = c.post("/api/tasks", json={"title": "Task", "priority": "X"})
        assert res.status_code == 422

    def test_domain_error_returns_400(self, client):
        c, uc = client
        uc["create"].execute.side_effect = RazTodoException("duplicate title")
        res = c.post("/api/tasks", json={"title": "Dup"})
        assert res.status_code == 400


# ---------------------------------------------------------------------------
# PUT /api/tasks/{id}
# ---------------------------------------------------------------------------


class TestUpdateTask:
    def test_updates_task(self, client):
        c, uc = client
        updated = make_task(1, "Updated title")
        uc["list"].execute.return_value = [updated]
        res = c.put("/api/tasks/1", json={"title": "Updated title"})
        assert res.status_code == 200
        assert res.json()["title"] == "Updated title"

    def test_domain_error_returns_400(self, client):
        c, uc = client
        uc["update"].execute.side_effect = RazTodoException("not found")
        res = c.put("/api/tasks/99", json={"title": "X"})
        assert res.status_code == 400


# ---------------------------------------------------------------------------
# DELETE /api/tasks/{id}
# ---------------------------------------------------------------------------


class TestDeleteTask:
    def test_deletes_task_returns_204(self, client):
        c, _ = client
        res = c.delete("/api/tasks/1")
        assert res.status_code == 204

    def test_not_found_returns_404(self, client):
        c, uc = client
        uc["delete"].execute.side_effect = RazTodoException("No task found with id 99")
        res = c.delete("/api/tasks/99")
        assert res.status_code == 404


# ---------------------------------------------------------------------------
# POST /api/tasks/clear
# ---------------------------------------------------------------------------


class TestClearTasks:
    def test_clears_all_tasks(self, client):
        c, uc = client
        uc["clear"].execute.return_value = 5
        res = c.post("/api/tasks/clear")
        assert res.status_code == 200
        assert res.json()["deleted"] == 5

    def test_always_passes_confirmed_true(self, client):
        c, uc = client
        uc["clear"].execute.return_value = 0
        c.post("/api/tasks/clear")
        uc["clear"].execute.assert_called_once_with(confirmed=True)


# ---------------------------------------------------------------------------
# PATCH /api/tasks/{id}/done
# ---------------------------------------------------------------------------


class TestToggleDone:
    def test_toggles_pending_to_done(self, client):
        c, uc = client
        pending = make_task(1, "Buy milk", done=False)
        completed = make_task(1, "Buy milk", done=True)
        uc["list"].execute.side_effect = [[pending], [completed]]
        res = c.patch("/api/tasks/1/done")
        assert res.status_code == 200
        assert res.json()["done"] is True
        uc["mark"].execute.assert_called_once_with(1, done=True)

    def test_toggles_done_to_pending(self, client):
        c, uc = client
        completed = make_task(1, "Buy milk", done=True)
        pending = make_task(1, "Buy milk", done=False)
        uc["list"].execute.side_effect = [[completed], [pending]]
        res = c.patch("/api/tasks/1/done")
        assert res.status_code == 200
        uc["mark"].execute.assert_called_once_with(1, done=False)

    def test_not_found_returns_404(self, client):
        c, uc = client
        uc["list"].execute.return_value = []
        res = c.patch("/api/tasks/99/done")
        assert res.status_code == 404


# ---------------------------------------------------------------------------
# GET /api/tasks/export
# ---------------------------------------------------------------------------


class TestExportTasks:
    def test_export_returns_json_file(self, client, tmp_path):
        c, uc = client
        export_file = tmp_path / "tasks.json"
        export_file.write_text('[{"id": 1, "title": "Buy milk"}]')

        def fake_export(path: str) -> bool:
            import shutil

            shutil.copy(str(export_file), path)
            return True

        uc["export"].execute.side_effect = fake_export
        res = c.get("/api/tasks/export")
        assert res.status_code == 200
        assert "application/json" in res.headers["content-type"]

    def test_domain_error_returns_400(self, client):
        c, uc = client
        uc["export"].execute.side_effect = RazTodoException("export failed")
        res = c.get("/api/tasks/export")
        assert res.status_code == 400


# ---------------------------------------------------------------------------
# POST /api/tasks/import
# ---------------------------------------------------------------------------


class TestImportTasks:
    def test_imports_tasks(self, client):
        c, uc = client
        uc["import"].execute.return_value = {"inserted": 2, "updated": 1}
        payload = [{"title": "Task A"}, {"title": "Task B"}]
        res = c.post("/api/tasks/import", json=payload)
        assert res.status_code == 200
        assert res.json() == {"inserted": 2, "updated": 1}

    def test_invalid_json_returns_422(self, client):
        c, _ = client
        res = c.post(
            "/api/tasks/import",
            content=b"not-json",
            headers={"Content-Type": "application/json"},
        )
        assert res.status_code == 422

    def test_domain_error_returns_400(self, client):
        c, uc = client
        uc["import"].execute.side_effect = RazTodoException("bad file")
        res = c.post("/api/tasks/import", json=[{"title": "X"}])
        assert res.status_code == 400
