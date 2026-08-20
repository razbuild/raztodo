import sys
from unittest.mock import MagicMock

import pytest

import raztodo.presentation.web.__main__ as web_main


@pytest.fixture
def uvicorn_mock(monkeypatch):
    mock = MagicMock()
    mock.__spec__ = MagicMock()
    monkeypatch.setitem(sys.modules, "uvicorn", mock)
    return mock


def test_main_uses_default_host_and_port(monkeypatch, uvicorn_mock):
    monkeypatch.delenv("RAZTODO_WEB_HOST", raising=False)
    monkeypatch.delenv("RAZTODO_WEB_PORT", raising=False)

    web_main.main()

    uvicorn_mock.run.assert_called_once()
    _, kwargs = uvicorn_mock.run.call_args
    assert kwargs["host"] == "127.0.0.1"
    assert kwargs["port"] == 8000


def test_main_reads_host_and_port_from_env(monkeypatch, uvicorn_mock):
    monkeypatch.setenv("RAZTODO_WEB_HOST", "0.0.0.0")
    monkeypatch.setenv("RAZTODO_WEB_PORT", "9000")

    web_main.main()

    _, kwargs = uvicorn_mock.run.call_args
    assert kwargs["host"] == "0.0.0.0"
    assert kwargs["port"] == 9000
