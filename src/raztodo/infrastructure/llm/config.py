import json
import os
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from raztodo.infrastructure.logger import get_logger
from raztodo.infrastructure.settings import Settings

logger = get_logger(__name__)

CONFIG_FILENAME = "llm.json"

DEFAULT_HOST = "http://localhost:11434"
DEFAULT_MODEL = None
DEFAULT_TIMEOUT = 120

DEFAULT_SYSTEM_PROMPT = (
    "You are a helpful productivity assistant. "
    "The user will give you a task in JSON format. "
    "Respond concisely and practically. "
    "Never repeat the raw JSON back to the user."
)


@dataclass
class OllamaConfig:
    host: str = DEFAULT_HOST
    model: str | None = None
    timeout: int = DEFAULT_TIMEOUT
    system_prompt: str = DEFAULT_SYSTEM_PROMPT

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "OllamaConfig":
        valid_keys = cls.__dataclass_fields__.keys()
        filtered = {k: v for k, v in data.items() if k in valid_keys}
        return cls(**filtered)


_settings = Settings()


def _config_path() -> Path:
    return _settings.data_dir / CONFIG_FILENAME


def load_config() -> OllamaConfig:
    """
    Load config from disk + override with environment variables.
    """
    cfg = _load_from_file()

    host = os.getenv("OLLAMA_HOST")
    if host:
        cfg.host = host.rstrip("/")

    model = os.getenv("OLLAMA_MODEL")
    if model:
        cfg.model = model

    timeout = os.getenv("OLLAMA_TIMEOUT")
    if timeout:
        try:
            cfg.timeout = int(timeout)
        except ValueError:
            logger.warning("Invalid OLLAMA_TIMEOUT=%r, ignoring", timeout)

    logger.debug(
        "Ollama config resolved: host=%s model=%s timeout=%d",
        cfg.host,
        cfg.model,
        cfg.timeout,
    )
    return cfg


def _load_from_file() -> OllamaConfig:
    path = _config_path()

    if not path.exists():
        logger.debug("No config file found at %s", path)
        return OllamaConfig()

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return OllamaConfig.from_dict(data)

    except (json.JSONDecodeError, TypeError) as exc:
        logger.warning("Failed to parse config %s: %s", path, exc)
        return OllamaConfig()


def save_config(cfg: OllamaConfig) -> Path:
    path = _config_path()

    path.write_text(
        json.dumps(cfg.to_dict(), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    logger.info("Config saved to %s", path)
    return path


def config_path() -> Path:
    return _config_path()
