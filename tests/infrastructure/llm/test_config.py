import json
from unittest.mock import Mock

import pytest

from raztodo.infrastructure.llm import config
from raztodo.infrastructure.llm.config import (
    CONFIG_FILENAME,
    DEFAULT_HOST,
    DEFAULT_MODEL,
    DEFAULT_SYSTEM_PROMPT,
    DEFAULT_TIMEOUT,
    OllamaConfig,
    _load_from_file,
    config_path,
    load_config,
    save_config,
)


@pytest.fixture
def config_dir(tmp_path, monkeypatch):
    from raztodo.infrastructure.llm import config

    monkeypatch.setattr(
        config,
        "_config_path",
        lambda: tmp_path / CONFIG_FILENAME,
    )

    return tmp_path


def test_to_dict():
    cfg = OllamaConfig()

    assert cfg.to_dict() == {
        "host": DEFAULT_HOST,
        "model": DEFAULT_MODEL,
        "timeout": DEFAULT_TIMEOUT,
        "system_prompt": DEFAULT_SYSTEM_PROMPT,
    }


def test_from_dict():
    cfg = OllamaConfig.from_dict(
        {
            "host": "http://server",
            "model": "mistral",
            "timeout": 30,
            "system_prompt": "hello",
        }
    )

    assert cfg.host == "http://server"
    assert cfg.model == "mistral"
    assert cfg.timeout == 30
    assert cfg.system_prompt == "hello"


def test_from_dict_ignores_unknown_keys():
    cfg = OllamaConfig.from_dict(
        {
            "host": "http://server",
            "unknown": "ignored",
        }
    )

    assert cfg.host == "http://server"
    assert not hasattr(cfg, "unknown")


def test_load_from_file_missing(config_dir):
    cfg = _load_from_file()
    assert cfg == OllamaConfig()


def test_load_from_file(config_dir):
    path = config_dir / CONFIG_FILENAME

    path.write_text(
        json.dumps(
            {
                "host": "http://example",
                "model": "phi4",
                "timeout": 99,
                "system_prompt": "test",
            }
        )
    )

    cfg = _load_from_file()

    assert cfg.host == "http://example"
    assert cfg.model == "phi4"
    assert cfg.timeout == 99
    assert cfg.system_prompt == "test"


def test_load_from_file_invalid_json(config_dir):
    path = config_dir / CONFIG_FILENAME
    path.write_text("{broken json")

    cfg = _load_from_file()

    assert cfg == OllamaConfig()


def test_load_config_env_overrides(monkeypatch):
    monkeypatch.setenv("OLLAMA_HOST", "http://env:11434/")
    monkeypatch.setenv("OLLAMA_MODEL", "deepseek")
    monkeypatch.setenv("OLLAMA_TIMEOUT", "55")

    cfg = load_config()

    assert cfg.host == "http://env:11434"
    assert cfg.model == "deepseek"
    assert cfg.timeout == 55


def test_load_config_invalid_timeout(monkeypatch):
    monkeypatch.setenv("OLLAMA_TIMEOUT", "not-an-int")

    cfg = load_config()

    assert cfg.timeout == DEFAULT_TIMEOUT


def test_save_config(config_dir):
    cfg = OllamaConfig(
        host="http://host",
        model="phi4",
        timeout=42,
        system_prompt="prompt",
    )

    path = save_config(cfg)

    assert path == config_dir / CONFIG_FILENAME
    assert path.exists()

    loaded = json.loads(path.read_text())

    assert loaded == cfg.to_dict()


def test_config_path(config_dir):
    assert config_path() == config_dir / CONFIG_FILENAME


def test_invalid_timeout_logs_warning(monkeypatch):
    warning = Mock()
    monkeypatch.setattr(config.logger, "warning", warning)

    monkeypatch.setenv("OLLAMA_TIMEOUT", "abc")

    config.load_config()

    warning.assert_called_once_with(
        "Invalid OLLAMA_TIMEOUT=%r, ignoring",
        "abc",
    )


def test_invalid_json_logs_warning(config_dir, monkeypatch):
    warning = Mock()
    monkeypatch.setattr(config.logger, "warning", warning)

    path = config_dir / CONFIG_FILENAME
    path.write_text("{invalid")

    config._load_from_file()

    warning.assert_called_once()

    message, *_ = warning.call_args.args
    assert message.startswith("Failed to parse config")


def test_load_config_without_env(config_dir, monkeypatch):
    monkeypatch.delenv("OLLAMA_HOST", raising=False)
    monkeypatch.delenv("OLLAMA_MODEL", raising=False)
    monkeypatch.delenv("OLLAMA_TIMEOUT", raising=False)

    cfg = load_config()

    assert cfg.host == DEFAULT_HOST
    assert cfg.model == DEFAULT_MODEL
    assert cfg.timeout == DEFAULT_TIMEOUT
