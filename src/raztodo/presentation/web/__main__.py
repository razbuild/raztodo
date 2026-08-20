from __future__ import annotations

import os


def web_host() -> str:
    return os.getenv("RAZTODO_WEB_HOST", "127.0.0.1")


def web_port() -> int:
    return int(os.getenv("RAZTODO_WEB_PORT", "8000"))


def main() -> None:
    import importlib.util

    if importlib.util.find_spec("fastapi") is None or importlib.util.find_spec("uvicorn") is None:
        raise SystemExit(
            "Web dependencies are not installed. Install with: pip install 'raztodo[web]'"
        )

    import uvicorn  # type: ignore[import]

    uvicorn.run(
        "raztodo.presentation.web.app:app",
        host=web_host(),
        port=web_port(),
        reload=False,
    )


if __name__ == "__main__":
    main()
