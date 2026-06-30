from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse

from raztodo.domain.exceptions import RazTodoException
from raztodo.presentation.web.dependencies import get_explain_uc

router = APIRouter(prefix="/api/tasks", tags=["tasks"])


@router.get("/{task_id}/explain")
def explain_task(
    task_id: int,
    mode: str = "short",
    uc: Any = Depends(get_explain_uc),  # noqa: B008
) -> StreamingResponse:
    """
    Stream the LLM explanation as Server-Sent Events (SSE).
    Each event: data: <token>\n\n
    Final event: data: [DONE]\n\n
    """
    if mode not in ("short", "deep", "plan"):
        raise HTTPException(status_code=422, detail="mode must be: short, deep, or plan")

    def _sse_generator():
        try:
            for token in uc.stream(task_id, mode=mode):
                safe = token.replace("\n", "\\n")
                yield f"data: {safe}\n\n"
        except RazTodoException as _exc:
            yield "event: error\ndata: An internal error occurred.\n\n"
        finally:
            yield "data: [DONE]\n\n"

    return StreamingResponse(
        _sse_generator(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
