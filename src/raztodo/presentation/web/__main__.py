"""Entry point for the RazTodo web UI.

Run with:
    rt-web
or:
    python -m raztodo.presentation.web
"""

from __future__ import annotations


def main() -> None:
    try:
        import uvicorn
    except ImportError as err:
        raise SystemExit("uvicorn is not installed. Run: uv sync --group web") from err

    uvicorn.run(
        "raztodo.presentation.web.app:app",
        host="127.0.0.1",
        port=8000,
        reload=False,
    )


if __name__ == "__main__":
    main()
