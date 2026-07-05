from __future__ import annotations

from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

from raztodo.domain.exceptions import RazTodoException
from raztodo.presentation.web.app import app


@pytest.fixture
def client():
    """TestClient with the explain use case mocked via dependency overrides."""
    from raztodo.presentation.web import dependencies as deps

    uc = MagicMock()
    app.dependency_overrides = {deps.get_explain_uc: lambda: uc}
    yield TestClient(app), uc
    app.dependency_overrides = {}


class TestExplainTask:
    @staticmethod
    def _sse_events(response_text: str) -> list[str]:
        return [event for event in response_text.strip().split("\n\n") if event]

    @pytest.mark.parametrize("mode", ["short", "deep", "plan"])
    def test_stream_tokens_for_valid_modes(self, client, mode):
        c, uc = client
        uc.stream.return_value = [f"token-{mode}-1", f"token-{mode}-2"]

        response = c.get(f"/api/tasks/1/explain?mode={mode}")

        assert response.status_code == 200
        assert response.headers["content-type"].startswith("text/event-stream")
        assert self._sse_events(response.text) == [
            f"data: token-{mode}-1",
            f"data: token-{mode}-2",
            "data: [DONE]",
        ]
        uc.stream.assert_called_once_with(1, mode=mode)

    def test_default_mode_is_short(self, client):
        c, uc = client
        uc.stream.return_value = ["hello"]

        response = c.get("/api/tasks/1/explain")

        assert response.status_code == 200
        assert self._sse_events(response.text) == [
            "data: hello",
            "data: [DONE]",
        ]
        uc.stream.assert_called_once_with(1, mode="short")

    def test_invalid_mode_returns_422(self, client):
        c, _ = client

        response = c.get("/api/tasks/1/explain?mode=invalid")

        assert response.status_code == 422
        assert response.json()["detail"] == "mode must be: short, deep, or plan"

    def test_raztodo_exception_yields_error_event(self, client):
        c, uc = client
        uc.stream.side_effect = RazTodoException("boom")

        response = c.get("/api/tasks/1/explain")

        assert response.status_code == 200
        assert self._sse_events(response.text) == [
            "event: error\ndata: An internal error occurred.",
            "data: [DONE]",
        ]

    def test_newline_in_token_is_escaped(self, client):
        c, uc = client
        uc.stream.return_value = ["line1\nline2"]

        response = c.get("/api/tasks/1/explain")

        assert response.status_code == 200
        assert self._sse_events(response.text) == [
            "data: line1\\nline2",
            "data: [DONE]",
        ]
