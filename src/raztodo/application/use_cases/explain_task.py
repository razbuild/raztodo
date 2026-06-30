import json
from collections.abc import Generator

from raztodo.domain.exceptions import RazTodoException
from raztodo.domain.task_repository import TaskRepository
from raztodo.infrastructure.llm.client import OllamaClientError, chat, stream_chat
from raztodo.infrastructure.logger import get_logger

logger = get_logger(__name__)

SYSTEM_PROMPT = (
    "You are a helpful productivity assistant. "
    "The user will give you a task in JSON format. "
    "Respond concisely and practically. "
    "Never repeat the raw JSON back to the user."
)

MODE_PROMPTS: dict[str, str] = {
    "short": (
        "Give a 2 or 3 sentence plain-language summary of this task. "
        "What is it about and why might it matter?\n\nTask JSON:\n{json}"
    ),
    "deep": (
        "Analyse this task in depth. Cover: goal, potential blockers, "
        "suggested approach, priority rationale, and any risks. "
        "Be structured but concise.\n\nTask JSON:\n{json}"
    ),
    "plan": (
        "Break this task into a concrete, numbered step-by-step action plan. "
        "Each step should be actionable and specific. "
        "Finish with a time estimate.\n\nTask JSON:\n{json}"
    ),
}


class ExplainTaskUseCase:
    """Fetches a task by ID and asks Ollama to explain / plan it."""

    def __init__(self, repo: TaskRepository) -> None:
        self.repo = repo

    def _get_prompt(self, task_id: int, mode: str) -> str:
        if mode not in MODE_PROMPTS:
            raise RazTodoException(f"Unknown explain mode '{mode}'. Choose: short, deep, plan")
        task = self.repo.get_task(task_id)
        if task is None:
            raise RazTodoException(f"TaskNotFoundError: No task with id={task_id}")
        return MODE_PROMPTS[mode].format(json=_task_to_json(task))

    def execute(self, task_id: int, mode: str = "short") -> str:
        """Blocking — used by the CLI."""
        prompt = self._get_prompt(task_id, mode)
        logger.info("Explaining task id=%d mode=%s (blocking)", task_id, mode)
        try:
            return chat(prompt, system=SYSTEM_PROMPT)
        except OllamaClientError as exc:
            raise RazTodoException(f"OllamaError: {exc}") from exc

    def stream(self, task_id: int, mode: str = "short") -> Generator[str, None, None]:
        """Streaming — used by the web endpoint; yields tokens as they arrive."""
        prompt = self._get_prompt(task_id, mode)
        logger.info("Explaining task id=%d mode=%s (streaming)", task_id, mode)
        try:
            yield from stream_chat(prompt, system=SYSTEM_PROMPT)
        except OllamaClientError as exc:
            raise RazTodoException(f"OllamaError: {exc}") from exc


def _task_to_json(task: object) -> str:
    data = {
        "id": getattr(task, "id", None),
        "title": getattr(task, "title", ""),
        "description": getattr(task, "description", ""),
        "priority": getattr(task, "priority", ""),
        "due_date": getattr(task, "due_date", None),
        "tags": getattr(task, "tags", []),
        "project": getattr(task, "project", None),
        "done": getattr(task, "done", False),
        "created_at": getattr(task, "created_at", ""),
    }
    return json.dumps(data, ensure_ascii=False, indent=2)
