from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from raztodo.infrastructure.version import get_version
from raztodo.presentation.web.routes.explain import router as explain_router
from raztodo.presentation.web.routes.tasks import router as tasks_router

_STATIC_DIR = Path(__file__).parent / "static"
_TEMPLATES_DIR = Path(__file__).parent / "templates"
_INDEX_FILE = _TEMPLATES_DIR / "index.html"

app = FastAPI(
    title="RazTodo",
    description="Local web interface for RazTodo",
    version=get_version(),
)

app.mount("/static", StaticFiles(directory=_STATIC_DIR), name="static")

app.include_router(tasks_router)
app.include_router(explain_router)


@app.get("/", response_class=FileResponse, include_in_schema=False)
async def index() -> FileResponse:
    """Serve the single-page UI."""

    if not _INDEX_FILE.is_file():
        raise HTTPException(
            status_code=500,
            detail="UI template 'index.html' is missing.",
        )

    return FileResponse(_INDEX_FILE)
