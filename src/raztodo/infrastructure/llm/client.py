import json
from collections.abc import Generator
from http.client import HTTPConnection, HTTPSConnection
from urllib.parse import urlparse

from raztodo.infrastructure.llm.config import OllamaConfig, load_config
from raztodo.infrastructure.logger import get_logger

logger = get_logger(__name__)


def _get_connection(host: str) -> tuple[HTTPConnection | HTTPSConnection, str]:
    parsed = urlparse(host)
    netloc = parsed.netloc or parsed.path
    path_prefix = parsed.path if parsed.netloc else ""
    if parsed.scheme == "https":
        return HTTPSConnection(netloc), path_prefix
    return HTTPConnection(netloc), path_prefix


def _build_messages(prompt: str, system_message: str) -> list[dict[str, str]]:
    messages: list[dict[str, str]] = []
    if system_message:
        messages.append({"role": "system", "content": system_message})
    messages.append({"role": "user", "content": prompt})
    return messages


def _open_response(cfg: OllamaConfig, payload: bytes):
    """Open HTTP connection, send request, return (conn, response)."""
    conn, path_prefix = _get_connection(cfg.host)
    endpoint = f"{path_prefix}/api/chat"

    logger.debug(
        "Ollama request: host=%s model=%s endpoint=%s timeout=%d",
        cfg.host,
        cfg.model,
        endpoint,
        cfg.timeout,
    )

    try:
        conn.connect()
        conn.request(
            "POST",
            endpoint,
            body=payload,
            headers={
                "Content-Type": "application/json",
                "Content-Length": str(len(payload)),
            },
        )
        conn.sock.settimeout(cfg.timeout)
        response = conn.getresponse()
    except OSError as exc:
        conn.close()
        raise OllamaClientError(
            f"Cannot connect to Ollama at '{cfg.host}'. "
            "Make sure Ollama is running: https://ollama.com"
        ) from exc

    if response.status == 404:
        conn.close()
        raise OllamaClientError(
            f"Model '{cfg.model}' not found on Ollama. "
            f"Run 'ollama list' to see available models, "
            f"or 'ollama pull {cfg.model}' to download it."
        )

    if response.status != 200:
        raw = response.read().decode("utf-8")
        conn.close()
        raise OllamaClientError(f"Ollama returned HTTP {response.status}: {raw[:200]}")

    return conn, response


def chat(prompt: str, system: str = "", cfg: OllamaConfig | None = None) -> str:
    """
    Send a prompt to Ollama and return the full response text (blocking).

    Used by the CLI path.
    """
    if cfg is None:
        cfg = load_config()

    payload = json.dumps(
        {
            "model": cfg.model,
            "messages": _build_messages(prompt, system or cfg.system_prompt),
            "stream": False,
        },
        ensure_ascii=False,
    ).encode("utf-8")

    conn, response = _open_response(cfg, payload)
    try:
        raw = response.read().decode("utf-8")
    finally:
        conn.close()

    try:
        return json.loads(raw)["message"]["content"]
    except (json.JSONDecodeError, KeyError) as exc:
        raise OllamaClientError(f"Unexpected Ollama response format: {raw[:200]}") from exc


def stream_chat(
    prompt: str,
    system: str = "",
    cfg: OllamaConfig | None = None,
) -> Generator[str, None, None]:
    """
    Send a prompt to Ollama and yield tokens as they arrive.

    Used by the web streaming endpoint.

    Yields:
        Individual content tokens (strings) as produced by the model.

    Raises:
        OllamaClientError: On connection failure or bad response status.
    """
    if cfg is None:
        cfg = load_config()

    payload = json.dumps(
        {
            "model": cfg.model,
            "messages": _build_messages(prompt, system or cfg.system_prompt),
            "stream": True,
        },
        ensure_ascii=False,
    ).encode("utf-8")

    conn, response = _open_response(cfg, payload)

    try:
        while True:
            line = response.readline()
            if not line:
                break
            try:
                chunk = json.loads(line.decode("utf-8"))
            except json.JSONDecodeError:
                continue

            token = chunk.get("message", {}).get("content", "")
            if token:
                yield token

            if chunk.get("done"):
                break
    finally:
        conn.close()


class OllamaClientError(Exception):
    """Raised when the Ollama client encounters an error."""
