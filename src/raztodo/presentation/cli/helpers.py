import json
from collections.abc import Callable
from typing import Any

from raztint import err, ok, tint

from raztodo.domain.exceptions import ERROR_TYPE_MAP
from raztodo.domain.task_entity import TaskEntity

ERROR_TYPE_PAIRS: list[tuple[type[BaseException], str]] = [
    (exc_class, key) for key, exc_class in ERROR_TYPE_MAP.items()
]


def parse_tags(tags_str: str | None) -> list[str] | None:
    if not tags_str:
        return None
    tags = [t.strip() for t in tags_str.split(",") if t.strip()]
    return tags if tags else None


def task_to_dict(task: TaskEntity) -> dict[str, Any]:
    fields: list[tuple[str, Any]] = [
        ("id", None),
        ("title", ""),
        ("description", ""),
        ("done", False),
        ("created_at", ""),
        ("priority", ""),
        ("due_date", None),
        ("tags", []),
        ("project", None),
    ]
    return {name: getattr(task, name, default) for name, default in fields}


def output_json(data: Any) -> None:
    print(json.dumps(data, ensure_ascii=False))


def output_success(message: str, json_mode: bool = False, **json_data: Any) -> None:
    if json_mode:
        output_json({"ok": True, **json_data})
    else:
        print(f"{ok()} {message}")


def output_error(
    error: BaseException,
    json_mode: bool = False,
    error_type: str | None = None,
    **json_data: Any,
) -> None:
    if json_mode:
        error_data: dict[str, Any] = {"ok": False, "error": str(error), **json_data}
        if error_type:
            error_data["type"] = error_type
        output_json(error_data)
    else:
        print(f"{err()} {error}")


def handle_command_error(
    error: BaseException,
    args: Any,
    json_mode_attr: str = "json",
    **json_extras: Any,
) -> int:
    json_mode: bool = getattr(args, json_mode_attr, False)

    json_data: dict[str, Any] = {}
    task_id = getattr(args, "id", None)
    filepath = getattr(args, "filepath", None)
    if task_id is not None:
        json_data["id"] = task_id
    if filepath is not None:
        json_data["filepath"] = filepath
    json_data.update(json_extras)

    error_type: str | None = next(
        (
            mapped
            for exc_class, mapped in ERROR_TYPE_PAIRS
            if isinstance(error, exc_class)
        ),
        None,
    )

    output_error(error, json_mode, error_type, **json_data)
    return 1


def format_task(task: TaskEntity) -> None:
    done: bool = getattr(task, "done", False)
    status_icon: str = ok() if done else err()
    status_text: str = tint.green("[Done]") if done else tint.yellow("[Pending]")

    created_raw: str = getattr(task, "created_at", "")
    created_date: str = created_raw.split(" ")[0] if created_raw else "N/A"

    priority: str = getattr(task, "priority", "") or ""
    project: str = getattr(task, "project", None) or ""
    tags: list[str] = getattr(task, "tags", []) or []
    due_date: str = getattr(task, "due_date", None) or ""

    meta_fields: list[tuple[Any, Callable[[Any], str]]] = [
        (priority, lambda v: f"Priority: {tint.yellow(v)}"),
        (project, lambda v: f"Project: {tint.cyan(v)}"),
        (tags, lambda v: f"Tags: {', '.join([tint.magenta(t) for t in v])}"),
        (due_date, lambda v: f"Due: {tint.gray(v)}"),
    ]

    metadata_parts: list[str] = [fmt(value) for value, fmt in meta_fields if value]
    metadata_parts.append(f"Created: {tint.gray(created_date)}")

    print(
        f"{status_icon} {tint.blue(f'#{task.id}')} {task.title} {tint.gray(f'{status_text}')}"
    )

    description: str = getattr(task, "description", "") or ""
    if description:
        print(f"   {tint.gray(description)}")

    print(f"   {tint.gray(' | '.join(metadata_parts))}")
    print()


def format_tasks_list(tasks: list[TaskEntity], json_mode: bool = False) -> None:
    if json_mode:
        output_json([task_to_dict(t) for t in tasks])
    else:
        for task in tasks:
            format_task(task)
