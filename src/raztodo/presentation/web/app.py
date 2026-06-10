"""FastAPI application for RazTodo web UI."""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from raztodo.presentation.web.routes.tasks import router as tasks_router
from raztodo.presentation.web.ui import render_index_html

app = FastAPI(
    title="RazTodo",
    description="Local web interface for RazTodo",
    version="0.4.1",
)

app.include_router(tasks_router)


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
async def index() -> str:
    """Serve the single-page UI."""
    return render_index_html()
