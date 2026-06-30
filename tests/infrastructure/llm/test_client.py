import contextlib
import json
from unittest.mock import MagicMock, patch

import pytest

from raztodo.infrastructure.llm.client import (
    OllamaClientError,
    _build_messages,
    _get_connection,
    chat,
    stream_chat,
)


class TestGetConnection:
    def test_http_host_returns_http_connection(self):
        conn, prefix = _get_connection("http://localhost:11434")
        from http.client import HTTPConnection

        assert isinstance(conn, HTTPConnection)
        assert prefix == ""

    def test_https_host_returns_https_connection(self):
        from http.client import HTTPSConnection

        conn, _ = _get_connection("https://localhost:11434")
        assert isinstance(conn, HTTPSConnection)

    def test_path_prefix_is_extracted(self):
        _, prefix = _get_connection("http://localhost:11434/ollama")
        assert prefix == "/ollama"

    def test_bare_host_without_scheme(self):
        from http.client import HTTPConnection

        prefix, _ = _get_connection("localhost:11434")
        assert isinstance(prefix, HTTPConnection)


class TestBuildMessages:
    def test_user_only_when_no_system(self):
        msgs = _build_messages("hello", "")
        assert msgs == [{"role": "user", "content": "hello"}]

    def test_system_prepended_when_provided(self):
        msgs = _build_messages("hello", "You are helpful.")
        assert msgs == [
            {"role": "system", "content": "You are helpful."},
            {"role": "user", "content": "hello"},
        ]

    def test_prompt_preserved_exactly(self):
        prompt = "  leading spaces and\nnewline  "
        msgs = _build_messages(prompt, "")
        assert msgs[-1]["content"] == prompt


def _make_response(status: int, body: bytes) -> MagicMock:
    """Create a mock HTTPResponse with the given status and body."""
    resp = MagicMock()
    resp.status = status
    resp.read.return_value = body
    lines = body.splitlines(keepends=True)
    resp.readline.side_effect = [*lines, b""]
    return resp


def _make_cfg(
    host="http://localhost:11434",
    model="llama3",
    system_prompt="",
    timeout=30,
) -> MagicMock:
    cfg = MagicMock()
    cfg.host = host
    cfg.model = model
    cfg.system_prompt = system_prompt
    cfg.timeout = timeout
    return cfg


class TestChat:
    def _patch_open_response(self, response_body: dict):
        """Patch _open_response to return (mock_conn, mock_response)."""
        body = json.dumps(response_body).encode()
        mock_conn = MagicMock()
        mock_resp = _make_response(200, body)
        return patch(
            "raztodo.infrastructure.llm.client._open_response",
            return_value=(mock_conn, mock_resp),
        )

    def test_returns_message_content(self):
        cfg = _make_cfg()
        expected = "Here is your answer."
        payload = {"message": {"content": expected}}
        with self._patch_open_response(payload):
            result = chat("What is 2+2?", cfg=cfg)
        assert result == expected

    def test_uses_explicit_system_over_cfg(self):
        cfg = _make_cfg(system_prompt="default system")
        captured = {}

        def fake_open_response(c, payload_bytes):
            captured["payload"] = json.loads(payload_bytes.decode())
            mock_conn = MagicMock()
            mock_resp = _make_response(200, json.dumps({"message": {"content": "ok"}}).encode())
            return mock_conn, mock_resp

        with patch(
            "raztodo.infrastructure.llm.client._open_response",
            side_effect=fake_open_response,
        ):
            chat("hi", system="override system", cfg=cfg)

        msgs = captured["payload"]["messages"]
        assert msgs[0] == {"role": "system", "content": "override system"}

    def test_falls_back_to_cfg_system_prompt(self):
        cfg = _make_cfg(system_prompt="cfg system")
        captured = {}

        def fake_open_response(c, payload_bytes):
            captured["payload"] = json.loads(payload_bytes.decode())
            mock_conn = MagicMock()
            mock_resp = _make_response(200, json.dumps({"message": {"content": "ok"}}).encode())
            return mock_conn, mock_resp

        with patch(
            "raztodo.infrastructure.llm.client._open_response",
            side_effect=fake_open_response,
        ):
            chat("hi", system="", cfg=cfg)

        msgs = captured["payload"]["messages"]
        assert msgs[0]["content"] == "cfg system"

    def test_stream_is_false_in_payload(self):
        cfg = _make_cfg()
        captured = {}

        def fake_open_response(c, payload_bytes):
            captured["payload"] = json.loads(payload_bytes.decode())
            mock_conn = MagicMock()
            mock_resp = _make_response(200, json.dumps({"message": {"content": "ok"}}).encode())
            return mock_conn, mock_resp

        with patch(
            "raztodo.infrastructure.llm.client._open_response",
            side_effect=fake_open_response,
        ):
            chat("hi", cfg=cfg)

        assert captured["payload"]["stream"] is False

    def test_closes_connection_on_success(self):
        cfg = _make_cfg()
        mock_conn = MagicMock()
        mock_resp = _make_response(200, json.dumps({"message": {"content": "ok"}}).encode())
        with patch(
            "raztodo.infrastructure.llm.client._open_response",
            return_value=(mock_conn, mock_resp),
        ):
            chat("hi", cfg=cfg)
        mock_conn.close.assert_called_once()

    def test_raises_on_invalid_json_response(self):
        cfg = _make_cfg()
        mock_conn = MagicMock()
        mock_resp = MagicMock()
        mock_resp.status = 200
        mock_resp.read.return_value = b"not json"
        with (
            patch(
                "raztodo.infrastructure.llm.client._open_response",
                return_value=(mock_conn, mock_resp),
            ),
            pytest.raises(OllamaClientError, match="Unexpected Ollama response"),
        ):
            chat("hi", cfg=cfg)

    def test_raises_on_missing_message_key(self):
        cfg = _make_cfg()
        mock_conn = MagicMock()
        mock_resp = _make_response(200, json.dumps({"result": "nope"}).encode())
        with (
            patch(
                "raztodo.infrastructure.llm.client._open_response",
                return_value=(mock_conn, mock_resp),
            ),
            pytest.raises(OllamaClientError, match="Unexpected Ollama response"),
        ):
            chat("hi", cfg=cfg)

    def test_loads_default_config_when_cfg_none(self):
        mock_cfg = _make_cfg()
        mock_conn = MagicMock()
        mock_resp = _make_response(200, json.dumps({"message": {"content": "ok"}}).encode())
        with (
            patch(
                "raztodo.infrastructure.llm.client.load_config",
                return_value=mock_cfg,
            ) as mock_load,
            patch(
                "raztodo.infrastructure.llm.client._open_response",
                return_value=(mock_conn, mock_resp),
            ),
        ):
            chat("hi")
        mock_load.assert_called_once()


class TestOpenResponse:
    """Test the HTTP layer directly."""

    def _make_conn_mock(self, status: int, body: bytes) -> MagicMock:
        conn = MagicMock()
        conn.sock = MagicMock()
        mock_resp = _make_response(status, body)
        conn.getresponse.return_value = mock_resp
        return conn

    @patch("raztodo.infrastructure.llm.client.HTTPConnection")
    def test_successful_200_returns_conn_and_response(self, mockhttpconn):
        cfg = _make_cfg()
        body = json.dumps({"message": {"content": "hi"}}).encode()
        mock_conn = self._make_conn_mock(200, body)
        mockhttpconn.return_value = mock_conn

        from raztodo.infrastructure.llm.client import _open_response

        _, resp = _open_response(cfg, b"{}")
        assert resp.status == 200

    @patch("raztodo.infrastructure.llm.client.HTTPConnection")
    def test_404_raises_model_not_found_error(self, mockhttpconn):
        cfg = _make_cfg(model="no-such-model")
        mock_conn = self._make_conn_mock(404, b"not found")
        mockhttpconn.return_value = mock_conn

        from raztodo.infrastructure.llm.client import _open_response

        with pytest.raises(OllamaClientError, match="not found on Ollama"):
            _open_response(cfg, b"{}")
        mock_conn.close.assert_called_once()

    @patch("raztodo.infrastructure.llm.client.HTTPConnection")
    def test_non_200_non_404_raises_generic_error(self, mockhttpconn):
        cfg = _make_cfg()
        mock_conn = self._make_conn_mock(500, b"internal server error")
        mockhttpconn.return_value = mock_conn

        from raztodo.infrastructure.llm.client import _open_response

        with pytest.raises(OllamaClientError, match="HTTP 500"):
            _open_response(cfg, b"{}")

    @patch("raztodo.infrastructure.llm.client.HTTPConnection")
    def test_os_error_raises_connection_error(self, mockhttpconn):
        cfg = _make_cfg()
        mock_conn = MagicMock()
        mock_conn.connect.side_effect = OSError("refused")
        mockhttpconn.return_value = mock_conn

        from raztodo.infrastructure.llm.client import _open_response

        with pytest.raises(OllamaClientError, match="Cannot connect to Ollama"):
            _open_response(cfg, b"{}")
        mock_conn.close.assert_called_once()

    @patch("raztodo.infrastructure.llm.client.HTTPConnection")
    def test_uses_correct_endpoint_with_path_prefix(self, mockhttpconn):
        cfg = _make_cfg(host="http://proxy.internal/ollama")
        mock_conn = self._make_conn_mock(200, b"{}")
        mockhttpconn.return_value = mock_conn

        from raztodo.infrastructure.llm.client import _open_response

        with contextlib.suppress(Exception):
            _open_response(cfg, b"{}")

        args = mock_conn.request.call_args
        assert args[0][1] == "/ollama/api/chat"


def _make_stream_response(*chunks: dict) -> MagicMock:
    """Build a mock response whose readline() yields NDJSON lines."""
    lines = [json.dumps(c).encode() + b"\n" for c in chunks] + [b""]
    resp = MagicMock()
    resp.status = 200
    resp.readline.side_effect = lines
    return resp


class TestStreamChat:
    def test_yields_tokens_in_order(self):
        cfg = _make_cfg()
        mock_conn = MagicMock()
        mock_resp = _make_stream_response(
            {"message": {"content": "Hello"}, "done": False},
            {"message": {"content": " world"}, "done": False},
            {"message": {"content": "!"}, "done": True},
        )
        with patch(
            "raztodo.infrastructure.llm.client._open_response",
            return_value=(mock_conn, mock_resp),
        ):
            tokens = list(stream_chat("hi", cfg=cfg))
        assert tokens == ["Hello", " world", "!"]

    def test_stops_at_done_true(self):
        cfg = _make_cfg()
        mock_conn = MagicMock()
        mock_resp = _make_stream_response(
            {"message": {"content": "tok"}, "done": True},
            {"message": {"content": "should-not-appear"}, "done": False},
        )
        with patch(
            "raztodo.infrastructure.llm.client._open_response",
            return_value=(mock_conn, mock_resp),
        ):
            tokens = list(stream_chat("hi", cfg=cfg))
        assert "should-not-appear" not in tokens

    def test_skips_empty_content_tokens(self):
        cfg = _make_cfg()
        mock_conn = MagicMock()
        mock_resp = _make_stream_response(
            {"message": {"content": ""}, "done": False},
            {"message": {"content": "real"}, "done": True},
        )
        with patch(
            "raztodo.infrastructure.llm.client._open_response",
            return_value=(mock_conn, mock_resp),
        ):
            tokens = list(stream_chat("hi", cfg=cfg))
        assert tokens == ["real"]

    def test_skips_malformed_json_lines(self):
        cfg = _make_cfg()
        mock_conn = MagicMock()
        resp = MagicMock()
        resp.status = 200
        resp.readline.side_effect = [
            b"not-json\n",
            json.dumps({"message": {"content": "ok"}, "done": True}).encode() + b"\n",
            b"",
        ]
        with patch(
            "raztodo.infrastructure.llm.client._open_response",
            return_value=(mock_conn, resp),
        ):
            tokens = list(stream_chat("hi", cfg=cfg))
        assert tokens == ["ok"]

    def test_closes_connection_after_stream(self):
        cfg = _make_cfg()
        mock_conn = MagicMock()
        mock_resp = _make_stream_response({"message": {"content": "x"}, "done": True})
        with patch(
            "raztodo.infrastructure.llm.client._open_response",
            return_value=(mock_conn, mock_resp),
        ):
            list(stream_chat("hi", cfg=cfg))
        mock_conn.close.assert_called_once()

    def test_closes_connection_on_exception(self):
        cfg = _make_cfg()
        mock_conn = MagicMock()
        resp = MagicMock()
        resp.status = 200
        resp.readline.side_effect = RuntimeError("network blip")
        with (
            patch(
                "raztodo.infrastructure.llm.client._open_response",
                return_value=(mock_conn, resp),
            ),
            pytest.raises(RuntimeError),
        ):
            list(stream_chat("hi", cfg=cfg))
        mock_conn.close.assert_called_once()

    def test_stream_is_true_in_payload(self):
        cfg = _make_cfg()
        captured = {}

        def fake_open_response(c, payload_bytes):
            captured["payload"] = json.loads(payload_bytes.decode())
            mock_conn = MagicMock()
            mock_resp = _make_stream_response({"message": {"content": "x"}, "done": True})
            return mock_conn, mock_resp

        with patch(
            "raztodo.infrastructure.llm.client._open_response",
            side_effect=fake_open_response,
        ):
            list(stream_chat("hi", cfg=cfg))

        assert captured["payload"]["stream"] is True

    def test_loads_default_config_when_cfg_none(self):
        mock_cfg = _make_cfg()
        mock_conn = MagicMock()
        mock_resp = _make_stream_response({"message": {"content": "x"}, "done": True})
        with (
            patch(
                "raztodo.infrastructure.llm.client.load_config",
                return_value=mock_cfg,
            ) as mock_load,
            patch(
                "raztodo.infrastructure.llm.client._open_response",
                return_value=(mock_conn, mock_resp),
            ),
        ):
            list(stream_chat("hi"))
        mock_load.assert_called_once()

    def test_empty_readline_ends_stream(self):
        """An immediate empty readline (connection closed) should produce no tokens."""
        cfg = _make_cfg()
        mock_conn = MagicMock()
        resp = MagicMock()
        resp.status = 200
        resp.readline.return_value = b""
        with patch(
            "raztodo.infrastructure.llm.client._open_response",
            return_value=(mock_conn, resp),
        ):
            tokens = list(stream_chat("hi", cfg=cfg))
        assert tokens == []


class TestOllamaClientError:
    def test_is_exception(self):
        err = OllamaClientError("boom")
        assert isinstance(err, Exception)

    def test_message_preserved(self):
        err = OllamaClientError("something went wrong")
        assert str(err) == "something went wrong"
