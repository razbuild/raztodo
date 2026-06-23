from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from raztodo.infrastructure.version import get_version
from raztodo.presentation.web.routes.tasks import router as tasks_router
from raztodo.presentation.web.ui import render_index_html

_STATIC_DIR = Path(__file__).parent / "static"

app = FastAPI(
    title="RazTodo",
    description="Local web interface for RazTodo",
    version=get_version(),
)

app.mount("/static", StaticFiles(directory=_STATIC_DIR), name="static")

app.include_router(tasks_router)


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
async def index() -> str:
    """Serve the single-page UI."""
    return render_index_html()
