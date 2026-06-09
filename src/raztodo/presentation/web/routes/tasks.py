from __future__ import annotations

import json
import tempfile
import os
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse

from raztodo.domain.exceptions import RazTodoException
from raztodo.presentation.web.dependencies import (
    get_clear_uc,
    get_create_uc,
    get_delete_uc,
    get_export_uc,
    get_import_uc,
    get_list_uc,
    get_mark_done_uc,
    get_update_uc,
)
from raztodo.presentation.web.schemas import (
    ClearResponse,
    ImportResponse,
    TaskCreate,
    TaskResponse,
    TaskUpdate,
)

router = APIRouter(prefix="/api/tasks", tags=["tasks"])


def _task_to_response(task: Any) -> TaskResponse:
    return TaskResponse(
        id=task.id,
        title=task.title,
        description=getattr(task, "description", "") or "",
        done=getattr(task, "done", False),
        created_at=getattr(task, "created_at", "") or "",
        priority=getattr(task, "priority", "") or "",
        due_date=getattr(task, "due_date", None),
        tags=list(getattr(task, "tags", None) or []),
        project=getattr(task, "project", None),
    )


def _domain_error(e: Exception) -> HTTPException:
    return HTTPException(status_code=400, detail=str(e))


@router.get("", response_model=list[TaskResponse])
def list_tasks(
    q: str | None = None,
    uc: Any = Depends(get_list_uc),
) -> list[TaskResponse]:
    try:
        if q:
            tasks = uc.execute()
            tasks = [t for t in tasks if q.lower() in t.title.lower()
                     or q.lower() in (getattr(t, "description", "") or "").lower()]
        else:
            tasks = uc.execute()
        return [_task_to_response(t) for t in tasks]
    except RazTodoException as e:
        raise _domain_error(e)


@router.post("", response_model=TaskResponse, status_code=201)
def create_task(
    body: TaskCreate,
    list_uc: Any = Depends(get_list_uc),
    create_uc: Any = Depends(get_create_uc),
) -> TaskResponse:
    try:
        task_id: int = create_uc.execute(
            title=body.title,
            description=body.description,
            priority=body.priority or "",
            due_date=body.due_date,
            tags=body.tags or [],
            project=body.project,
        )
        tasks = list_uc.execute()
        task = next((t for t in tasks if t.id == task_id), None)
        if task is None:
            raise HTTPException(status_code=500, detail="Task created but could not be retrieved")
        return _task_to_response(task)
    except RazTodoException as e:
        raise _domain_error(e)


@router.put("/{task_id}", response_model=TaskResponse)
def update_task(
    task_id: int,
    body: TaskUpdate,
    list_uc: Any = Depends(get_list_uc),
    update_uc: Any = Depends(get_update_uc),
) -> TaskResponse:
    try:
        update_uc.execute(
            task_id,
            title=body.title,
            description=body.description,
            priority=body.priority,
            due_date=body.due_date,
            tags=body.tags,
            project=body.project,
        )
        tasks = list_uc.execute()
        task = next((t for t in tasks if t.id == task_id), None)
        if task is None:
            raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
        return _task_to_response(task)
    except RazTodoException as e:
        raise _domain_error(e)


@router.delete("/{task_id}", status_code=204)
def delete_task(
    task_id: int,
    uc: Any = Depends(get_delete_uc),
) -> None:
    try:
        uc.execute(task_id)
    except RazTodoException as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/clear", response_model=ClearResponse)
def clear_tasks(uc: Any = Depends(get_clear_uc)) -> ClearResponse:
    try:
        deleted: int = uc.execute(confirmed=True)
        return ClearResponse(deleted=deleted)
    except RazTodoException as e:
        raise _domain_error(e)


@router.patch("/{task_id}/done", response_model=TaskResponse)
def toggle_done(
    task_id: int,
    list_uc: Any = Depends(get_list_uc),
    mark_uc: Any = Depends(get_mark_done_uc),
) -> TaskResponse:
    try:
        tasks = list_uc.execute()
        task = next((t for t in tasks if t.id == task_id), None)
        if task is None:
            raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
        mark_uc.execute(task_id, done=not task.done)
        tasks = list_uc.execute()
        task = next((t for t in tasks if t.id == task_id), None)
        if task is None:
            raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
        return _task_to_response(task)
    except RazTodoException as e:
        raise _domain_error(e)


@router.post("/export")
def export_tasks(
    project: str | None = None,
    uc: Any = Depends(get_export_uc)
) -> FileResponse:
    try:
        tmp = tempfile.NamedTemporaryFile(
            suffix=".json", delete=False, mode="w", encoding="utf-8"
        )
        tmp.close()
        uc.execute(tmp.name)
        return FileResponse(
            path=tmp.name,
            media_type="application/json",
            filename="raztodo_export.json",
        )
    except RazTodoException as e:
        raise _domain_error(e)


@router.post("/import", response_model=ImportResponse)
def import_tasks(
    tasks: list[TaskCreate],
    uc: Any = Depends(get_import_uc),
) -> ImportResponse:
    try:
        tmp = tempfile.NamedTemporaryFile(
            suffix=".json", delete=False, mode="w", encoding="utf-8"
        )
        json.dump([t.model_dump() for t in tasks], tmp, ensure_ascii=False)
        tmp.close()

        result = uc.execute(tmp.name, upsert=True)
        os.unlink(tmp.name)

        if isinstance(result, dict):
            return ImportResponse(
                inserted=result.get("inserted", 0),
                updated=result.get("updated", 0),
            )
        return ImportResponse(inserted=int(result), updated=0)
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Import failed: {e}")