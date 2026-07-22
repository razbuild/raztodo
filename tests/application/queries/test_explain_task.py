import json
from collections.abc import Generator
from unittest.mock import MagicMock, patch

import pytest

from raztodo.application.queries.explain_task import (
    MODE_PROMPTS,
    ExplainTaskUseCase,
    _task_to_json,
)
from raztodo.domain.exceptions import RazTodoException


def _make_task(
    id=1,
    title="Write tests",
    description="Cover the explain use-case",
    priority="high",
    due_date="2025-12-31",
    tags=None,
    project="raztodo",
    done=False,
    created_at="2025-01-01T00:00:00",
):
    task = MagicMock()
    task.id = id
    task.title = title
    task.description = description
    task.priority = priority
    task.due_date = due_date
    task.tags = tags
    task.project = project
    task.done = done
    task.created_at = created_at
    return task


@pytest.fixture()
def task():
    return _make_task()


@pytest.fixture()
def repo(task):
    r = MagicMock()
    r.get_task.side_effect = lambda task_id: task if task_id == task.id else None
    return r


@pytest.fixture()
def use_case(repo):
    return ExplainTaskUseCase(repo)


class TestTaskToJson:
    def test_all_fields_serialised(self, task):
        result = _task_to_json(task)
        data = json.loads(result)

        assert data["id"] == task.id
        assert data["title"] == task.title
        assert data["description"] == task.description
        assert data["priority"] == task.priority
        assert data["due_date"] == task.due_date
        assert data["tags"] == task.tags
        assert data["project"] == task.project
        assert data["done"] == task.done
        assert data["created_at"] == task.created_at

    def test_missing_attrs_use_defaults(self):
        empty = object()
        data = json.loads(_task_to_json(empty))

        assert data["id"] is None
        assert data["title"] == ""
        assert data["description"] == ""
        assert data["priority"] == ""
        assert data["due_date"] is None
        assert data["tags"] == []
        assert data["project"] is None
        assert data["done"] is False
        assert data["created_at"] == ""

    def test_non_ascii_characters_preserved(self):
        task = _make_task(title="Réunion équipe", description="Ünit ✓")
        data = json.loads(_task_to_json(task))
        assert data["title"] == "Réunion équipe"
        assert data["description"] == "Ünit ✓"

    def test_output_is_valid_json_string(self, task):
        result = _task_to_json(task)
        assert isinstance(result, str)
        json.loads(result)


class TestGetPrompt:
    def test_valid_mode_returns_prompt_containing_task_json(self, use_case, task):
        prompt = use_case._get_prompt(task.id, "short")
        assert task.title in prompt
        assert "short" not in prompt

    @pytest.mark.parametrize("mode", ["short", "deep", "plan"])
    def test_all_modes_produce_non_empty_prompt(self, use_case, task, mode):
        prompt = use_case._get_prompt(task.id, mode)
        assert len(prompt) > 0

    def test_unknown_mode_raises(self, use_case, task):
        with pytest.raises(RazTodoException, match="Unknown explain mode"):
            use_case._get_prompt(task.id, "turbo")

    def test_unknown_task_id_raises(self, use_case):
        with pytest.raises(RazTodoException, match="TaskNotFoundError"):
            use_case._get_prompt(999, "short")

    def test_prompt_contains_json_block(self, use_case, task):
        prompt = use_case._get_prompt(task.id, "deep")
        assert json.dumps(task.title) in prompt

    def test_repo_get_task_called_once(self, use_case, repo, task):
        use_case._get_prompt(task.id, "plan")
        repo.get_task.assert_called_once_with(task.id)

    def test_correct_mode_template_used(self, use_case, task):
        for mode, template in MODE_PROMPTS.items():
            prompt = use_case._get_prompt(task.id, mode)
            assert template[:20] in prompt


class TestExecute:
    def test_returns_chat_response(self, use_case, task):
        with patch(
            "raztodo.application.queries.explain_task.chat", return_value="Here is a summary."
        ) as mock_chat:
            result = use_case.execute(task.id, mode="short")

        assert result == "Here is a summary."
        mock_chat.assert_called_once()

    def test_does_not_override_system_prompt(self, use_case, task):
        """execute() should not pass `system`, so client.chat() falls back to cfg.system_prompt."""
        with patch("raztodo.application.queries.explain_task.chat", return_value="ok") as mock_chat:
            use_case.execute(task.id)

        _, kwargs = mock_chat.call_args
        assert "system" not in kwargs

    def test_default_mode_is_short(self, use_case, task):
        with patch("raztodo.application.queries.explain_task.chat", return_value="ok") as mock_chat:
            use_case.execute(task.id)

        prompt_arg = mock_chat.call_args[0][0]
        assert MODE_PROMPTS["short"][:20] in prompt_arg

    def test_ollama_error_wrapped_in_raztodo_exception(self, use_case, task):
        from raztodo.infrastructure.llm.client import OllamaClientError

        with (
            patch(
                "raztodo.application.queries.explain_task.chat",
                side_effect=OllamaClientError("conn refused"),
            ),
            pytest.raises(RazTodoException, match="OllamaError"),
        ):
            use_case.execute(task.id)

    def test_unknown_mode_raises_before_calling_chat(self, use_case, task):
        with (
            patch("raztodo.application.queries.explain_task.chat") as mock_chat,
            pytest.raises(RazTodoException, match="Unknown explain mode"),
        ):
            use_case.execute(task.id, mode="invalid")

        mock_chat.assert_not_called()

    def test_missing_task_raises_before_calling_chat(self, use_case):
        with (
            patch("raztodo.application.queries.explain_task.chat") as mock_chat,
            pytest.raises(RazTodoException, match="TaskNotFoundError"),
        ):
            use_case.execute(999)

        mock_chat.assert_not_called()


class TestStream:
    def _token_gen(self, *tokens):
        """Build a generator that yields the given tokens."""
        return (t for t in tokens)

    def test_yields_tokens_from_stream_chat(self, use_case, task):
        tokens = ["Here", " is", " a", " plan."]
        with patch(
            "raztodo.application.queries.explain_task.stream_chat", return_value=iter(tokens)
        ):
            result = list(use_case.stream(task.id, mode="plan"))

        assert result == tokens

    def test_returns_generator(self, use_case, task):
        with patch("raztodo.application.queries.explain_task.stream_chat", return_value=iter([])):
            result = use_case.stream(task.id)

        assert isinstance(result, Generator)

    def test_does_not_override_system_prompt(self, use_case, task):
        with patch(
            "raztodo.application.queries.explain_task.stream_chat", return_value=iter([])
        ) as mock_stream:
            list(use_case.stream(task.id))

        _, kwargs = mock_stream.call_args
        assert "system" not in kwargs

    def test_default_mode_is_short(self, use_case, task):
        with patch(
            "raztodo.application.queries.explain_task.stream_chat", return_value=iter([])
        ) as mock_stream:
            list(use_case.stream(task.id))

        prompt_arg = mock_stream.call_args[0][0]
        assert MODE_PROMPTS["short"][:20] in prompt_arg

    def test_ollama_error_wrapped_in_raztodo_exception(self, use_case, task):
        from raztodo.infrastructure.llm.client import OllamaClientError

        def bad_stream(*_, **__):
            raise OllamaClientError("timeout")

        with (
            patch(
                "raztodo.application.queries.explain_task.stream_chat",
                side_effect=bad_stream,
            ),
            pytest.raises(RazTodoException, match="OllamaError"),
        ):
            list(use_case.stream(task.id))

    def test_unknown_mode_raises_before_streaming(self, use_case, task):
        with (
            patch("raztodo.application.queries.explain_task.stream_chat") as mock_stream,
            pytest.raises(RazTodoException, match="Unknown explain mode"),
        ):
            list(use_case.stream(task.id, mode="bogus"))

        mock_stream.assert_not_called()

    def test_all_tokens_consumed(self, use_case, task):
        tokens = [f"token{i}" for i in range(50)]
        with patch(
            "raztodo.application.queries.explain_task.stream_chat", return_value=iter(tokens)
        ):
            result = list(use_case.stream(task.id, mode="deep"))

        assert result == tokens


class TestPromptConsistency:
    """Both execute() and stream() must send the same prompt for the same inputs."""

    def test_execute_and_stream_use_same_prompt(self, use_case, task):
        captured = {}

        def fake_chat(prompt, system=None):
            captured["execute"] = prompt
            return "ok"

        def fake_stream(prompt, system=None):
            captured["stream"] = prompt
            return iter([])

        with (
            patch("raztodo.application.queries.explain_task.chat", side_effect=fake_chat),
            patch("raztodo.application.queries.explain_task.stream_chat", side_effect=fake_stream),
        ):
            use_case.execute(task.id, mode="deep")
            list(use_case.stream(task.id, mode="deep"))

        assert captured["execute"] == captured["stream"]
