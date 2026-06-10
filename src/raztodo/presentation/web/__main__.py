from __future__ import annotations


def main() -> None:
    import importlib.util

    if importlib.util.find_spec("fastapi") is None or importlib.util.find_spec("uvicorn") is None:
        raise SystemExit(
            "Web dependencies are not installed. Install with: pip install 'raztodo[web]'"
        )

    import uvicorn  # type: ignore[import]

    uvicorn.run(
        "raztodo.presentation.web.app:app",
        host="127.0.0.1",
        port=8000,
        reload=False,
    )


if __name__ == "__main__":
    main()
